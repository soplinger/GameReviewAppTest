"""Social schemas for friend requests and user search."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .user import UserResponse


class FriendRequestCreate(BaseModel):
    """Schema for creating a friend request."""
    addressee_id: int = Field(..., description="ID of user to send friend request to")


class FriendshipResponse(BaseModel):
    """Schema for friendship response."""
    id: int
    requester_id: int
    addressee_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    # Optional user details (populated when needed)
    requester: Optional[UserResponse] = None
    addressee: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True


class FriendRequestResponse(BaseModel):
    """Schema for friend request with requester info."""
    id: int
    requester: UserResponse
    created_at: datetime
    
    class Config:
        from_attributes = True


class FriendResponse(BaseModel):
    """Schema for friend user info."""
    id: int
    username: str
    email: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    friend_since: datetime  # When friendship was accepted
    
    class Config:
        from_attributes = True


class UserSearchParams(BaseModel):
    """Schema for user search parameters."""
    query: str = Field(..., min_length=1, max_length=100, description="Search query for username")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")


class UserSearchResult(BaseModel):
    """Schema for user search result."""
    id: int
    username: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    
    # Friendship status with current user
    friendship_status: Optional[str] = None  # None, 'pending', 'accepted', 'declined'
    is_requester: Optional[bool] = None  # If pending, whether current user is requester
    
    class Config:
        from_attributes = True


class UserSearchResponse(BaseModel):
    """Schema for user search response with pagination."""
    users: list[UserSearchResult]
    total: int
    limit: int
    offset: int
    
    class Config:
        from_attributes = True


class FriendRequestUpdate(BaseModel):
    """Schema for updating friend request status."""
    action: str = Field(..., pattern="^(accept|decline|block)$", description="Action to take on friend request")


class FriendsListResponse(BaseModel):
    """Schema for friends list response."""
    friends: list[FriendResponse]
    total: int
    
    class Config:
        from_attributes = True


class PendingRequestsResponse(BaseModel):
    """Schema for pending friend requests response."""
    received_requests: list[FriendRequestResponse]
    sent_requests: list[FriendRequestResponse]
    
    class Config:
        from_attributes = True