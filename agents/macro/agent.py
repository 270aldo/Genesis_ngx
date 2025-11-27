"""MACRO - Agente especializado en Macronutrientes.

MACRO calcula objetivos de macronutrientes, distribuye proteína,
planifica ciclado de carbohidratos y ayuda a componer comidas.

Uso con ADK:
    $ adk web agents/macro
    $ adk run agents/macro --prompt "Calcula mis macros para 2000 calorías"
"""

from __future__ import annotations

from google.adk import Agent

from agents.macro.prompts import MACRO_SYSTEM_PROMPT
from agents.macro.tools import (
    ALL_TOOLS,
    calculate_macros,
    distribute_protein,
    compose_meal,
    MACRO_RATIOS,
    PROTEIN_TARGETS,
    CARB_CYCLING_PATTERNS,
)


# =============================================================================
# CONFIGURACIÓN DEL AGENTE
# =============================================================================


AGENT_CONFIG = {
    "domain": "nutrition",
    "specialty": "macronutrients",
    "capabilities": [
        "macro_calculation",
        "protein_distribution",
        "carb_cycling",
        "fat_optimization",
        "meal_composition",
    ],
    "model_tier": "flash",
    "cost_tier": "low",
    "latency_tier": "fast",
}


# =============================================================================
# AGENT CARD (A2A Protocol v0.3)
# =============================================================================


AGENT_CARD = {
    "name": "macro",
    "description": "Especialista en macronutrientes para calcular objetivos, distribuir proteína y planificar ciclado de carbohidratos",
    "version": "1.0.0",
    "protocol": "a2a/0.3",
    "domain": "nutrition",
    "specialty": "macronutrients",
    "capabilities": AGENT_CONFIG["capabilities"],
    "methods": [
        {
            "name": "calculate_macros",
            "description": "Calcula macronutrientes diarios según objetivo y calorías",
            "parameters": {
                "daily_calories": {"type": "integer", "required": True},
                "goal": {"type": "string", "required": False, "default": "maintenance"},
                "approach": {"type": "string", "required": False, "default": "standard"},
                "weight_kg": {"type": "number", "required": False},
                "activity_type": {"type": "string", "required": False},
                "custom_protein_g": {"type": "number", "required": False},
            },
            "returns": "Macros calculados con gramos, calorías y porcentajes",
        },
        {
            "name": "distribute_protein",
            "description": "Distribuye proteína diaria entre comidas de forma óptima",
            "parameters": {
                "daily_protein_g": {"type": "number", "required": True},
                "meals_per_day": {"type": "integer", "required": False, "default": 4},
                "training_time": {"type": "string", "required": False},
                "weight_kg": {"type": "number", "required": False},
                "goal": {"type": "string", "required": False},
            },
            "returns": "Distribución de proteína por comida con recomendaciones",
        },
        {
            "name": "plan_carb_cycling",
            "description": "Planifica ciclado de carbohidratos semanal",
            "parameters": {
                "base_carbs_g": {"type": "number", "required": True},
                "training_days": {"type": "array", "required": True},
                "pattern": {"type": "string", "required": False, "default": "training_based"},
                "goal": {"type": "string", "required": False, "default": "fat_loss"},
                "daily_calories": {"type": "integer", "required": False},
            },
            "returns": "Plan semanal de carbohidratos con días altos/bajos",
        },
        {
            "name": "optimize_fat_intake",
            "description": "Optimiza distribución de tipos de grasas",
            "parameters": {
                "daily_fat_g": {"type": "number", "required": True},
                "current_omega3_g": {"type": "number", "required": False, "default": 0},
                "has_health_conditions": {"type": "boolean", "required": False},
                "dietary_restrictions": {"type": "array", "required": False},
            },
            "returns": "Distribución óptima de grasas con fuentes recomendadas",
        },
        {
            "name": "compose_meal",
            "description": "Compone una comida que cumpla objetivos de macros",
            "parameters": {
                "target_calories": {"type": "integer", "required": True},
                "target_protein_g": {"type": "number", "required": False},
                "meal_type": {"type": "string", "required": False, "default": "balanced"},
                "available_foods": {"type": "array", "required": False},
                "dietary_restrictions": {"type": "array", "required": False},
            },
            "returns": "Composición de comida con alimentos sugeridos",
        },
    ],
    "limits": {
        "max_input_tokens": 4096,
        "max_output_tokens": 2048,
        "max_latency_ms": 2000,
        "max_cost_per_invoke": 0.01,
    },
    "privacy": {
        "pii": False,
        "phi": False,
        "data_retention_days": 0,
    },
    "auth": {
        "method": "bearer",
        "audience": "genesis-ngx",
    },
}


# =============================================================================
# DEFINICIÓN DEL AGENTE
# =============================================================================


macro = Agent(
    name="macro",
    model="gemini-2.5-flash",
    description="Especialista en macronutrientes: cálculo, distribución de proteína, ciclado de carbohidratos y composición de comidas",
    instruction=MACRO_SYSTEM_PROMPT,
    tools=ALL_TOOLS,
    output_key="macro_response",
)


# Root agent para ADK CLI
root_agent = macro


# =============================================================================
# FUNCIONES HELPER
# =============================================================================


def get_status() -> dict:
    """Retorna el estado del agente y sus capacidades.

    Returns:
        Dict con estado, goals soportados y configuración.
    """
    return {
        "status": "healthy",
        "agent": "macro",
        "version": AGENT_CARD["version"],
        "goals_supported": list(MACRO_RATIOS.keys()),
        "activity_types": list(PROTEIN_TARGETS.keys()),
        "carb_cycling_patterns": list(CARB_CYCLING_PATTERNS.keys()),
        "capabilities": AGENT_CONFIG["capabilities"],
        "model": "gemini-2.5-flash",
    }


def calculate_user_macros(
    daily_calories: int,
    weight_kg: float | None = None,
    goal: str = "maintenance",
    activity_type: str = "moderate",
) -> dict:
    """Función helper para calcular macros de un usuario.

    Simplifica la interfaz de calculate_macros para uso directo.

    Args:
        daily_calories: Calorías totales diarias.
        weight_kg: Peso en kg (para cálculo de proteína por kg).
        goal: Objetivo nutricional.
        activity_type: Tipo de actividad física.

    Returns:
        Dict con macros calculados.
    """
    return calculate_macros(
        daily_calories=daily_calories,
        goal=goal,
        weight_kg=weight_kg,
        activity_type=activity_type,
    )


def create_meal_plan(
    daily_calories: int,
    meals_per_day: int = 4,
    goal: str = "maintenance",
) -> dict:
    """Crea un plan de comidas básico con distribución de macros.

    Args:
        daily_calories: Calorías totales diarias.
        meals_per_day: Número de comidas.
        goal: Objetivo nutricional.

    Returns:
        Dict con plan de comidas.
    """
    # Calcular macros totales
    macros = calculate_macros(daily_calories=daily_calories, goal=goal)

    if macros["status"] != "calculated":
        return macros

    # Distribuir proteína
    protein_dist = distribute_protein(
        daily_protein_g=macros["macros"]["protein"]["grams"],
        meals_per_day=meals_per_day,
        goal=goal,
    )

    # Calcular calorías por comida
    cals_per_meal = round(daily_calories / meals_per_day)

    meals = []
    for i, meal in enumerate(protein_dist.get("distribution", [])):
        meal_data = compose_meal(
            target_calories=cals_per_meal,
            target_protein_g=meal["protein_g"],
            meal_type="balanced",
        )
        meals.append({
            "meal_number": i + 1,
            "name": meal["name"],
            "calories": cals_per_meal,
            "protein_g": meal["protein_g"],
            "suggestions": meal_data.get("suggested_foods", {}),
        })

    return {
        "status": "created",
        "daily_totals": macros["macros"],
        "meals_per_day": meals_per_day,
        "meal_plan": meals,
        "goal": goal,
    }


__all__ = [
    "macro",
    "root_agent",
    "get_status",
    "calculate_user_macros",
    "create_meal_plan",
    "AGENT_CARD",
    "AGENT_CONFIG",
]
