"""Integration tests for review API endpoints."""

import pytest
from httpx import AsyncClient
from datetime import datetime

from src.main import app
from src.core.database import Base, get_db
from src.models.user import User
from src.models.game import Game
from src.core.security import get_password_hash, create_access_token
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture
async def db_session():
    """Create test database."""
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
async def client(db_session: AsyncSession):
    """Create test client with database override."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("password123"),
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
    """Create test game."""
    game = Game(
        igdb_id=1234,
        name="Test Game",
        slug="test-game",
        summary="A test game",
        rating=85.5,
        platforms=["PC"],
        genres=["Action"],
        last_synced_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(game)
    await db_session.commit()
    await db_session.refresh(game)
    return game


@pytest.fixture
def auth_headers(test_user: User):
    """Create authentication headers."""
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_review(client: AsyncClient, test_game: Game, auth_headers: dict):
    """Test creating a review."""
    response = await client.post(
        "/api/v1/reviews/",
        json={
            "game_id": test_game.id,
            "rating": 4.5,
            "title": "Great game!",
            "content": "This is a fantastic game with amazing graphics and gameplay. " * 3,
            "playtime_hours": 25.5,
            "platform": "PC",
            "is_recommended": True,
        },
        headers=auth_headers,
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 4.5
    assert data["title"] == "Great game!"
    assert data["game_id"] == test_game.id


@pytest.mark.asyncio
async def test_create_review_unauthorized(client: AsyncClient, test_game: Game):
    """Test creating review without auth fails."""
    response = await client.post(
        "/api/v1/reviews/",
        json={
            "game_id": test_game.id,
            "rating": 4.5,
            "title": "Great game!",
            "content": "This is a fantastic game. " * 10,
            "is_recommended": True,
        },
    )
    
    assert response.status_code == 403  # Forbidden


@pytest.mark.asyncio
async def test_get_review(client: AsyncClient, test_game: Game, auth_headers: dict):
    """Test getting a review by ID."""
    # Create review first
    create_response = await client.post(
        "/api/v1/reviews/",
        json={
            "game_id": test_game.id,
            "rating": 4.5,
            "title": "Great game!",
            "content": "This is a fantastic game. " * 10,
            "is_recommended": True,
        },
        headers=auth_headers,
    )
    review_id = create_response.json()["id"]
    
    # Get review
    response = await client.get(f"/api/v1/reviews/{review_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == review_id
    assert data["rating"] == 4.5


@pytest.mark.asyncio
async def test_update_review(client: AsyncClient, test_game: Game, auth_headers: dict):
    """Test updating a review."""
    # Create review
    create_response = await client.post(
        "/api/v1/reviews/",
        json={
            "game_id": test_game.id,
            "rating": 4.5,
            "title": "Great game!",
            "content": "This is a fantastic game. " * 10,
            "is_recommended": True,
        },
        headers=auth_headers,
    )
    review_id = create_response.json()["id"]
    
    # Update review
    response = await client.put(
        f"/api/v1/reviews/{review_id}",
        json={
            "rating": 5.0,
            "title": "Amazing game!",
        },
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == 5.0
    assert data["title"] == "Amazing game!"


@pytest.mark.asyncio
async def test_delete_review(client: AsyncClient, test_game: Game, auth_headers: dict):
    """Test deleting a review."""
    # Create review
    create_response = await client.post(
        "/api/v1/reviews/",
        json={
            "game_id": test_game.id,
            "rating": 4.5,
            "title": "Great game!",
            "content": "This is a fantastic game. " * 10,
            "is_recommended": True,
        },
        headers=auth_headers,
    )
    review_id = create_response.json()["id"]
    
    # Delete review
    response = await client.delete(
        f"/api/v1/reviews/{review_id}",
        headers=auth_headers,
    )
    
    assert response.status_code == 204
    
    # Verify deleted
    get_response = await client.get(f"/api/v1/reviews/{review_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_list_reviews_by_game(client: AsyncClient, test_game: Game, auth_headers: dict):
    """Test listing reviews for a game."""
    # Create review
    await client.post(
        "/api/v1/reviews/",
        json={
            "game_id": test_game.id,
            "rating": 4.5,
            "title": "Great game!",
            "content": "This is a fantastic game. " * 10,
            "is_recommended": True,
        },
        headers=auth_headers,
    )
    
    # List reviews
    response = await client.get(
        "/api/v1/reviews/",
        params={"game_id": test_game.id},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["reviews"]) >= 1
    assert data["reviews"][0]["game_id"] == test_game.id


@pytest.mark.asyncio
async def test_get_my_reviews(client: AsyncClient, test_game: Game, auth_headers: dict):
    """Test getting authenticated user's reviews."""
    # Create review
    await client.post(
        "/api/v1/reviews/",
        json={
            "game_id": test_game.id,
            "rating": 4.5,
            "title": "Great game!",
            "content": "This is a fantastic game. " * 10,
            "is_recommended": True,
        },
        headers=auth_headers,
    )
    
    # Get my reviews
    response = await client.get(
        "/api/v1/reviews/users/me/reviews",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["reviews"]) >= 1
