"""Gateway configuration extending shared settings."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GatewaySettings(BaseSettings):
    """Gateway-specific settings."""

    model_config = SettingsConfigDict(
        env_prefix="GATEWAY_",
        env_file=".env.local",
        extra="ignore",
    )

    # ==========================================================================
    # Environment
    # ==========================================================================
    environment: str = Field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development"),
        description="Deployment environment",
    )
    debug: bool = Field(default=False, description="Enable debug mode")

    # ==========================================================================
    # Supabase Configuration
    # ==========================================================================
    supabase_url: str = Field(
        default_factory=lambda: os.getenv("SUPABASE_URL", ""),
        description="Supabase project URL",
    )
    supabase_anon_key: str = Field(
        default_factory=lambda: os.getenv("SUPABASE_ANON_KEY", ""),
        description="Supabase anonymous key",
    )
    supabase_service_role_key: str = Field(
        default_factory=lambda: os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
        description="Supabase service role key (for agent operations)",
    )
    supabase_jwt_secret: str = Field(
        default_factory=lambda: os.getenv("SUPABASE_JWT_SECRET", ""),
        description="Supabase JWT secret for token validation",
    )

    # ==========================================================================
    # Rate Limiting
    # ==========================================================================
    rate_limit_per_user: int = Field(
        default=60,
        description="Maximum requests per minute per user",
    )
    rate_limit_per_ip: int = Field(
        default=100,
        description="Maximum requests per minute per IP",
    )
    rate_limit_burst: int = Field(
        default=10,
        description="Burst allowance for rate limiting",
    )

    # ==========================================================================
    # Budget
    # ==========================================================================
    default_budget_usd: float = Field(
        default=0.10,
        description="Default budget per request if not specified",
    )
    min_budget_usd: float = Field(
        default=0.05,
        description="Minimum budget required for GENESIS_X (Pro model)",
    )

    # ==========================================================================
    # CORS
    # ==========================================================================
    cors_allowed_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",      # Next.js dev
            "http://localhost:8081",      # Expo dev
            "http://localhost:19006",     # Expo web
            "https://genesis-ngx.vercel.app",  # Production web
        ],
        description="Allowed CORS origins",
    )

    # ==========================================================================
    # Agent Engine
    # ==========================================================================
    gcp_project_id: str = Field(
        default_factory=lambda: os.getenv("GOOGLE_CLOUD_PROJECT", "ngx-genesis-dev"),
        description="Google Cloud project ID",
    )
    gcp_region: str = Field(
        default_factory=lambda: os.getenv("GCP_REGION", "us-central1"),
        description="Google Cloud region",
    )

    # ==========================================================================
    # Timeouts
    # ==========================================================================
    request_timeout_seconds: float = Field(
        default=30.0,
        description="Default request timeout",
    )
    agent_timeout_seconds: float = Field(
        default=60.0,
        description="Timeout for agent invocations",
    )

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development or test."""
        return self.environment in ("development", "test")

    @property
    def is_test(self) -> bool:
        """Check if running in test environment."""
        return self.environment == "test"


@lru_cache
def get_settings() -> GatewaySettings:
    """Get gateway settings singleton."""
    return GatewaySettings()
