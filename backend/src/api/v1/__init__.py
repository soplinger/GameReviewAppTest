"""API v1 package initialization."""
from .auth import router as auth_router
from .social import router as social_router

__all__ = ["auth_router", "social_router"]
