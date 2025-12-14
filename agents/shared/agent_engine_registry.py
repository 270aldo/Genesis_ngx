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

import asyncio
import json
import logging
import os
import threading
import uuid
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


@dataclass(frozen=True)
class _AgentEngineClients:
    """Holds low-level Vertex AI clients used by the registry."""

    reasoning_engine_service: Any
    reasoning_engine_execution_service: Any
    session_service: Any


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

    def _mock_fallback_allowed(self) -> bool:
        """Whether it is acceptable to fall back to mock mode.

        Mock fallback is convenient for local development, but dangerous in staging/
        production because it can silently break real orchestration.
        """
        allow_mock_env = os.getenv("AGENT_ENGINE_ALLOW_MOCK", "").strip().lower()
        if allow_mock_env in {"1", "true", "yes", "on"}:
            return True

        # Default policy: never fall back in staging/production.
        return self.config.environment not in {"staging", "production"}

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
            import google.auth
            from google.api_core.client_options import ClientOptions
            from google.auth.exceptions import DefaultCredentialsError
            from google.cloud.aiplatform_v1beta1.services.reasoning_engine_execution_service import (
                ReasoningEngineExecutionServiceClient,
            )
            from google.cloud.aiplatform_v1beta1.services.reasoning_engine_service import (
                ReasoningEngineServiceClient,
            )
            from google.cloud.aiplatform_v1beta1.services.session_service import (
                SessionServiceClient,
            )

            # Fail early if ADC isn't configured so we can decide whether to mock.
            try:
                google.auth.default()
            except DefaultCredentialsError as exc:
                if self._mock_fallback_allowed():
                    logger.warning(
                        "No Application Default Credentials available; "
                        "AgentEngineRegistry operating in mock mode.",
                    )
                    self._client = None
                    return
                raise AgentEngineError(
                    "Application Default Credentials not available; refusing to fall "
                    "back to mock mode in staging/production."
                ) from exc

            api_endpoint = f"{self.config.location}-aiplatform.googleapis.com"
            client_options = ClientOptions(api_endpoint=api_endpoint)

            self._client = _AgentEngineClients(
                reasoning_engine_service=ReasoningEngineServiceClient(
                    client_options=client_options
                ),
                reasoning_engine_execution_service=ReasoningEngineExecutionServiceClient(
                    client_options=client_options
                ),
                session_service=SessionServiceClient(client_options=client_options),
            )
            logger.info(
                f"AgentEngineRegistry initialized for project={self.config.project_id}, "
                f"location={self.config.location}"
            )
        except ImportError as exc:
            # Dependency missing or incompatible install. This should never be
            # silently swallowed in staging/production.
            if self._mock_fallback_allowed():
                logger.warning(
                    f"Could not import Agent Engine dependencies: {exc}. "
                    "Operating in mock mode."
                )
                self._client = None
                return
            raise AgentEngineError(
                "Agent Engine dependencies are missing/incompatible; refusing to fall "
                "back to mock mode in staging/production."
            ) from exc

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

        # We no longer fetch a higher-level SDK object here. Instead, we cache the
        # ReasoningEngine resource name and use the execution client directly.
        resource_name = self.get_resource_name(agent_id)
        self._agent_cache[agent_id] = resource_name
        return resource_name

    async def _create_session(self, resource_name: str, user_id: str) -> str:
        """Create a Vertex AI session for a reasoning engine.

        Returns the session ID (last path segment).
        """
        if not self.is_connected:
            return str(uuid.uuid4())

        from google.cloud.aiplatform_v1beta1.types.session import Session

        try:
            operation = await asyncio.to_thread(
                self._client.session_service.create_session,
                parent=resource_name,
                session=Session(
                    user_id=user_id,
                    display_name=f"genesis-ngx:{user_id}",
                ),
                timeout=self.config.default_timeout_seconds,
            )

            created_session = await asyncio.to_thread(
                operation.result,
                timeout=self.config.default_timeout_seconds,
            )

            if not created_session.name:
                return str(uuid.uuid4())

            # projects/.../reasoningEngines/.../sessions/{session}
            return created_session.name.split("/")[-1]
        except Exception as exc:
            logger.error(f"Failed to create session for {resource_name}: {exc}")
            raise AgentInvocationError(
                f"Failed to create session for {resource_name}: {exc}"
            ) from exc

    @staticmethod
    def _extract_response(output: Any) -> tuple[str, list[dict[str, Any]]]:
        """Normalize execution output into (response_text, events)."""
        if output is None:
            return "", []

        if isinstance(output, str):
            return output, [{"type": "output", "content": output}]

        if isinstance(output, list):
            text = "".join(str(item) for item in output)
            return text, [{"type": "chunk", "content": str(item)} for item in output]

        if isinstance(output, dict):
            # If the engine already returns structured events, prefer them.
            events = output.get("events")
            if isinstance(events, list):
                response_text = ""
                for event in events:
                    if isinstance(event, dict) and "content" in event:
                        response_text += str(event.get("content", ""))
                if response_text:
                    return response_text, [e for e in events if isinstance(e, dict)]

            for key in ("response", "content", "text", "message", "answer", "output"):
                value = output.get(key)
                if isinstance(value, str) and value.strip():
                    return value, [{"type": "output", "content": value, "raw": output}]

            # If there's exactly one string value, use it as the response.
            string_values = [v for v in output.values() if isinstance(v, str) and v.strip()]
            if len(string_values) == 1:
                value = string_values[0]
                return value, [{"type": "output", "content": value, "raw": output}]

            return json.dumps(output, ensure_ascii=False), [{"type": "output", "content": output}]

        return str(output), [{"type": "output", "content": str(output)}]

    async def _query_reasoning_engine(
        self,
        resource_name: str,
        *,
        user_id: str,
        session_id: str,
        message: str,
        timeout_seconds: float,
    ) -> tuple[str, list[dict[str, Any]]]:
        """Invoke a reasoning engine via the GAPIC execution client."""
        from google.cloud.aiplatform_v1beta1.types.reasoning_engine_execution_service import (
            QueryReasoningEngineRequest,
        )
        from google.protobuf import json_format
        from google.protobuf.struct_pb2 import Struct

        input_struct = Struct()
        input_struct.update(
            {
                "user_id": user_id,
                "session_id": session_id,
                "message": message,
            }
        )

        request = QueryReasoningEngineRequest(
            name=resource_name,
            input=input_struct,
        )

        response = await asyncio.to_thread(
            self._client.reasoning_engine_execution_service.query_reasoning_engine,
            request,
            timeout=timeout_seconds,
        )

        output = json_format.MessageToDict(response.output)
        return self._extract_response(output)

    async def _stream_reasoning_engine(
        self,
        resource_name: str,
        *,
        user_id: str,
        session_id: str,
        message: str,
        timeout_seconds: float,
    ) -> AsyncIterator[dict[str, Any]]:
        """Stream a reasoning engine response.

        The underlying GAPIC client is synchronous, so we bridge it to async with a
        background thread.
        """
        from google.cloud.aiplatform_v1beta1.types.reasoning_engine_execution_service import (
            StreamQueryReasoningEngineRequest,
        )
        from google.protobuf.struct_pb2 import Struct

        input_struct = Struct()
        input_struct.update(
            {
                "user_id": user_id,
                "session_id": session_id,
                "message": message,
            }
        )

        request = StreamQueryReasoningEngineRequest(
            name=resource_name,
            input=input_struct,
        )

        queue: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def worker() -> None:
            try:
                stream = self._client.reasoning_engine_execution_service.stream_query_reasoning_engine(  # type: ignore[union-attr]
                    request,
                    timeout=timeout_seconds,
                )
                for body in stream:
                    data = getattr(body, "data", b"") or b""
                    text = data.decode("utf-8", errors="replace")
                    event: dict[str, Any]
                    try:
                        parsed = json.loads(text)
                        if isinstance(parsed, dict):
                            event = parsed
                        else:
                            event = {"type": "chunk", "content": str(parsed)}
                    except json.JSONDecodeError:
                        event = {"type": "chunk", "content": text}

                    # Ensure downstream can reconstruct text similarly to invoke().
                    if "content" not in event:
                        event["content"] = text

                    loop.call_soon_threadsafe(queue.put_nowait, event)
            except Exception as exc:
                loop.call_soon_threadsafe(
                    queue.put_nowait,
                    {"type": "error", "content": f"{exc}"},
                )
            finally:
                loop.call_soon_threadsafe(queue.put_nowait, None)

        threading.Thread(target=worker, daemon=True).start()

        while True:
            event = await queue.get()
            if event is None:
                return
            yield event

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

        resource_name = await self._get_agent(agent_id)

        try:
            # Create or use session
            if session_id is None:
                session_id = await self._create_session(resource_name, user_id=user_id)

            # Use unary query for invoke(); stream is available via invoke_stream().
            timeout_seconds = max(
                self.config.default_timeout_seconds,
                (config["max_latency_ms"] / 1000.0) + 5.0,
            )
            response_text, events = await self._query_reasoning_engine(
                resource_name,
                user_id=user_id,
                session_id=session_id,
                message=message,
                timeout_seconds=timeout_seconds,
            )

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

        resource_name = await self._get_agent(agent_id)

        if session_id is None:
            session_id = await self._create_session(resource_name, user_id=user_id)

        timeout_seconds = self.config.default_timeout_seconds
        async for event in self._stream_reasoning_engine(
            resource_name,
            user_id=user_id,
            session_id=session_id,
            message=message,
            timeout_seconds=timeout_seconds,
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
