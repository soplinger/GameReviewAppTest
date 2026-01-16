"""Repository for game library operations."""

from datetime import datetime
from typing import Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..models.game_library import GameLibrary


class GameLibraryRepository:
    """Repository for managing user game library entries."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        user_id: int,
        game_id: int,
        linked_account_id: Optional[int] = None,
        playtime_hours: int = 0,
        achievements_count: int = 0,
        last_played_at: Optional[datetime] = None,
    ) -> GameLibrary:
        """Create a new game library entry."""
        entry = GameLibrary(
            user_id=user_id,
            game_id=game_id,
            linked_account_id=linked_account_id,
            playtime_hours=playtime_hours,
            achievements_count=achievements_count,
            last_played_at=last_played_at,
            imported_at=datetime.utcnow(),
        )
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry
    
    async def get_by_id(self, entry_id: int) -> Optional[GameLibrary]:
        """Get library entry by ID."""
        result = await self.db.execute(
            select(GameLibrary)
            .options(joinedload(GameLibrary.game))
            .where(GameLibrary.id == entry_id)
        )
        return result.unique().scalar_one_or_none()
    
    async def get_by_user_game(
        self, user_id: int, game_id: int, linked_account_id: Optional[int] = None
    ) -> Optional[GameLibrary]:
        """Get library entry by user, game, and optionally linked account."""
        conditions = [
            GameLibrary.user_id == user_id,
            GameLibrary.game_id == game_id,
        ]
        if linked_account_id is not None:
            conditions.append(GameLibrary.linked_account_id == linked_account_id)
        
        result = await self.db.execute(
            select(GameLibrary)
            .where(and_(*conditions))
        )
        return result.scalar_one_or_none()
    
    async def get_user_library(
        self,
        user_id: int,
        linked_account_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[GameLibrary]:
        """Get user's game library with optional filtering."""
        query = select(GameLibrary).options(joinedload(GameLibrary.game))
        
        conditions = [GameLibrary.user_id == user_id]
        if linked_account_id is not None:
            conditions.append(GameLibrary.linked_account_id == linked_account_id)
        
        query = query.where(and_(*conditions))
        query = query.order_by(GameLibrary.playtime_hours.desc())
        query = query.limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def count_user_library(
        self, user_id: int, linked_account_id: Optional[int] = None
    ) -> int:
        """Count total games in user's library."""
        conditions = [GameLibrary.user_id == user_id]
        if linked_account_id is not None:
            conditions.append(GameLibrary.linked_account_id == linked_account_id)
        
        result = await self.db.execute(
            select(func.count(GameLibrary.id)).where(and_(*conditions))
        )
        return result.scalar_one()
    
    async def get_game_playtime(self, user_id: int, game_id: int) -> int:
        """Get total playtime for a game across all linked accounts."""
        result = await self.db.execute(
            select(func.sum(GameLibrary.playtime_hours))
            .where(
                GameLibrary.user_id == user_id,
                GameLibrary.game_id == game_id
            )
        )
        total = result.scalar_one_or_none()
        return total or 0
    
    async def update_playtime(
        self,
        entry_id: int,
        playtime_hours: int,
        last_played_at: Optional[datetime] = None,
    ) -> Optional[GameLibrary]:
        """Update playtime for a library entry."""
        entry = await self.get_by_id(entry_id)
        if not entry:
            return None
        
        entry.playtime_hours = playtime_hours
        if last_played_at:
            entry.last_played_at = last_played_at
        
        await self.db.commit()
        await self.db.refresh(entry)
        return entry
    
    async def update_achievements(
        self, entry_id: int, achievements_count: int
    ) -> Optional[GameLibrary]:
        """Update achievement count for a library entry."""
        entry = await self.get_by_id(entry_id)
        if not entry:
            return None
        
        entry.achievements_count = achievements_count
        await self.db.commit()
        await self.db.refresh(entry)
        return entry
    
    async def upsert(
        self,
        user_id: int,
        game_id: int,
        linked_account_id: Optional[int],
        playtime_hours: int,
        achievements_count: int = 0,
        last_played_at: Optional[datetime] = None,
    ) -> GameLibrary:
        """Create or update a library entry."""
        existing = await self.get_by_user_game(user_id, game_id, linked_account_id)
        
        if existing:
            existing.playtime_hours = playtime_hours
            existing.achievements_count = achievements_count
            if last_played_at:
                existing.last_played_at = last_played_at
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            return await self.create(
                user_id=user_id,
                game_id=game_id,
                linked_account_id=linked_account_id,
                playtime_hours=playtime_hours,
                achievements_count=achievements_count,
                last_played_at=last_played_at,
            )
    
    async def delete(self, entry_id: int) -> bool:
        """Delete a library entry."""
        entry = await self.get_by_id(entry_id)
        if not entry:
            return False
        
        await self.db.delete(entry)
        await self.db.commit()
        return True
    
    async def delete_by_linked_account(self, linked_account_id: int) -> int:
        """Delete all library entries for a linked account."""
        result = await self.db.execute(
            select(GameLibrary).where(
                GameLibrary.linked_account_id == linked_account_id
            )
        )
        entries = result.scalars().all()
        
        count = 0
        for entry in entries:
            await self.db.delete(entry)
            count += 1
        
        await self.db.commit()
        return count
