"""Game library model for imported games from linked accounts."""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


class GameLibrary(Base):
    """
    Games owned/played from linked gaming accounts.
    
    Imported from Steam, PlayStation, or Xbox accounts to show
    play time and achievements in reviews and profiles.
    """
    
    __tablename__ = "game_library"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id"), nullable=False)
    linked_account_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("linked_accounts.id"),
        nullable=True,
        doc="Source linked account (null if manually added)"
    )
    
    # Game stats
    playtime_hours: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Total hours played (from platform API)"
    )
    achievements_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of achievements unlocked"
    )
    
    # Timestamps
    last_played_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        doc="Last play session timestamp"
    )
    imported_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        doc="When this entry was created/imported"
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="game_library")
    game: Mapped["Game"] = relationship("Game", back_populates="library_entries")
    linked_account: Mapped[Optional["LinkedAccount"]] = relationship(
        "LinkedAccount",
        back_populates="library_entries"
    )
    
    # Table constraints
    __table_args__ = (
        # One entry per user/game/linked account combination
        UniqueConstraint(
            "user_id", "game_id", "linked_account_id",
            name="uq_user_game_linked_account"
        ),
        # Indexes
        Index("idx_game_library_user_id", "user_id"),
        Index("idx_game_library_game_id", "game_id"),
        Index("idx_game_library_linked_account_id", "linked_account_id"),
        Index("idx_game_library_playtime", "playtime_hours"),
    )
    
    def __repr__(self) -> str:
        return (
            f"<GameLibrary(id={self.id}, user_id={self.user_id}, "
            f"game_id={self.game_id}, playtime_hours={self.playtime_hours})>"
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "game_id": self.game_id,
            "linked_account_id": self.linked_account_id,
            "playtime_hours": self.playtime_hours,
            "achievements_count": self.achievements_count,
            "last_played_at": self.last_played_at.isoformat() if self.last_played_at else None,
            "imported_at": self.imported_at.isoformat() if self.imported_at else None,
        }
