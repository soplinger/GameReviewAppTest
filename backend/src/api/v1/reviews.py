"""Review API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...api.deps import get_current_user, get_review_service
from ...models.user import User
from ...schemas.review import (
    ReviewCreate,
    ReviewListResponse,
    ReviewResponse,
    ReviewUpdate,
)
from ...services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    review_service: Annotated[ReviewService, Depends(get_review_service)],
) -> ReviewResponse:
    """
    Create a new review.
    
    Requires authentication.
    """
    try:
        return await review_service.create_review(current_user.id, review_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: int,
    review_service: Annotated[ReviewService, Depends(get_review_service)],
) -> ReviewResponse:
    """
    Get a review by ID.
    """
    review = await review_service.get_review(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )
    return review


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    review_service: Annotated[ReviewService, Depends(get_review_service)],
) -> ReviewResponse:
    """
    Update a review.
    
    Requires authentication and ownership of the review.
    """
    try:
        return await review_service.update_review(
            current_user.id, review_id, review_data
        )
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    review_service: Annotated[ReviewService, Depends(get_review_service)],
):
    """
    Delete a review.
    
    Requires authentication and ownership of the review.
    """
    try:
        success = await review_service.delete_review(current_user.id, review_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
            )
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=ReviewListResponse)
async def list_reviews(
    review_service: Annotated[ReviewService, Depends(get_review_service)],
    game_id: int = Query(None, description="Filter by game ID"),
    user_id: int = Query(None, description="Filter by user ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> ReviewListResponse:
    """
    List reviews with optional filtering.
    
    Can filter by game_id or user_id.
    """
    offset = (page - 1) * page_size

    if game_id:
        reviews = await review_service.get_game_reviews(
            game_id, limit=page_size, offset=offset
        )
        from ...repositories.review_repository import ReviewRepository
        from ...core.database import get_db

        # Get total count (this is a bit hacky, ideally service should handle this)
        async for db in get_db():
            repo = ReviewRepository(db)
            total = await repo.count_by_game(game_id)
            break
    elif user_id:
        reviews = await review_service.get_user_reviews(
            user_id, limit=page_size, offset=offset
        )
        from ...repositories.review_repository import ReviewRepository
        from ...core.database import get_db

        async for db in get_db():
            repo = ReviewRepository(db)
            total = await repo.count_by_user(user_id)
            break
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either game_id or user_id filter",
        )

    total_pages = (total + page_size - 1) // page_size

    return ReviewListResponse(
        reviews=reviews,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("/{review_id}/helpful", response_model=ReviewResponse)
async def mark_review_helpful(
    review_id: int,
    review_service: Annotated[ReviewService, Depends(get_review_service)],
) -> ReviewResponse:
    """
    Mark a review as helpful (increment helpful count).
    """
    review = await review_service.mark_helpful(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )
    return review


@router.get("/users/me/reviews", response_model=ReviewListResponse)
async def get_my_reviews(
    current_user: Annotated[User, Depends(get_current_user)],
    review_service: Annotated[ReviewService, Depends(get_review_service)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> ReviewListResponse:
    """
    Get reviews for the currently authenticated user.
    
    Requires authentication.
    """
    offset = (page - 1) * page_size
    reviews = await review_service.get_user_reviews(
        current_user.id, limit=page_size, offset=offset
    )

    from ...repositories.review_repository import ReviewRepository
    from ...core.database import get_db

    async for db in get_db():
        repo = ReviewRepository(db)
        total = await repo.count_by_user(current_user.id)
        break

    total_pages = (total + page_size - 1) // page_size

    return ReviewListResponse(
        reviews=reviews,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
