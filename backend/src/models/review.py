"""Review database model."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..core.database import Base


class Review(Base):
    """Review model representing user reviews of games."""

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Review content
    rating = Column(Float, nullable=False)  # 1.0 to 5.0
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)  # Minimum 50 characters
    
    # Optional metadata
    playtime_hours = Column(Integer, nullable=True)
    platform = Column(String(100), nullable=True)  # PC, PS5, Xbox, Switch, etc.
    is_recommended = Column(Boolean, nullable=False, default=True)
    
    # Social metrics
    helpful_count = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    game = relationship("Game", back_populates="reviews")
    
    def __repr__(self) -> str:
        return f"<Review(id={self.id}, user_id={self.user_id}, game_id={self.game_id}, rating={self.rating})>"
