"""Schemas package initialization."""
from .auth import Token, TokenData, UserLogin, UserRegister, UserResponse, UserUpdate
from .game import (
    GameDetail,
    GameListResponse,
    GameSearchParams,
    GameSearchResult,
)
from .review import (
    ReviewCreate,
    ReviewListResponse,
    ReviewResponse,
    ReviewSummary,
    ReviewUpdate,
)
from .social import (
    FriendRequestCreate,
    FriendRequestResponse,
    FriendRequestUpdate,
    FriendResponse,
    FriendsListResponse,
    FriendshipResponse,
    PendingRequestsResponse,
    UserSearchParams,
    UserSearchResponse,
    UserSearchResult,
)

__all__ = [
    "Token",
    "TokenData",
    "UserLogin",
    "UserRegister",
    "UserResponse",
    "UserUpdate",
    "GameDetail",
    "GameSearchResult",
    "GameSearchParams",
    "GameListResponse",
    "ReviewCreate",
    "ReviewUpdate",
    "ReviewResponse",
    "ReviewListResponse",
    "ReviewSummary",
]
