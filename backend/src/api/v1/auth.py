"""
Authentication API endpoints.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from ...core.config import settings
from ...schemas.auth import AuthSession, TokenRefreshRequest, UserLogin, UserRegister, UserResponse
from ...services.auth_service import AuthService
from ..deps import get_auth_service, get_current_user
from ...models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    """
    Register a new user account.
    
    Args:
        user_data: User registration data
        auth_service: Authentication service
        
    Returns:
        Created user data
        
    Raises:
        HTTPException: If registration fails (email/username already exists)
    """
    try:
        user = await auth_service.register(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=AuthSession)
async def login(
    login_data: UserLogin,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthSession:
    """
    Login and get access token.
    
    Args:
        login_data: User login credentials
        auth_service: Authentication service
        
    Returns:
        JWT access and refresh tokens
        
    Raises:
        HTTPException: If login fails (invalid credentials)
    """
    try:
        _, access_token, refresh_token = await auth_service.login(login_data)
        return AuthSession(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            access_token_expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_token_expires_in=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/refresh", response_model=AuthSession)
async def refresh_session(
    refresh_request: TokenRefreshRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthSession:
    """
    Refresh an authenticated session using a valid refresh token.

    This endpoint is intended for mobile clients that need seamless
    session renewal without forcing users to log in again.
    """
    try:
        access_token, refresh_token = await auth_service.refresh_access_token(
            refresh_request.refresh_token
        )
        return AuthSession(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            access_token_expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_token_expires_in=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/logout")
async def logout() -> dict[str, str]:
    """
    Logout endpoint for mobile/web parity.

    JWTs are stateless, so clients should delete stored tokens.
    """
    return {"message": "Logged out. Delete local tokens on the client."}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User data
    """
    return current_user
