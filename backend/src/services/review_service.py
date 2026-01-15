"""Review service for business logic."""

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.game import Game
from ..models.review import Review
from ..models.user import User
from ..repositories.game_repository import GameRepository
from ..repositories.review_repository import ReviewRepository
from ..repositories.user_repository import UserRepository
from ..schemas.review import ReviewCreate, ReviewResponse, ReviewUpdate


class ReviewService:
    """Service for review business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.review_repo = ReviewRepository(db)
        self.user_repo = UserRepository(db)
        self.game_repo = GameRepository(db)

    async def create_review(
        self, user_id: int, review_data: ReviewCreate
    ) -> ReviewResponse:
        """Create a new review.
        
        Args:
            user_id: ID of the user creating the review
            review_data: Review creation data
            
        Returns:
            Created review response
            
        Raises:
            ValueError: If validation fails
        """
        # Validate user exists
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Validate game exists
        game = await self.game_repo.get_by_id(review_data.game_id)
        if not game:
            raise ValueError("Game not found")

        # Check if user already reviewed this game
        existing_review = await self.review_repo.get_by_user_and_game(
            user_id, review_data.game_id
        )
        if existing_review:
            raise ValueError("You have already reviewed this game")

        # Validate rating range (schema should handle this, but double-check)
        if not 1.0 <= review_data.rating <= 5.0:
            raise ValueError("Rating must be between 1.0 and 5.0")

        # Validate content length (schema should handle this too)
        if len(review_data.content.strip()) < 50:
            raise ValueError("Review content must be at least 50 characters")

        # Create review
        review_dict = review_data.model_dump()
        review_dict["user_id"] = user_id
        review = await self.review_repo.create(review_dict)

        # Build response with populated fields
        return await self._build_review_response(review, user, game)

    async def update_review(
        self, user_id: int, review_id: int, review_data: ReviewUpdate
    ) -> ReviewResponse:
        """Update an existing review.
        
        Args:
            user_id: ID of the user updating the review
            review_id: ID of the review to update
            review_data: Review update data
            
        Returns:
            Updated review response
            
        Raises:
            ValueError: If validation fails
        """
        # Get existing review
        review = await self.review_repo.get_by_id(review_id, load_relations=True)
        if not review:
            raise ValueError("Review not found")

        # Verify user owns the review
        if review.user_id != user_id:
            raise ValueError("You can only update your own reviews")

        # Validate rating if provided
        if review_data.rating is not None:
            if not 1.0 <= review_data.rating <= 5.0:
                raise ValueError("Rating must be between 1.0 and 5.0")

        # Validate content length if provided
        if review_data.content is not None:
            if len(review_data.content.strip()) < 50:
                raise ValueError("Review content must be at least 50 characters")

        # Update review
        update_dict = review_data.model_dump(exclude_unset=True)
        updated_review = await self.review_repo.update(review_id, update_dict)

        # Build response
        return await self._build_review_response(
            updated_review, updated_review.user, updated_review.game
        )

    async def delete_review(self, user_id: int, review_id: int) -> bool:
        """Delete a review.
        
        Args:
            user_id: ID of the user deleting the review
            review_id: ID of the review to delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            ValueError: If validation fails
        """
        # Get existing review
        review = await self.review_repo.get_by_id(review_id)
        if not review:
            raise ValueError("Review not found")

        # Verify user owns the review
        if review.user_id != user_id:
            raise ValueError("You can only delete your own reviews")

        return await self.review_repo.delete(review_id)

    async def get_review(self, review_id: int) -> Optional[ReviewResponse]:
        """Get a review by ID.
        
        Args:
            review_id: Review ID
            
        Returns:
            Review response or None
        """
        review = await self.review_repo.get_by_id(review_id, load_relations=True)
        if not review:
            return None

        return await self._build_review_response(review, review.user, review.game)

    async def get_user_reviews(
        self, user_id: int, limit: int = 20, offset: int = 0
    ) -> List[ReviewResponse]:
        """Get all reviews by a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of review responses
        """
        reviews = await self.review_repo.get_by_user(
            user_id, limit=limit, offset=offset, load_relations=True
        )

        return [
            await self._build_review_response(review, review.user, review.game)
            for review in reviews
        ]

    async def get_game_reviews(
        self, game_id: int, limit: int = 20, offset: int = 0
    ) -> List[ReviewResponse]:
        """Get all reviews for a game.
        
        Args:
            game_id: Game ID
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of review responses
        """
        reviews = await self.review_repo.get_by_game(
            game_id, limit=limit, offset=offset, load_relations=True
        )

        return [
            await self._build_review_response(review, review.user, review.game)
            for review in reviews
        ]

    async def mark_helpful(self, review_id: int) -> Optional[ReviewResponse]:
        """Mark a review as helpful (increment helpful count).
        
        Args:
            review_id: Review ID
            
        Returns:
            Updated review response or None
        """
        review = await self.review_repo.increment_helpful_count(review_id)
        if not review:
            return None

        # Load relations for response
        review = await self.review_repo.get_by_id(review_id, load_relations=True)
        return await self._build_review_response(review, review.user, review.game)

    async def _build_review_response(
        self, review: Review, user: User, game: Game
    ) -> ReviewResponse:
        """Build a review response with populated fields.
        
        Args:
            review: Review instance
            user: User instance
            game: Game instance
            
        Returns:
            Review response with populated fields
        """
        return ReviewResponse(
            id=review.id,
            user_id=review.user_id,
            game_id=review.game_id,
            rating=review.rating,
            title=review.title,
            content=review.content,
            playtime_hours=review.playtime_hours,
            platform=review.platform,
            is_recommended=review.is_recommended,
            helpful_count=review.helpful_count,
            created_at=review.created_at,
            updated_at=review.updated_at,
            username=user.username,
            user_avatar_url=user.avatar_url,
            game_name=game.name,
            game_cover_url=game.cover_url,
        )
