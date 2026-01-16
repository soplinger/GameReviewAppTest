"""Xbox Live OAuth client for authentication and library syncing."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from authlib.integrations.httpx_client import AsyncOAuth2Client
import httpx

from ...core.config import settings
from ...core.logging import get_logger

logger = get_logger(__name__)


class XboxOAuthClient:
    """
    Xbox Live OAuth 2.0 client.
    
    Handles Xbox/Microsoft authentication and retrieves user library and achievement data.
    """
    
    def __init__(self):
        self.client_id = settings.XBOX_CLIENT_ID
        self.client_secret = settings.XBOX_CLIENT_SECRET
        self.authorization_endpoint = "https://login.live.com/oauth20_authorize.srf"
        self.token_endpoint = "https://login.live.com/oauth20_token.srf"
        self.xbox_auth_url = "https://user.auth.xboxlive.com/user/authenticate"
        self.xsts_auth_url = "https://xsts.auth.xboxlive.com/xsts/authorize"
        self.api_base_url = "https://xbl.io/api/v2"
        
    async def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        """
        Generate Microsoft/Xbox OAuth authorization URL.
        
        Args:
            redirect_uri: Callback URL after authentication
            state: CSRF protection state token
            
        Returns:
            Authorization URL to redirect user to
        """
        client = AsyncOAuth2Client(
            client_id=self.client_id,
            redirect_uri=redirect_uri,
            scope="Xboxlive.signin Xboxlive.offline_access"
        )
        
        auth_url, _ = client.create_authorization_url(
            self.authorization_endpoint,
            state=state
        )
        
        logger.info("xbox_auth_url_generated", redirect_uri=redirect_uri)
        return auth_url
    
    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str
    ) -> Optional[Dict[str, Any]]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            redirect_uri: Original redirect URI (must match)
            
        Returns:
            Token data with access_token, refresh_token, expires_in
        """
        try:
            client = AsyncOAuth2Client(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=redirect_uri
            )
            
            token = await client.fetch_token(
                self.token_endpoint,
                code=code,
                grant_type="authorization_code"
            )
            
            # Get Xbox Live token
            xbox_token = await self._get_xbox_token(token["access_token"])
            if not xbox_token:
                return None
            
            # Get XSTS token
            xsts_data = await self._get_xsts_token(xbox_token)
            if not xsts_data:
                return None
            
            logger.info("xbox_token_exchanged", xuid=xsts_data["xuid"])
            return {
                "access_token": token["access_token"],
                "refresh_token": token.get("refresh_token"),
                "expires_at": datetime.utcnow() + timedelta(seconds=token.get("expires_in", 3600)),
                "token_type": token.get("token_type", "Bearer"),
                "xbox_token": xbox_token,
                "xsts_token": xsts_data["token"],
                "xuid": xsts_data["xuid"],
                "gamertag": xsts_data["gamertag"]
            }
            
        except Exception as e:
            logger.error("xbox_token_exchange_error", error=str(e))
            return None
    
    async def _get_xbox_token(self, access_token: str) -> Optional[str]:
        """
        Get Xbox Live authentication token.
        
        Args:
            access_token: Microsoft access token
            
        Returns:
            Xbox Live token or None if error
        """
        try:
            payload = {
                "Properties": {
                    "AuthMethod": "RPS",
                    "SiteName": "user.auth.xboxlive.com",
                    "RpsTicket": f"d={access_token}"
                },
                "RelyingParty": "http://auth.xboxlive.com",
                "TokenType": "JWT"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.xbox_auth_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10.0
                )
                response.raise_for_status()
                
                data = response.json()
                return data.get("Token")
                
        except Exception as e:
            logger.error("xbox_token_error", error=str(e))
            return None
    
    async def _get_xsts_token(self, xbox_token: str) -> Optional[Dict[str, Any]]:
        """
        Get Xbox Secure Token Service (XSTS) token.
        
        Args:
            xbox_token: Xbox Live token
            
        Returns:
            XSTS data with token, xuid, and gamertag
        """
        try:
            payload = {
                "Properties": {
                    "SandboxId": "RETAIL",
                    "UserTokens": [xbox_token]
                },
                "RelyingParty": "http://xboxlive.com",
                "TokenType": "JWT"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.xsts_auth_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10.0
                )
                response.raise_for_status()
                
                data = response.json()
                display_claims = data.get("DisplayClaims", {})
                xui = display_claims.get("xui", [{}])[0]
                
                return {
                    "token": data.get("Token"),
                    "xuid": xui.get("xid"),
                    "gamertag": xui.get("gtg")
                }
                
        except Exception as e:
            logger.error("xsts_token_error", error=str(e))
            return None
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token from previous authentication
            
        Returns:
            New token data or None if error
        """
        try:
            client = AsyncOAuth2Client(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            token = await client.fetch_token(
                self.token_endpoint,
                refresh_token=refresh_token,
                grant_type="refresh_token"
            )
            
            # Get new Xbox tokens
            xbox_token = await self._get_xbox_token(token["access_token"])
            if not xbox_token:
                return None
            
            xsts_data = await self._get_xsts_token(xbox_token)
            if not xsts_data:
                return None
            
            logger.info("xbox_token_refreshed")
            return {
                "access_token": token["access_token"],
                "refresh_token": token.get("refresh_token", refresh_token),
                "expires_at": datetime.utcnow() + timedelta(seconds=token.get("expires_in", 3600)),
                "token_type": token.get("token_type", "Bearer"),
                "xbox_token": xbox_token,
                "xsts_token": xsts_data["token"],
                "xuid": xsts_data["xuid"],
                "gamertag": xsts_data["gamertag"]
            }
            
        except Exception as e:
            logger.error("xbox_token_refresh_error", error=str(e))
            return None
    
    async def get_user_info(self, xuid: str, xsts_token: str) -> Optional[Dict[str, Any]]:
        """
        Get Xbox Live user profile.
        
        Args:
            xuid: Xbox User ID
            xsts_token: XSTS authentication token
            
        Returns:
            User profile data or None if error
        """
        try:
            headers = {
                "Authorization": f"XBL3.0 x={xuid};{xsts_token}",
                "Accept": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/account/{xuid}",
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                
                data = response.json()
                
                logger.info("xbox_user_info_retrieved", xuid=xuid)
                return {
                    "xuid": xuid,
                    "gamertag": data.get("gamertag"),
                    "gamerscore": data.get("gamerScore"),
                    "account_tier": data.get("accountTier"),
                    "avatar_url": data.get("displayPicRaw")
                }
                
        except Exception as e:
            logger.error("xbox_user_info_error", xuid=xuid, error=str(e))
            return None
    
    async def get_user_titles(self, xuid: str, xsts_token: str) -> list[Dict[str, Any]]:
        """
        Get list of games/titles played by Xbox user.
        
        Args:
            xuid: Xbox User ID
            xsts_token: XSTS authentication token
            
        Returns:
            List of game data with achievement and playtime information
        """
        try:
            headers = {
                "Authorization": f"XBL3.0 x={xuid};{xsts_token}",
                "Accept": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/account/{xuid}/titles",
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                titles = data.get("titles", [])
                
                logger.info(
                    "xbox_titles_retrieved",
                    xuid=xuid,
                    title_count=len(titles)
                )
                
                # Transform to our format
                return [
                    {
                        "platform_game_id": str(title.get("titleId")),
                        "name": title.get("name"),
                        "modern_title_id": title.get("modernTitleId"),
                        "image_url": title.get("displayImage"),
                        "current_gamerscore": title.get("achievement", {}).get("currentGamerscore", 0),
                        "max_gamerscore": title.get("achievement", {}).get("totalGamerscore", 0),
                        "achievements_earned": title.get("achievement", {}).get("currentAchievements", 0),
                        "achievements_total": title.get("achievement", {}).get("totalAchievements", 0),
                        "progress_percentage": title.get("achievement", {}).get("progressPercentage", 0),
                        "last_played": (
                            datetime.fromisoformat(title["titleHistory"]["lastTimePlayed"].replace("Z", "+00:00"))
                            if title.get("titleHistory", {}).get("lastTimePlayed")
                            else None
                        )
                    }
                    for title in titles
                    if title.get("titleId")
                ]
                
        except Exception as e:
            logger.error("xbox_titles_error", xuid=xuid, error=str(e))
            return []
    
    async def get_title_achievements(
        self,
        xuid: str,
        xsts_token: str,
        title_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed achievement information for a specific title.
        
        Args:
            xuid: Xbox User ID
            xsts_token: XSTS authentication token
            title_id: Xbox title ID
            
        Returns:
            Achievement data or None if error
        """
        try:
            headers = {
                "Authorization": f"XBL3.0 x={xuid};{xsts_token}",
                "Accept": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/achievements/player/{xuid}/title/{title_id}",
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                
                data = response.json()
                achievements = data.get("achievements", [])
                
                unlocked_count = sum(1 for a in achievements if a.get("progressState") == "Achieved")
                
                logger.info(
                    "xbox_achievements_retrieved",
                    title_id=title_id,
                    unlocked=unlocked_count,
                    total=len(achievements)
                )
                
                return {
                    "total": len(achievements),
                    "unlocked": unlocked_count,
                    "achievements": achievements
                }
                
        except Exception as e:
            logger.error(
                "xbox_achievements_error",
                title_id=title_id,
                error=str(e)
            )
            return None
