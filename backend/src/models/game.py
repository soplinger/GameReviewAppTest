"""Game database model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from ..core.database import Base


class Game(Base):
    """Game model representing games from external APIs.
    
    Games are synced from IGDB (primary) and RAWG (fallback) APIs.
    External IDs allow mapping to original API sources.
    """

    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    
    # External API identifiers
    igdb_id = Column(Integer, unique=True, nullable=True, index=True)
    rawg_id = Column(Integer, unique=True, nullable=True, index=True)
    
    # Core game information
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    summary = Column(Text, nullable=True)
    storyline = Column(Text, nullable=True)
    
    # Media
    cover_url = Column(String(512), nullable=True)
    screenshots = Column(JSON, nullable=True)  # Array of image URLs
    artworks = Column(JSON, nullable=True)  # Array of artwork URLs
    videos = Column(JSON, nullable=True)  # Array of video IDs/URLs
    
    # Release information
    release_date = Column(DateTime, nullable=True, index=True)
    
    # Ratings from external sources
    rating = Column(Float, nullable=True)  # Aggregate rating (0-100)
    rating_count = Column(Integer, nullable=True)
    metacritic_score = Column(Integer, nullable=True)
    
    # Classification
    platforms = Column(JSON, nullable=True)  # Array of platform names
    genres = Column(JSON, nullable=True)  # Array of genre names
    themes = Column(JSON, nullable=True)  # Array of theme names
    game_modes = Column(JSON, nullable=True)  # Array of game modes
    
    # Companies
    developers = Column(JSON, nullable=True)  # Array of developer names
    publishers = Column(JSON, nullable=True)  # Array of publisher names
    
    # Additional metadata
    websites = Column(JSON, nullable=True)  # Array of official websites
    similar_games = Column(JSON, nullable=True)  # Array of similar game IDs
    
    # Data management
    last_synced_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    
    # Relationships
    reviews = relationship("Review", back_populates="game", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Game(id={self.id}, name='{self.name}', igdb_id={self.igdb_id})>"
