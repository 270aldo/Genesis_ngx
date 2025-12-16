"""API v1 router aggregator.

Combines all v1 endpoints into a single router.
"""

from fastapi import APIRouter

from gateway.api.v1.chat import router as chat_router
from gateway.api.v1.conversations import router as conversations_router

router = APIRouter(tags=["v1"])

# Include sub-routers
router.include_router(chat_router)
router.include_router(conversations_router)
