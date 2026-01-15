"""IGDB API client for fetching game data."""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
from loguru import logger

from ...core.config import settings


class IGDBClient:
    """Client for IGDB (Internet Game Database) API.
    
    IGDB uses Twitch OAuth for authentication and requires:
    1. Client ID from Twitch Developer Console
    2. Client Secret from Twitch Developer Console
    3. Access token obtained via OAuth flow
    
    Rate limit: 4 requests per second
    """

    BASE_URL = "https://api.igdb.com/v4"
    AUTH_URL = "https://id.twitch.tv/oauth2/token"
    RATE_LIMIT = 4  # requests per second
    
    def __init__(self):
        self.client_id = settings.IGDB_CLIENT_ID
        self.client_secret = settings.IGDB_CLIENT_SECRET
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._rate_limiter = asyncio.Semaphore(self.RATE_LIMIT)
        self._last_request_time = datetime.now()
        
    async def _get_access_token(self) -> str:
        """Get or refresh Twitch OAuth access token."""
        if self._access_token and self._token_expires_at:
            if datetime.now() < self._token_expires_at:
                return self._access_token
        
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.AUTH_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            self._access_token = data["access_token"]
            # Token expires in 'expires_in' seconds, refresh 5 minutes before
            expires_in = data.get("expires_in", 3600)
            self._token_expires_at = datetime.now() + timedelta(
                seconds=expires_in - 300
            )
            
            logger.info("IGDB access token refreshed")
            return self._access_token
    
    async def _make_request(
        self, endpoint: str, body: str, method: str = "POST"
    ) -> List[Dict[str, Any]]:
        """Make authenticated request to IGDB API with rate limiting."""
        async with self._rate_limiter:
            # Ensure 1 second has passed since last request
            now = datetime.now()
            time_since_last = (now - self._last_request_time).total_seconds()
            if time_since_last < 1.0:
                await asyncio.sleep(1.0 - time_since_last)
            
            self._last_request_time = datetime.now()
            
            token = await self._get_access_token()
            headers = {
                "Client-ID": self.client_id,
                "Authorization": f"Bearer {token}",
            }
            
            url = f"{self.BASE_URL}/{endpoint}"
            
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method, url, headers=headers, content=body
                )
                response.raise_for_status()
                return response.json()
    
    async def search_games(
        self, query: str, limit: int = 10, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Search for games by name.
        
        Args:
            query: Search query string
            limit: Maximum number of results (default: 10, max: 500)
            offset: Pagination offset
            
        Returns:
            List of game objects with id, name, cover, release_date, etc.
        """
        body = f"""
        search "{query}";
        fields id, name, summary, cover.url, first_release_date, 
               rating, rating_count, platforms.name, genres.name,
               involved_companies.company.name, screenshots.url;
        limit {limit};
        offset {offset};
        """
        
        try:
            return await self._make_request("games", body)
        except Exception as e:
            logger.error(f"IGDB search failed for query '{query}': {e}")
            return []
    
    async def get_game_by_id(self, igdb_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed game information by IGDB ID.
        
        Args:
            igdb_id: IGDB game ID
            
        Returns:
            Game object or None if not found
        """
        body = f"""
        fields id, name, summary, storyline, cover.url, 
               first_release_date, release_dates.date, 
               rating, rating_count, aggregated_rating,
               platforms.name, platforms.platform_logo.url,
               genres.name, themes.name, game_modes.name,
               player_perspectives.name, involved_companies.company.name,
               involved_companies.developer, involved_companies.publisher,
               screenshots.url, artworks.url, videos.video_id,
               websites.url, websites.category, similar_games.name;
        where id = {igdb_id};
        """
        
        try:
            results = await self._make_request("games", body)
            return results[0] if results else None
        except Exception as e:
            logger.error(f"IGDB get game failed for ID {igdb_id}: {e}")
            return None
    
    async def get_popular_games(
        self, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get popular games sorted by rating count.
        
        Args:
            limit: Maximum number of results (default: 50, max: 500)
            offset: Pagination offset
            
        Returns:
            List of popular game objects
        """
        body = f"""
        fields id, name, summary, cover.url, first_release_date,
               rating, rating_count, platforms.name, genres.name;
        where rating_count > 100 & rating > 70;
        sort rating_count desc;
        limit {limit};
        offset {offset};
        """
        
        try:
            return await self._make_request("games", body)
        except Exception as e:
            logger.error(f"IGDB get popular games failed: {e}")
            return []
    
    async def get_recent_games(
        self, days: int = 30, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get recently released games.
        
        Args:
            days: Number of days to look back (default: 30)
            limit: Maximum number of results (default: 50, max: 500)
            
        Returns:
            List of recent game objects
        """
        timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
        
        body = f"""
        fields id, name, summary, cover.url, first_release_date,
               rating, rating_count, platforms.name, genres.name;
        where first_release_date >= {timestamp};
        sort first_release_date desc;
        limit {limit};
        """
        
        try:
            return await self._make_request("games", body)
        except Exception as e:
            logger.error(f"IGDB get recent games failed: {e}")
            return []
    
    async def get_games_by_platform(
        self, platform_name: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get games for a specific platform.
        
        Args:
            platform_name: Platform name (e.g., "PlayStation 5", "PC")
            limit: Maximum number of results (default: 50, max: 500)
            
        Returns:
            List of game objects
        """
        body = f"""
        fields id, name, summary, cover.url, first_release_date,
               rating, rating_count, platforms.name, genres.name;
        where platforms.name ~ *"{platform_name}"*;
        sort rating_count desc;
        limit {limit};
        """
        
        try:
            return await self._make_request("games", body)
        except Exception as e:
            logger.error(f"IGDB get games by platform '{platform_name}' failed: {e}")
            return []
    
    async def get_games_by_genre(
        self, genre_name: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get games for a specific genre.
        
        Args:
            genre_name: Genre name (e.g., "Action", "RPG")
            limit: Maximum number of results (default: 50, max: 500)
            
        Returns:
            List of game objects
        """
        body = f"""
        fields id, name, summary, cover.url, first_release_date,
               rating, rating_count, platforms.name, genres.name;
        where genres.name ~ *"{genre_name}"*;
        sort rating_count desc;
        limit {limit};
        """
        
        try:
            return await self._make_request("games", body)
        except Exception as e:
            logger.error(f"IGDB get games by genre '{genre_name}' failed: {e}")
            return []
