"""Game service for business logic."""

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.game import Game
from ..repositories.game_repository import GameRepository
from ..repositories.review_repository import ReviewRepository
from ..schemas.game import GameDetail, GameSearchParams, GameSearchResult


class GameService:
    """Service for game business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.game_repo = GameRepository(db)
        self.review_repo = ReviewRepository(db)

    async def search_games(
        self, params: GameSearchParams
    ) -> tuple[List[GameSearchResult], int]:
        """Search for games with filters.
        
        Args:
            params: Search parameters
            
        Returns:
            Tuple of (list of games, total count)
        """
        offset = (params.page - 1) * params.page_size

        if params.query:
            # Text search
            games = await self.game_repo.search(
                query=params.query, limit=params.page_size, offset=offset
            )
            # TODO: Get total count - for now using len(games) as approximation
            total = len(games) + offset if len(games) == params.page_size else len(games) + offset
        elif params.platform:
            # Platform filter
            games = await self.game_repo.get_by_platform(
                platform=params.platform, limit=params.page_size, offset=offset
            )
            total = len(games) + offset if len(games) == params.page_size else len(games) + offset
        elif params.genre:
            # Genre filter
            games = await self.game_repo.get_by_genre(
                genre=params.genre, limit=params.page_size, offset=offset
            )
            total = len(games) + offset if len(games) == params.page_size else len(games) + offset
        else:
            # Default: popular games
            games = await self.game_repo.get_popular(
                limit=params.page_size, offset=offset
            )
            total = len(games) + offset if len(games) == params.page_size else len(games) + offset

        # Convert to search results
        results = [
            GameSearchResult(
                id=game.id,
                igdb_id=game.igdb_id,
                rawg_id=game.rawg_id,
                name=game.name,
                slug=game.slug,
                summary=game.summary,
                cover_url=game.cover_url,
                release_date=game.release_date,
                rating=game.rating,
                platforms=game.platforms,
                genres=game.genres,
                metacritic_score=game.metacritic_score,
            )
            for game in games
        ]

        return results, total

    async def get_game_details(self, game_id: int) -> Optional[GameDetail]:
        """Get detailed game information with aggregated review data.
        
        Args:
            game_id: Game ID
            
        Returns:
            GameDetail with user ratings or None
        """
        game = await self.game_repo.get_by_id(game_id)
        if not game:
            return None

        # Get aggregated review data
        avg_rating = await self.review_repo.get_average_rating(game_id)
        review_count = await self.review_repo.count_by_game(game_id)

        # Build detailed response
        return GameDetail(
            id=game.id,
            igdb_id=game.igdb_id,
            rawg_id=game.rawg_id,
            name=game.name,
            slug=game.slug,
            summary=game.summary,
            storyline=game.storyline,
            cover_url=game.cover_url,
            screenshots=game.screenshots,
            artworks=game.artworks,
            videos=game.videos,
            release_date=game.release_date,
            rating=game.rating,
            rating_count=game.rating_count,
            metacritic_score=game.metacritic_score,
            platforms=game.platforms,
            genres=game.genres,
            themes=game.themes,
            game_modes=game.game_modes,
            developers=game.developers,
            publishers=game.publishers,
            websites=game.websites,
            similar_games=game.similar_games,
            last_synced_at=game.last_synced_at,
            created_at=game.created_at,
            updated_at=game.updated_at,
            user_rating=avg_rating,
            user_rating_count=review_count,
        )

    async def get_game_by_slug(self, slug: str) -> Optional[GameDetail]:
        """Get game by slug.
        
        Args:
            slug: Game slug
            
        Returns:
            GameDetail or None
        """
        game = await self.game_repo.get_by_slug(slug)
        if not game:
            return None

        return await self.get_game_details(game.id)

    async def get_popular_games(
        self, limit: int = 20, offset: int = 0
    ) -> List[GameSearchResult]:
        """Get popular games.
        
        Args:
            limit: Maximum results
            offset: Pagination offset
            
        Returns:
            List of popular games
        """
        games = await self.game_repo.get_popular(limit=limit, offset=offset)
        
        return [
            GameSearchResult(
                id=game.id,
                igdb_id=game.igdb_id,
                rawg_id=game.rawg_id,
                name=game.name,
                slug=game.slug,
                summary=game.summary,
                cover_url=game.cover_url,
                release_date=game.release_date,
                rating=game.rating,
                platforms=game.platforms,
                genres=game.genres,
                metacritic_score=game.metacritic_score,
            )
            for game in games
        ]

    async def get_recent_games(
        self, limit: int = 20, offset: int = 0
    ) -> List[GameSearchResult]:
        """Get recently released games.
        
        Args:
            limit: Maximum results
            offset: Pagination offset
            
        Returns:
            List of recent games
        """
        games = await self.game_repo.get_recent(limit=limit, offset=offset)
        
        return [
            GameSearchResult(
                id=game.id,
                igdb_id=game.igdb_id,
                rawg_id=game.rawg_id,
                name=game.name,
                slug=game.slug,
                summary=game.summary,
                cover_url=game.cover_url,
                release_date=game.release_date,
                rating=game.rating,
                platforms=game.platforms,
                genres=game.genres,
                metacritic_score=game.metacritic_score,
            )
            for game in games
        ]
