"""Unit tests for ReviewService."""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base
from src.models.user import User
from src.models.game import Game
from src.models.review import Review
from src.services.review_service import ReviewService
from src.schemas.review import ReviewCreate, ReviewUpdate


@pytest.fixture
async def db_session():
    """Create an in-memory test database."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_game(db_session: AsyncSession):
    """Create a test game."""
    game = Game(
        igdb_id=1234,
        name="Test Game",
        slug="test-game",
        summary="A test game for testing",
        rating=85.5,
        platforms=["PC", "PlayStation 5"],
        genres=["Action", "Adventure"],
        last_synced_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(game)
    await db_session.commit()
    await db_session.refresh(game)
    return game


@pytest.mark.asyncio
async def test_create_review_success(db_session: AsyncSession, test_user: User, test_game: Game):
    """Test successful review creation."""
    service = ReviewService(db_session)
    
    review_data = ReviewCreate(
        game_id=test_game.id,
        rating=4.5,
        title="Great game!",
        content="This is a fantastic game with amazing graphics and gameplay. " * 3,
        playtime_hours=25.5,
        platform="PC",
        is_recommended=True,
    )
    
    review = await service.create_review(test_user.id, review_data)
    
    assert review.id is not None
    assert review.user_id == test_user.id
    assert review.game_id == test_game.id
    assert review.rating == 4.5
    assert review.title == "Great game!"
    assert review.playtime_hours == 25.5
    assert review.is_recommended is True
    assert review.username == test_user.username
    assert review.game_name == test_game.name


@pytest.mark.asyncio
async def test_create_review_duplicate(db_session: AsyncSession, test_user: User, test_game: Game):
    """Test that creating a duplicate review fails."""
    service = ReviewService(db_session)
    
    review_data = ReviewCreate(
        game_id=test_game.id,
        rating=4.5,
        title="Great game!",
        content="This is a fantastic game with amazing graphics and gameplay. " * 3,
        is_recommended=True,
    )
    
    # Create first review
    await service.create_review(test_user.id, review_data)
    
    # Try to create duplicate
    with pytest.raises(ValueError, match="already reviewed"):
        await service.create_review(test_user.id, review_data)


@pytest.mark.asyncio
async def test_create_review_invalid_rating(db_session: AsyncSession, test_user: User, test_game: Game):
    """Test that invalid rating fails."""
    service = ReviewService(db_session)
    
    review_data = ReviewCreate(
        game_id=test_game.id,
        rating=6.0,  # Invalid: > 5
        title="Great game!",
        content="This is a fantastic game with amazing graphics and gameplay. " * 3,
        is_recommended=True,
    )
    
    with pytest.raises(ValueError, match="Rating must be between"):
        await service.create_review(test_user.id, review_data)


@pytest.mark.asyncio
async def test_create_review_short_content(db_session: AsyncSession, test_user: User, test_game: Game):
    """Test that short content fails validation."""
    service = ReviewService(db_session)
    
    review_data = ReviewCreate(
        game_id=test_game.id,
        rating=4.5,
        title="Great game!",
        content="Too short",  # Invalid: < 50 chars
        is_recommended=True,
    )
    
    with pytest.raises(ValueError, match="at least 50 characters"):
        await service.create_review(test_user.id, review_data)


@pytest.mark.asyncio
async def test_update_review_success(db_session: AsyncSession, test_user: User, test_game: Game):
    """Test successful review update."""
    service = ReviewService(db_session)
    
    # Create review
    review_data = ReviewCreate(
        game_id=test_game.id,
        rating=4.5,
        title="Great game!",
        content="This is a fantastic game with amazing graphics and gameplay. " * 3,
        is_recommended=True,
    )
    review = await service.create_review(test_user.id, review_data)
    
    # Update review
    update_data = ReviewUpdate(
        rating=5.0,
        title="Amazing game!",
        content="Updated: This is an even better game than I initially thought! " * 3,
    )
    updated = await service.update_review(test_user.id, review.id, update_data)
    
    assert updated.rating == 5.0
    assert updated.title == "Amazing game!"
    assert "Updated:" in updated.content


@pytest.mark.asyncio
async def test_update_review_not_owner(db_session: AsyncSession, test_user: User, test_game: Game):
    """Test that non-owner cannot update review."""
    service = ReviewService(db_session)
    
    # Create review
    review_data = ReviewCreate(
        game_id=test_game.id,
        rating=4.5,
        title="Great game!",
        content="This is a fantastic game with amazing graphics and gameplay. " * 3,
        is_recommended=True,
    )
    review = await service.create_review(test_user.id, review_data)
    
    # Try to update as different user
    update_data = ReviewUpdate(rating=5.0)
    with pytest.raises(ValueError, match="only update your own"):
        await service.update_review(test_user.id + 999, review.id, update_data)


@pytest.mark.asyncio
async def test_delete_review_success(db_session: AsyncSession, test_user: User, test_game: Game):
    """Test successful review deletion."""
    service = ReviewService(db_session)
    
    # Create review
    review_data = ReviewCreate(
        game_id=test_game.id,
        rating=4.5,
        title="Great game!",
        content="This is a fantastic game with amazing graphics and gameplay. " * 3,
        is_recommended=True,
    )
    review = await service.create_review(test_user.id, review_data)
    
    # Delete review
    result = await service.delete_review(test_user.id, review.id)
    assert result is True
    
    # Verify it's gone
    deleted = await service.get_review(review.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_delete_review_not_owner(db_session: AsyncSession, test_user: User, test_game: Game):
    """Test that non-owner cannot delete review."""
    service = ReviewService(db_session)
    
    # Create review
    review_data = ReviewCreate(
        game_id=test_game.id,
        rating=4.5,
        title="Great game!",
        content="This is a fantastic game with amazing graphics and gameplay. " * 3,
        is_recommended=True,
    )
    review = await service.create_review(test_user.id, review_data)
    
    # Try to delete as different user
    with pytest.raises(ValueError, match="only delete your own"):
        await service.delete_review(test_user.id + 999, review.id)


@pytest.mark.asyncio
async def test_get_user_reviews(db_session: AsyncSession, test_user: User, test_game: Game):
    """Test getting reviews by user."""
    service = ReviewService(db_session)
    
    # Create multiple reviews for different games
    for i in range(3):
        game = Game(
            igdb_id=1234 + i,
            name=f"Test Game {i}",
            slug=f"test-game-{i}",
            last_synced_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(game)
        await db_session.commit()
        await db_session.refresh(game)
        
        review_data = ReviewCreate(
            game_id=game.id,
            rating=4.0 + i * 0.5,
            title=f"Review {i}",
            content=f"Content for review {i}. " * 10,
            is_recommended=True,
        )
        await service.create_review(test_user.id, review_data)
    
    # Get user reviews
    reviews = await service.get_user_reviews(test_user.id, limit=10, offset=0)
    
    assert len(reviews) == 3
    assert all(r.user_id == test_user.id for r in reviews)
