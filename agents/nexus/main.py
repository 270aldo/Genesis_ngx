"""NEXUS Orchestrator con integraciones completas.

Características:
- Gemini 2.5 para clasificación de intents y orquestación
- Supabase para persistencia de conversaciones y mensajes
- Logging estructurado con Cloud Logging
- A2A protocol para comunicación con agentes especializados
- Cost tracking y budget enforcement
"""

from __future__ import annotations

import time
import uuid
from typing import Any, AsyncGenerator, Dict, Optional

from fastapi import Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from agents.shared.a2a_client import A2AClient
from agents.shared.a2a_server import A2AServer
from agents.shared.config import get_settings
from agents.shared.gemini_client import GeminiModel, get_gemini_client
from agents.shared.logging_config import (
    get_request_logger,
    log_agent_invocation,
    log_gemini_generation,
    log_request,
    log_response,
)
from agents.shared.supabase_client import get_supabase_client

# Configuración
settings = get_settings()

# Agent Card
AGENT_CARD: Dict[str, Any] = {
    "id": "nexus-orchestrator",
    "version": "0.1.0",
    "description": "NEXUS orchestrator para sistema multi-agente de bienestar",
    "capabilities": [
        "orchestration",
        "intent_classification",
        "consensus",
        "handoff",
        "planning",
    ],
    "limits": {
        "max_input_tokens": 50000,
        "max_output_tokens": 4000,
        "max_latency_ms": 8000,
        "max_cost_per_invoke": 0.05,
    },
    "privacy": {
        "pii": False,
        "phi": False,
        "data_retention_days": 90,
        "notes": "NEXUS no persiste PII/PHI directamente, solo metadata de orquestación",
    },
    "auth": {
        "method": "oidc",
        "audience": "nexus-orchestrator",
        "issuer": settings.auth.oidc_issuer,
    },
}


class NexusAgent(A2AServer):
    """NEXUS orchestrator agent."""

    def __init__(self) -> None:
        super().__init__(AGENT_CARD)
        self.gemini = get_gemini_client()
        self.supabase = get_supabase_client()

        # Configurar CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_allowed_origins,
            allow_credentials=settings.cors_allow_credentials,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Agregar middleware de logging
        @self.app.middleware("http")
        async def logging_middleware(request: Request, call_next):
            """Middleware para logging de requests."""
            start_time = time.time()
            request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

            # Logger con contexto
            logger = get_request_logger(
                name="nexus",
                request_id=request_id,
                agent_type="nexus",
            )

            # Log request
            log_request(
                logger=logger,
                method=request.method,
                path=request.url.path,
                query_params=dict(request.query_params),
            )

            # Procesar request
            response = await call_next(request)

            # Log response
            latency_ms = (time.time() - start_time) * 1000
            log_response(
                logger=logger,
                status_code=response.status_code,
                latency_ms=latency_ms,
            )

            # Agregar headers de respuesta
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Agent-ID"] = "nexus-orchestrator"

            return response

    async def negotiate_capabilities(
        self, request
    ) -> Dict[str, Any]:
        """Negocia capacidades con el cliente."""
        missing = [
            cap for cap in request.capabilities if cap not in AGENT_CARD["capabilities"]
        ]

        if missing:
            return {
                "accepted": False,
                "missing_capabilities": missing,
                "available_capabilities": AGENT_CARD["capabilities"],
            }

        # Verificar presupuesto
        if request.budget_usd < AGENT_CARD["limits"]["max_cost_per_invoke"]:
            return {
                "accepted": False,
                "reason": "insufficient_budget",
                "minimum_budget_usd": AGENT_CARD["limits"]["max_cost_per_invoke"],
            }

        return {
            "accepted": True,
            "limitations": {
                "max_input_tokens": AGENT_CARD["limits"]["max_input_tokens"],
                "max_output_tokens": AGENT_CARD["limits"]["max_output_tokens"],
            },
        }

    async def handle_method(
        self,
        method: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Maneja métodos A2A."""
        logger = get_request_logger(
            name="nexus.handle_method",
            agent_type="nexus",
            method=method,
        )

        try:
            if method == "classify_intent":
                return await self._classify_intent(params, logger)

            if method == "orchestrate":
                return await self._orchestrate(params, logger)

            if method == "echo":
                return {"echo": params}

            return {"status": "unknown_method", "method": method}

        except Exception as exc:
            logger.error("method_execution_error", method=method, error=str(exc))
            raise

    async def handle_stream(
        self,
        method: str,
        params: Dict[str, Any],
    ) -> AsyncGenerator[str, None]:
        """Maneja métodos con streaming."""
        logger = get_request_logger(
            name="nexus.handle_stream",
            agent_type="nexus",
            method=method,
        )

        try:
            if method == "plan":
                async for chunk in self._plan_stream(params, logger):
                    yield chunk
                return

            if method == "orchestrate_stream":
                async for chunk in self._orchestrate_stream(params, logger):
                    yield chunk
                return

            yield "method_not_supported"

        except Exception as exc:
            logger.error("stream_execution_error", method=method, error=str(exc))
            yield f"error:{str(exc)}"

    # =========================================================================
    # Métodos privados
    # =========================================================================

    async def _classify_intent(
        self,
        params: Dict[str, Any],
        logger,
    ) -> Dict[str, Any]:
        """Clasifica el intent del usuario usando Gemini Flash-Lite."""
        message = params.get("message", "")
        possible_intents = params.get(
            "intents",
            ["check_in", "plan", "track", "advice", "general_inquiry"],
        )

        logger.info("classifying_intent", message=message[:100])

        # Usar Gemini para clasificar
        intent, confidence = await self.gemini.classify_intent(
            message=message,
            possible_intents=possible_intents,
        )

        logger.info(
            "intent_classified",
            intent=intent,
            confidence=confidence,
        )

        return {
            "intent": intent,
            "confidence": confidence,
            "suggested_agent": self._intent_to_agent(intent),
        }

    def _intent_to_agent(self, intent: str) -> str:
        """Mapea intent a agente especializado."""
        intent_map = {
            "check_in": "fitness",
            "plan": "nexus",  # NEXUS maneja planning multi-agente
            "track": "fitness",
            "advice": "nexus",  # Consulta a múltiples agentes
            "nutrition": "nutrition",
            "mental_health": "mental",
        }
        return intent_map.get(intent, "nexus")

    async def _orchestrate(
        self,
        params: Dict[str, Any],
        logger,
    ) -> Dict[str, Any]:
        """Orquesta llamada a agentes especializados."""
        user_message = params.get("message", "")
        conversation_id = params.get("conversation_id")
        user_id = params.get("user_id")

        logger.info(
            "orchestrating",
            conversation_id=conversation_id,
            user_id=user_id,
        )

        # 1. Clasificar intent
        intent_result = await self._classify_intent(
            {"message": user_message},
            logger,
        )
        intent = intent_result["intent"]
        agent_type = intent_result["suggested_agent"]

        # 2. Si es NEXUS, responder directamente con Gemini Pro
        if agent_type == "nexus":
            response_text, metrics = await self.gemini.generate(
                prompt=user_message,
                model=GeminiModel.FLASH,
                system_instruction="""Eres NEXUS, un asistente de bienestar que ayuda a coordinar
diferentes aspectos de salud: fitness, nutrición y salud mental.
Proporciona respuestas útiles, empáticas y basadas en evidencia.""",
                max_output_tokens=2048,
                temperature=0.8,
            )

            # Log de métricas Gemini
            log_gemini_generation(
                logger=logger,
                model=metrics.model,
                prompt_tokens=metrics.prompt_tokens,
                output_tokens=metrics.output_tokens,
                cached_tokens=metrics.cached_tokens,
                cost_usd=metrics.cost_usd,
                latency_ms=metrics.latency_ms,
            )

            # Persistir si se provee conversation_id
            if conversation_id and user_id:
                try:
                    await self.supabase.agent_append_message(
                        conversation_id=uuid.UUID(conversation_id),
                        agent_type="nexus",
                        content=response_text,
                        tokens_used=metrics.total_tokens,
                        cost_usd=metrics.cost_usd,
                    )
                except Exception as exc:
                    logger.warning("failed_to_persist_message", error=str(exc))

            return {
                "agent": "nexus",
                "response": response_text,
                "intent": intent,
                "metrics": metrics.to_dict(),
            }

        # 3. Para otros agentes, hacer handoff (por ahora mock)
        # TODO: Implementar A2A client para invocar agentes especializados
        logger.info("handoff_to_agent", target_agent=agent_type)

        return {
            "agent": agent_type,
            "response": f"Handoff a agente {agent_type} (TODO: implementar A2A invocation)",
            "intent": intent,
            "handoff": True,
        }

    async def _plan_stream(
        self,
        params: Dict[str, Any],
        logger,
    ) -> AsyncGenerator[str, None]:
        """Genera un plan con streaming."""
        steps = params.get("steps", ["analyze", "recommend", "summarize"])

        for step in steps:
            logger.info("processing_plan_step", step=step)
            yield f"processing:{step}\n"
            # Simular procesamiento
            import asyncio
            await asyncio.sleep(0.5)

        yield "completed\n"

    async def _orchestrate_stream(
        self,
        params: Dict[str, Any],
        logger,
    ) -> AsyncGenerator[str, None]:
        """Orquesta con streaming de respuesta."""
        user_message = params.get("message", "")

        # Clasificar intent
        intent_result = await self._classify_intent(
            {"message": user_message},
            logger,
        )

        yield f"intent:{intent_result['intent']}\n"

        # Generar respuesta con streaming
        async for chunk in self.gemini.generate_stream(
            prompt=user_message,
            model=GeminiModel.FLASH,
            system_instruction="Eres NEXUS, un asistente de bienestar empático.",
            max_output_tokens=1024,
        ):
            yield f"text:{chunk}\n"


# Instancia del agente
agent = NexusAgent()
app = agent.app


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(
        "agents.nexus.main:app",
        host=settings.service.host,
        port=settings.service.port,
        reload=settings.service.reload,
        log_level=settings.logging.level.value.lower(),
    )
