"""METABOL - Agente especializado en Metabolismo.

Este modulo define el agente METABOL usando Google ADK.
METABOL calcula TDEE, evalua tasas metabolicas, planifica timing
nutricional y detecta adaptaciones para usuarios de 30-60 años.

Capabilities:
- TDEE calculation
- Metabolic rate assessment
- Nutrient timing planning
- Metabolic adaptation detection
- Insulin sensitivity assessment

SLOs (de PRD Seccion 4.2):
- Latency p95: ≤2.0s
- Cost per invoke: ≤$0.01
"""

from __future__ import annotations

import logging
from typing import Any

from google.adk import Agent

from agents.metabol.prompts import METABOL_SYSTEM_PROMPT
from agents.metabol.tools import ALL_TOOLS

logger = logging.getLogger(__name__)

# =============================================================================
# Agent Configuration
# =============================================================================

AGENT_CONFIG = {
    "agent_id": "metabol",
    "display_name": "METABOL",
    "domain": "nutrition",
    "specialty": "metabolism",
    "model": "gemini-2.5-flash",
    "thinking_level": "low",
    "capabilities": [
        "metabolic_assessment",
        "tdee_calculation",
        "insulin_sensitivity",
        "nutrient_timing",
        "metabolic_adaptation",
    ],
    "limits": {
        "max_input_tokens": 20000,
        "max_output_tokens": 2000,
        "max_latency_ms": 2000,
        "max_cost_per_invoke": 0.01,
    },
}

# =============================================================================
# Agent Definition
# =============================================================================

metabol = Agent(
    name="metabol",
    model=AGENT_CONFIG["model"],
    description=(
        "Especialista en metabolismo, calculo de TDEE y requerimientos "
        "energeticos. Evalua tasas metabolicas, planifica timing nutricional, "
        "detecta adaptaciones metabolicas y evalua sensibilidad a insulina "
        "para usuarios de 30-60 años."
    ),
    instruction=METABOL_SYSTEM_PROMPT,
    tools=ALL_TOOLS,
    output_key="metabol_response",
)

# =============================================================================
# Agent Card (A2A Protocol)
# =============================================================================

AGENT_CARD = {
    "name": AGENT_CONFIG["display_name"],
    "description": metabol.description,
    "version": "1.0.0",
    "protocol": "a2a/0.3",
    "domain": AGENT_CONFIG["domain"],
    "specialty": AGENT_CONFIG["specialty"],
    "capabilities": AGENT_CONFIG["capabilities"],
    "methods": [
        {
            "name": "calculate_tdee",
            "description": "Calcula el gasto energetico diario total",
            "params": {
                "weight_kg": {"type": "number", "required": True},
                "height_cm": {"type": "number", "required": True},
                "age": {"type": "integer", "required": True},
                "sex": {"type": "string", "required": False},
                "activity_level": {"type": "string", "required": False},
                "goal": {"type": "string", "required": False},
            },
        },
        {
            "name": "assess_metabolic_rate",
            "description": "Evalua la tasa metabolica basal con multiples formulas",
            "params": {
                "weight_kg": {"type": "number", "required": True},
                "height_cm": {"type": "number", "required": True},
                "age": {"type": "integer", "required": True},
                "sex": {"type": "string", "required": False},
                "body_fat_percent": {"type": "number", "required": False},
            },
        },
        {
            "name": "plan_nutrient_timing",
            "description": "Planifica el timing nutricional optimo",
            "params": {
                "training_time": {"type": "string", "required": True},
                "wake_time": {"type": "string", "required": False},
                "sleep_time": {"type": "string", "required": False},
                "meals_per_day": {"type": "integer", "required": False},
            },
        },
        {
            "name": "detect_metabolic_adaptation",
            "description": "Detecta signos de adaptacion metabolica",
            "params": {
                "weekly_weights": {"type": "array", "required": True},
                "daily_calories": {"type": "integer", "required": True},
                "weeks_in_deficit": {"type": "integer", "required": False},
            },
        },
        {
            "name": "assess_insulin_sensitivity",
            "description": "Evalua indicadores de sensibilidad a insulina",
            "params": {
                "fasting_glucose_mg_dl": {"type": "number", "required": False},
                "post_meal_energy": {"type": "string", "required": False},
                "exercise_frequency": {"type": "string", "required": False},
            },
        },
        {
            "name": "respond",
            "description": "Responde preguntas generales sobre metabolismo",
            "params": {
                "message": {"type": "string", "required": True},
                "user_context": {"type": "object", "required": False},
            },
        },
    ],
    "limits": AGENT_CONFIG["limits"],
    "privacy": {
        "pii": False,
        "phi": False,
        "data_retention_days": 90,
    },
    "auth": {
        "method": "oidc",
        "audience": "metabol-metabolism-agent",
    },
}

# =============================================================================
# Helper Functions
# =============================================================================


def calculate_user_tdee(
    weight_kg: float,
    height_cm: float,
    age: int,
    sex: str = "male",
    activity_level: str = "moderate",
    goal: str = "maintenance",
) -> dict[str, Any]:
    """Calcula el TDEE del usuario.

    Args:
        weight_kg: Peso en kg
        height_cm: Altura en cm
        age: Edad en años
        sex: Sexo
        activity_level: Nivel de actividad
        goal: Objetivo

    Returns:
        dict con TDEE calculado
    """
    from agents.metabol.tools import calculate_tdee

    return calculate_tdee(
        weight_kg=weight_kg,
        height_cm=height_cm,
        age=age,
        sex=sex,
        activity_level=activity_level,
        goal=goal,
    )


def get_status() -> dict[str, Any]:
    """Obtiene el estado actual del agente METABOL."""
    from agents.metabol.tools import ACTIVITY_LEVELS, METABOLIC_FORMULAS, GOAL_ADJUSTMENTS

    return {
        "status": "healthy",
        "version": AGENT_CARD["version"],
        "agent_id": AGENT_CONFIG["agent_id"],
        "model": AGENT_CONFIG["model"],
        "domain": AGENT_CONFIG["domain"],
        "specialty": AGENT_CONFIG["specialty"],
        "activity_levels": list(ACTIVITY_LEVELS.keys()),
        "formulas_available": list(METABOLIC_FORMULAS.keys()),
        "goals_supported": list(GOAL_ADJUSTMENTS.keys()),
        "capabilities": AGENT_CONFIG["capabilities"],
    }


# =============================================================================
# ADK Entry Point
# =============================================================================

root_agent = metabol
