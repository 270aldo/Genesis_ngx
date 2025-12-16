"""Conversations API endpoints.

Provides:
- GET /v1/conversations - List user conversations
- GET /v1/conversations/{id}/messages - Get conversation messages
"""

from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from gateway.api.schemas.chat import (
    ConversationListResponse,
    ConversationResponse,
    MessageResponse,
)
from gateway.api.schemas.common import PaginatedResponse
from gateway.dependencies import CurrentUser, RequestID, Settings
from gateway.services.persistence import PersistenceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get(
    "",
    response_model=ConversationListResponse,
    summary="List conversations",
    description="Get all conversations for the authenticated user.",
)
async def list_conversations(
    current_user: CurrentUser,
    settings: Settings,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(
        default=20, ge=1, le=100, description="Items per page"
    ),
    status_filter: Optional[str] = Query(
        default=None,
        alias="status",
        description="Filter by status (active, archived)",
    ),
) -> ConversationListResponse:
    """List user's conversations with pagination."""
    try:
        persistence = PersistenceService(settings)

        conversations, total = await persistence.list_conversations(
            user_id=current_user.user_id,
            page=page,
            page_size=page_size,
            status_filter=status_filter,
        )

        return ConversationListResponse(
            conversations=conversations,
            total=total,
            page=page,
            page_size=page_size,
        )

    except Exception as e:
        logger.error(f"Failed to list conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations",
        )


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
    summary="Get conversation",
    description="Get conversation details by ID.",
)
async def get_conversation(
    conversation_id: str,
    current_user: CurrentUser,
    settings: Settings,
) -> ConversationResponse:
    """Get a specific conversation."""
    try:
        persistence = PersistenceService(settings)

        conversation = await persistence.get_conversation(
            conversation_id=conversation_id,
            user_id=current_user.user_id,
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        return conversation

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation",
        )


@router.get(
    "/{conversation_id}/messages",
    response_model=List[MessageResponse],
    summary="Get conversation messages",
    description="Get all messages in a conversation.",
)
async def get_conversation_messages(
    conversation_id: str,
    current_user: CurrentUser,
    settings: Settings,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(
        default=50, ge=1, le=100, description="Items per page"
    ),
) -> List[MessageResponse]:
    """Get messages for a conversation with pagination."""
    try:
        persistence = PersistenceService(settings)

        # Verify user owns the conversation
        conversation = await persistence.get_conversation(
            conversation_id=conversation_id,
            user_id=current_user.user_id,
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        messages = await persistence.get_messages(
            conversation_id=conversation_id,
            page=page,
            page_size=page_size,
        )

        return messages

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve messages",
        )


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Archive conversation",
    description="Archive a conversation (soft delete).",
    response_model=None,
)
async def archive_conversation(
    conversation_id: str,
    current_user: CurrentUser,
    settings: Settings,
):
    """Archive a conversation."""
    try:
        persistence = PersistenceService(settings)

        # Verify user owns the conversation
        conversation = await persistence.get_conversation(
            conversation_id=conversation_id,
            user_id=current_user.user_id,
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        await persistence.archive_conversation(conversation_id=conversation_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to archive conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to archive conversation",
        )
