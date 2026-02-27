"""
Authentication service for user registration and login.
"""
from typing import Optional, Tuple

from jose import JWTError

from ..core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from ..models.user import User
from ..repositories.user_repository import UserRepository
from ..schemas.auth import TokenData, UserLogin, UserRegister


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def register(self, user_data: UserRegister) -> User:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
            
        Returns:
            Created User instance
            
        Raises:
            ValueError: If email or username already exists
        """
        # Check if email exists
        existing_user = await self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Check if username exists
        existing_username = await self.user_repository.get_by_username(user_data.username)
        if existing_username:
            raise ValueError("Username already taken")
        
        # Hash password and create user
        password_hash = get_password_hash(user_data.password)
        user = await self.user_repository.create(
            username=user_data.username,
            email=user_data.email,
            password_hash=password_hash,
        )
        
        return user
    
    async def login(self, login_data: UserLogin) -> Tuple[User, str, str]:
        """
        Authenticate user and generate tokens.
        
        Args:
            login_data: User login credentials
            
        Returns:
            Tuple of (User, access_token, refresh_token)
            
        Raises:
            ValueError: If credentials are invalid
        """
        # Get user by email
        user = await self.user_repository.get_by_email(login_data.email)
        if not user:
            raise ValueError("Invalid email or password")
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            raise ValueError("Invalid email or password")
        
        # Check if user is active
        if not user.is_active:
            raise ValueError("Account is inactive")
        
        # Generate tokens
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Update last login
        await self.user_repository.update_last_login(user)
        
        return user, access_token, refresh_token
    
    async def verify_token(self, token: str, expected_type: Optional[str] = None) -> TokenData:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            TokenData with user information
            
        Raises:
            ValueError: If token is invalid
        """
        try:
            payload = decode_token(token)
            token_type = payload.get("type")
            if expected_type and token_type != expected_type:
                raise ValueError(f"Invalid token type: expected {expected_type}")

            user_id = int(payload.get("sub", 0))
            email = payload.get("email", "")
            
            if not user_id or not email:
                raise ValueError("Invalid token payload")
            
            return TokenData(user_id=user_id, email=email)
        except JWTError as e:
            raise ValueError(f"Invalid token: {str(e)}")
    
    async def get_current_user(self, token: str) -> User:
        """
        Get current user from token.
        
        Args:
            token: JWT access token
            
        Returns:
            User instance
            
        Raises:
            ValueError: If token is invalid or user not found
        """
        token_data = await self.verify_token(token, expected_type="access")
        user = await self.user_repository.get_by_id(token_data.user_id)
        
        if not user:
            raise ValueError("User not found")
        
        if not user.is_active:
            raise ValueError("User is inactive")
        
        return user

    async def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        """
        Validate refresh token and issue a new token pair.

        Args:
            refresh_token: JWT refresh token

        Returns:
            Tuple of (access_token, refresh_token)
        """
        token_data = await self.verify_token(refresh_token, expected_type="refresh")

        token_payload = {
            "sub": str(token_data.user_id),
            "email": token_data.email,
        }
        new_access_token = create_access_token(token_payload)
        new_refresh_token = create_refresh_token(token_payload)
        return new_access_token, new_refresh_token
