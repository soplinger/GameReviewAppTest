"""Game API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from ...api.deps import get_db
from ...schemas.game import GameDetail, GameListResponse, GameSearchParams, GameSearchResult
from ...services.game_service import GameService
from ...services.game_data_service import GameDataService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/games", tags=["games"])


async def get_game_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> GameService:
    """Get game service instance."""
    return GameService(db)


async def get_game_data_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> GameDataService:
    """Get game data service instance."""
    from ...repositories.game_repository import GameRepository
    return GameDataService(GameRepository(db))


class SyncResponse(BaseModel):
    """Response for sync operations."""
    
    success: bool
    message: str
    count: int


@router.get("/search", response_model=GameListResponse)
async def search_games(
    game_service: Annotated[GameService, Depends(get_game_service)],
    query: str = Query(None, min_length=1, description="Search query"),
    platform: str = Query(None, description="Filter by platform"),
    genre: str = Query(None, description="Filter by genre"),
    min_rating: float = Query(None, ge=0, le=100, description="Minimum rating"),
    sort_by: str = Query(
        "popularity", description="Sort by: popularity, rating, release_date, name"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> GameListResponse:
    """
    Search for games with optional filters.
    
    Returns paginated list of games matching search criteria.
    """
    params = GameSearchParams(
        query=query,
        platform=platform,
        genre=genre,
        min_rating=min_rating,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )

    games, total = await game_service.search_games(params)
    total_pages = (total + page_size - 1) // page_size

    return GameListResponse(
        games=games,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/popular", response_model=GameListResponse)
async def get_popular_games(
    game_service: Annotated[GameService, Depends(get_game_service)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> GameListResponse:
    """
    Get popular games.
    
    Returns paginated list of popular games by rating.
    """
    offset = (page - 1) * page_size
    games = await game_service.get_popular_games(limit=page_size, offset=offset)
    
    # Estimate total (we don't have exact count without additional query)
    total = len(games) + offset if len(games) == page_size else len(games) + offset
    total_pages = (total + page_size - 1) // page_size

    return GameListResponse(
        games=games,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/recent", response_model=GameListResponse)
async def get_recent_games(
    game_service: Annotated[GameService, Depends(get_game_service)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> GameListResponse:
    """
    Get recently released games.
    
    Returns paginated list of games by release date.
    """
    offset = (page - 1) * page_size
    games = await game_service.get_recent_games(limit=page_size, offset=offset)
    
    total = len(games) + offset if len(games) == page_size else len(games) + offset
    total_pages = (total + page_size - 1) // page_size

    return GameListResponse(
        games=games,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{game_id}", response_model=GameDetail)
async def get_game(
    game_id: int,
    game_service: Annotated[GameService, Depends(get_game_service)],
) -> GameDetail:
    """
    Get detailed game information by ID.
    
    Includes aggregated user review ratings.
    """
    game = await game_service.get_game_details(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )
    return game


@router.get("/slug/{slug}", response_model=GameDetail)
async def get_game_by_slug(
    slug: str,
    game_service: Annotated[GameService, Depends(get_game_service)],
) -> GameDetail:
    """
    Get detailed game information by slug.
    
    Includes aggregated user review ratings.
    """
    game = await game_service.get_game_by_slug(slug)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )
    return game


@router.post("/sync/popular", response_model=SyncResponse)
async def sync_popular_games(
    game_data_service: Annotated[GameDataService, Depends(get_game_data_service)],
    limit: int = Query(50, ge=1, le=100, description="Number of games to sync"),
) -> SyncResponse:
    """
    Sync popular games from IGDB API to database.
    
    This endpoint fetches popular games from IGDB and stores them locally.
    Useful for initially populating the database or refreshing popular games.
    """
    try:
        count = await game_data_service.sync_popular_games(limit=limit)
        return SyncResponse(
            success=True,
            message=f"Successfully synced {count} popular games from IGDB",
            count=count
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync games: {str(e)}"
        )


@router.post("/sync/search", response_model=SyncResponse)
async def sync_games_by_search(
    game_data_service: Annotated[GameDataService, Depends(get_game_data_service)],
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=50, description="Number of games to sync"),
) -> SyncResponse:
    """
    Search for games on IGDB and sync them to database.
    
    Useful for adding specific games or genres to the database.
    """
    try:
        games = await game_data_service.search_games(query=query, limit=limit)
        count = len(games)
        return SyncResponse(
            success=True,
            message=f"Successfully synced {count} games for query '{query}'",
            count=count
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync games: {str(e)}"
        )
