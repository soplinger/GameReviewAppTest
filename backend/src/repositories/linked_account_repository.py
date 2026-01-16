"""Repository for linked account operations."""

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.linked_account import LinkedAccount, PlatformType


class LinkedAccountRepository:
    """Repository for managing linked gaming platform accounts."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        user_id: int,
        platform: PlatformType,
        platform_user_id: str,
        platform_username: Optional[str] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        token_expires_at: Optional[datetime] = None,
    ) -> LinkedAccount:
        """Create a new linked account."""
        linked_account = LinkedAccount(
            user_id=user_id,
            platform=platform,
            platform_user_id=platform_user_id,
            platform_username=platform_username,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=token_expires_at,
            connected_at=datetime.utcnow(),
        )
        self.db.add(linked_account)
        await self.db.commit()
        await self.db.refresh(linked_account)
        return linked_account
    
    async def get_by_id(self, account_id: int) -> Optional[LinkedAccount]:
        """Get linked account by ID."""
        result = await self.db.execute(
            select(LinkedAccount).where(LinkedAccount.id == account_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user_and_platform(
        self, user_id: int, platform: PlatformType
    ) -> Optional[LinkedAccount]:
        """Get user's linked account for a specific platform."""
        result = await self.db.execute(
            select(LinkedAccount)
            .where(
                LinkedAccount.user_id == user_id,
                LinkedAccount.platform == platform
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_platform_user(
        self, platform: PlatformType, platform_user_id: str
    ) -> Optional[LinkedAccount]:
        """Get linked account by platform and platform user ID."""
        result = await self.db.execute(
            select(LinkedAccount)
            .where(
                LinkedAccount.platform == platform,
                LinkedAccount.platform_user_id == platform_user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def get_user_accounts(self, user_id: int) -> list[LinkedAccount]:
        """Get all linked accounts for a user."""
        result = await self.db.execute(
            select(LinkedAccount)
            .where(LinkedAccount.user_id == user_id)
            .order_by(LinkedAccount.connected_at.desc())
        )
        return list(result.scalars().all())
    
    async def update_tokens(
        self,
        account_id: int,
        access_token: str,
        refresh_token: Optional[str] = None,
        token_expires_at: Optional[datetime] = None,
    ) -> Optional[LinkedAccount]:
        """Update OAuth tokens for a linked account."""
        account = await self.get_by_id(account_id)
        if not account:
            return None
        
        account.access_token = access_token
        if refresh_token:
            account.refresh_token = refresh_token
        if token_expires_at:
            account.token_expires_at = token_expires_at
        
        await self.db.commit()
        await self.db.refresh(account)
        return account
    
    async def update_sync_time(self, account_id: int) -> Optional[LinkedAccount]:
        """Update the last sync timestamp."""
        account = await self.get_by_id(account_id)
        if not account:
            return None
        
        account.last_synced_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(account)
        return account
    
    async def delete(self, account_id: int) -> bool:
        """Delete a linked account."""
        account = await self.get_by_id(account_id)
        if not account:
            return False
        
        await self.db.delete(account)
        await self.db.commit()
        return True
    
    async def delete_by_user_and_platform(
        self, user_id: int, platform: PlatformType
    ) -> bool:
        """Delete a user's linked account for a specific platform."""
        account = await self.get_by_user_and_platform(user_id, platform)
        if not account:
            return False
        
        await self.db.delete(account)
        await self.db.commit()
        return True
