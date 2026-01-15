"""Friendship repository for social connection data access."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.friendship import Friendship, FriendshipStatus
from ..models.user import User


class FriendshipRepository:
    """Repository for Friendship model CRUD operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_request(self, requester_id: int, addressee_id: int) -> Friendship:
        """Create a new friendship request.
        
        Args:
            requester_id: ID of user sending the request
            addressee_id: ID of user receiving the request
            
        Returns:
            Created Friendship instance
        """
        friendship = Friendship(
            requester_id=requester_id,
            addressee_id=addressee_id,
            status=FriendshipStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(friendship)
        await self.db.commit()
        await self.db.refresh(friendship)
        return friendship

    async def get_by_id(self, friendship_id: int, load_users: bool = False) -> Optional[Friendship]:
        """Get friendship by ID.
        
        Args:
            friendship_id: Friendship ID
            load_users: Whether to load related user objects
            
        Returns:
            Friendship instance or None
        """
        query = select(Friendship).where(Friendship.id == friendship_id)
        
        if load_users:
            query = query.options(
                selectinload(Friendship.requester),
                selectinload(Friendship.addressee)
            )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_friendship_between_users(
        self, 
        user1_id: int, 
        user2_id: int
    ) -> Optional[Friendship]:
        """Get friendship between two users (bidirectional).
        
        Args:
            user1_id: First user ID
            user2_id: Second user ID
            
        Returns:
            Friendship instance or None
        """
        result = await self.db.execute(
            select(Friendship).where(
                or_(
                    and_(
                        Friendship.requester_id == user1_id,
                        Friendship.addressee_id == user2_id
                    ),
                    and_(
                        Friendship.requester_id == user2_id,
                        Friendship.addressee_id == user1_id
                    )
                )
            )
        )
        return result.scalar_one_or_none()

    async def update_status(
        self, 
        friendship_id: int, 
        new_status: FriendshipStatus
    ) -> Optional[Friendship]:
        """Update friendship status.
        
        Args:
            friendship_id: Friendship ID
            new_status: New status to set
            
        Returns:
            Updated Friendship instance or None
        """
        friendship = await self.get_by_id(friendship_id)
        if not friendship:
            return None
        
        friendship.status = new_status
        friendship.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(friendship)
        return friendship

    async def delete(self, friendship_id: int) -> bool:
        """Delete a friendship.
        
        Args:
            friendship_id: Friendship ID
            
        Returns:
            True if deleted, False if not found
        """
        friendship = await self.get_by_id(friendship_id)
        if not friendship:
            return False
        
        await self.db.delete(friendship)
        await self.db.commit()
        return True

    async def get_friends(self, user_id: int) -> List[User]:
        """Get all accepted friends for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of User objects who are friends
        """
        # Query friendships where user is involved and status is accepted
        result = await self.db.execute(
            select(Friendship)
            .options(
                selectinload(Friendship.requester),
                selectinload(Friendship.addressee)
            )
            .where(
                and_(
                    or_(
                        Friendship.requester_id == user_id,
                        Friendship.addressee_id == user_id
                    ),
                    Friendship.status == FriendshipStatus.ACCEPTED
                )
            )
        )
        
        friendships = result.scalars().all()
        friends = []
        
        for friendship in friendships:
            if friendship.requester_id == user_id:
                friends.append(friendship.addressee)
            else:
                friends.append(friendship.requester)
        
        return friends

    async def get_friend_ids(self, user_id: int) -> List[int]:
        """Get friend user IDs for a user (faster than loading full User objects).
        
        Args:
            user_id: User ID
            
        Returns:
            List of friend user IDs
        """
        result = await self.db.execute(
            select(Friendship.requester_id, Friendship.addressee_id)
            .where(
                and_(
                    or_(
                        Friendship.requester_id == user_id,
                        Friendship.addressee_id == user_id
                    ),
                    Friendship.status == FriendshipStatus.ACCEPTED
                )
            )
        )
        
        friendships = result.all()
        friend_ids = []
        
        for requester_id, addressee_id in friendships:
            friend_id = addressee_id if requester_id == user_id else requester_id
            friend_ids.append(friend_id)
        
        return friend_ids

    async def get_pending_requests_received(self, user_id: int) -> List[Friendship]:
        """Get pending friend requests received by a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of pending Friendship requests
        """
        result = await self.db.execute(
            select(Friendship)
            .options(selectinload(Friendship.requester))
            .where(
                and_(
                    Friendship.addressee_id == user_id,
                    Friendship.status == FriendshipStatus.PENDING
                )
            )
            .order_by(Friendship.created_at.desc())
        )
        
        return list(result.scalars().all())

    async def get_pending_requests_sent(self, user_id: int) -> List[Friendship]:
        """Get pending friend requests sent by a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of pending Friendship requests
        """
        result = await self.db.execute(
            select(Friendship)
            .options(selectinload(Friendship.addressee))
            .where(
                and_(
                    Friendship.requester_id == user_id,
                    Friendship.status == FriendshipStatus.PENDING
                )
            )
            .order_by(Friendship.created_at.desc())
        )
        
        return list(result.scalars().all())

    async def count_friends(self, user_id: int) -> int:
        """Count number of accepted friends for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of friends
        """
        from sqlalchemy import func
        
        result = await self.db.execute(
            select(func.count(Friendship.id))
            .where(
                and_(
                    or_(
                        Friendship.requester_id == user_id,
                        Friendship.addressee_id == user_id
                    ),
                    Friendship.status == FriendshipStatus.ACCEPTED
                )
            )
        )
        
        return result.scalar() or 0

    async def are_friends(self, user1_id: int, user2_id: int) -> bool:
        """Check if two users are friends.
        
        Args:
            user1_id: First user ID
            user2_id: Second user ID
            
        Returns:
            True if users are friends (accepted status)
        """
        friendship = await self.get_friendship_between_users(user1_id, user2_id)
        return friendship is not None and friendship.is_accepted