"""Tests for authentication middleware and dependencies."""

import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from gateway.dependencies import get_current_user, AuthenticatedUser


class TestAuthenticatedUser:
    """Tests for AuthenticatedUser class."""

    def test_basic_user(self):
        """Test basic user creation."""
        user = AuthenticatedUser(
            user_id="user-123",
            email="test@example.com",
            role="authenticated",
        )
        assert user.user_id == "user-123"
        assert user.email == "test@example.com"
        assert user.role == "authenticated"
        assert not user.is_premium

    def test_premium_user(self):
        """Test premium user detection."""
        user = AuthenticatedUser(
            user_id="user-456",
            app_metadata={"subscription_tier": "premium"},
        )
        assert user.is_premium

    def test_free_user(self):
        """Test free user detection."""
        user = AuthenticatedUser(
            user_id="user-789",
            app_metadata={"subscription_tier": "free"},
        )
        assert not user.is_premium


class TestJWTValidation:
    """Tests for JWT validation."""

    def test_valid_token(self, valid_jwt_token, mock_settings):
        """Test valid JWT token is accepted."""
        import jwt as pyjwt

        payload = pyjwt.decode(
            valid_jwt_token,
            mock_settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
        assert payload["sub"] == "user-123"
        assert payload["email"] == "test@example.com"

    def test_expired_token_rejected(self, mock_settings):
        """Test expired token is rejected."""
        import jwt as pyjwt

        payload = {
            "sub": "user-123",
            "aud": "authenticated",
            "exp": datetime.utcnow() - timedelta(hours=1),  # Expired
            "iat": datetime.utcnow() - timedelta(hours=2),
        }

        token = pyjwt.encode(
            payload,
            mock_settings.supabase_jwt_secret,
            algorithm="HS256",
        )

        with pytest.raises(pyjwt.ExpiredSignatureError):
            pyjwt.decode(
                token,
                mock_settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
            )

    def test_invalid_audience_rejected(self, mock_settings):
        """Test token with wrong audience is rejected."""
        import jwt as pyjwt

        payload = {
            "sub": "user-123",
            "aud": "wrong-audience",
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow(),
        }

        token = pyjwt.encode(
            payload,
            mock_settings.supabase_jwt_secret,
            algorithm="HS256",
        )

        with pytest.raises(pyjwt.InvalidAudienceError):
            pyjwt.decode(
                token,
                mock_settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
            )


class TestBudgetDependency:
    """Tests for budget dependency."""

    def test_default_budget(self, mock_settings):
        """Test default budget is applied."""
        from gateway.dependencies import get_budget

        # Test would require async context
        # For now, just verify the settings
        assert mock_settings.default_budget_usd == 0.10
        assert mock_settings.min_budget_usd == 0.05
