"""Schemas for linked gaming accounts and OAuth responses."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from ..models.linked_account import PlatformType


class LinkedAccountResponse(BaseModel):
    """Linked gaming account response (excludes sensitive tokens)."""
    
    id: int
    platform: PlatformType
    platform_user_id: str
    platform_username: str
    connected_at: datetime
    last_synced_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class OAuthInitiateResponse(BaseModel):
    """OAuth flow initiation response."""
    
    authorization_url: str
    state: Optional[str] = None


class LibrarySyncResponse(BaseModel):
    """Library sync operation response."""
    
    synced_platforms: List[str]
    total_games: int
    new_games: int
    updated_games: int
    errors: List[str]


class GameLibraryResponse(BaseModel):
    """Game library entry response with game details."""
    
    id: int
    user_id: int
    game_id: int
    linked_account_id: int
    playtime_hours: float
    achievements_count: int
    last_played_at: Optional[datetime] = None
    imported_at: datetime
    
    # Include basic game info from joined relationship
    game: Optional[dict] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_orm(cls, obj):
        """Create response from ORM model with game details."""
        data = {
            "id": obj.id,
            "user_id": obj.user_id,
            "game_id": obj.game_id,
            "linked_account_id": obj.linked_account_id,
            "playtime_hours": obj.playtime_hours,
            "achievements_count": obj.achievements_count,
            "last_played_at": obj.last_played_at,
            "imported_at": obj.imported_at,
        }
        
        # Add game info if available
        if hasattr(obj, "game") and obj.game:
            data["game"] = {
                "id": obj.game.id,
                "name": obj.game.name,
                "slug": obj.game.slug,
                "cover_image_url": obj.game.cover_url,
                "release_date": obj.game.release_date.isoformat() if obj.game.release_date else None,
                "rating": obj.game.rating
            }
        
        return cls(**data)


class GameLibraryListResponse(BaseModel):
    """Paginated game library list response."""
    
    items: List[GameLibraryResponse]
    total: int
    skip: int
    limit: int
