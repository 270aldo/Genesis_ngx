"""SAGE - Agente especializado en Estrategia Nutricional.

Este módulo define el agente SAGE usando Google ADK.
SAGE diseña estrategias nutricionales personalizadas para usuarios
de 30-60 años que buscan optimizar composición corporal y salud.

Capabilities:
- Nutrition planning
- Diet periodization
- Goal alignment
- Preference integration
- Restriction handling

SLOs (de PRD Sección 4.3):
- Latency p95: ≤2.0s
- Cost per invoke: ≤$0.01
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from google.adk import Agent

from agents.sage.prompts import SAGE_SYSTEM_PROMPT
from agents.sage.tools import ALL_TOOLS

logger = logging.getLogger(__name__)

# =============================================================================
# Agent Configuration
# =============================================================================

AGENT_CONFIG = {
    "agent_id": "sage",
    "display_name": "SAGE",
    "domain": "nutrition",
    "specialty": "strategy",
    "model": "gemini-2.5-flash",
    "thinking_level": "low",
    "capabilities": [
        "nutrition_planning",
        "diet_periodization",
        "goal_alignment",
        "preference_integration",
        "restriction_handling",
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

sage = Agent(
    name="sage",
    model=AGENT_CONFIG["model"],
    description=(
        "Estratega nutricional del sistema NGX. "
        "Diseña planes de alimentación personalizados, calcula macros, "
        "y periodiza nutrición según objetivos y fases de entrenamiento."
    ),
    instruction=SAGE_SYSTEM_PROMPT,
    tools=ALL_TOOLS,
    output_key="sage_response",
)

# =============================================================================
# Agent Card (A2A Protocol)
# =============================================================================

AGENT_CARD = {
    "name": AGENT_CONFIG["display_name"],
    "description": sage.description,
    "version": "1.0.0",
    "protocol": "a2a/0.3",
    "domain": AGENT_CONFIG["domain"],
    "specialty": AGENT_CONFIG["specialty"],
    "capabilities": AGENT_CONFIG["capabilities"],
    "methods": [
        {
            "name": "calculate_nutrition_plan",
            "description": "Calcula TDEE y macros para un usuario",
            "params": {
                "user_id": {"type": "string", "required": True},
                "weight_kg": {"type": "number", "required": True},
                "height_cm": {"type": "number", "required": True},
                "age": {"type": "integer", "required": True},
                "sex": {"type": "string", "required": True},
                "activity_level": {"type": "string", "required": True},
                "goal": {"type": "string", "required": True},
            },
        },
        {
            "name": "create_meal_plan",
            "description": "Crea un plan de comidas basado en macros",
            "params": {
                "macros": {"type": "object", "required": True},
                "meals_per_day": {"type": "integer", "required": False},
                "preferences": {"type": "array", "required": False},
                "restrictions": {"type": "array", "required": False},
            },
        },
        {
            "name": "evaluate_progress",
            "description": "Evalúa progreso y sugiere ajustes",
            "params": {
                "starting_weight": {"type": "number", "required": True},
                "current_weight": {"type": "number", "required": True},
                "weeks_elapsed": {"type": "integer", "required": True},
                "goal": {"type": "string", "required": True},
            },
        },
        {
            "name": "respond",
            "description": "Responde preguntas generales sobre nutrición",
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
        "audience": "sage-nutrition-agent",
    },
}

# =============================================================================
# Helper Functions
# =============================================================================


def calculate_nutrition_plan(
    user_id: str,
    weight_kg: float,
    height_cm: float,
    age: int,
    sex: str,
    activity_level: str,
    goal: str,
    body_fat_pct: Optional[float] = None,
    dietary_preference: str = "omnivore",
) -> dict[str, Any]:
    """Calcula un plan nutricional completo para el usuario.

    Args:
        user_id: ID del usuario
        weight_kg: Peso en kg
        height_cm: Altura en cm
        age: Edad
        sex: Sexo ('male' o 'female')
        activity_level: Nivel de actividad
        goal: Objetivo nutricional
        body_fat_pct: Porcentaje de grasa (opcional)
        dietary_preference: Preferencia dietética

    Returns:
        dict con plan nutricional completo
    """
    from agents.sage.tools import (
        calculate_tdee,
        calculate_macros,
        suggest_meal_distribution,
    )

    # Calcular TDEE
    tdee_result = calculate_tdee(
        weight_kg=weight_kg,
        height_cm=height_cm,
        age=age,
        sex=sex,
        activity_level=activity_level,
        body_fat_pct=body_fat_pct,
    )

    # Determinar calorías objetivo según goal
    calorie_ranges = tdee_result["calorie_ranges"]
    if goal == "fat_loss":
        target_calories = calorie_ranges["moderate_deficit"]
    elif goal == "muscle_gain":
        target_calories = calorie_ranges["lean_bulk"]
    elif goal == "aggressive_fat_loss":
        target_calories = calorie_ranges["aggressive_deficit"]
    else:
        target_calories = calorie_ranges["maintenance"]

    # Calcular macros
    macros = calculate_macros(
        target_calories=target_calories,
        weight_kg=weight_kg,
        goal=goal,
    )

    # Distribución de comidas
    meal_distribution = suggest_meal_distribution(
        macros=macros,
        meals_per_day=4,
    )

    return {
        "user_id": user_id,
        "tdee": tdee_result,
        "target_calories": target_calories,
        "macros": macros,
        "meal_distribution": meal_distribution,
        "goal": goal,
        "dietary_preference": dietary_preference,
        "recommendations": [
            f"Proteína: {macros['protein']['grams']}g ({macros['protein']['per_kg']}g/kg)",
            f"Hidratación: {macros['water_liters']}L de agua diarios",
            f"Fibra: {macros['fiber']['grams']}g diarios mínimo",
        ],
    }


def get_status() -> dict[str, Any]:
    """Obtiene el estado actual del agente SAGE."""
    from agents.sage.tools import FOOD_DATABASE, ACTIVITY_MULTIPLIERS

    total_foods = sum(len(foods) for foods in FOOD_DATABASE.values())

    return {
        "status": "healthy",
        "version": AGENT_CARD["version"],
        "agent_id": AGENT_CONFIG["agent_id"],
        "model": AGENT_CONFIG["model"],
        "domain": AGENT_CONFIG["domain"],
        "specialty": AGENT_CONFIG["specialty"],
        "foods_in_database": total_foods,
        "food_categories": list(FOOD_DATABASE.keys()),
        "activity_levels_supported": list(ACTIVITY_MULTIPLIERS.keys()),
        "capabilities": AGENT_CONFIG["capabilities"],
    }


# =============================================================================
# ADK Entry Point
# =============================================================================

root_agent = sage
