"""Social API endpoints for friend requests and user search."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...api.deps import get_current_user
from ...models.user import User
from ...services.social_service import SocialService
from ...schemas.social import (
    FriendRequestCreate,
    FriendRequestUpdate,
    FriendshipResponse,
    FriendsListResponse,
    PendingRequestsResponse,
    UserSearchParams,
    UserSearchResponse,
)

router = APIRouter(prefix="/social", tags=["social"])


@router.post(
    "/friends/request",
    response_model=FriendshipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send friend request",
    description="Send a friend request to another user",
)
async def send_friend_request(
    request_data: FriendRequestCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Send a friend request to another user."""
    social_service = SocialService(db)
    
    try:
        return await social_service.send_friend_request(
            current_user.id, request_data
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put(
    "/friends/{friendship_id}",
    response_model=FriendshipResponse,
    summary="Respond to friend request",
    description="Accept, decline, or block a friend request",
)
async def respond_to_friend_request(
    friendship_id: int,
    update_data: FriendRequestUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Respond to a friend request (accept/decline/block)."""
    social_service = SocialService(db)
    
    try:
        return await social_service.respond_to_friend_request(
            current_user.id, friendship_id, update_data.action
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/friends/{friend_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove friend",
    description="Remove a friend (delete friendship)",
)
async def remove_friend(
    friend_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Remove a friend (delete friendship)."""
    social_service = SocialService(db)
    
    try:
        await social_service.remove_friend(current_user.id, friend_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/friends",
    response_model=FriendsListResponse,
    summary="Get friends list",
    description="Get the current user's friends list",
)
async def get_friends(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get the current user's friends list."""
    social_service = SocialService(db)
    return await social_service.get_friends(current_user.id)


@router.get(
    "/friends/requests",
    response_model=PendingRequestsResponse,
    summary="Get pending friend requests",
    description="Get pending friend requests (sent and received)",
)
async def get_pending_requests(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get pending friend requests (sent and received)."""
    social_service = SocialService(db)
    return await social_service.get_pending_requests(current_user.id)


@router.get(
    "/users/search",
    response_model=UserSearchResponse,
    summary="Search users",
    description="Search for users by username with friendship status",
)
async def search_users(
    search_params: Annotated[UserSearchParams, Depends()],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Search for users by username."""
    social_service = SocialService(db)
    return await social_service.search_users(current_user.id, search_params)


@router.get(
    "/friends/{user_id}/status",
    response_model=FriendshipResponse | None,
    summary="Get friendship status",
    description="Get friendship status with another user",
)
async def get_friendship_status(
    user_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get friendship status with another user."""
    social_service = SocialService(db)
    return await social_service.get_friendship_status(current_user.id, user_id)