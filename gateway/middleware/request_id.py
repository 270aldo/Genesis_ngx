"""Request ID middleware for distributed tracing.

Generates or propagates X-Request-ID header for request correlation
across the Gateway and Agent Engine services.
"""

from __future__ import annotations

import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to generate or propagate X-Request-ID header.

    If the client provides X-Request-ID, it's propagated through the system.
    Otherwise, a new UUID is generated for the request.

    The request ID is:
    - Stored in request.state.request_id for use by other middlewares/handlers
    - Added to the response headers
    """

    HEADER_NAME = "X-Request-ID"

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Process the request and add request ID."""
        # Get existing request ID or generate new one
        request_id = request.headers.get(self.HEADER_NAME)
        if not request_id:
            request_id = str(uuid.uuid4())

        # Store in request state for use by other components
        request.state.request_id = request_id

        # Process the request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers[self.HEADER_NAME] = request_id

        return response
