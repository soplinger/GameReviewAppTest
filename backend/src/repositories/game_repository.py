"""Game repository for data access operations."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.game import Game


class GameRepository:
    """Repository for Game model CRUD operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, game_data: dict) -> Game:
        """Create a new game.
        
        Args:
            game_data: Dictionary with game attributes
            
        Returns:
            Created Game instance
        """
        game = Game(**game_data)
        self.db.add(game)
        await self.db.commit()
        await self.db.refresh(game)
        return game

    async def get_by_id(self, game_id: int) -> Optional[Game]:
        """Get game by ID.
        
        Args:
            game_id: Game ID
            
        Returns:
            Game instance or None
        """
        result = await self.db.execute(
            select(Game).where(Game.id == game_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Game]:
        """Get game by slug.
        
        Args:
            slug: Game slug
            
        Returns:
            Game instance or None
        """
        result = await self.db.execute(
            select(Game).where(Game.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_by_igdb_id(self, igdb_id: int) -> Optional[Game]:
        """Get game by IGDB ID.
        
        Args:
            igdb_id: IGDB API game ID
            
        Returns:
            Game instance or None
        """
        result = await self.db.execute(
            select(Game).where(Game.igdb_id == igdb_id)
        )
        return result.scalar_one_or_none()

    async def get_by_rawg_id(self, rawg_id: int) -> Optional[Game]:
        """Get game by RAWG ID.
        
        Args:
            rawg_id: RAWG API game ID
            
        Returns:
            Game instance or None
        """
        result = await self.db.execute(
            select(Game).where(Game.rawg_id == rawg_id)
        )
        return result.scalar_one_or_none()

    async def search(
        self, query: str, limit: int = 20, offset: int = 0
    ) -> List[Game]:
        """Search games by name.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of matching Game instances
        """
        result = await self.db.execute(
            select(Game)
            .where(Game.name.ilike(f"%{query}%"))
            .order_by(Game.rating_count.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_popular(
        self, limit: int = 20, offset: int = 0
    ) -> List[Game]:
        """Get popular games sorted by rating count.
        
        Args:
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of Game instances
        """
        result = await self.db.execute(
            select(Game)
            .where(Game.rating_count.isnot(None))
            .order_by(Game.rating_count.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_recent(
        self, limit: int = 20, offset: int = 0
    ) -> List[Game]:
        """Get recently released games.
        
        Args:
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of Game instances
        """
        result = await self.db.execute(
            select(Game)
            .where(Game.release_date.isnot(None))
            .order_by(Game.release_date.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_platform(
        self, platform: str, limit: int = 20, offset: int = 0
    ) -> List[Game]:
        """Get games by platform.
        
        Args:
            platform: Platform name to filter by
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of Game instances
        """
        # Using JSON_CONTAINS would be better but SQLite has limited JSON support
        # Using text search on JSON field as workaround
        result = await self.db.execute(
            select(Game)
            .where(func.json_extract(Game.platforms, "$").like(f"%{platform}%"))
            .order_by(Game.rating_count.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_genre(
        self, genre: str, limit: int = 20, offset: int = 0
    ) -> List[Game]:
        """Get games by genre.
        
        Args:
            genre: Genre name to filter by
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of Game instances
        """
        result = await self.db.execute(
            select(Game)
            .where(func.json_extract(Game.genres, "$").like(f"%{genre}%"))
            .order_by(Game.rating_count.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def update(self, game_id: int, update_data: dict) -> Optional[Game]:
        """Update game information.
        
        Args:
            game_id: Game ID
            update_data: Dictionary with fields to update
            
        Returns:
            Updated Game instance or None
        """
        game = await self.get_by_id(game_id)
        if not game:
            return None

        for key, value in update_data.items():
            if hasattr(game, key):
                setattr(game, key, value)

        game.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(game)
        return game

    async def update_sync_timestamp(self, game_id: int) -> Optional[Game]:
        """Update last synced timestamp.
        
        Args:
            game_id: Game ID
            
        Returns:
            Updated Game instance or None
        """
        game = await self.get_by_id(game_id)
        if not game:
            return None

        game.last_synced_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(game)
        return game

    async def count(self) -> int:
        """Count total number of games.
        
        Returns:
            Total game count
        """
        result = await self.db.execute(select(func.count()).select_from(Game))
        return result.scalar_one()

    async def get_stale_games(
        self, days: int = 30, limit: int = 100
    ) -> List[Game]:
        """Get games that haven't been synced in N days.
        
        Args:
            days: Number of days since last sync
            limit: Maximum number of results
            
        Returns:
            List of Game instances needing updates
        """
        cutoff = datetime.utcnow().timestamp() - (days * 24 * 60 * 60)
        cutoff_datetime = datetime.fromtimestamp(cutoff)
        
        result = await self.db.execute(
            select(Game)
            .where(Game.last_synced_at < cutoff_datetime)
            .order_by(Game.last_synced_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())
