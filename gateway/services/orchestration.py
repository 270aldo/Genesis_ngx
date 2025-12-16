"""Orchestration service for agent invocations.

This service wraps the Agent Engine Registry and provides:
- Agent invocation with budget validation
- Streaming support
- Error handling and retries
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, AsyncIterator, Optional

from gateway.config import GatewaySettings

logger = logging.getLogger(__name__)


@dataclass
class OrchestrationResult:
    """Result of an agent invocation."""

    agent_id: str
    response: str
    tokens_used: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    status: str = "success"
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class OrchestrationService:
    """Service for orchestrating agent invocations.

    Uses the Agent Engine Registry to invoke agents deployed on
    Vertex AI Agent Engine.
    """

    def __init__(self, registry: Any, settings: GatewaySettings):
        """Initialize the orchestration service.

        Args:
            registry: Agent Engine Registry instance
            settings: Gateway settings
        """
        self.registry = registry
        self.settings = settings

    async def invoke(
        self,
        message: str,
        user_id: str,
        session_id: Optional[str] = None,
        budget_usd: Optional[float] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> OrchestrationResult:
        """Invoke the main orchestrator agent.

        Args:
            message: User message
            user_id: User ID for the invocation
            session_id: Session/conversation ID
            budget_usd: Budget limit for this invocation
            context: Additional context for the agent

        Returns:
            OrchestrationResult with the agent's response

        Raises:
            Exception: If invocation fails
        """
        try:
            # Build the message with context if provided
            full_message = message
            if context:
                context_str = "\n".join(f"{k}: {v}" for k, v in context.items())
                full_message = f"Context:\n{context_str}\n\nUser: {message}"

            # Invoke genesis_x (main orchestrator)
            result = await self.registry.invoke(
                agent_id="genesis_x",
                message=full_message,
                session_id=session_id,
                user_id=user_id,
                budget_usd=budget_usd or self.settings.default_budget_usd,
            )

            return OrchestrationResult(
                agent_id=result.agent_id,
                response=result.response,
                tokens_used=result.tokens_used,
                cost_usd=result.cost_usd,
                latency_ms=result.latency_ms,
                status=result.status,
            )

        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            raise

    async def invoke_stream(
        self,
        message: str,
        user_id: str,
        session_id: Optional[str] = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Invoke the orchestrator and stream the response.

        Args:
            message: User message
            user_id: User ID
            session_id: Session/conversation ID

        Yields:
            Events from the agent's execution
        """
        try:
            async for event in self.registry.invoke_stream(
                agent_id="genesis_x",
                message=message,
                session_id=session_id,
                user_id=user_id,
            ):
                yield event

        except Exception as e:
            logger.error(f"Stream orchestration failed: {e}")
            yield {"type": "error", "content": str(e)}

    async def invoke_specialist(
        self,
        agent_id: str,
        message: str,
        user_id: str,
        session_id: Optional[str] = None,
        budget_usd: Optional[float] = None,
    ) -> OrchestrationResult:
        """Invoke a specific specialist agent directly.

        Use this for testing or when the orchestrator has already
        determined which specialist to invoke.

        Args:
            agent_id: Specialist agent ID (e.g., "blaze", "sage")
            message: User message
            user_id: User ID
            session_id: Session/conversation ID
            budget_usd: Budget limit

        Returns:
            OrchestrationResult with the specialist's response
        """
        try:
            result = await self.registry.invoke(
                agent_id=agent_id,
                message=message,
                session_id=session_id,
                user_id=user_id,
                budget_usd=budget_usd or self.settings.default_budget_usd,
            )

            return OrchestrationResult(
                agent_id=result.agent_id,
                response=result.response,
                tokens_used=result.tokens_used,
                cost_usd=result.cost_usd,
                latency_ms=result.latency_ms,
                status=result.status,
            )

        except Exception as e:
            logger.error(f"Specialist invocation failed: {e}")
            raise
