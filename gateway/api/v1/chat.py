"""Chat API endpoints.

Provides:
- POST /v1/chat - Synchronous chat request/response
- POST /v1/chat/stream - Server-Sent Events streaming
"""

from __future__ import annotations

import logging
import time
from typing import AsyncIterator

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from gateway.api.schemas.chat import (
    AgentType,
    ChatRequest,
    ChatResponse,
    MessageResponse,
    MessageRole,
    StreamEvent,
    StreamEventType,
)
from gateway.dependencies import (
    AgentRegistry,
    Budget,
    CurrentUser,
    RequestID,
    Settings,
    UserRateLimit,
)
from gateway.services.orchestration import OrchestrationService
from gateway.services.persistence import PersistenceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "",
    response_model=ChatResponse,
    summary="Send a chat message",
    description="Send a message to Genesis NGX and receive a response.",
)
async def chat(
    request: ChatRequest,
    current_user: CurrentUser,
    budget: Budget,
    request_id: RequestID,
    settings: Settings,
    registry: AgentRegistry,
    _rate_limit: UserRateLimit = None,  # Validates user rate limit
) -> ChatResponse:
    """Handle synchronous chat request.

    Flow:
    1. Create or retrieve conversation
    2. Persist user message
    3. Invoke GENESIS_X orchestrator
    4. Persist agent response
    5. Return response
    """
    start_time = time.time()

    try:
        orchestration = OrchestrationService(registry, settings)
        persistence = PersistenceService(settings)

        # Get or create conversation
        conversation_id = request.conversation_id
        if not conversation_id:
            conversation_id = await persistence.create_conversation(
                user_id=current_user.user_id
            )

        # Persist user message
        await persistence.append_user_message(
            conversation_id=conversation_id,
            user_id=current_user.user_id,
            content=request.message,
        )

        # Invoke orchestrator
        result = await orchestration.invoke(
            message=request.message,
            user_id=current_user.user_id,
            session_id=conversation_id,
            budget_usd=budget,
            context=request.context,
        )

        # Persist agent response
        message_id = await persistence.append_agent_message(
            conversation_id=conversation_id,
            user_id=current_user.user_id,
            agent_type=result.agent_id,
            content=result.response,
            tokens_used=result.tokens_used,
            cost_usd=result.cost_usd,
        )

        latency_ms = (time.time() - start_time) * 1000

        return ChatResponse(
            conversation_id=conversation_id,
            message=MessageResponse(
                id=message_id,
                conversation_id=conversation_id,
                role=MessageRole.AGENT,
                content=result.response,
                agent_type=AgentType(result.agent_id),
                tokens_used=result.tokens_used,
                cost_usd=result.cost_usd,
                created_at=result.created_at or time.time(),
            ),
            agent_type=AgentType(result.agent_id),
            tokens_used=result.tokens_used,
            cost_usd=result.cost_usd,
            latency_ms=latency_ms,
        )

    except Exception as e:
        logger.error(f"Chat error: {e}", extra={"request_id": request_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat request failed: {str(e)}",
        )


@router.post(
    "/stream",
    summary="Stream a chat response",
    description="Send a message and receive the response as Server-Sent Events.",
)
async def chat_stream(
    request: ChatRequest,
    current_user: CurrentUser,
    budget: Budget,
    request_id: RequestID,
    settings: Settings,
    registry: AgentRegistry,
    _rate_limit: UserRateLimit = None,  # Validates user rate limit
) -> StreamingResponse:
    """Handle streaming chat request using SSE.

    Returns a stream of events:
    - start: Indicates stream start with conversation_id
    - chunk: Content chunk from the agent
    - tool_call: Agent is calling a tool
    - tool_result: Tool returned a result
    - done: Stream complete with final metadata
    - error: An error occurred
    """
    orchestration = OrchestrationService(registry, settings)
    persistence = PersistenceService(settings)

    async def event_generator() -> AsyncIterator[str]:
        """Generate SSE events."""
        try:
            # Get or create conversation
            conversation_id = request.conversation_id
            if not conversation_id:
                conversation_id = await persistence.create_conversation(
                    user_id=current_user.user_id
                )

            # Send start event
            yield StreamEvent(
                event=StreamEventType.START,
                data={"conversation_id": conversation_id},
            ).to_sse()

            # Persist user message
            await persistence.append_user_message(
                conversation_id=conversation_id,
                user_id=current_user.user_id,
                content=request.message,
            )

            # Stream from orchestrator
            full_response = ""
            tokens_used = 0
            cost_usd = 0.0
            agent_id = "genesis_x"

            async for event in orchestration.invoke_stream(
                message=request.message,
                user_id=current_user.user_id,
                session_id=conversation_id,
            ):
                event_type = event.get("type", "chunk")
                content = event.get("content", "")

                if event_type == "chunk":
                    full_response += content
                    yield StreamEvent(
                        event=StreamEventType.CHUNK,
                        data={"content": content},
                    ).to_sse()
                elif event_type == "tool_call":
                    yield StreamEvent(
                        event=StreamEventType.TOOL_CALL,
                        data=event,
                    ).to_sse()
                elif event_type == "tool_result":
                    yield StreamEvent(
                        event=StreamEventType.TOOL_RESULT,
                        data=event,
                    ).to_sse()
                elif event_type == "done":
                    tokens_used = event.get("tokens_used", 0)
                    cost_usd = event.get("cost_usd", 0.0)
                    agent_id = event.get("agent_id", "genesis_x")

            # Persist agent response
            await persistence.append_agent_message(
                conversation_id=conversation_id,
                user_id=current_user.user_id,
                agent_type=agent_id,
                content=full_response,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
            )

            # Send done event
            yield StreamEvent(
                event=StreamEventType.DONE,
                data={
                    "conversation_id": conversation_id,
                    "agent_type": agent_id,
                    "tokens_used": tokens_used,
                    "cost_usd": cost_usd,
                },
            ).to_sse()

        except Exception as e:
            logger.error(f"Stream error: {e}", extra={"request_id": request_id})
            yield StreamEvent(
                event=StreamEventType.ERROR,
                data={"error": str(e)},
            ).to_sse()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Request-ID": request_id,
        },
    )
