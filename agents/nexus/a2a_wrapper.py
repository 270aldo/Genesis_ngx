"""Wrapper A2A para exponer agentes ADK como endpoints A2A v0.3.

Este módulo proporciona un servidor FastAPI que expone agentes ADK
siguiendo el protocolo A2A v0.3 (JSON-RPC + SSE).
"""

from __future__ import annotations

import time
import uuid
from typing import Any, AsyncGenerator, Dict, Optional

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google.adk.core import Session, SessionService
from google.adk.runners import Runner
from pydantic import BaseModel, ValidationError
from sse_starlette.sse import EventSourceResponse

from agents.shared.config import get_settings
from agents.shared.logging_config import (
    get_request_logger,
    log_request,
    log_response,
)

settings = get_settings()


class JsonRpcRequest(BaseModel):
    """JSON-RPC 2.0 request."""

    jsonrpc: str
    method: str
    params: Dict[str, Any]
    id: Any


class NegotiationRequest(BaseModel):
    """Negotiation request."""

    capabilities: list[str]
    budget_usd: float


class A2AWrapper:
    """Wrapper que expone un agente ADK como servidor A2A v0.3."""

    def __init__(
        self,
        agent,
        agent_card: Dict[str, Any],
        session_service: Optional[SessionService] = None,
    ):
        """Inicializa el wrapper A2A.

        Args:
            agent: El agente ADK (root_agent)
            agent_card: Agent Card conforme a A2A v0.3
            session_service: SessionService opcional (usa InMemorySessionService por defecto)
        """
        self.agent = agent
        self.agent_card = agent_card
        self.session_service = session_service or SessionService()

        # Crear FastAPI app
        self.app = FastAPI(title=agent_card.get("id", "adk-agent"))

        # Configurar CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_allowed_origins,
            allow_credentials=settings.cors_allow_credentials,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Registrar routes
        self._register_routes()

        # Middleware de logging
        @self.app.middleware("http")
        async def logging_middleware(request: Request, call_next):
            start_time = time.time()
            request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

            logger = get_request_logger(
                name="a2a_wrapper",
                request_id=request_id,
                agent_type=self.agent_card.get("id"),
            )

            log_request(
                logger=logger,
                method=request.method,
                path=request.url.path,
                query_params=dict(request.query_params),
            )

            response = await call_next(request)

            latency_ms = (time.time() - start_time) * 1000
            log_response(
                logger=logger,
                status_code=response.status_code,
                latency_ms=latency_ms,
            )

            response.headers["X-Request-ID"] = request_id
            response.headers["X-Agent-ID"] = self.agent_card.get("id", "unknown")

            return response

    def _register_routes(self) -> None:
        """Registra routes A2A v0.3."""

        @self.app.get("/card")
        async def get_card() -> Dict[str, Any]:
            """GET /card - Devuelve Agent Card."""
            return self.agent_card

        @self.app.get("/healthz")
        async def healthz() -> Dict[str, str]:
            """GET /healthz - Health check."""
            return {"status": "ok"}

        @self.app.post("/negotiate")
        async def negotiate(request: NegotiationRequest) -> Dict[str, Any]:
            """POST /negotiate - Negociación de capacidades."""
            return await self._negotiate_capabilities(request)

        @self.app.post("/invoke")
        async def invoke(
            request: Request,
            x_request_id: Optional[str] = Header(default=None),
            x_budget_usd: Optional[float] = Header(default=None),
        ) -> JSONResponse:
            """POST /invoke - Invocación JSON-RPC."""
            try:
                payload = JsonRpcRequest.parse_obj(await request.json())
            except ValidationError as exc:
                return JSONResponse(
                    status_code=400,
                    content={
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32600,
                            "message": "Invalid Request",
                            "data": {"reason": "VALIDATION_ERROR", "detail": exc.errors()},
                        },
                        "id": None,
                    },
                )

            if payload.jsonrpc != "2.0":
                raise HTTPException(status_code=400, detail="Invalid JSON-RPC version")

            # Verificar budget
            max_cost = self.agent_card["limits"].get("max_cost_per_invoke", 0.0)
            if x_budget_usd is not None and x_budget_usd < max_cost:
                return JSONResponse(
                    status_code=402,
                    content={
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32001,
                            "message": "Budget insufficient",
                            "data": {"reason": "BUDGET_EXCEEDED"},
                        },
                        "id": payload.id,
                    },
                )

            # Ejecutar agente ADK
            result = await self._execute_agent(
                method=payload.method,
                params=payload.params,
                request_id=x_request_id or str(uuid.uuid4()),
            )

            return JSONResponse(
                status_code=200,
                content={"jsonrpc": "2.0", "result": result, "id": payload.id},
            )

        @self.app.post("/invoke/stream")
        async def invoke_stream(
            request: Request,
            x_request_id: Optional[str] = Header(default=None),
        ) -> EventSourceResponse:
            """POST /invoke/stream - Invocación con streaming SSE."""
            try:
                payload = JsonRpcRequest.parse_obj(await request.json())
            except ValidationError as exc:
                raise HTTPException(status_code=400, detail=f"Invalid Request: {exc}")

            async def event_generator() -> AsyncGenerator[dict[str, str], None]:
                async for chunk in self._execute_agent_stream(
                    method=payload.method,
                    params=payload.params,
                    request_id=x_request_id or str(uuid.uuid4()),
                ):
                    yield {"data": chunk}

            return EventSourceResponse(event_generator())

    async def _negotiate_capabilities(
        self, request: NegotiationRequest
    ) -> Dict[str, Any]:
        """Negocia capacidades."""
        missing = [
            cap
            for cap in request.capabilities
            if cap not in self.agent_card["capabilities"]
        ]

        if missing:
            return {
                "accepted": False,
                "missing_capabilities": missing,
                "available_capabilities": self.agent_card["capabilities"],
            }

        if request.budget_usd < self.agent_card["limits"]["max_cost_per_invoke"]:
            return {
                "accepted": False,
                "reason": "insufficient_budget",
                "minimum_budget_usd": self.agent_card["limits"]["max_cost_per_invoke"],
            }

        return {
            "accepted": True,
            "limitations": {
                "max_input_tokens": self.agent_card["limits"]["max_input_tokens"],
                "max_output_tokens": self.agent_card["limits"]["max_output_tokens"],
            },
        }

    async def _execute_agent(
        self,
        method: str,
        params: Dict[str, Any],
        request_id: str,
    ) -> Dict[str, Any]:
        """Ejecuta el agente ADK y devuelve resultado."""
        # Crear session ADK
        session = Session(
            id=request_id,
            app_name=self.agent_card.get("id", "app"),
            user_id=params.get("user_id", "anonymous"),
        )

        # Preparar mensaje del usuario
        user_message = params.get("message", "")

        # Ejecutar agente
        runner = Runner(self.agent, session_service=self.session_service)

        try:
            # Run agent
            result_events = []
            async for event in runner.run_async(user_message, session=session):
                result_events.append(event)

            # Obtener respuesta final
            if result_events:
                last_event = result_events[-1]
                response_text = ""

                # Extraer texto de la respuesta
                if hasattr(last_event, "content") and last_event.content:
                    if hasattr(last_event.content, "parts"):
                        for part in last_event.content.parts:
                            if hasattr(part, "text"):
                                response_text += part.text

                # Obtener datos del state si se configuró output_key
                output_key = self.agent.output_key if hasattr(self.agent, "output_key") else None
                state_data = {}
                if output_key and hasattr(session, "state"):
                    state_data = session.state.get(output_key, {})

                return {
                    "response": response_text,
                    "method": method,
                    "state": state_data,
                    "metadata": {
                        "events_count": len(result_events),
                        "session_id": session.id,
                    },
                }
            else:
                return {
                    "response": "No response generated",
                    "method": method,
                    "error": "No events returned",
                }

        except Exception as exc:
            return {
                "error": str(exc),
                "method": method,
            }

    async def _execute_agent_stream(
        self,
        method: str,
        params: Dict[str, Any],
        request_id: str,
    ) -> AsyncGenerator[str, None]:
        """Ejecuta el agente ADK con streaming."""
        # Crear session ADK
        session = Session(
            id=request_id,
            app_name=self.agent_card.get("id", "app"),
            user_id=params.get("user_id", "anonymous"),
        )

        # Preparar mensaje
        user_message = params.get("message", "")

        # Ejecutar agente con streaming
        runner = Runner(self.agent, session_service=self.session_service)

        try:
            async for event in runner.run_async(user_message, session=session):
                # Enviar cada chunk
                if hasattr(event, "content") and event.content:
                    if hasattr(event.content, "parts"):
                        for part in event.content.parts:
                            if hasattr(part, "text") and part.text:
                                yield part.text

        except Exception as exc:
            yield f"error:{str(exc)}"
