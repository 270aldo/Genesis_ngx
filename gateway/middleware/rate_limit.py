"""Rate limiting middleware using token bucket algorithm.

Implements per-user and per-IP rate limiting with burst allowance.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Callable, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)


@dataclass
class TokenBucket:
    """Token bucket for rate limiting.

    Attributes:
        capacity: Maximum number of tokens
        tokens: Current number of tokens
        refill_rate: Tokens added per second
        last_refill: Last refill timestamp
    """

    capacity: float
    tokens: float = field(default=0.0)
    refill_rate: float = field(default=1.0)  # tokens per second
    last_refill: float = field(default_factory=time.time)

    def __post_init__(self):
        """Initialize tokens to capacity."""
        if self.tokens == 0.0:
            self.tokens = self.capacity

    def consume(self, tokens: float = 1.0) -> bool:
        """Try to consume tokens from the bucket.

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens were consumed, False if not enough tokens
        """
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    @property
    def time_until_available(self) -> float:
        """Time in seconds until a token is available."""
        if self.tokens >= 1:
            return 0.0
        return (1 - self.tokens) / self.refill_rate


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with per-user and per-IP limits.

    Uses token bucket algorithm for smooth rate limiting with burst allowance.

    Attributes:
        rate_per_user: Max requests per minute per authenticated user
        rate_per_ip: Max requests per minute per IP address
        burst: Additional burst allowance
    """

    # Paths exempt from rate limiting
    EXEMPT_PATHS = {"/health", "/ready", "/version"}

    def __init__(
        self,
        app,
        rate_per_user: int = 60,
        rate_per_ip: int = 100,
        burst: int = 10,
    ):
        """Initialize rate limiter.

        Args:
            app: ASGI application
            rate_per_user: Requests per minute per user
            rate_per_ip: Requests per minute per IP
            burst: Burst allowance above base rate
        """
        super().__init__(app)
        self.rate_per_user = rate_per_user
        self.rate_per_ip = rate_per_ip
        self.burst = burst

        # Token buckets keyed by user_id or IP
        self._user_buckets: dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(
                capacity=rate_per_user + burst,
                refill_rate=rate_per_user / 60.0,
            )
        )
        self._ip_buckets: dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(
                capacity=rate_per_ip + burst,
                refill_rate=rate_per_ip / 60.0,
            )
        )
        self._lock = Lock()

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Check rate limits and process request."""
        # Skip rate limiting for exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        client_ip = self._get_client_ip(request)

        # Check IP-based rate limit first
        with self._lock:
            ip_bucket = self._ip_buckets[client_ip]
            if not ip_bucket.consume():
                retry_after = int(ip_bucket.time_until_available) + 1
                return self._rate_limit_response(
                    f"IP rate limit exceeded. Try again in {retry_after}s",
                    retry_after,
                )

        # If request has authenticated user, also check user rate limit
        # Note: User is extracted from JWT by the auth dependency, not available here
        # We'll check user-based rate limiting at the endpoint level

        return await call_next(request)

    def check_user_rate_limit(self, user_id: str) -> Optional[JSONResponse]:
        """Check rate limit for authenticated user.

        Args:
            user_id: Authenticated user ID

        Returns:
            JSONResponse if rate limited, None if allowed
        """
        with self._lock:
            bucket = self._user_buckets[user_id]
            if not bucket.consume():
                retry_after = int(bucket.time_until_available) + 1
                return self._rate_limit_response(
                    f"User rate limit exceeded. Try again in {retry_after}s",
                    retry_after,
                )
        return None

    def _rate_limit_response(
        self, message: str, retry_after: int
    ) -> JSONResponse:
        """Create a rate limit exceeded response."""
        return JSONResponse(
            status_code=429,
            content={
                "error": "rate_limit_exceeded",
                "message": message,
            },
            headers={"Retry-After": str(retry_after)},
        )

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP, considering proxy headers."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        if request.client:
            return request.client.host

        return "unknown"
