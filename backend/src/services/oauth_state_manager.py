"""OAuth state management for tracking OAuth flows."""

from datetime import datetime, timedelta
from typing import Dict, Optional
import secrets


class OAuthStateManager:
    """
    Manages OAuth state tokens to link callbacks to authenticated users.
    
    In production, this should use Redis or another persistent store.
    """
    
    def __init__(self):
        # In-memory store: {state_token: {"user_id": int, "platform": str, "expires_at": datetime}}
        self._states: Dict[str, dict] = {}
    
    def create_state(self, user_id: int, platform: str) -> str:
        """
        Create a new state token for an OAuth flow.
        
        Args:
            user_id: User initiating the OAuth flow
            platform: Platform being linked
            
        Returns:
            State token
        """
        state = secrets.token_urlsafe(32)
        self._states[state] = {
            "user_id": user_id,
            "platform": platform,
            "expires_at": datetime.utcnow() + timedelta(minutes=10)
        }
        
        # Clean up expired states
        self._cleanup_expired()
        
        return state
    
    def get_user_id(self, state: str) -> Optional[int]:
        """
        Get user_id from state token and remove it.
        
        Args:
            state: State token from OAuth callback
            
        Returns:
            User ID or None if invalid/expired
        """
        state_data = self._states.get(state)
        
        if not state_data:
            return None
        
        # Check if expired
        if datetime.utcnow() > state_data["expires_at"]:
            del self._states[state]
            return None
        
        # Remove state after use (one-time use)
        user_id = state_data["user_id"]
        del self._states[state]
        
        return user_id
    
    def _cleanup_expired(self):
        """Remove expired state tokens."""
        now = datetime.utcnow()
        expired_keys = [
            key for key, data in self._states.items()
            if now > data["expires_at"]
        ]
        for key in expired_keys:
            del self._states[key]


# Global instance (in production, use dependency injection with Redis)
oauth_state_manager = OAuthStateManager()
