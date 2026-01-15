"""Integration tests for game API endpoints."""

import pytest
from httpx import AsyncClient
from datetime import datetime

from src.main import app
from src.core.database import Base, get_db
from src.models.game import Game
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
    """Create test client."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_games(db_session: AsyncSession):
    """Create test games."""
    games = [
        Game(
            igdb_id=1000 + i,
            name=f"Action Game {i}",
            slug=f"action-game-{i}",
            summary=f"An action game {i}",
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
async def test_search_games(client: AsyncClient, test_games: list[Game]):
    """Test game search endpoint."""
    response = await client.get(
        "/api/v1/games/search",
        params={"query": "Action", "page": 1, "page_size": 10},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "games" in data
    assert "total" in data
    assert "page" in data
    assert len(data["games"]) > 0


@pytest.mark.asyncio
async def test_get_game_by_id(client: AsyncClient, test_games: list[Game]):
    """Test getting game by ID."""
    game = test_games[0]
    
    response = await client.get(f"/api/v1/games/{game.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == game.id
    assert data["name"] == game.name
    assert data["rating"] == game.rating


@pytest.mark.asyncio
async def test_get_game_by_slug(client: AsyncClient, test_games: list[Game]):
    """Test getting game by slug."""
    game = test_games[0]
    
    response = await client.get(f"/api/v1/games/slug/{game.slug}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == game.slug
    assert data["name"] == game.name


@pytest.mark.asyncio
async def test_get_popular_games(client: AsyncClient, test_games: list[Game]):
    """Test getting popular games."""
    response = await client.get(
        "/api/v1/games/popular",
        params={"page": 1, "page_size": 3},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "games" in data
    assert len(data["games"]) > 0
    assert len(data["games"]) <= 3


@pytest.mark.asyncio
async def test_get_recent_games(client: AsyncClient, test_games: list[Game]):
    """Test getting recent games."""
    response = await client.get(
        "/api/v1/games/recent",
        params={"page": 1, "page_size": 3},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "games" in data
    assert len(data["games"]) > 0


@pytest.mark.asyncio
async def test_search_games_pagination(client: AsyncClient, test_games: list[Game]):
    """Test game search pagination."""
    # Page 1
    response1 = await client.get(
        "/api/v1/games/search",
        params={"page": 1, "page_size": 2},
    )
    
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["page"] == 1
    assert len(data1["games"]) <= 2
    
    # Page 2
    response2 = await client.get(
        "/api/v1/games/search",
        params={"page": 2, "page_size": 2},
    )
    
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["page"] == 2


@pytest.mark.asyncio
async def test_get_nonexistent_game(client: AsyncClient):
    """Test getting a game that doesn't exist."""
    response = await client.get("/api/v1/games/99999")
    
    assert response.status_code == 404
