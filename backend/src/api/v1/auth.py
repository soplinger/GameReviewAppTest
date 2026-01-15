"""
Authentication API endpoints.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from ...schemas.auth import Token, UserLogin, UserRegister, UserResponse
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


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
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
        user, access_token, refresh_token = await auth_service.login(login_data)
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


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
