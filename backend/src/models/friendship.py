"""Friendship model for user social connections."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .user import User


class FriendshipStatus(str, Enum):
    """Friendship status options."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    BLOCKED = "blocked"


class Friendship(Base):
    """Friendship model for managing user social connections.
    
    This model uses a bidirectional approach where each friendship
    has a requester and addressee, with status tracking.
    """
    
    __tablename__ = "friendships"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    requester_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    addressee_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    
    # Friendship status
    status: Mapped[FriendshipStatus] = mapped_column(
        String(20), 
        nullable=False, 
        default=FriendshipStatus.PENDING,
        index=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        default=datetime.utcnow,
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    # Relationships
    requester: Mapped["User"] = relationship(
        "User", 
        foreign_keys=[requester_id],
        back_populates="sent_friend_requests"
    )
    addressee: Mapped["User"] = relationship(
        "User", 
        foreign_keys=[addressee_id],
        back_populates="received_friend_requests"
    )
    
    def __repr__(self) -> str:
        return f"<Friendship(id={self.id}, requester_id={self.requester_id}, addressee_id={self.addressee_id}, status={self.status})>"
    
    @property
    def is_pending(self) -> bool:
        """Check if friendship is pending approval."""
        return self.status == FriendshipStatus.PENDING
    
    @property
    def is_accepted(self) -> bool:
        """Check if friendship is accepted."""
        return self.status == FriendshipStatus.ACCEPTED
    
    @property
    def is_declined(self) -> bool:
        """Check if friendship is declined."""
        return self.status == FriendshipStatus.DECLINED
    
    @property
    def is_blocked(self) -> bool:
        """Check if friendship is blocked."""
        return self.status == FriendshipStatus.BLOCKED
    
    def get_friend_id(self, user_id: int) -> Optional[int]:
        """Get the friend's user ID given a user ID.
        
        Args:
            user_id: The user ID to find the friend for
            
        Returns:
            Friend's user ID, or None if user_id is not in this friendship
        """
        if user_id == self.requester_id:
            return self.addressee_id
        elif user_id == self.addressee_id:
            return self.requester_id
        return None
    
    def involves_user(self, user_id: int) -> bool:
        """Check if this friendship involves the given user.
        
        Args:
            user_id: User ID to check
            
        Returns:
            True if the user is either requester or addressee
        """
        return user_id in (self.requester_id, self.addressee_id)