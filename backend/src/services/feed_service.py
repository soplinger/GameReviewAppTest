"""Feed service for social review feed functionality."""

from typing import List

from ..repositories.friendship_repository import FriendshipRepository
from ..repositories.review_repository import ReviewRepository
from ..models.review import Review


class FeedService:
    """Service for managing user's social feed."""

    def __init__(
        self, 
        review_repo: ReviewRepository,
        friendship_repo: FriendshipRepository
    ):
        self.review_repo = review_repo
        self.friendship_repo = friendship_repo

    async def get_user_feed(
        self, 
        user_id: int, 
        page: int = 1, 
        per_page: int = 20
    ) -> List[Review]:
        """Get paginated feed of reviews from user's friends.
        
        Args:
            user_id: Current user ID
            page: Page number (1-based)
            per_page: Number of reviews per page (max 50)
            
        Returns:
            List of Review instances with user and game relationships loaded
            
        Raises:
            ValueError: If page < 1 or per_page > 50
        """
        if page < 1:
            raise ValueError("Page must be >= 1")
        
        if per_page > 50:
            raise ValueError("Per page limit is 50")

        # Get list of user's friends
        friend_ids = await self.friendship_repo.get_friend_ids(user_id)
        
        if not friend_ids:
            return []

        # Calculate offset for pagination
        offset = (page - 1) * per_page
        
        # Get feed reviews from friends
        reviews = await self.review_repo.get_feed_for_user(
            user_id=user_id,
            friend_ids=friend_ids,
            limit=per_page,
            offset=offset
        )
        
        return reviews

    async def get_feed_count(self, user_id: int) -> int:
        """Get total count of reviews available in user's feed.
        
        Args:
            user_id: Current user ID
            
        Returns:
            Total number of reviews in feed
        """
        friend_ids = await self.friendship_repo.get_friend_ids(user_id)
        
        if not friend_ids:
            return 0

        # Count reviews from all friends
        count = 0
        for friend_id in friend_ids:
            count += await self.review_repo.count_by_user(friend_id)
            
        return count