"""Unit tests for AuthService token behavior."""

import pytest

from src.core.security import create_refresh_token
from src.schemas.auth import TokenData
from src.services.auth_service import AuthService


class DummyUserRepo:
    """Minimal repository stub for AuthService tests."""


@pytest.mark.asyncio
async def test_verify_token_rejects_wrong_token_type():
    """Access verification should reject refresh tokens."""
    service = AuthService(DummyUserRepo())
    refresh_token = create_refresh_token({"sub": "1", "email": "ios@example.com"})

    with pytest.raises(ValueError, match="Invalid token type"):
        await service.verify_token(refresh_token, expected_type="access")


@pytest.mark.asyncio
async def test_refresh_access_token_success(monkeypatch):
    """Refreshing a session should return a new token pair."""
    service = AuthService(DummyUserRepo())

    async def fake_verify_token(token: str, expected_type: str = None) -> TokenData:
        assert token == "refresh-token"
        assert expected_type == "refresh"
        return TokenData(user_id=42, email="ios@example.com")

    monkeypatch.setattr(service, "verify_token", fake_verify_token)

    access_token, refresh_token = await service.refresh_access_token("refresh-token")

    assert isinstance(access_token, str)
    assert isinstance(refresh_token, str)
    assert access_token
    assert refresh_token
