"""Chat API schemas."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Message role in conversation.

    Note: Uses 'agent' instead of 'assistant' to match database constraint
    and multi-agent architecture pattern.
    """

    USER = "user"
    AGENT = "agent"  # Multi-agent pattern (not 'assistant')
    SYSTEM = "system"


class AgentType(str, Enum):
    """Agent types in Genesis NGX."""

    GENESIS_X = "genesis_x"
    BLAZE = "blaze"
    ATLAS = "atlas"
    TEMPO = "tempo"
    WAVE = "wave"
    SAGE = "sage"
    METABOL = "metabol"
    MACRO = "macro"
    NOVA = "nova"
    SPARK = "spark"
    STELLA = "stella"
    LUNA = "luna"
    LOGOS = "logos"


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User message content",
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Existing conversation ID. If not provided, a new conversation is created.",
    )
    context: Optional[dict[str, Any]] = Field(
        default=None,
        description="Additional context for the agent (e.g., user preferences, goals)",
    )


class MessageResponse(BaseModel):
    """A single message in a conversation."""

    id: str = Field(..., description="Message ID")
    conversation_id: str = Field(..., description="Parent conversation ID")
    role: MessageRole = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    agent_type: Optional[AgentType] = Field(
        default=None, description="Agent that generated this message"
    )
    tokens_used: Optional[int] = Field(
        default=None, description="Tokens used for this message"
    )
    cost_usd: Optional[float] = Field(
        default=None, description="Cost in USD for this message"
    )
    created_at: datetime = Field(..., description="Message creation timestamp")


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    conversation_id: str = Field(..., description="Conversation ID")
    message: MessageResponse = Field(..., description="Assistant's response message")
    agent_type: AgentType = Field(
        ..., description="Agent that handled the request"
    )
    tokens_used: int = Field(
        default=0, description="Total tokens used for this request"
    )
    cost_usd: float = Field(
        default=0.0, description="Total cost in USD for this request"
    )
    latency_ms: float = Field(
        default=0.0, description="Response latency in milliseconds"
    )


class StreamEventType(str, Enum):
    """Types of streaming events."""

    START = "start"
    CHUNK = "chunk"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    DONE = "done"
    ERROR = "error"


class StreamEvent(BaseModel):
    """A streaming event in SSE format."""

    event: StreamEventType = Field(..., description="Event type")
    data: dict[str, Any] = Field(..., description="Event data")

    def to_sse(self) -> str:
        """Convert to SSE format."""
        import json

        return f"event: {self.event.value}\ndata: {json.dumps(self.data)}\n\n"


class ConversationStatus(str, Enum):
    """Conversation status."""

    ACTIVE = "active"
    ARCHIVED = "archived"


class ConversationResponse(BaseModel):
    """Conversation metadata."""

    id: str = Field(..., description="Conversation ID")
    user_id: str = Field(..., description="Owner user ID")
    title: Optional[str] = Field(default=None, description="Conversation title")
    status: ConversationStatus = Field(..., description="Conversation status")
    message_count: int = Field(default=0, description="Number of messages")
    total_tokens: int = Field(default=0, description="Total tokens used")
    total_cost_usd: float = Field(default=0.0, description="Total cost in USD")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ConversationListResponse(BaseModel):
    """List of conversations response."""

    conversations: List[ConversationResponse] = Field(
        ..., description="List of conversations"
    )
    total: int = Field(..., description="Total number of conversations")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
