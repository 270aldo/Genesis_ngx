"""Nutrition Agent for Genesis NGX.

Specialized in meal planning, calorie tracking, and macronutrient analysis.
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
    "id": "nutrition-agent",
    "version": "0.1.0",
    "description": "Agente especializado en nutrición y planificación de dietas.",
    "capabilities": [
        "meal_planning",
        "calorie_tracking",
        "macro_analysis",
    ],
    "limits": {
        "max_input_tokens": 30000,
        "max_output_tokens": 2000,
        "max_latency_ms": 5000,
        "max_cost_per_invoke": 0.02,
    },
    "privacy": {
        "pii": False,
        "phi": False,
    },
    "auth": {
        "method": "oidc",
        "audience": "nutrition-agent",
        "issuer": settings.auth.oidc_issuer,
    },
}


class NutritionAgent(A2AServer):
    """Agente de Nutrición."""

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
                name="nutrition",
                request_id=request_id,
                agent_type="nutrition",
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
            response.headers["X-Agent-ID"] = "nutrition-agent"

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
            name="nutrition.handle_method",
            agent_type="nutrition",
            method=method,
        )

        try:
            if method == "meal_planning":
                return await self._plan_meals(params, logger)
            
            if method == "calorie_tracking":
                return await self._track_calories(params, logger)

            if method == "macro_analysis":
                return await self._analyze_macros(params, logger)

            return {"status": "unknown_method", "method": method}

        except Exception as exc:
            logger.error("method_execution_error", method=method, error=str(exc))
            raise

    # =========================================================================
    # Implementación de Capacidades
    # =========================================================================

    async def _plan_meals(
        self,
        params: Dict[str, Any],
        logger,
    ) -> Dict[str, Any]:
        """Genera un plan de comidas usando Gemini."""
        dietary_preferences = params.get("preferences", "none")
        allergies = params.get("allergies", "none")
        goals = params.get("goals", "healthy eating")

        prompt = f"""
        Act as an expert nutritionist. Create a meal plan based on:
        Preferences: {dietary_preferences}
        Allergies: {allergies}
        Goals: {goals}

        Provide the plan in JSON format with 'breakfast', 'lunch', 'dinner', and 'snacks'.
        Include macronutrient estimates per meal.
        """

        response_text, metrics = await self.gemini.generate(
            prompt=prompt,
            model=GeminiModel.FLASH_LITE,
            system_instruction="You are a precise nutritionist. Output JSON only.",
            max_output_tokens=1500,
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
            "plan": response_text,
            "metrics": metrics.to_dict(),
        }

    async def _track_calories(
        self,
        params: Dict[str, Any],
        logger,
    ) -> Dict[str, Any]:
        """Registra ingesta calórica (Mock)."""
        logger.info("tracking_calories", params=params)
        return {"status": "recorded", "id": str(uuid.uuid4())}

    async def _analyze_macros(
        self,
        params: Dict[str, Any],
        logger,
    ) -> Dict[str, Any]:
        """Analiza macronutrientes (Mock)."""
        logger.info("analyzing_macros", params=params)
        return {
            "status": "analyzed",
            "balance": "balanced",
            "recommendation": "Maintain current protein intake."
        }


# Instancia del agente
agent = NutritionAgent()
app = agent.app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "agents.nutrition.main:app",
        host="0.0.0.0",
        port=8082,  # Puerto diferente a Nexus (8080) y Fitness (8081)
        reload=settings.service.reload,
        log_level=settings.logging.level.value.lower(),
    )
