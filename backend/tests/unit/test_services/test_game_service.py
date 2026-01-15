"""Unit tests for GameService."""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base
from src.models.game import Game
from src.models.user import User
from src.models.review import Review
from src.services.game_service import GameService
from src.schemas.game import GameSearchParams


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
async def test_games(db_session: AsyncSession):
    """Create test games."""
    games = [
        Game(
            igdb_id=1000 + i,
            name=f"Action Game {i}",
            slug=f"action-game-{i}",
            summary=f"An action-packed game {i}",
            rating=70.0 + i * 5,
            platforms=["PC", "PlayStation 5"],
            genres=["Action", "Adventure"],
            last_synced_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        for i in range(5)
    ]
    
    for game in games:
        db_session.add(game)
    
    await db_session.commit()
    
    for game in games:
        await db_session.refresh(game)
    
    return games


@pytest.mark.asyncio
async def test_search_games_by_query(db_session: AsyncSession, test_games: list[Game]):
    """Test searching games by query."""
    service = GameService(db_session)
    
    params = GameSearchParams(
        query="Action",
        page=1,
        page_size=10,
    )
    
    results, total = await service.search_games(params)
    
    assert len(results) > 0
    assert all("Action" in r.name or "Action" in (r.summary or "") for r in results)


@pytest.mark.asyncio
async def test_get_game_details(db_session: AsyncSession, test_games: list[Game]):
    """Test getting game details."""
    service = GameService(db_session)
    
    game = test_games[0]
    details = await service.get_game_details(game.id)
    
    assert details is not None
    assert details.id == game.id
    assert details.name == game.name
    assert details.rating == game.rating
    assert details.user_rating is None  # No reviews yet
    assert details.user_rating_count == 0


@pytest.mark.asyncio
async def test_get_game_details_with_reviews(db_session: AsyncSession, test_games: list[Game]):
    """Test getting game details with aggregated review ratings."""
    service = GameService(db_session)
    
    # Create a user
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Create reviews for a game
    game = test_games[0]
    reviews = [
        Review(
            user_id=user.id,
            game_id=game.id,
            rating=4.0,
            title="Good game",
            content="This is a good game with decent gameplay. " * 5,
            is_recommended=True,
            helpful_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
    ]
    
    for review in reviews:
        db_session.add(review)
    
    await db_session.commit()
    
    # Get game details
    details = await service.get_game_details(game.id)
    
    assert details is not None
    assert details.user_rating == 4.0
    assert details.user_rating_count == 1


@pytest.mark.asyncio
async def test_get_game_by_slug(db_session: AsyncSession, test_games: list[Game]):
    """Test getting game by slug."""
    service = GameService(db_session)
    
    game = test_games[0]
    details = await service.get_game_by_slug(game.slug)
    
    assert details is not None
    assert details.slug == game.slug
    assert details.name == game.name


@pytest.mark.asyncio
async def test_get_popular_games(db_session: AsyncSession, test_games: list[Game]):
    """Test getting popular games."""
    service = GameService(db_session)
    
    popular = await service.get_popular_games(limit=3, offset=0)
    
    assert len(popular) > 0
    assert len(popular) <= 3


@pytest.mark.asyncio
async def test_search_games_pagination(db_session: AsyncSession, test_games: list[Game]):
    """Test game search pagination."""
    service = GameService(db_session)
    
    # First page
    params_page1 = GameSearchParams(page=1, page_size=2)
    results_page1, total = await service.search_games(params_page1)
    
    # Second page
    params_page2 = GameSearchParams(page=2, page_size=2)
    results_page2, _ = await service.search_games(params_page2)
    
    assert len(results_page1) <= 2
    assert len(results_page2) <= 2
    
    # Results should be different
    if len(results_page1) > 0 and len(results_page2) > 0:
        assert results_page1[0].id != results_page2[0].id
