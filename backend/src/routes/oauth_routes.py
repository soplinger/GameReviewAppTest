"""OAuth routes for gaming platform authentication and account linking."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..api.deps import get_current_user
from ..models.user import User
from ..models.linked_account import PlatformType
from ..schemas.linked_account import (
    OAuthInitiateResponse,
    LinkedAccountResponse,
    LibrarySyncResponse,
    GameLibraryResponse,
    GameLibraryListResponse
)
from ..services.oauth_service import OAuthService
from ..services.library_sync_service import LibrarySyncService
from ..services.oauth_state_manager import oauth_state_manager
from ..services.sync_job_manager import sync_job_manager, JobStatus
from ..core.logging import get_logger
from ..core.errors import ValidationError, AuthenticationError

logger = get_logger(__name__)
router = APIRouter(prefix="/oauth", tags=["OAuth"])


@router.get("/{platform}", response_model=OAuthInitiateResponse)
async def initiate_oauth(
    platform: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Initiate OAuth flow for a gaming platform.
    
    Returns authorization URL to redirect user to platform login.
    """
    # Validate platform
    try:
        platform_type = PlatformType(platform.lower())
    except ValueError:
        raise ValidationError(f"Invalid platform: {platform}. Must be one of: steam, playstation, xbox")
    
    # Create state token for this OAuth flow
    state = oauth_state_manager.create_state(current_user.id, platform)
    
    # Build redirect URI
    base_url = str(request.base_url).rstrip("/")
    redirect_uri = f"{base_url}/api/v1/oauth/{platform}/callback?state={state}"
    
    oauth_service = OAuthService(db)
    result = await oauth_service.initiate_oauth_flow(
        user_id=current_user.id,
        platform=platform_type,
        redirect_uri=redirect_uri
    )
    
    logger.info(
        "oauth_initiated",
        user_id=current_user.id,
        platform=platform,
        redirect_uri=redirect_uri
    )
    
    return OAuthInitiateResponse(
        authorization_url=result["authorization_url"],
        state=state
    )


@router.get("/{platform}/callback")
async def oauth_callback(
    platform: str,
    request: Request,
    state: str = Query(..., description="OAuth state token"),
    code: Optional[str] = Query(None),
    # Steam OpenID params
    openid_mode: Optional[str] = Query(None, alias="openid.mode"),
    openid_claimed_id: Optional[str] = Query(None, alias="openid.claimed_id"),
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth callback handler for gaming platforms.
    
    Processes authorization response and creates linked account.
    Note: This endpoint does NOT require authentication - it uses state token.
    """
    # Validate state and get user_id
    user_id = oauth_state_manager.get_user_id(state)
    if not user_id:
        logger.error("oauth_invalid_state", state=state)
        raise AuthenticationError("Invalid or expired OAuth state token")
    
    # Validate platform
    try:
        platform_type = PlatformType(platform.lower())
    except ValueError:
        raise ValidationError(f"Invalid platform: {platform}")
    
    oauth_service = OAuthService(db)
    
    # Handle Steam OpenID callback
    if platform_type == PlatformType.STEAM:
        callback_params = dict(request.query_params)
        linked_account = await oauth_service.handle_steam_callback(
            user_id=user_id,
            callback_params=callback_params
        )
    else:
        # Handle OAuth 2.0 callback (PSN, Xbox)
        if not code:
            raise ValidationError("Missing authorization code")
        
        base_url = str(request.base_url).rstrip("/")
        redirect_uri = f"{base_url}/api/v1/oauth/{platform}/callback?state={state}"
        
        linked_account = await oauth_service.handle_oauth_callback(
            user_id=user_id,
            platform=platform_type,
            code=code,
            state=state or "",
            redirect_uri=redirect_uri
        )
    
    logger.info(
        "oauth_callback_success",
        user_id=user_id,
        platform=platform,
        linked_account_id=linked_account.id
    )
    
    # Redirect to frontend success page
    frontend_url = "http://localhost:5173"  # TODO: Get from config
    return RedirectResponse(
        url=f"{frontend_url}/linked-accounts?success=true&platform={platform}"
    )


@router.get("/accounts/me", response_model=list[LinkedAccountResponse])
async def get_my_linked_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all linked gaming accounts for current user.
    """
    oauth_service = OAuthService(db)
    accounts = await oauth_service.get_user_linked_accounts(current_user.id)
    
    logger.info(
        "fetched_linked_accounts",
        user_id=current_user.id,
        count=len(accounts)
    )
    
    return [LinkedAccountResponse.from_orm(account) for account in accounts]


@router.delete("/accounts/{platform}")
async def unlink_account(
    platform: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Unlink a gaming platform account.
    """
    # Validate platform
    try:
        platform_type = PlatformType(platform.lower())
    except ValueError:
        raise ValidationError(f"Invalid platform: {platform}")
    
    oauth_service = OAuthService(db)
    await oauth_service.unlink_account(current_user.id, platform_type)
    
    logger.info(
        "account_unlinked",
        user_id=current_user.id,
        platform=platform
    )
    
    return {"message": f"{platform.capitalize()} account unlinked successfully"}


@router.post("/library/sync")
async def sync_game_library(
    platform: Optional[str] = Query(None, description="Specific platform to sync, or all if not specified"),
    current_user: User = Depends(get_current_user)
):
    """
    Start library sync job in background.
    
    Returns job ID to check progress using /library/sync/status/{job_id}.
    """
    platform_type = None
    if platform:
        try:
            platform_type = PlatformType(platform.lower())
        except ValueError:
            raise ValidationError(f"Invalid platform: {platform}")
    
    # Create job
    job_id = sync_job_manager.create_job(
        user_id=current_user.id,
        platform=platform_type.value if platform_type else None
    )
    
    # Create a wrapper coroutine that manages its own DB session
    async def run_sync_with_new_session():
        from ..core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            library_sync_service = LibrarySyncService(session)
            return await library_sync_service.sync_user_library(
                user_id=current_user.id,
                platform=platform_type,
                job_id=job_id
            )
    
    # Start sync in background with new session
    sync_job_manager.start_job(job_id, run_sync_with_new_session())
    
    logger.info(
        "library_sync_started",
        user_id=current_user.id,
        platform=platform or "all",
        job_id=job_id
    )
    
    return {
        "job_id": job_id,
        "status": "started",
        "message": "Library sync started in background. Use job_id to check progress."
    }


@router.get("/library/sync/status/{job_id}")
async def get_sync_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get status of a library sync job.
    
    Returns job progress, status, and results if completed.
    """
    job = sync_job_manager.get_job(job_id)
    
    if not job:
        raise ValidationError(f"Job {job_id} not found")
    
    # Verify job belongs to current user
    if job.user_id != current_user.id:
        raise ValidationError("Unauthorized access to job")
    
    return {
        "job_id": job.job_id,
        "status": job.status.value,
        "platform": job.platform,
        "progress": job.progress,
        "total_games": job.total_games,
        "synced_games": job.synced_games,
        "failed_games": job.failed_games,
        "created_at": job.created_at.isoformat(),
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "error": job.error,
        "result": job.result
    }


@router.get("/library/sync/jobs")
async def get_my_sync_jobs(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user)
):
    """
    Get recent sync jobs for current user.
    """
    jobs = sync_job_manager.get_user_jobs(current_user.id, limit=limit)
    
    return {
        "jobs": [
            {
                "job_id": job.job_id,
                "status": job.status.value,
                "platform": job.platform,
                "progress": job.progress,
                "total_games": job.total_games,
                "synced_games": job.synced_games,
                "failed_games": job.failed_games,
                "created_at": job.created_at.isoformat(),
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "error": job.error
            }
            for job in jobs
        ]
    }


@router.get("/library/me", response_model=GameLibraryListResponse)
async def get_my_game_library(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's game library.
    
    Returns games imported from linked platforms with playtime and achievements.
    """
    platform_type = None
    if platform:
        try:
            platform_type = PlatformType(platform.lower())
        except ValueError:
            raise ValidationError(f"Invalid platform: {platform}")
    
    library_sync_service = LibrarySyncService(db)
    library, total = await library_sync_service.get_user_library(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        platform=platform_type
    )
    
    logger.info(
        "fetched_game_library",
        user_id=current_user.id,
        count=len(library),
        total=total,
        platform=platform or "all"
    )
    
    return GameLibraryListResponse(
        items=[GameLibraryResponse.from_orm(entry) for entry in library],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/library/games/{game_id}/playtime")
async def get_game_playtime(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get total playtime for a specific game across all platforms.
    """
    library_sync_service = LibrarySyncService(db)
    playtime = await library_sync_service.get_game_playtime(
        user_id=current_user.id,
        game_id=game_id
    )
    
    return {
        "game_id": game_id,
        "playtime_hours": playtime
    }
