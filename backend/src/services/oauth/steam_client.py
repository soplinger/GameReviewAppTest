"""Steam OAuth client for authentication and library syncing."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from authlib.integrations.httpx_client import AsyncOAuth2Client
import httpx

from ...core.config import settings
from ...core.logging import get_logger

logger = get_logger(__name__)


class SteamOAuthClient:
    """
    Steam OAuth client using OpenID authentication.
    
    Steam uses OpenID 2.0 for authentication, not OAuth 2.0.
    Library data is accessed via Steam Web API.
    """
    
    def __init__(self):
        self.api_key = settings.STEAM_API_KEY
        self.openid_url = "https://steamcommunity.com/openid/login"
        self.api_base_url = "https://api.steampowered.com"
        
    async def get_authorization_url(self, redirect_uri: str) -> str:
        """
        Generate Steam OpenID authorization URL.
        
        Args:
            redirect_uri: Callback URL after authentication
            
        Returns:
            Authorization URL to redirect user to
        """
        params = {
            "openid.ns": "http://specs.openid.net/auth/2.0",
            "openid.mode": "checkid_setup",
            "openid.return_to": redirect_uri,
            "openid.realm": redirect_uri.rsplit("/", 1)[0],  # Base URL
            "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
            "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
        }
        
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        auth_url = f"{self.openid_url}?{query_string}"
        
        logger.info("steam_auth_url_generated", redirect_uri=redirect_uri)
        return auth_url
    
    async def verify_authentication(self, params: Dict[str, str]) -> Optional[str]:
        """
        Verify Steam OpenID response and extract Steam ID.
        
        Args:
            params: Query parameters from callback URL
            
        Returns:
            Steam ID (64-bit) if valid, None otherwise
        """
        try:
            # Change mode to check_authentication
            verify_params = dict(params)
            verify_params["openid.mode"] = "check_authentication"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.openid_url,
                    data=verify_params,
                    timeout=10.0
                )
                
                if response.status_code == 200 and "is_valid:true" in response.text:
                    # Extract Steam ID from claimed_id
                    claimed_id = params.get("openid.claimed_id", "")
                    if claimed_id:
                        steam_id = claimed_id.split("/")[-1]
                        logger.info("steam_auth_verified", steam_id=steam_id)
                        return steam_id
                        
            logger.warning("steam_auth_failed", reason="invalid_response")
            return None
            
        except Exception as e:
            logger.error("steam_auth_error", error=str(e))
            return None
    
    async def get_user_info(self, steam_id: str) -> Optional[Dict[str, Any]]:
        """
        Get Steam user profile information.
        
        Args:
            steam_id: Steam ID (64-bit)
            
        Returns:
            User profile data or None if error
        """
        try:
            url = f"{self.api_base_url}/ISteamUser/GetPlayerSummaries/v0002/"
            params = {
                "key": self.api_key,
                "steamids": steam_id
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                players = data.get("response", {}).get("players", [])
                
                if players:
                    player = players[0]
                    logger.info("steam_user_info_retrieved", steam_id=steam_id)
                    return {
                        "steam_id": player.get("steamid"),
                        "username": player.get("personaname"),
                        "avatar_url": player.get("avatarfull"),
                        "profile_url": player.get("profileurl")
                    }
                    
            logger.warning("steam_user_not_found", steam_id=steam_id)
            return None
            
        except Exception as e:
            logger.error("steam_user_info_error", steam_id=steam_id, error=str(e))
            return None
    
    async def get_owned_games(self, steam_id: str) -> list[Dict[str, Any]]:
        """
        Get list of games owned by Steam user.
        
        Args:
            steam_id: Steam ID (64-bit)
            
        Returns:
            List of game data with playtime information
        """
        try:
            url = f"{self.api_base_url}/IPlayerService/GetOwnedGames/v0001/"
            params = {
                "key": self.api_key,
                "steamid": steam_id,
                "include_appinfo": 1,
                "include_played_free_games": 1
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=30.0)
                response.raise_for_status()
                
                data = response.json()
                games = data.get("response", {}).get("games", [])
                
                logger.info(
                    "steam_games_retrieved",
                    steam_id=steam_id,
                    game_count=len(games)
                )
                
                # Transform to our format
                return [
                    {
                        "platform_game_id": str(game["appid"]),
                        "name": game.get("name", f"App {game['appid']}"),
                        "playtime_hours": round(game.get("playtime_forever", 0) / 60, 2),
                        "last_played_at": (
                            datetime.fromtimestamp(game["rtime_last_played"])
                            if game.get("rtime_last_played")
                            else None
                        )
                    }
                    for game in games
                ]
                
        except Exception as e:
            logger.error("steam_games_error", steam_id=steam_id, error=str(e))
            return []
    
    async def get_achievements(
        self,
        steam_id: str,
        app_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get achievement data for a specific game.
        
        Args:
            steam_id: Steam ID (64-bit)
            app_id: Steam application ID
            
        Returns:
            Achievement data or None if error
        """
        try:
            url = f"{self.api_base_url}/ISteamUserStats/GetPlayerAchievements/v0001/"
            params = {
                "key": self.api_key,
                "steamid": steam_id,
                "appid": app_id
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                achievements = data.get("playerstats", {}).get("achievements", [])
                
                achieved_count = sum(1 for a in achievements if a.get("achieved") == 1)
                
                logger.info(
                    "steam_achievements_retrieved",
                    steam_id=steam_id,
                    app_id=app_id,
                    achieved=achieved_count,
                    total=len(achievements)
                )
                
                return {
                    "total": len(achievements),
                    "achieved": achieved_count,
                    "achievements": achievements
                }
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                # Game doesn't have achievements
                logger.debug("steam_no_achievements", app_id=app_id)
                return None
            logger.error("steam_achievements_error", steam_id=steam_id, app_id=app_id, error=str(e))
            return None
        except Exception as e:
            logger.error("steam_achievements_error", steam_id=steam_id, app_id=app_id, error=str(e))
            return None
