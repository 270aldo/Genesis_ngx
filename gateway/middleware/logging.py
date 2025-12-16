"""Structured logging middleware for request/response logging.

Logs all requests with structured JSON format including:
- Request ID for correlation
- Method, path, status code
- Latency
- User ID (if authenticated)
"""

from __future__ import annotations

import json
import logging
import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("gateway.access")


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request logging.

    Logs each request with:
    - request_id: Correlation ID from RequestIDMiddleware
    - method: HTTP method
    - path: Request path
    - status_code: Response status code
    - latency_ms: Request processing time
    - client_ip: Client IP address
    - user_id: User ID if authenticated (from request state)
    """

    # Paths to exclude from logging (health checks, etc.)
    EXCLUDE_PATHS = {"/health", "/ready", "/version", "/favicon.ico"}

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Process the request and log it."""
        # Skip logging for excluded paths
        if request.url.path in self.EXCLUDE_PATHS:
            return await call_next(request)

        start_time = time.time()

        # Process the request
        response = await call_next(request)

        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000

        # Build log entry
        log_entry = {
            "request_id": getattr(request.state, "request_id", "unknown"),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": round(latency_ms, 2),
            "client_ip": self._get_client_ip(request),
        }

        # Add user_id if authenticated
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            log_entry["user_id"] = user_id

        # Add query params for debugging (in development)
        if request.query_params:
            log_entry["query_params"] = dict(request.query_params)

        # Log at appropriate level
        if response.status_code >= 500:
            logger.error(json.dumps(log_entry))
        elif response.status_code >= 400:
            logger.warning(json.dumps(log_entry))
        else:
            logger.info(json.dumps(log_entry))

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP, considering proxy headers."""
        # Check X-Forwarded-For (from load balancer/proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # First IP in the list is the original client
            return forwarded_for.split(",")[0].strip()

        # Check X-Real-IP (nginx)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct client
        if request.client:
            return request.client.host

        return "unknown"
