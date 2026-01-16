"""OAuth service for managing gaming platform authentication and account linking."""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import secrets

from ..models.linked_account import LinkedAccount, PlatformType
from ..repositories.linked_account_repository import LinkedAccountRepository
from ..core.logging import get_logger
from ..core.errors import AuthenticationError, NotFoundError, ConflictError
from .oauth.steam_client import SteamOAuthClient
from .oauth.playstation_client import PlayStationOAuthClient
from .oauth.xbox_client import XboxOAuthClient

logger = get_logger(__name__)


class OAuthService:
    """
    Service for managing OAuth authentication with gaming platforms.
    
    Handles:
    - Initiating OAuth flows for Steam, PSN, Xbox
    - Processing OAuth callbacks and storing tokens
    - Refreshing expired tokens
    - Unlinking accounts
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.linked_account_repo = LinkedAccountRepository(db)
        self.steam_client = SteamOAuthClient()
        self.psn_client = PlayStationOAuthClient()
        self.xbox_client = XboxOAuthClient()
        
        # Platform client mapping
        self._clients = {
            PlatformType.STEAM: self.steam_client,
            PlatformType.PLAYSTATION: self.psn_client,
            PlatformType.XBOX: self.xbox_client
        }
    
    async def initiate_oauth_flow(
        self,
        user_id: int,
        platform: PlatformType,
        redirect_uri: str
    ) -> Dict[str, str]:
        """
        Initiate OAuth authorization flow for a platform.
        
        Args:
            user_id: User initiating the OAuth flow
            platform: Gaming platform to link
            redirect_uri: Callback URL after authentication
            
        Returns:
            Dict with authorization_url and state token
            
        Raises:
            ConflictError: If account already linked
        """
        # Check if user already has this platform linked
        existing = await self.linked_account_repo.get_by_user_and_platform(
            user_id, platform
        )
        if existing:
            logger.warning(
                "oauth_already_linked",
                user_id=user_id,
                platform=platform.value
            )
            raise ConflictError(f"User already has {platform.value} account linked")
        
        # Generate CSRF protection state token
        state = secrets.token_urlsafe(32)
        
        # Get authorization URL from platform client
        client = self._clients[platform]
        
        if platform == PlatformType.STEAM:
            # Steam uses OpenID, no state needed
            auth_url = await client.get_authorization_url(redirect_uri)
        else:
            # PSN and Xbox use OAuth 2.0 with state
            auth_url = await client.get_authorization_url(redirect_uri, state)
        
        logger.info(
            "oauth_flow_initiated",
            user_id=user_id,
            platform=platform.value,
            redirect_uri=redirect_uri
        )
        
        return {
            "authorization_url": auth_url,
            "state": state if platform != PlatformType.STEAM else None
        }
    
    async def handle_steam_callback(
        self,
        user_id: int,
        callback_params: Dict[str, str]
    ) -> LinkedAccount:
        """
        Handle Steam OpenID callback and create linked account.
        
        Args:
            user_id: User linking the account
            callback_params: Query parameters from callback URL
            
        Returns:
            Created LinkedAccount
            
        Raises:
            AuthenticationError: If authentication fails
        """
        # Verify Steam OpenID response
        steam_id = await self.steam_client.verify_authentication(callback_params)
        if not steam_id:
            logger.error("steam_auth_failed", user_id=user_id)
            raise AuthenticationError("Steam authentication failed")
        
        # Get user info
        user_info = await self.steam_client.get_user_info(steam_id)
        if not user_info:
            logger.error("steam_user_info_failed", steam_id=steam_id)
            raise AuthenticationError("Failed to retrieve Steam user info")
        
        # Check if this Steam account is already linked to another user
        existing = await self.linked_account_repo.get_by_platform_user(
            PlatformType.STEAM, steam_id
        )
        if existing and existing.user_id != user_id:
            logger.warning(
                "steam_account_already_linked",
                steam_id=steam_id,
                existing_user_id=existing.user_id,
                new_user_id=user_id
            )
            raise ConflictError("This Steam account is already linked to another user")
        
        # Create or update linked account
        if existing:
            # Update existing
            existing.platform_username = user_info["username"]
            existing.connected_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(existing)
            
            logger.info(
                "steam_account_reconnected",
                user_id=user_id,
                steam_id=steam_id
            )
            return existing
        
        # Create new linked account
        # Steam doesn't use OAuth tokens, so we store empty values
        linked_account = await self.linked_account_repo.create(
            user_id=user_id,
            platform=PlatformType.STEAM,
            platform_user_id=steam_id,
            platform_username=user_info["username"],
            access_token="",  # Steam uses API key, not OAuth
            refresh_token=None,
            token_expires_at=None
        )
        
        logger.info(
            "steam_account_linked",
            user_id=user_id,
            steam_id=steam_id,
            username=user_info["username"]
        )
        
        return linked_account
    
    async def handle_oauth_callback(
        self,
        user_id: int,
        platform: PlatformType,
        code: str,
        state: str,
        redirect_uri: str
    ) -> LinkedAccount:
        """
        Handle OAuth 2.0 callback for PSN or Xbox and create linked account.
        
        Args:
            user_id: User linking the account
            platform: Platform (PSN or Xbox)
            code: Authorization code from callback
            state: State token for CSRF protection
            redirect_uri: Original redirect URI
            
        Returns:
            Created LinkedAccount
            
        Raises:
            AuthenticationError: If authentication fails
        """
        if platform not in [PlatformType.PLAYSTATION, PlatformType.XBOX]:
            raise ValueError(f"Invalid platform for OAuth callback: {platform}")
        
        client = self._clients[platform]
        
        # Exchange code for token
        token_data = await client.exchange_code_for_token(code, redirect_uri)
        if not token_data:
            logger.error("oauth_token_exchange_failed", platform=platform.value)
            raise AuthenticationError(f"{platform.value} token exchange failed")
        
        # Get user info
        if platform == PlatformType.PLAYSTATION:
            user_info = await client.get_user_info(token_data["access_token"])
            platform_user_id = user_info["account_id"]
            platform_username = user_info["username"]
        else:  # Xbox
            platform_user_id = token_data["xuid"]
            platform_username = token_data["gamertag"]
        
        if not platform_user_id:
            logger.error("oauth_user_info_failed", platform=platform.value)
            raise AuthenticationError(f"Failed to retrieve {platform.value} user info")
        
        # Check if this account is already linked to another user
        existing = await self.linked_account_repo.get_by_platform_user(
            platform, platform_user_id
        )
        if existing and existing.user_id != user_id:
            logger.warning(
                "platform_account_already_linked",
                platform=platform.value,
                platform_user_id=platform_user_id,
                existing_user_id=existing.user_id,
                new_user_id=user_id
            )
            raise ConflictError(f"This {platform.value} account is already linked to another user")
        
        # Create or update linked account
        if existing:
            # Update tokens
            await self.linked_account_repo.update_tokens(
                existing.id,
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                expires_at=token_data["expires_at"]
            )
            existing.platform_username = platform_username
            existing.connected_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(existing)
            
            logger.info(
                "platform_account_reconnected",
                platform=platform.value,
                user_id=user_id,
                platform_user_id=platform_user_id
            )
            return existing
        
        # Create new linked account
        linked_account = await self.linked_account_repo.create(
            user_id=user_id,
            platform=platform,
            platform_user_id=platform_user_id,
            platform_username=platform_username,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            token_expires_at=token_data["expires_at"]
        )
        
        logger.info(
            "platform_account_linked",
            platform=platform.value,
            user_id=user_id,
            platform_user_id=platform_user_id,
            username=platform_username
        )
        
        return linked_account
    
    async def refresh_token_if_needed(
        self,
        linked_account: LinkedAccount
    ) -> LinkedAccount:
        """
        Refresh OAuth token if expired or about to expire.
        
        Args:
            linked_account: Linked account to check
            
        Returns:
            Updated linked account with fresh token
        """
        # Steam doesn't use OAuth tokens
        if linked_account.platform == PlatformType.STEAM:
            return linked_account
        
        # Check if token needs refresh (expired or expires within 5 minutes)
        if not linked_account.is_token_expired():
            return linked_account
        
        logger.info(
            "refreshing_token",
            platform=linked_account.platform.value,
            linked_account_id=linked_account.id
        )
        
        client = self._clients[linked_account.platform]
        
        # Refresh token
        token_data = await client.refresh_access_token(linked_account.refresh_token)
        if not token_data:
            logger.error(
                "token_refresh_failed",
                platform=linked_account.platform.value,
                linked_account_id=linked_account.id
            )
            raise AuthenticationError(f"Failed to refresh {linked_account.platform.value} token")
        
        # Update stored tokens
        await self.linked_account_repo.update_tokens(
            linked_account.id,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token", linked_account.refresh_token),
            expires_at=token_data["expires_at"]
        )
        
        await self.db.refresh(linked_account)
        
        logger.info(
            "token_refreshed",
            platform=linked_account.platform.value,
            linked_account_id=linked_account.id
        )
        
        return linked_account
    
    async def unlink_account(self, user_id: int, platform: PlatformType) -> None:
        """
        Unlink a gaming platform account.
        
        Args:
            user_id: User unlinking the account
            platform: Platform to unlink
            
        Raises:
            NotFoundError: If account not found
        """
        deleted = await self.linked_account_repo.delete_by_user_and_platform(
            user_id, platform
        )
        
        if not deleted:
            logger.warning(
                "unlink_account_not_found",
                user_id=user_id,
                platform=platform.value
            )
            raise NotFoundError(f"No {platform.value} account linked for this user")
        
        logger.info(
            "account_unlinked",
            user_id=user_id,
            platform=platform.value
        )
    
    async def get_user_linked_accounts(self, user_id: int) -> list[LinkedAccount]:
        """
        Get all linked accounts for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of linked accounts
        """
        accounts = await self.linked_account_repo.get_user_accounts(user_id)
        
        logger.info(
            "fetched_linked_accounts",
            user_id=user_id,
            count=len(accounts)
        )
        
        return accounts
