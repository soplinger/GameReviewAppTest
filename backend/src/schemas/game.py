"""Game schemas for API requests and responses."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class GameBase(BaseModel):
    """Base game schema with common fields."""

    name: str
    slug: str
    summary: Optional[str] = None
    cover_url: Optional[str] = None
    release_date: Optional[datetime] = None
    rating: Optional[float] = None
    platforms: Optional[List[str]] = None
    genres: Optional[List[str]] = None


class GameSearchResult(GameBase):
    """Game schema for search results (minimal fields)."""

    id: int
    igdb_id: Optional[int] = None
    rawg_id: Optional[int] = None
    metacritic_score: Optional[int] = None
    
    class Config:
        from_attributes = True


class GameDetail(BaseModel):
    """Detailed game schema with all fields."""

    id: int
    igdb_id: Optional[int] = None
    rawg_id: Optional[int] = None
    name: str
    slug: str
    summary: Optional[str] = None
    storyline: Optional[str] = None
    cover_url: Optional[str] = None
    screenshots: Optional[List[str]] = None
    artworks: Optional[List[str]] = None
    videos: Optional[List[str]] = None
    release_date: Optional[datetime] = None
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    metacritic_score: Optional[int] = None
    platforms: Optional[List[str]] = None
    genres: Optional[List[str]] = None
    themes: Optional[List[str]] = None
    game_modes: Optional[List[str]] = None
    developers: Optional[List[str]] = None
    publishers: Optional[List[str]] = None
    websites: Optional[List[str]] = None
    similar_games: Optional[List[int]] = None
    last_synced_at: datetime
    created_at: datetime
    updated_at: datetime
    
    # Aggregated review data (populated by service)
    user_rating: Optional[float] = Field(
        None, description="Average user rating from reviews"
    )
    user_rating_count: Optional[int] = Field(
        None, description="Number of user reviews"
    )
    
    class Config:
        from_attributes = True


class GameListResponse(BaseModel):
    """Paginated game list response."""

    games: List[GameSearchResult]
    total: int
    page: int
    page_size: int
    total_pages: int


class GameSearchParams(BaseModel):
    """Game search parameters."""

    query: Optional[str] = Field(None, min_length=1, description="Search query")
    platform: Optional[str] = Field(None, description="Filter by platform")
    genre: Optional[str] = Field(None, description="Filter by genre")
    min_rating: Optional[float] = Field(None, ge=0, le=100, description="Minimum rating")
    sort_by: Optional[str] = Field(
        "popularity", description="Sort by: popularity, rating, release_date, name"
    )
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
