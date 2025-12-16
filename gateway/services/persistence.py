"""Persistence service for conversations and messages.

Uses Supabase RPCs for all write operations (per RLS policy).
Read operations use direct table access with RLS filtering.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, List, Optional, Tuple

from gateway.api.schemas.chat import (
    ConversationResponse,
    ConversationStatus,
    MessageResponse,
    MessageRole,
)
from gateway.config import GatewaySettings

logger = logging.getLogger(__name__)


class PersistenceService:
    """Service for persisting conversations and messages.

    All writes go through Supabase RPCs (SECURITY DEFINER functions)
    to comply with RLS policies that block direct writes.
    """

    def __init__(self, settings: GatewaySettings):
        """Initialize the persistence service.

        Args:
            settings: Gateway settings with Supabase configuration
        """
        self.settings = settings
        self._client = None

    @property
    def client(self) -> Any:
        """Get or create the Supabase client."""
        if self._client is None:
            from supabase import create_client

            self._client = create_client(
                self.settings.supabase_url,
                self.settings.supabase_service_role_key,
            )
        return self._client

    async def create_conversation(
        self,
        user_id: str,
        title: Optional[str] = None,
    ) -> str:
        """Create a new conversation.

        Uses user_create_conversation RPC which validates ownership.

        Args:
            user_id: Owner user ID
            title: Optional conversation title

        Returns:
            New conversation ID

        Raises:
            RuntimeError: If conversation creation fails
        """
        try:
            result = self.client.rpc(
                "user_create_conversation",
                {
                    "p_user_id": user_id,
                    "p_title": title,
                },
            ).execute()

            if result.data is None:
                raise RuntimeError("RPC returned no data")

            return result.data

        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            raise RuntimeError(f"Failed to create conversation: {e}") from e

    async def get_conversation(
        self,
        conversation_id: str,
        user_id: str,
    ) -> Optional[ConversationResponse]:
        """Get a conversation by ID.

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for RLS filtering)

        Returns:
            ConversationResponse or None if not found
        """
        try:
            result = (
                self.client.table("conversations")
                .select("*")
                .eq("id", conversation_id)
                .eq("user_id", user_id)
                .single()
                .execute()
            )

            if not result.data:
                return None

            data = result.data
            return ConversationResponse(
                id=data["id"],
                user_id=data["user_id"],
                title=data.get("title"),
                status=ConversationStatus(data.get("status", "active")),
                message_count=data.get("message_count", 0),
                total_tokens=data.get("total_tokens", 0),
                total_cost_usd=data.get("total_cost_usd", 0.0),
                created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
            )

        except Exception as e:
            logger.error(f"Failed to get conversation: {e}")
            return None

    async def list_conversations(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        status_filter: Optional[str] = None,
    ) -> Tuple[List[ConversationResponse], int]:
        """List conversations for a user.

        Args:
            user_id: User ID
            page: Page number (1-indexed)
            page_size: Items per page
            status_filter: Optional status filter

        Returns:
            Tuple of (conversations, total_count)
        """
        try:
            query = (
                self.client.table("conversations")
                .select("*", count="exact")
                .eq("user_id", user_id)
            )

            if status_filter:
                query = query.eq("status", status_filter)

            offset = (page - 1) * page_size
            result = (
                query.order("updated_at", desc=True)
                .range(offset, offset + page_size - 1)
                .execute()
            )

            conversations = [
                ConversationResponse(
                    id=data["id"],
                    user_id=data["user_id"],
                    title=data.get("title"),
                    status=ConversationStatus(data.get("status", "active")),
                    message_count=data.get("message_count", 0),
                    total_tokens=data.get("total_tokens", 0),
                    total_cost_usd=data.get("total_cost_usd", 0.0),
                    created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
                    updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
                )
                for data in result.data
            ]

            return conversations, result.count or 0

        except Exception as e:
            logger.error(f"Failed to list conversations: {e}")
            return [], 0

    async def append_user_message(
        self,
        conversation_id: str,
        user_id: str,
        content: str,
    ) -> str:
        """Append a user message to a conversation.

        Uses gateway_append_user_message RPC which validates ownership
        and works with service_role authentication.

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for ownership validation)
            content: Message content

        Returns:
            New message ID

        Raises:
            RuntimeError: If message append fails
        """
        try:
            result = self.client.rpc(
                "gateway_append_user_message",
                {
                    "p_conversation_id": conversation_id,
                    "p_user_id": user_id,
                    "p_content": content,
                },
            ).execute()

            if result.data is None:
                raise RuntimeError("RPC returned no data")

            return result.data

        except Exception as e:
            logger.error(f"Failed to append user message: {e}")
            raise RuntimeError(f"Failed to append user message: {e}") from e

    async def append_agent_message(
        self,
        conversation_id: str,
        user_id: str,
        agent_type: str,
        content: str,
        tokens_used: int = 0,
        cost_usd: float = 0.0,
    ) -> str:
        """Append an agent message to a conversation.

        Uses gateway_append_agent_message RPC which validates ownership
        and works with service_role authentication. Uses role='agent'
        to comply with messages table constraint.

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for ownership validation)
            agent_type: Agent type (e.g., "genesis_x", "blaze")
            content: Message content
            tokens_used: Tokens consumed
            cost_usd: Cost in USD

        Returns:
            New message ID

        Raises:
            RuntimeError: If message append fails
        """
        try:
            result = self.client.rpc(
                "gateway_append_agent_message",
                {
                    "p_conversation_id": conversation_id,
                    "p_user_id": user_id,
                    "p_agent_type": agent_type,
                    "p_content": content,
                    "p_tokens_used": tokens_used,
                    "p_cost_usd": cost_usd,
                },
            ).execute()

            if result.data is None:
                raise RuntimeError("RPC returned no data")

            return result.data

        except Exception as e:
            logger.error(f"Failed to append agent message: {e}")
            raise RuntimeError(f"Failed to append agent message: {e}") from e

    async def get_messages(
        self,
        conversation_id: str,
        page: int = 1,
        page_size: int = 50,
    ) -> List[MessageResponse]:
        """Get messages for a conversation.

        Args:
            conversation_id: Conversation ID
            page: Page number
            page_size: Items per page

        Returns:
            List of messages
        """
        try:
            offset = (page - 1) * page_size
            result = (
                self.client.table("messages")
                .select("*")
                .eq("conversation_id", conversation_id)
                .order("created_at", desc=False)
                .range(offset, offset + page_size - 1)
                .execute()
            )

            return [
                MessageResponse(
                    id=data["id"],
                    conversation_id=data["conversation_id"],
                    role=MessageRole(data["role"]),
                    content=data["content"],
                    agent_type=data.get("agent_type"),
                    tokens_used=data.get("tokens_used"),
                    cost_usd=data.get("cost_usd"),
                    created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
                )
                for data in result.data
            ]

        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return []

    async def archive_conversation(self, conversation_id: str) -> bool:
        """Archive a conversation (soft delete).

        Uses user_archive_conversation RPC which validates ownership.

        Args:
            conversation_id: Conversation ID

        Returns:
            True if successful

        Raises:
            RuntimeError: If archive fails
        """
        try:
            result = self.client.rpc(
                "user_archive_conversation",
                {
                    "p_conversation_id": conversation_id,
                },
            ).execute()

            return result.data is True

        except Exception as e:
            logger.error(f"Failed to archive conversation: {e}")
            raise RuntimeError(f"Failed to archive conversation: {e}") from e
