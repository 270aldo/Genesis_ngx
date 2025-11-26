"""Fitness Agent for Genesis NGX.

Specialized in workout planning, exercise tracking, and physical progress analysis.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Optional

from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

from agents.shared.a2a_server import A2AServer
from agents.shared.config import get_settings
from agents.shared.gemini_client import GeminiModel, get_gemini_client
from agents.shared.logging_config import (
    get_request_logger,
    log_gemini_generation,
    log_request,
    log_response,
)
from agents.shared.supabase_client import get_supabase_client

# Configuración
settings = get_settings()

# Agent Card
AGENT_CARD: Dict[str, Any] = {
    "id": "fitness-agent",
    "version": "0.1.0",
    "description": "Agente especializado en fitness y planificación de entrenamientos.",
    "capabilities": [
        "workout_planning",
        "exercise_tracking",
        "progress_analysis",
    ],
    "limits": {
        "max_input_tokens": 30000,
        "max_output_tokens": 2000,
        "max_latency_ms": 5000,
        "max_cost_per_invoke": 0.02,
    },
    "privacy": {
        "pii": False,
        "phi": False,  # No maneja datos médicos sensibles directamente, solo fitness
    },
    "auth": {
        "method": "oidc",
        "audience": "fitness-agent",
        "issuer": settings.auth.oidc_issuer,
    },
}


class FitnessAgent(A2AServer):
    """Agente de Fitness."""

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
            start_time = time.time()
            request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

            logger = get_request_logger(
                name="fitness",
                request_id=request_id,
                agent_type="fitness",
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
            response.headers["X-Agent-ID"] = "fitness-agent"

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
            name="fitness.handle_method",
            agent_type="fitness",
            method=method,
        )

        try:
            if method == "workout_planning":
                return await self._plan_workout(params, logger)
            
            if method == "exercise_tracking":
                return await self._track_exercise(params, logger)

            if method == "progress_analysis":
                return await self._analyze_progress(params, logger)

            return {"status": "unknown_method", "method": method}

        except Exception as exc:
            logger.error("method_execution_error", method=method, error=str(exc))
            raise

    # =========================================================================
    # Implementación de Capacidades
    # =========================================================================

    async def _plan_workout(
        self,
        params: Dict[str, Any],
        logger,
    ) -> Dict[str, Any]:
        """Genera un plan de entrenamiento usando Gemini."""
        user_profile = params.get("user_profile", {})
        goals = params.get("goals", "general fitness")
        constraints = params.get("constraints", "none")

        prompt = f"""
        Act as an expert fitness coach. Create a structured workout plan based on:
        User Profile: {user_profile}
        Goals: {goals}
        Constraints: {constraints}

        Provide the plan in JSON format with 'warmup', 'exercises' (list with name, sets, reps), and 'cooldown'.
        """

        response_text, metrics = await self.gemini.generate(
            prompt=prompt,
            model=GeminiModel.FLASH_LITE,  # Efficient model for structured tasks
            system_instruction="You are a strict and efficient fitness planner. Output JSON only.",
            max_output_tokens=1000,
            temperature=0.3,
        )

        log_gemini_generation(
            logger=logger,
            model=metrics.model,
            prompt_tokens=metrics.prompt_tokens,
            output_tokens=metrics.output_tokens,
            cached_tokens=metrics.cached_tokens,
            cost_usd=metrics.cost_usd,
            latency_ms=metrics.latency_ms,
        )

        return {
            "plan": response_text,  # En producción idealmente parsearíamos JSON aquí
            "metrics": metrics.to_dict(),
        }

    async def _track_exercise(
        self,
        params: Dict[str, Any],
        logger,
    ) -> Dict[str, Any]:
        """Registra un ejercicio (Mock por ahora, luego a Supabase)."""
        # TODO: Implementar persistencia en health_metrics
        logger.info("tracking_exercise", params=params)
        return {"status": "recorded", "id": str(uuid.uuid4())}

    async def _analyze_progress(
        self,
        params: Dict[str, Any],
        logger,
    ) -> Dict[str, Any]:
        """Analiza progreso (Mock por ahora)."""
        logger.info("analyzing_progress", params=params)
        return {
            "status": "analyzed",
            "trend": "improving",
            "summary": "Consistent activity detected over the last week."
        }


# Instancia del agente
agent = FitnessAgent()
app = agent.app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "agents.fitness.main:app",
        host="0.0.0.0",
        port=8081,  # Puerto diferente a Nexus (8080)
        reload=settings.service.reload,
        log_level=settings.logging.level.value.lower(),
    )
