"""Gateway middleware package.

Middlewares are applied in the following order (first added = last executed):
1. CORS - Handles preflight requests
2. RequestID - Generates/propagates X-Request-ID
3. StructuredLogging - Logs requests with request_id
4. RateLimit - Token bucket rate limiting
5. Auth - JWT validation (applied at endpoint level)
6. Budget - Budget verification (applied at endpoint level)
"""

from gateway.middleware.logging import StructuredLoggingMiddleware
from gateway.middleware.rate_limit import RateLimitMiddleware
from gateway.middleware.request_id import RequestIDMiddleware

__all__ = [
    "StructuredLoggingMiddleware",
    "RateLimitMiddleware",
    "RequestIDMiddleware",
]
