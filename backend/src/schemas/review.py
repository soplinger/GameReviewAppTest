"""Review Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .auth import UserResponse
from .game import GameSearchResult


class ReviewCreate(BaseModel):
    """Schema for creating a new review."""
    
    game_id: int = Field(..., gt=0, description="Game ID")
    rating: float = Field(..., ge=1.0, le=5.0, description="Rating from 1.0 to 5.0")
    title: str = Field(..., min_length=5, max_length=200, description="Review title")
    content: str = Field(..., min_length=50, max_length=5000, description="Review content (min 50 chars)")
    playtime_hours: Optional[int] = Field(None, ge=0, description="Hours played")
    platform: Optional[str] = Field(None, max_length=100, description="Platform played on")
    is_recommended: bool = Field(True, description="Whether game is recommended")
    
    @field_validator('content')
    @classmethod
    def validate_content_length(cls, v: str) -> str:
        """Ensure content meets minimum length requirement."""
        if len(v.strip()) < 50:
            raise ValueError('Review content must be at least 50 characters')
        return v.strip()
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Ensure title is not empty after stripping."""
        if not v.strip():
            raise ValueError('Review title cannot be empty')
        return v.strip()


class ReviewUpdate(BaseModel):
    """Schema for updating an existing review."""
    
    rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="Rating from 1.0 to 5.0")
    title: Optional[str] = Field(None, min_length=5, max_length=200, description="Review title")
    content: Optional[str] = Field(None, min_length=50, max_length=5000, description="Review content")
    playtime_hours: Optional[int] = Field(None, ge=0, description="Hours played")
    platform: Optional[str] = Field(None, max_length=100, description="Platform played on")
    is_recommended: Optional[bool] = Field(None, description="Whether game is recommended")
    
    @field_validator('content')
    @classmethod
    def validate_content_length(cls, v: Optional[str]) -> Optional[str]:
        """Ensure content meets minimum length requirement if provided."""
        if v is not None and len(v.strip()) < 50:
            raise ValueError('Review content must be at least 50 characters')
        return v.strip() if v else None
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Ensure title is not empty after stripping if provided."""
        if v is not None and not v.strip():
            raise ValueError('Review title cannot be empty')
        return v.strip() if v else None


class ReviewResponse(BaseModel):
    """Schema for review response with full details."""
    
    id: int
    user_id: int
    game_id: int
    rating: float
    title: str
    content: str
    playtime_hours: Optional[int]
    platform: Optional[str]
    is_recommended: bool
    helpful_count: int
    created_at: datetime
    updated_at: datetime
    
    # Nested objects
    user: Optional[UserResponse] = None
    game: Optional[GameSearchResult] = None
    
    model_config = {
        "from_attributes": True
    }


class ReviewListResponse(BaseModel):
    """Schema for paginated review list response."""
    
    reviews: list[ReviewResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ReviewSummary(BaseModel):
    """Schema for brief review summary (for cards/lists)."""
    
    id: int
    user_id: int
    game_id: int
    rating: float
    title: str
    content_preview: str  # First 200 characters
    is_recommended: bool
    helpful_count: int
    created_at: datetime
    username: Optional[str] = None
    game_name: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }
