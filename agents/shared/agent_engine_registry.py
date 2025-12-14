"""Agent Engine Registry for Genesis NGX.

This module provides a registry for agents deployed to Vertex AI Agent Engine,
enabling programmatic invocation of specialist agents from the orchestrator.

Usage:
    from agents.shared.agent_engine_registry import get_registry

    registry = get_registry()

    # Get resource name for an agent
    resource_name = registry.get_resource_name("blaze")

    # Invoke an agent
    result = await registry.invoke(
        agent_id="blaze",
        message="Create a strength workout",
        session_id="session-123",
        user_id="user-456",
    )

References:
    - https://cloud.google.com/agent-builder/agent-engine/overview
    - https://cloud.google.com/agent-builder/agent-engine/use/adk
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Optional

logger = logging.getLogger(__name__)


class AgentEngineError(RuntimeError):
    """Base error for Agent Engine operations."""


class AgentNotFoundError(AgentEngineError):
    """Raised when an agent is not found in the registry."""


class AgentInvocationError(AgentEngineError):
    """Raised when an agent invocation fails."""


class BudgetExceededError(AgentEngineError):
    """Raised when invocation would exceed budget."""


# =============================================================================
# Agent Configuration
# =============================================================================

# Agent IDs mapped to their configuration
AGENT_CONFIGS: dict[str, dict[str, Any]] = {
    "genesis_x": {
        "model": "gemini-2.5-pro",
        "max_latency_ms": 6000,
        "max_cost_per_invoke": 0.05,
        "description": "Main orchestrator",
    },
    "blaze": {
        "model": "gemini-2.5-flash",
        "max_latency_ms": 2000,
        "max_cost_per_invoke": 0.01,
        "description": "Strength and hypertrophy specialist",
    },
    "sage": {
        "model": "gemini-2.5-flash",
        "max_latency_ms": 2000,
        "max_cost_per_invoke": 0.01,
        "description": "Nutrition strategy specialist",
    },
    "atlas": {
        "model": "gemini-2.5-flash",
        "max_latency_ms": 2000,
        "max_cost_per_invoke": 0.01,
        "description": "Mobility and flexibility specialist",
    },
    "tempo": {
        "model": "gemini-2.5-flash",
        "max_latency_ms": 2000,
        "max_cost_per_invoke": 0.01,
        "description": "Cardio and endurance specialist",
    },
    "wave": {
        "model": "gemini-2.5-flash",
        "max_latency_ms": 2000,
        "max_cost_per_invoke": 0.01,
        "description": "Recovery specialist",
    },
    "stella": {
        "model": "gemini-2.5-flash",
        "max_latency_ms": 2000,
        "max_cost_per_invoke": 0.01,
        "description": "Analytics specialist",
    },
    "metabol": {
        "model": "gemini-2.5-flash",
        "max_latency_ms": 2000,
        "max_cost_per_invoke": 0.01,
        "description": "Metabolism and TDEE specialist",
    },
    "macro": {
        "model": "gemini-2.5-flash",
        "max_latency_ms": 2000,
        "max_cost_per_invoke": 0.01,
        "description": "Macronutrients specialist",
    },
    "spark": {
        "model": "gemini-2.5-flash",
        "max_latency_ms": 2000,
        "max_cost_per_invoke": 0.01,
        "description": "Behavior and habits specialist",
    },
    "nova": {
        "model": "gemini-2.5-flash",
        "max_latency_ms": 2000,
        "max_cost_per_invoke": 0.01,
        "description": "Supplementation specialist",
    },
    "luna": {
        "model": "gemini-2.5-flash",
        "max_latency_ms": 2000,
        "max_cost_per_invoke": 0.01,
        "description": "Women's health specialist",
    },
    "logos": {
        "model": "gemini-2.5-pro",
        "max_latency_ms": 6000,
        "max_cost_per_invoke": 0.05,
        "description": "Education specialist",
    },
}


@dataclass
class AgentEngineConfig:
    """Configuration for Agent Engine connection."""

    project_id: str = field(
        default_factory=lambda: os.getenv("GOOGLE_CLOUD_PROJECT", "ngx-genesis-dev")
    )
    location: str = field(default_factory=lambda: os.getenv("GCP_REGION", "us-central1"))
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))

    # Resource ID prefix (agents are named: {prefix}-{agent_id})
    resource_prefix: str = field(
        default_factory=lambda: os.getenv("AGENT_ENGINE_PREFIX", "genesis-ngx")
    )

    # Timeouts
    default_timeout_seconds: float = 30.0
    max_retries: int = 3


@dataclass
class InvocationResult:
    """Result of an agent invocation."""

    agent_id: str
    session_id: str
    response: str
    events: list[dict[str, Any]] = field(default_factory=list)
    tokens_used: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    status: str = "success"  # success, error, timeout, budget_exceeded

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "response": self.response,
            "events": self.events,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
            "latency_ms": self.latency_ms,
            "status": self.status,
        }


@dataclass
class AgentEngineRegistry:
    """Registry for Agent Engine agents.

    Provides methods to resolve agent IDs to resource names and invoke agents
    deployed to Vertex AI Agent Engine.

    In development mode (no Agent Engine connection), returns mock responses.
    In production, connects to the actual Agent Engine.
    """

    config: AgentEngineConfig = field(default_factory=AgentEngineConfig)
    _client: Any = field(default=None, init=False, repr=False)
    _agent_cache: dict[str, Any] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize the registry."""
        self._init_client()

    def _init_client(self) -> None:
        """Initialize the Vertex AI client.

        Attempts to connect to Vertex AI. If not available (e.g., in tests
        or local development without credentials), operates in mock mode.

        In test environments (environment="test"), the client is not initialized
        to avoid making real API calls.
        """
        # Skip initialization in test environment
        if self.config.environment == "test":
            logger.info(
                "AgentEngineRegistry operating in mock mode (test environment)"
            )
            self._client = None
            return

        try:
            import vertexai

            self._client = vertexai.Client(
                project=self.config.project_id,
                location=self.config.location,
            )
            logger.info(
                f"AgentEngineRegistry initialized for project={self.config.project_id}, "
                f"location={self.config.location}"
            )
        except Exception as exc:
            logger.warning(
                f"Could not initialize Vertex AI client: {exc}. "
                "Operating in mock mode."
            )
            self._client = None

    @property
    def is_connected(self) -> bool:
        """Check if connected to Agent Engine."""
        return self._client is not None

    def get_agent_ids(self) -> list[str]:
        """Get list of all registered agent IDs."""
        return list(AGENT_CONFIGS.keys())

    def get_agent_config(self, agent_id: str) -> dict[str, Any]:
        """Get configuration for an agent.

        Args:
            agent_id: Agent identifier (e.g., "blaze", "sage")

        Returns:
            Agent configuration dictionary

        Raises:
            AgentNotFoundError: If agent is not registered
        """
        if agent_id not in AGENT_CONFIGS:
            raise AgentNotFoundError(f"Agent '{agent_id}' not found in registry")
        return AGENT_CONFIGS[agent_id].copy()

    def get_resource_name(self, agent_id: str) -> str:
        """Get the full resource name for an agent in Agent Engine.

        Args:
            agent_id: Agent identifier (e.g., "blaze", "sage")

        Returns:
            Full resource name in format:
            projects/{project}/locations/{location}/reasoningEngines/{resource_id}

        Raises:
            AgentNotFoundError: If agent is not registered
        """
        if agent_id not in AGENT_CONFIGS:
            raise AgentNotFoundError(f"Agent '{agent_id}' not found in registry")

        resource_id = f"{self.config.resource_prefix}-{agent_id}"

        return (
            f"projects/{self.config.project_id}/"
            f"locations/{self.config.location}/"
            f"reasoningEngines/{resource_id}"
        )

    def get_resource_id(self, agent_id: str) -> str:
        """Get just the resource ID for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Resource ID (e.g., "genesis-ngx-blaze")
        """
        if agent_id not in AGENT_CONFIGS:
            raise AgentNotFoundError(f"Agent '{agent_id}' not found in registry")

        return f"{self.config.resource_prefix}-{agent_id}"

    async def _get_agent(self, agent_id: str) -> Any:
        """Get or create a cached agent instance.

        Args:
            agent_id: Agent identifier

        Returns:
            Agent Engine instance
        """
        if agent_id in self._agent_cache:
            return self._agent_cache[agent_id]

        if not self.is_connected:
            return None

        resource_name = self.get_resource_name(agent_id)

        try:
            agent = self._client.agent_engines.get(name=resource_name)
            self._agent_cache[agent_id] = agent
            return agent
        except Exception as exc:
            logger.error(f"Failed to get agent {agent_id}: {exc}")
            raise AgentInvocationError(f"Failed to get agent {agent_id}: {exc}") from exc

    async def invoke(
        self,
        agent_id: str,
        message: str,
        session_id: Optional[str] = None,
        user_id: str = "anonymous",
        budget_usd: Optional[float] = None,
    ) -> InvocationResult:
        """Invoke an agent with a message.

        Args:
            agent_id: Agent to invoke
            message: Message/query for the agent
            session_id: Optional session ID for conversation continuity
            user_id: User ID for the invocation
            budget_usd: Maximum budget for this invocation

        Returns:
            InvocationResult with the agent's response

        Raises:
            AgentNotFoundError: If agent is not registered
            BudgetExceededError: If invocation would exceed budget
            AgentInvocationError: If invocation fails
        """
        import time

        start_time = time.time()

        # Validate agent exists
        config = self.get_agent_config(agent_id)

        # Check budget
        if budget_usd is not None and budget_usd < config["max_cost_per_invoke"]:
            logger.warning(
                f"Budget ${budget_usd:.4f} may be insufficient for {agent_id} "
                f"(max ${config['max_cost_per_invoke']:.4f})"
            )

        # In mock mode, return a mock response
        if not self.is_connected:
            return self._mock_invoke(agent_id, message, session_id, user_id, start_time)

        # Get the agent
        agent = await self._get_agent(agent_id)

        try:
            # Create or use session
            if session_id is None:
                session = agent.create_session(user_id=user_id)
                session_id = session["id"]

            # Invoke with streaming and collect response
            events: list[dict[str, Any]] = []
            response_text = ""

            async for event in agent.async_stream_query(
                user_id=user_id,
                session_id=session_id,
                message=message,
            ):
                events.append(event)
                # Extract text from the event if available
                if isinstance(event, dict) and "content" in event:
                    response_text += str(event.get("content", ""))

            latency_ms = (time.time() - start_time) * 1000

            return InvocationResult(
                agent_id=agent_id,
                session_id=session_id,
                response=response_text or "Agent completed successfully",
                events=events,
                latency_ms=latency_ms,
                status="success",
            )

        except Exception as exc:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"Agent invocation failed: {exc}")

            return InvocationResult(
                agent_id=agent_id,
                session_id=session_id or "",
                response=f"Error: {exc}",
                latency_ms=latency_ms,
                status="error",
            )

    def _mock_invoke(
        self,
        agent_id: str,
        message: str,
        session_id: Optional[str],
        user_id: str,
        start_time: float,
    ) -> InvocationResult:
        """Generate a mock response for development/testing.

        Args:
            agent_id: Agent being invoked
            message: Original message
            session_id: Session ID
            user_id: User ID
            start_time: Invocation start time

        Returns:
            Mock InvocationResult
        """
        import time
        import uuid

        config = AGENT_CONFIGS[agent_id]
        mock_session_id = session_id or str(uuid.uuid4())

        # Simulate some latency
        latency_ms = (time.time() - start_time) * 1000 + 50  # Add 50ms mock latency

        truncated_msg = f"'{message[:100]}...'" if len(message) > 100 else f"'{message}'"
        mock_response = (
            f"[MOCK] {config['description']} ({agent_id}) responding to: {truncated_msg}"
        )

        logger.info(
            f"Mock invoke: agent={agent_id}, user={user_id}, "
            f"session={mock_session_id[:8]}..."
        )

        return InvocationResult(
            agent_id=agent_id,
            session_id=mock_session_id,
            response=mock_response,
            events=[{"type": "mock", "content": mock_response}],
            tokens_used=0,
            cost_usd=0.0,
            latency_ms=latency_ms,
            status="success",
        )

    async def invoke_stream(
        self,
        agent_id: str,
        message: str,
        session_id: Optional[str] = None,
        user_id: str = "anonymous",
    ) -> AsyncIterator[dict[str, Any]]:
        """Invoke an agent and stream the response.

        Args:
            agent_id: Agent to invoke
            message: Message/query for the agent
            session_id: Optional session ID
            user_id: User ID

        Yields:
            Events from the agent's execution
        """
        # Validate agent exists
        _ = self.get_agent_config(agent_id)

        if not self.is_connected:
            # Mock streaming response
            yield {"type": "mock", "content": f"[MOCK] {agent_id} responding..."}
            yield {"type": "done", "content": ""}
            return

        agent = await self._get_agent(agent_id)

        if session_id is None:
            session = agent.create_session(user_id=user_id)
            session_id = session["id"]

        async for event in agent.async_stream_query(
            user_id=user_id,
            session_id=session_id,
            message=message,
        ):
            yield event


# =============================================================================
# Module-level singleton
# =============================================================================

_registry: Optional[AgentEngineRegistry] = None


def get_registry(config: Optional[AgentEngineConfig] = None) -> AgentEngineRegistry:
    """Get the global AgentEngineRegistry instance.

    Args:
        config: Optional configuration (only used on first call)

    Returns:
        AgentEngineRegistry singleton
    """
    global _registry
    if _registry is None:
        _registry = AgentEngineRegistry(config=config or AgentEngineConfig())
    return _registry


def reset_registry() -> None:
    """Reset the global registry (for testing)."""
    global _registry
    _registry = None
