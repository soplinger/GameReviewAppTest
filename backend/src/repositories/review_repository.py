"""Review repository for data access operations."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..models.review import Review


class ReviewRepository:
    """Repository for Review model CRUD operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, review_data: dict) -> Review:
        """Create a new review.
        
        Args:
            review_data: Dictionary with review attributes
            
        Returns:
            Created Review instance
        """
        review = Review(**review_data)
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def get_by_id(self, review_id: int, load_relations: bool = False) -> Optional[Review]:
        """Get review by ID.
        
        Args:
            review_id: Review ID
            load_relations: Whether to eagerly load user and game relationships
            
        Returns:
            Review instance or None
        """
        query = select(Review).where(Review.id == review_id)
        
        if load_relations:
            query = query.options(
                joinedload(Review.user),
                joinedload(Review.game)
            )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user_and_game(
        self, user_id: int, game_id: int
    ) -> Optional[Review]:
        """Get review by user and game (for uniqueness check).
        
        Args:
            user_id: User ID
            game_id: Game ID
            
        Returns:
            Review instance or None
        """
        result = await self.db.execute(
            select(Review).where(
                Review.user_id == user_id,
                Review.game_id == game_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user(
        self, user_id: int, limit: int = 20, offset: int = 0, load_relations: bool = False
    ) -> List[Review]:
        """Get all reviews by a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            offset: Pagination offset
            load_relations: Whether to eagerly load relationships
            
        Returns:
            List of Review instances
        """
        query = (
            select(Review)
            .where(Review.user_id == user_id)
            .order_by(Review.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        if load_relations:
            query = query.options(
                joinedload(Review.user),
                joinedload(Review.game)
            )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_game(
        self, game_id: int, limit: int = 20, offset: int = 0, load_relations: bool = False
    ) -> List[Review]:
        """Get all reviews for a game.
        
        Args:
            game_id: Game ID
            limit: Maximum number of results
            offset: Pagination offset
            load_relations: Whether to eagerly load relationships
            
        Returns:
            List of Review instances
        """
        query = (
            select(Review)
            .where(Review.game_id == game_id)
            .order_by(Review.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        if load_relations:
            query = query.options(
                joinedload(Review.user),
                joinedload(Review.game)
            )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, review_id: int, update_data: dict) -> Optional[Review]:
        """Update a review.
        
        Args:
            review_id: Review ID
            update_data: Dictionary with fields to update
            
        Returns:
            Updated Review instance or None
        """
        review = await self.get_by_id(review_id)
        if not review:
            return None

        for key, value in update_data.items():
            if hasattr(review, key) and value is not None:
                setattr(review, key, value)

        review.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def delete(self, review_id: int) -> bool:
        """Delete a review.
        
        Args:
            review_id: Review ID
            
        Returns:
            True if deleted, False if not found
        """
        review = await self.get_by_id(review_id)
        if not review:
            return False

        await self.db.delete(review)
        await self.db.commit()
        return True

    async def count_by_user(self, user_id: int) -> int:
        """Count total reviews by a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Total review count
        """
        result = await self.db.execute(
            select(func.count()).select_from(Review).where(Review.user_id == user_id)
        )
        return result.scalar_one()

    async def count_by_game(self, game_id: int) -> int:
        """Count total reviews for a game.
        
        Args:
            game_id: Game ID
            
        Returns:
            Total review count
        """
        result = await self.db.execute(
            select(func.count()).select_from(Review).where(Review.game_id == game_id)
        )
        return result.scalar_one()

    async def get_average_rating(self, game_id: int) -> Optional[float]:
        """Get average rating for a game.
        
        Args:
            game_id: Game ID
            
        Returns:
            Average rating or None if no reviews
        """
        result = await self.db.execute(
            select(func.avg(Review.rating)).where(Review.game_id == game_id)
        )
        avg_rating = result.scalar_one()
        return round(avg_rating, 2) if avg_rating else None

    async def increment_helpful_count(self, review_id: int) -> Optional[Review]:
        """Increment helpful count for a review.
        
        Args:
            review_id: Review ID
            
        Returns:
            Updated Review instance or None
        """
        review = await self.get_by_id(review_id)
        if not review:
            return None

        review.helpful_count += 1
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def get_feed_for_user(
        self, 
        user_id: int, 
        friend_ids: List[int],
        limit: int = 20, 
        offset: int = 0
    ) -> List[Review]:
        """Get feed of reviews from friends ordered by recency.
        
        Args:
            user_id: Current user ID
            friend_ids: List of friend user IDs
            limit: Number of reviews to return
            offset: Number of reviews to skip for pagination
            
        Returns:
            List of Review instances with user and game loaded
        """
        if not friend_ids:
            return []
        
        query = (
            select(Review)
            .where(Review.user_id.in_(friend_ids))
            .options(
                joinedload(Review.user),
                joinedload(Review.game)
            )
            .order_by(Review.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().unique())
