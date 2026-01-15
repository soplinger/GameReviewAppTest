"""RAWG API client for fetching game data."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
from loguru import logger

from ...core.config import settings


class RAWGClient:
    """Client for RAWG Video Games Database API.
    
    RAWG provides free access with API key authentication.
    Rate limit: 20,000 requests per month (~27 requests per hour)
    
    This serves as a fallback when IGDB is unavailable.
    """

    BASE_URL = "https://api.rawg.io/api"
    
    def __init__(self):
        self.api_key = settings.RAWG_API_KEY
        
    async def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to RAWG API.
        
        Args:
            endpoint: API endpoint (e.g., "games", "games/{id}")
            params: Query parameters
            
        Returns:
            Response JSON data
        """
        if params is None:
            params = {}
        
        params["key"] = self.api_key
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"RAWG request failed for {endpoint}: {e}")
            raise
    
    async def search_games(
        self, query: str, page: int = 1, page_size: int = 10
    ) -> Dict[str, Any]:
        """Search for games by name.
        
        Args:
            query: Search query string
            page: Page number (default: 1)
            page_size: Results per page (default: 10, max: 40)
            
        Returns:
            Response with 'results' array and pagination info
        """
        params = {
            "search": query,
            "page": page,
            "page_size": min(page_size, 40),
        }
        
        try:
            return await self._make_request("games", params)
        except Exception as e:
            logger.error(f"RAWG search failed for query '{query}': {e}")
            return {"results": [], "count": 0}
    
    async def get_game_by_id(self, rawg_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed game information by RAWG ID.
        
        Args:
            rawg_id: RAWG game ID
            
        Returns:
            Game object or None if not found
        """
        try:
            return await self._make_request(f"games/{rawg_id}")
        except Exception as e:
            logger.error(f"RAWG get game failed for ID {rawg_id}: {e}")
            return None
    
    async def get_game_screenshots(self, rawg_id: int) -> List[Dict[str, Any]]:
        """Get screenshots for a game.
        
        Args:
            rawg_id: RAWG game ID
            
        Returns:
            List of screenshot objects with image URLs
        """
        try:
            data = await self._make_request(f"games/{rawg_id}/screenshots")
            return data.get("results", [])
        except Exception as e:
            logger.error(f"RAWG get screenshots failed for ID {rawg_id}: {e}")
            return []
    
    async def get_popular_games(
        self, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:
        """Get popular games sorted by rating.
        
        Args:
            page: Page number (default: 1)
            page_size: Results per page (default: 20, max: 40)
            
        Returns:
            Response with 'results' array and pagination info
        """
        params = {
            "ordering": "-rating",
            "page": page,
            "page_size": min(page_size, 40),
        }
        
        try:
            return await self._make_request("games", params)
        except Exception as e:
            logger.error(f"RAWG get popular games failed: {e}")
            return {"results": [], "count": 0}
    
    async def get_recent_games(
        self, days: int = 30, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:
        """Get recently released games.
        
        Args:
            days: Number of days to look back (default: 30)
            page: Page number (default: 1)
            page_size: Results per page (default: 20, max: 40)
            
        Returns:
            Response with 'results' array and pagination info
        """
        date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        date_to = datetime.now().strftime("%Y-%m-%d")
        
        params = {
            "dates": f"{date_from},{date_to}",
            "ordering": "-released",
            "page": page,
            "page_size": min(page_size, 40),
        }
        
        try:
            return await self._make_request("games", params)
        except Exception as e:
            logger.error(f"RAWG get recent games failed: {e}")
            return {"results": [], "count": 0}
    
    async def get_games_by_platform(
        self, platform_id: int, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:
        """Get games for a specific platform.
        
        Common platform IDs:
        - 4: PC
        - 187: PlayStation 5
        - 186: Xbox Series S/X
        - 7: Nintendo Switch
        
        Args:
            platform_id: RAWG platform ID
            page: Page number (default: 1)
            page_size: Results per page (default: 20, max: 40)
            
        Returns:
            Response with 'results' array and pagination info
        """
        params = {
            "platforms": platform_id,
            "ordering": "-rating",
            "page": page,
            "page_size": min(page_size, 40),
        }
        
        try:
            return await self._make_request("games", params)
        except Exception as e:
            logger.error(f"RAWG get games by platform {platform_id} failed: {e}")
            return {"results": [], "count": 0}
    
    async def get_games_by_genre(
        self, genre_slug: str, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:
        """Get games for a specific genre.
        
        Common genre slugs: action, adventure, rpg, strategy, shooter, puzzle
        
        Args:
            genre_slug: RAWG genre slug
            page: Page number (default: 1)
            page_size: Results per page (default: 20, max: 40)
            
        Returns:
            Response with 'results' array and pagination info
        """
        params = {
            "genres": genre_slug,
            "ordering": "-rating",
            "page": page,
            "page_size": min(page_size, 40),
        }
        
        try:
            return await self._make_request("games", params)
        except Exception as e:
            logger.error(f"RAWG get games by genre '{genre_slug}' failed: {e}")
            return {"results": [], "count": 0}
    
    async def get_platforms(self) -> List[Dict[str, Any]]:
        """Get list of all platforms.
        
        Returns:
            List of platform objects with id, name, slug
        """
        try:
            data = await self._make_request("platforms", {"page_size": 40})
            return data.get("results", [])
        except Exception as e:
            logger.error(f"RAWG get platforms failed: {e}")
            return []
    
    async def get_genres(self) -> List[Dict[str, Any]]:
        """Get list of all genres.
        
        Returns:
            List of genre objects with id, name, slug
        """
        try:
            data = await self._make_request("genres", {"page_size": 40})
            return data.get("results", [])
        except Exception as e:
            logger.error(f"RAWG get genres failed: {e}")
            return []
