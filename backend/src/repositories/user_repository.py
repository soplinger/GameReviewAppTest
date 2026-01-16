"""
User repository for database operations.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User


class UserRepository:
    """Repository for User database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, username: str, email: str, password_hash: str) -> User:
        """
        Create a new user.
        
        Args:
            username: User's username
            email: User's email
            password_hash: Hashed password
            
        Returns:
            Created User instance
        """
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    async def update(self, user: User, **kwargs) -> User:
        """
        Update user attributes.
        
        Args:
            user: User instance to update
            **kwargs: Attributes to update
            
        Returns:
            Updated User instance
        """
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        user.updated_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def update_last_login(self, user: User) -> User:
        """Update user's last login timestamp."""
        user.last_login = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(user)
        return user
