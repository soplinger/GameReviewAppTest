"""Game data service for managing game information from external APIs."""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

from ..repositories.game_repository import GameRepository
from .external.igdb_client import IGDBClient
from .external.rawg_client import RAWGClient


class GameDataService:
    """Service for fetching and managing game data from external APIs.
    
    Uses IGDB as primary source with RAWG as fallback.
    Handles data transformation and storage.
    """

    def __init__(
        self,
        game_repo: GameRepository,
        igdb_client: Optional[IGDBClient] = None,
        rawg_client: Optional[RAWGClient] = None,
    ):
        self.game_repo = game_repo
        self.igdb_client = igdb_client or IGDBClient()
        self.rawg_client = rawg_client or RAWGClient()

    @staticmethod
    def _create_slug(name: str) -> str:
        """Create URL-friendly slug from game name.
        
        Args:
            name: Game name
            
        Returns:
            Slugified name
        """
        slug = name.lower()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"\s+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")

    def _transform_igdb_game(self, igdb_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform IGDB game data to internal format.
        
        Args:
            igdb_data: Raw IGDB API response
            
        Returns:
            Transformed game data dictionary
        """
        name = igdb_data.get("name", "Unknown Game")
        
        # Extract cover URL
        cover_url = None
        if "cover" in igdb_data and "url" in igdb_data["cover"]:
            cover_url = igdb_data["cover"]["url"].replace("t_thumb", "t_cover_big")
        
        # Extract screenshots
        screenshots = []
        if "screenshots" in igdb_data:
            screenshots = [
                s["url"].replace("t_thumb", "t_screenshot_big")
                for s in igdb_data["screenshots"]
                if "url" in s
            ]
        
        # Extract artworks
        artworks = []
        if "artworks" in igdb_data:
            artworks = [
                a["url"].replace("t_thumb", "t_1080p")
                for a in igdb_data["artworks"]
                if "url" in a
            ]
        
        # Extract platforms
        platforms = []
        if "platforms" in igdb_data:
            platforms = [p.get("name") for p in igdb_data["platforms"] if "name" in p]
        
        # Extract genres
        genres = []
        if "genres" in igdb_data:
            genres = [g.get("name") for g in igdb_data["genres"] if "name" in g]
        
        # Extract themes
        themes = []
        if "themes" in igdb_data:
            themes = [t.get("name") for t in igdb_data["themes"] if "name" in t]
        
        # Extract companies
        developers = []
        publishers = []
        if "involved_companies" in igdb_data:
            for company in igdb_data["involved_companies"]:
                if "company" in company and "name" in company["company"]:
                    company_name = company["company"]["name"]
                    if company.get("developer"):
                        developers.append(company_name)
                    if company.get("publisher"):
                        publishers.append(company_name)
        
        # Extract release date
        release_date = None
        if "first_release_date" in igdb_data:
            release_date = datetime.fromtimestamp(igdb_data["first_release_date"])
        
        return {
            "igdb_id": igdb_data.get("id"),
            "name": name,
            "slug": self._create_slug(name),
            "summary": igdb_data.get("summary"),
            "storyline": igdb_data.get("storyline"),
            "cover_url": cover_url,
            "screenshots": screenshots,
            "artworks": artworks,
            "release_date": release_date,
            "rating": igdb_data.get("rating"),
            "rating_count": igdb_data.get("rating_count"),
            "platforms": platforms,
            "genres": genres,
            "themes": themes,
            "developers": developers,
            "publishers": publishers,
            "last_synced_at": datetime.utcnow(),
        }

    def _transform_rawg_game(self, rawg_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform RAWG game data to internal format.
        
        Args:
            rawg_data: Raw RAWG API response
            
        Returns:
            Transformed game data dictionary
        """
        name = rawg_data.get("name", "Unknown Game")
        
        # Extract platforms
        platforms = []
        if "platforms" in rawg_data:
            platforms = [
                p["platform"]["name"]
                for p in rawg_data["platforms"]
                if "platform" in p and "name" in p["platform"]
            ]
        
        # Extract genres
        genres = []
        if "genres" in rawg_data:
            genres = [g.get("name") for g in rawg_data["genres"] if "name" in g]
        
        # Extract screenshots
        screenshots = []
        if "short_screenshots" in rawg_data:
            screenshots = [
                s["image"] for s in rawg_data["short_screenshots"] if "image" in s
            ]
        
        # Extract release date
        release_date = None
        if "released" in rawg_data:
            try:
                release_date = datetime.strptime(rawg_data["released"], "%Y-%m-%d")
            except ValueError:
                pass
        
        return {
            "rawg_id": rawg_data.get("id"),
            "name": name,
            "slug": rawg_data.get("slug", self._create_slug(name)),
            "summary": rawg_data.get("description_raw"),
            "cover_url": rawg_data.get("background_image"),
            "screenshots": screenshots,
            "release_date": release_date,
            "rating": rawg_data.get("rating", 0) * 20,  # Convert 0-5 to 0-100
            "rating_count": rawg_data.get("ratings_count"),
            "metacritic_score": rawg_data.get("metacritic"),
            "platforms": platforms,
            "genres": genres,
            "developers": [d.get("name") for d in rawg_data.get("developers", [])],
            "publishers": [p.get("name") for p in rawg_data.get("publishers", [])],
            "last_synced_at": datetime.utcnow(),
        }

    async def search_games(
        self, query: str, limit: int = 10, use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """Search for games across all sources.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            use_cache: Check database first before hitting APIs
            
        Returns:
            List of game data dictionaries
        """
        results = []
        
        # Check database first if caching enabled
        if use_cache:
            db_results = await self.game_repo.search(query, limit=limit)
            if db_results:
                logger.info(f"Found {len(db_results)} games in database for '{query}'")
                return [self._game_to_dict(game) for game in db_results]
        
        # Try IGDB first
        try:
            igdb_results = await self.igdb_client.search_games(query, limit=limit)
            if igdb_results:
                logger.info(f"Found {len(igdb_results)} games from IGDB for '{query}'")
                return igdb_results
        except Exception as e:
            logger.warning(f"IGDB search failed, trying RAWG: {e}")
        
        # Fallback to RAWG
        try:
            rawg_results = await self.rawg_client.search_games(
                query, page_size=limit
            )
            results = rawg_results.get("results", [])
            logger.info(f"Found {len(results)} games from RAWG for '{query}'")
        except Exception as e:
            logger.error(f"Both IGDB and RAWG searches failed: {e}")
        
        return results

    async def get_or_fetch_game(
        self, igdb_id: Optional[int] = None, rawg_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Get game from database or fetch from API.
        
        Args:
            igdb_id: IGDB game ID
            rawg_id: RAWG game ID
            
        Returns:
            Game data dictionary or None
        """
        # Check database first
        if igdb_id:
            game = await self.game_repo.get_by_igdb_id(igdb_id)
            if game:
                return self._game_to_dict(game)
        
        if rawg_id:
            game = await self.game_repo.get_by_rawg_id(rawg_id)
            if game:
                return self._game_to_dict(game)
        
        # Fetch from APIs
        if igdb_id:
            try:
                igdb_data = await self.igdb_client.get_game_by_id(igdb_id)
                if igdb_data:
                    game_data = self._transform_igdb_game(igdb_data)
                    game = await self.game_repo.create(game_data)
                    logger.info(f"Created game from IGDB: {game.name}")
                    return self._game_to_dict(game)
            except Exception as e:
                logger.error(f"Failed to fetch game {igdb_id} from IGDB: {e}")
        
        if rawg_id:
            try:
                rawg_data = await self.rawg_client.get_game_by_id(rawg_id)
                if rawg_data:
                    game_data = self._transform_rawg_game(rawg_data)
                    game = await self.game_repo.create(game_data)
                    logger.info(f"Created game from RAWG: {game.name}")
                    return self._game_to_dict(game)
            except Exception as e:
                logger.error(f"Failed to fetch game {rawg_id} from RAWG: {e}")
        
        return None

    async def sync_popular_games(self, limit: int = 50) -> int:
        """Sync popular games from IGDB to database.
        
        Args:
            limit: Number of games to sync
            
        Returns:
            Number of games synced
        """
        try:
            igdb_games = await self.igdb_client.get_popular_games(limit=limit)
            synced = 0
            
            for igdb_data in igdb_games:
                igdb_id = igdb_data.get("id")
                if not igdb_id:
                    continue
                
                # Check if already exists
                existing = await self.game_repo.get_by_igdb_id(igdb_id)
                if existing:
                    # Update if stale (older than 7 days)
                    if (datetime.utcnow() - existing.last_synced_at).days > 7:
                        game_data = self._transform_igdb_game(igdb_data)
                        await self.game_repo.update(existing.id, game_data)
                        synced += 1
                else:
                    # Create new game
                    game_data = self._transform_igdb_game(igdb_data)
                    await self.game_repo.create(game_data)
                    synced += 1
            
            logger.info(f"Synced {synced} popular games from IGDB")
            return synced
        except Exception as e:
            logger.error(f"Failed to sync popular games: {e}")
            return 0

    @staticmethod
    def _game_to_dict(game) -> Dict[str, Any]:
        """Convert Game model instance to dictionary.
        
        Args:
            game: Game model instance
            
        Returns:
            Game data dictionary
        """
        return {
            "id": game.id,
            "igdb_id": game.igdb_id,
            "rawg_id": game.rawg_id,
            "name": game.name,
            "slug": game.slug,
            "summary": game.summary,
            "storyline": game.storyline,
            "cover_url": game.cover_url,
            "screenshots": game.screenshots,
            "artworks": game.artworks,
            "videos": game.videos,
            "release_date": game.release_date.isoformat() if game.release_date else None,
            "rating": game.rating,
            "rating_count": game.rating_count,
            "metacritic_score": game.metacritic_score,
            "platforms": game.platforms,
            "genres": game.genres,
            "themes": game.themes,
            "game_modes": game.game_modes,
            "developers": game.developers,
            "publishers": game.publishers,
            "websites": game.websites,
            "similar_games": game.similar_games,
            "last_synced_at": game.last_synced_at.isoformat(),
            "created_at": game.created_at.isoformat(),
            "updated_at": game.updated_at.isoformat(),
        }
