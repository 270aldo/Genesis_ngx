"""Servidor base para agentes A2A (JSON-RPC + SSE)."""

from __future__ import annotations

import asyncio
from typing import Any, AsyncGenerator, Dict, Optional

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sse_starlette.sse import EventSourceResponse


class JsonRpcRequest(BaseModel):
    jsonrpc: str
    method: str
    params: Dict[str, Any]
    id: Any


class NegotiationRequest(BaseModel):
    capabilities: list[str]
    budget_usd: float


class A2AServer:
    """Base server A2A. Subclases definen lógica de negocio."""

    def __init__(self, agent_card: Dict[str, Any]) -> None:
        self.agent_card = agent_card
        self.app = FastAPI()
        self._register_routes()

    # ------------------------------------------------------------------
    # Métodos para override en subclases
    # ------------------------------------------------------------------
    async def negotiate_capabilities(
        self, request: NegotiationRequest
    ) -> Dict[str, Any]:  # pragma: no cover - override esperado
        return {"accepted": True, "limitations": {}}

    async def handle_method(self, method: str, params: Dict[str, Any]) -> Any:
        raise NotImplementedError

    async def handle_stream(self, method: str, params: Dict[str, Any]) -> AsyncGenerator[str, None]:
        yield "unsupported"

    # ------------------------------------------------------------------
    # Rutas
    # ------------------------------------------------------------------
    def _register_routes(self) -> None:
        @self.app.get("/card")
        async def get_card() -> Dict[str, Any]:
            return self.agent_card

        @self.app.get("/healthz")
        async def healthz() -> Dict[str, str]:
            return {"status": "ok"}

        @self.app.post("/negotiate")
        async def negotiate(request: NegotiationRequest) -> Dict[str, Any]:
            return await self.negotiate_capabilities(request)

        @self.app.post("/invoke")
        async def invoke(
            request: Request,
            x_request_id: Optional[str] = Header(default=None),
            x_budget_usd: Optional[float] = Header(default=None),
        ) -> JSONResponse:
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

            result = await self.handle_method(payload.method, payload.params)
            return JSONResponse(
                status_code=200,
                content={"jsonrpc": "2.0", "result": result, "id": payload.id},
            )

        @self.app.post("/invoke/stream")
        async def invoke_stream(
            request: Request,
            x_request_id: Optional[str] = Header(default=None),
        ) -> EventSourceResponse:
            try:
                payload = JsonRpcRequest.parse_obj(await request.json())
            except ValidationError as exc:
                raise HTTPException(status_code=400, detail=f"Invalid Request: {exc}")

            async def event_generator() -> AsyncGenerator[dict[str, str], None]:
                async for chunk in self.handle_stream(payload.method, payload.params):
                    yield {"data": chunk}

            return EventSourceResponse(event_generator())


async def periodic_keepalive(interval: float = 15.0) -> AsyncGenerator[str, None]:
    """Genera comentarios SSE para mantener conexiones largas."""

    while True:  # pragma: no cover - se usa en runtime
        await asyncio.sleep(interval)
        yield ":keep-alive"
