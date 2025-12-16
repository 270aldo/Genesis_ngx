"""Genesis NGX Gateway - FastAPI Application Entry Point.

This is the main FastAPI application that serves as the BFF (Backend for Frontend)
for Expo mobile app and Next.js web app, connecting to the Genesis NGX multi-agent
system via Vertex AI Agent Engine.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from gateway.api.v1.router import router as v1_router
from gateway.config import get_settings
from gateway.middleware.logging import StructuredLoggingMiddleware
from gateway.middleware.rate_limit import RateLimitMiddleware
from gateway.middleware.request_id import RequestIDMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager."""
    settings = get_settings()
    logger.info(
        f"Starting Genesis NGX Gateway (env={settings.environment}, "
        f"debug={settings.debug})"
    )

    # Initialize rate limiter and store in app state for dependency access
    app.state.rate_limiter = RateLimitMiddleware(
        app=None,  # Not used as middleware, just for rate checking
        rate_per_user=settings.rate_limit_per_user,
        rate_per_ip=settings.rate_limit_per_ip,
        burst=settings.rate_limit_burst,
    )

    yield
    logger.info("Shutting down Genesis NGX Gateway")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Genesis NGX Gateway",
        description="API Gateway for Genesis NGX multi-agent wellness system",
        version="1.0.0",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )

    # Add middlewares (order matters - first added = last executed)
    # 1. CORS (outermost - handles preflight)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # 2. Request ID (generates/propagates X-Request-ID)
    app.add_middleware(RequestIDMiddleware)

    # 3. Structured Logging (logs requests with request_id)
    app.add_middleware(StructuredLoggingMiddleware)

    # 4. Rate Limiting (per-user and per-IP)
    app.add_middleware(
        RateLimitMiddleware,
        rate_per_user=settings.rate_limit_per_user,
        rate_per_ip=settings.rate_limit_per_ip,
        burst=settings.rate_limit_burst,
    )

    # Include routers
    app.include_router(v1_router, prefix="/v1")

    return app


# Create the app instance
app = create_app()


# Health check endpoints at root level
@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "healthy"}


@app.get("/ready", tags=["Health"], response_model=None)
async def readiness_check() -> dict:
    """Readiness probe for Kubernetes/Cloud Run.

    Checks:
    - Supabase database connectivity
    - Agent Engine registry availability
    """
    from fastapi import HTTPException, status

    settings = get_settings()
    checks = {
        "database": "unknown",
        "agent_registry": "unknown",
    }
    all_ready = True

    # Check Supabase connectivity
    try:
        from supabase import create_client

        client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key,
        )
        # Simple query to verify connection
        client.table("conversations").select("id").limit(1).execute()
        checks["database"] = "ready"
    except Exception as e:
        logger.warning(f"Database readiness check failed: {e}")
        checks["database"] = f"error: {type(e).__name__}"
        all_ready = False

    # Check Agent Engine registry
    try:
        from agents.shared.agent_engine_registry import get_registry

        registry = get_registry()
        # Verify registry has agents registered
        if hasattr(registry, "_agents") and len(registry._agents) > 0:
            checks["agent_registry"] = "ready"
        else:
            checks["agent_registry"] = "ready (no agents cached yet)"
    except Exception as e:
        logger.warning(f"Agent registry readiness check failed: {e}")
        checks["agent_registry"] = f"error: {type(e).__name__}"
        all_ready = False

    if not all_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "checks": checks},
        )

    return {"status": "ready", "checks": checks}


@app.get("/version", tags=["Health"])
async def version_info() -> dict[str, str]:
    """Return version information."""
    from gateway import __version__

    settings = get_settings()
    return {
        "version": __version__,
        "environment": settings.environment,
    }
