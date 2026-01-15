"""Social service for friend request and user management."""

from typing import List, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..models.friendship import Friendship, FriendshipStatus
from ..models.user import User
from ..repositories.friendship_repository import FriendshipRepository
from ..schemas.social import (
    FriendRequestCreate,
    FriendshipResponse,
    FriendRequestResponse,
    FriendResponse,
    FriendsListResponse,
    PendingRequestsResponse,
    UserSearchParams,
    UserSearchResponse,
    UserSearchResult
)


class SocialService:
    """Service for social features including friend requests and user search."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.friendship_repo = FriendshipRepository(db)

    async def send_friend_request(
        self, 
        requester_id: int, 
        request_data: FriendRequestCreate
    ) -> FriendshipResponse:
        """Send a friend request.
        
        Args:
            requester_id: ID of user sending the request
            request_data: Friend request data
            
        Returns:
            Created friendship response
            
        Raises:
            ValueError: If request is invalid (self-request, already exists, etc.)
        """
        addressee_id = request_data.addressee_id
        
        # Validation
        if requester_id == addressee_id:
            raise ValueError("Cannot send friend request to yourself")
        
        # Check if addressee exists
        addressee_result = await self.db.execute(
            select(User).where(User.id == addressee_id)
        )
        addressee = addressee_result.scalar_one_or_none()
        if not addressee:
            raise ValueError("User not found")
        
        # Check if friendship already exists
        existing = await self.friendship_repo.get_friendship_between_users(
            requester_id, addressee_id
        )
        if existing:
            if existing.is_pending:
                raise ValueError("Friend request already pending")
            elif existing.is_accepted:
                raise ValueError("Users are already friends")
            elif existing.is_declined:
                # Allow re-requesting after decline
                await self.friendship_repo.delete(existing.id)
        
        # Create new friendship request
        friendship = await self.friendship_repo.create_request(
            requester_id, addressee_id
        )
        
        return FriendshipResponse.model_validate(friendship)

    async def respond_to_friend_request(
        self, 
        user_id: int, 
        friendship_id: int, 
        action: str
    ) -> FriendshipResponse:
        """Respond to a friend request (accept/decline/block).
        
        Args:
            user_id: ID of user responding (must be addressee)
            friendship_id: ID of friendship to respond to
            action: 'accept', 'decline', or 'block'
            
        Returns:
            Updated friendship response
            
        Raises:
            ValueError: If request is invalid or user unauthorized
        """
        friendship = await self.friendship_repo.get_by_id(friendship_id, load_users=True)
        if not friendship:
            raise ValueError("Friend request not found")
        
        # Verify user is the addressee
        if friendship.addressee_id != user_id:
            raise ValueError("You can only respond to friend requests sent to you")
        
        # Verify request is pending
        if not friendship.is_pending:
            raise ValueError("Friend request is not pending")
        
        # Update status based on action
        status_map = {
            "accept": FriendshipStatus.ACCEPTED,
            "decline": FriendshipStatus.DECLINED,
            "block": FriendshipStatus.BLOCKED,
        }
        
        if action not in status_map:
            raise ValueError(f"Invalid action: {action}")
        
        new_status = status_map[action]
        updated_friendship = await self.friendship_repo.update_status(
            friendship_id, new_status
        )
        
        return FriendshipResponse.model_validate(updated_friendship)

    async def remove_friend(self, user_id: int, friend_id: int) -> bool:
        """Remove a friend (delete friendship).
        
        Args:
            user_id: ID of user removing friend
            friend_id: ID of friend to remove
            
        Returns:
            True if removed successfully
            
        Raises:
            ValueError: If friendship not found or users not friends
        """
        friendship = await self.friendship_repo.get_friendship_between_users(
            user_id, friend_id
        )
        if not friendship:
            raise ValueError("Friendship not found")
        
        if not friendship.is_accepted:
            raise ValueError("Users are not friends")
        
        return await self.friendship_repo.delete(friendship.id)

    async def get_friends(self, user_id: int) -> FriendsListResponse:
        """Get user's friends list.
        
        Args:
            user_id: User ID
            
        Returns:
            Friends list response
        """
        # Get friendships with user details
        result = await self.db.execute(
            select(Friendship)
            .options(
                selectinload(Friendship.requester),
                selectinload(Friendship.addressee)
            )
            .where(
                (
                    (Friendship.requester_id == user_id) |
                    (Friendship.addressee_id == user_id)
                ) &
                (Friendship.status == FriendshipStatus.ACCEPTED)
            )
            .order_by(Friendship.updated_at.desc())
        )
        
        friendships = result.scalars().all()
        friends = []
        
        for friendship in friendships:
            # Determine which user is the friend
            if friendship.requester_id == user_id:
                friend_user = friendship.addressee
            else:
                friend_user = friendship.requester
            
            friend_response = FriendResponse(
                id=friend_user.id,
                username=friend_user.username,
                email=friend_user.email,
                bio=friend_user.bio,
                avatar_url=friend_user.avatar_url,
                created_at=friend_user.created_at,
                friend_since=friendship.updated_at,  # When friendship was accepted
            )
            friends.append(friend_response)
        
        return FriendsListResponse(
            friends=friends,
            total=len(friends)
        )

    async def get_pending_requests(self, user_id: int) -> PendingRequestsResponse:
        """Get pending friend requests (sent and received).
        
        Args:
            user_id: User ID
            
        Returns:
            Pending requests response
        """
        received_requests = await self.friendship_repo.get_pending_requests_received(user_id)
        sent_requests = await self.friendship_repo.get_pending_requests_sent(user_id)
        
        received_responses = [
            FriendRequestResponse(
                id=req.id,
                requester=req.requester,
                addressee=req.addressee,
                status=req.status,
                created_at=req.created_at,
                updated_at=req.updated_at
            )
            for req in received_requests
        ]
        
        sent_responses = [
            FriendRequestResponse(
                id=req.id,
                requester=req.requester,
                addressee=req.addressee,
                status=req.status,
                created_at=req.created_at,
                updated_at=req.updated_at
            )
            for req in sent_requests
        ]
        
        return PendingRequestsResponse(
            received_requests=received_responses,
            sent_requests=sent_responses
        )

    async def search_users(
        self, 
        current_user_id: int, 
        search_params: UserSearchParams
    ) -> UserSearchResponse:
        """Search for users by username.
        
        Args:
            current_user_id: ID of user performing search
            search_params: Search parameters
            
        Returns:
            User search response with friendship status
        """
        # Search users by username (case-insensitive)
        query = select(User).where(
            User.username.ilike(f"%{search_params.query}%")
        ).where(
            User.id != current_user_id  # Exclude current user
        ).order_by(User.username).limit(search_params.limit).offset(search_params.offset)
        
        result = await self.db.execute(query)
        users = result.scalars().all()
        
        # Get friendship status for each user
        user_results = []
        for user in users:
            friendship = await self.friendship_repo.get_friendship_between_users(
                current_user_id, user.id
            )
            
            friendship_status = "none"  # Default to 'none'
            is_requester = None
            
            if friendship:
                # Map internal status to frontend-expected status
                if friendship.status == 'accepted':
                    friendship_status = "friends"
                elif friendship.status == 'blocked':
                    friendship_status = "blocked"
                elif friendship.status == 'pending':
                    # Determine if current user sent or received the request
                    is_requester = friendship.requester_id == current_user_id
                    friendship_status = "pending_sent" if is_requester else "pending_received"
                elif friendship.status == 'declined':
                    friendship_status = "none"  # Treat declined as none for UI purposes
            
            user_result = UserSearchResult(
                id=user.id,
                username=user.username,
                bio=user.bio,
                avatar_url=user.avatar_url,
                created_at=user.created_at,
                friendship_status=friendship_status,
                is_requester=is_requester
            )
            user_results.append(user_result)
        
        # Get total count for pagination
        count_result = await self.db.execute(
            select(User).where(
                User.username.ilike(f"%{search_params.query}%")
            ).where(
                User.id != current_user_id
            )
        )
        total = len(list(count_result.scalars().all()))
        
        return UserSearchResponse(
            users=user_results,
            total=total,
            limit=search_params.limit,
            offset=search_params.offset
        )

    async def get_friendship_status(
        self, 
        user1_id: int, 
        user2_id: int
    ) -> Optional[FriendshipResponse]:
        """Get friendship status between two users.
        
        Args:
            user1_id: First user ID
            user2_id: Second user ID
            
        Returns:
            Friendship response or None if no friendship exists
        """
        friendship = await self.friendship_repo.get_friendship_between_users(
            user1_id, user2_id
        )
        
        if friendship:
            return FriendshipResponse.model_validate(friendship)
        return None