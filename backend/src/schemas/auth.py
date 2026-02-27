"""
Authentication schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    """User registration request."""
    
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)  # Bcrypt limit is 72 bytes
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username must contain only letters, numbers, underscores, and hyphens")
        return v
    
    @field_validator("password")
    @classmethod  
    def validate_password(cls, v: str) -> str:
        """Validate password length for bcrypt compatibility."""
        password_bytes = v.encode('utf-8')
        if len(password_bytes) > 72:
            raise ValueError("Password cannot exceed 72 bytes when encoded as UTF-8")
        return v


class UserLogin(BaseModel):
    """User login request."""
    
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    """Refresh access token request."""

    refresh_token: str


class AuthSession(BaseModel):
    """Authentication session details for mobile clients."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    access_token_expires_in: int
    refresh_token_expires_in: int


class TokenData(BaseModel):
    """Data encoded in JWT token."""
    
    user_id: int
    email: str


class UserResponse(BaseModel):
    """User response model."""
    
    id: int
    username: str
    email: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User profile update request."""
    
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
