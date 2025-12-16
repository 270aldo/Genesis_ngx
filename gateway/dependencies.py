"""Dependency injection for Gateway endpoints.

This module provides FastAPI dependencies for:
- Authentication (Supabase JWT validation)
- Budget verification
- Agent Engine registry access
- Supabase client access
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException, Request, status

from gateway.config import GatewaySettings, get_settings

logger = logging.getLogger(__name__)


# =============================================================================
# Settings Dependency
# =============================================================================


def get_gateway_settings() -> GatewaySettings:
    """Get gateway settings."""
    return get_settings()


Settings = Annotated[GatewaySettings, Depends(get_gateway_settings)]


# =============================================================================
# Authentication Dependencies
# =============================================================================


class AuthenticatedUser:
    """Authenticated user context."""

    def __init__(
        self,
        user_id: str,
        email: Optional[str] = None,
        role: str = "user",
        app_metadata: Optional[dict] = None,
    ):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.app_metadata = app_metadata or {}

    @property
    def is_premium(self) -> bool:
        """Check if user has premium subscription."""
        return self.app_metadata.get("subscription_tier") == "premium"


async def get_current_user(
    request: Request,
    authorization: Annotated[Optional[str], Header()] = None,
    settings: Settings = None,
) -> AuthenticatedUser:
    """Validate Supabase JWT and return authenticated user.

    Args:
        request: FastAPI request object
        authorization: Authorization header (Bearer token)
        settings: Gateway settings

    Returns:
        AuthenticatedUser with validated claims

    Raises:
        HTTPException: If token is missing or invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme. Use 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization[7:]  # Remove "Bearer " prefix

    try:
        import jwt

        # Decode and validate the JWT
        # Supabase JWTs use HS256 with the JWT secret
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
            )

        return AuthenticatedUser(
            user_id=user_id,
            email=payload.get("email"),
            role=payload.get("role", "user"),
            app_metadata=payload.get("app_metadata", {}),
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]


# =============================================================================
# Budget Dependencies
# =============================================================================


async def get_budget(
    x_budget_usd: Annotated[Optional[float], Header(alias="X-Budget-USD")] = None,
    settings: Settings = None,
) -> float:
    """Get the budget for the request.

    Args:
        x_budget_usd: Budget header in USD
        settings: Gateway settings

    Returns:
        Budget in USD (default or specified)

    Raises:
        HTTPException: If budget is below minimum
    """
    budget = x_budget_usd or settings.default_budget_usd

    if budget < settings.min_budget_usd:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Budget ${budget:.2f} is below minimum ${settings.min_budget_usd:.2f}",
        )

    return budget


Budget = Annotated[float, Depends(get_budget)]


# =============================================================================
# Agent Engine Registry Dependency
# =============================================================================


@lru_cache
def get_agent_registry():
    """Get the Agent Engine registry singleton."""
    from agents.shared.agent_engine_registry import get_registry

    return get_registry()


AgentRegistry = Annotated[object, Depends(get_agent_registry)]


# =============================================================================
# Request Context Dependencies
# =============================================================================


def get_request_id(request: Request) -> str:
    """Get the request ID from the request state."""
    return getattr(request.state, "request_id", "unknown")


RequestID = Annotated[str, Depends(get_request_id)]
