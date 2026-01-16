"""PlayStation Network OAuth client for authentication and library syncing."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from authlib.integrations.httpx_client import AsyncOAuth2Client
import httpx

from ...core.config import settings
from ...core.logging import get_logger

logger = get_logger(__name__)


class PlayStationOAuthClient:
    """
    PlayStation Network OAuth 2.0 client.
    
    Handles PSN authentication and retrieves user library and trophy data.
    """
    
    def __init__(self):
        self.client_id = settings.PSN_CLIENT_ID
        self.client_secret = settings.PSN_CLIENT_SECRET
        self.authorization_endpoint = "https://ca.account.sony.com/api/authz/v3/oauth/authorize"
        self.token_endpoint = "https://ca.account.sony.com/api/authz/v3/oauth/token"
        self.api_base_url = "https://m.np.playstation.com/api"
        
    async def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        """
        Generate PlayStation OAuth authorization URL.
        
        Args:
            redirect_uri: Callback URL after authentication
            state: CSRF protection state token
            
        Returns:
            Authorization URL to redirect user to
        """
        client = AsyncOAuth2Client(
            client_id=self.client_id,
            redirect_uri=redirect_uri,
            scope="psn:mobile.v1 psn:clientapp"
        )
        
        auth_url, _ = client.create_authorization_url(
            self.authorization_endpoint,
            state=state
        )
        
        logger.info("psn_auth_url_generated", redirect_uri=redirect_uri)
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
            
            logger.info("psn_token_exchanged")
            return {
                "access_token": token["access_token"],
                "refresh_token": token.get("refresh_token"),
                "expires_at": datetime.utcnow() + timedelta(seconds=token.get("expires_in", 3600)),
                "token_type": token.get("token_type", "Bearer")
            }
            
        except Exception as e:
            logger.error("psn_token_exchange_error", error=str(e))
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
            
            logger.info("psn_token_refreshed")
            return {
                "access_token": token["access_token"],
                "refresh_token": token.get("refresh_token", refresh_token),
                "expires_at": datetime.utcnow() + timedelta(seconds=token.get("expires_in", 3600)),
                "token_type": token.get("token_type", "Bearer")
            }
            
        except Exception as e:
            logger.error("psn_token_refresh_error", error=str(e))
            return None
    
    async def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Get PlayStation Network user profile.
        
        Args:
            access_token: Valid PSN access token
            
        Returns:
            User profile data or None if error
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                # Get account ID first
                response = await client.get(
                    f"{self.api_base_url}/userProfile/v1/internal/users/me/profile",
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                
                data = response.json()
                profile = data.get("profile", {})
                
                logger.info("psn_user_info_retrieved", account_id=profile.get("accountId"))
                return {
                    "account_id": profile.get("accountId"),
                    "username": profile.get("onlineId"),
                    "avatar_url": profile.get("avatarUrls", [{}])[0].get("avatarUrl") if profile.get("avatarUrls") else None,
                    "about_me": profile.get("aboutMe")
                }
                
        except Exception as e:
            logger.error("psn_user_info_error", error=str(e))
            return None
    
    async def get_user_titles(self, access_token: str, account_id: str) -> list[Dict[str, Any]]:
        """
        Get list of games/titles owned by PSN user.
        
        Args:
            access_token: Valid PSN access token
            account_id: PSN account ID
            
        Returns:
            List of game data with trophy and playtime information
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                # Get trophy titles (games with trophies)
                response = await client.get(
                    f"{self.api_base_url}/trophy/v1/users/{account_id}/trophyTitles",
                    headers=headers,
                    params={"limit": 100},
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                titles = data.get("trophyTitles", [])
                
                logger.info(
                    "psn_titles_retrieved",
                    account_id=account_id,
                    title_count=len(titles)
                )
                
                # Transform to our format
                return [
                    {
                        "platform_game_id": title.get("npCommunicationId"),
                        "name": title.get("trophyTitleName"),
                        "platform": title.get("trophyTitlePlatform"),
                        "icon_url": title.get("trophyTitleIconUrl"),
                        "progress": title.get("progress"),  # Trophy completion percentage
                        "earned_trophies": {
                            "bronze": title.get("earnedTrophies", {}).get("bronze", 0),
                            "silver": title.get("earnedTrophies", {}).get("silver", 0),
                            "gold": title.get("earnedTrophies", {}).get("gold", 0),
                            "platinum": title.get("earnedTrophies", {}).get("platinum", 0)
                        },
                        "total_trophies": {
                            "bronze": title.get("definedTrophies", {}).get("bronze", 0),
                            "silver": title.get("definedTrophies", {}).get("silver", 0),
                            "gold": title.get("definedTrophies", {}).get("gold", 0),
                            "platinum": title.get("definedTrophies", {}).get("platinum", 0)
                        },
                        "last_updated": (
                            datetime.fromisoformat(title["lastUpdatedDateTime"].replace("Z", "+00:00"))
                            if title.get("lastUpdatedDateTime")
                            else None
                        )
                    }
                    for title in titles
                    if title.get("npCommunicationId")  # Filter out titles without IDs
                ]
                
        except Exception as e:
            logger.error("psn_titles_error", account_id=account_id, error=str(e))
            return []
    
    async def get_title_trophies(
        self,
        access_token: str,
        account_id: str,
        np_communication_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed trophy information for a specific title.
        
        Args:
            access_token: Valid PSN access token
            account_id: PSN account ID
            np_communication_id: PlayStation title communication ID
            
        Returns:
            Trophy data or None if error
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/trophy/v1/users/{account_id}/npCommunicationIds/{np_communication_id}/trophyGroups/all/trophies",
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                
                data = response.json()
                trophies = data.get("trophies", [])
                
                earned_count = sum(1 for t in trophies if t.get("earned"))
                
                logger.info(
                    "psn_trophies_retrieved",
                    np_communication_id=np_communication_id,
                    earned=earned_count,
                    total=len(trophies)
                )
                
                return {
                    "total": len(trophies),
                    "earned": earned_count,
                    "trophies": trophies
                }
                
        except Exception as e:
            logger.error(
                "psn_trophies_error",
                np_communication_id=np_communication_id,
                error=str(e)
            )
            return None
