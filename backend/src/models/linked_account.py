"""Linked account model for gaming platform connections."""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


class PlatformType(str, PyEnum):
    """Supported gaming platforms."""
    STEAM = "steam"
    PLAYSTATION = "playstation"
    XBOX = "xbox"


class LinkedAccount(Base):
    """
    Connection to a gaming platform account (Steam, PSN, Xbox).
    
    Stores OAuth tokens (encrypted) and platform user information
    for importing game library and playtime data.
    """
    
    __tablename__ = "linked_accounts"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Platform information
    platform: Mapped[str] = mapped_column(
        Enum(PlatformType),
        nullable=False,
        doc="Gaming platform (steam, playstation, xbox)"
    )
    platform_user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="User ID on the external platform"
    )
    platform_username: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Display name on the platform"
    )
    
    # OAuth tokens (should be encrypted at rest in production)
    # For now storing as plain text, would use SQLAlchemy-Utils EncryptedType in production
    access_token: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        doc="OAuth access token (encrypted)"
    )
    refresh_token: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        doc="OAuth refresh token (encrypted)"
    )
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        doc="When the access token expires"
    )
    
    # Timestamps
    connected_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        doc="When the account was linked"
    )
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        doc="Last time game library was synced"
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="linked_accounts")
    library_entries: Mapped[list["GameLibrary"]] = relationship(
        "GameLibrary",
        back_populates="linked_account",
        cascade="all, delete-orphan"
    )
    
    # Table constraints
    __table_args__ = (
        # One account per platform per user
        UniqueConstraint("user_id", "platform", name="uq_user_platform"),
        # Prevent duplicate platform connections
        UniqueConstraint("platform", "platform_user_id", name="uq_platform_user"),
        # Indexes
        Index("idx_linked_account_user_id", "user_id"),
        Index("idx_linked_account_platform", "platform"),
    )
    
    def __repr__(self) -> str:
        return f"<LinkedAccount(id={self.id}, user_id={self.user_id}, platform={self.platform})>"
    
    def is_token_expired(self) -> bool:
        """Check if the OAuth token is expired."""
        if not self.token_expires_at:
            return False
        return datetime.utcnow() >= self.token_expires_at
    
    def to_dict(self) -> dict:
        """Convert to dictionary (excluding sensitive tokens)."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "platform": self.platform,
            "platform_username": self.platform_username,
            "connected_at": self.connected_at.isoformat() if self.connected_at else None,
            "last_synced_at": self.last_synced_at.isoformat() if self.last_synced_at else None,
        }
