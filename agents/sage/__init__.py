"""SAGE - Agente especializado en Estrategia Nutricional.

Uso:
    from agents.sage import sage, calculate_nutrition_plan, AGENT_CARD

    # Con ADK CLI
    $ adk web agents/sage
"""

from __future__ import annotations

from agents.sage.agent import (
    sage,
    root_agent,
    calculate_nutrition_plan,
    get_status,
    AGENT_CARD,
    AGENT_CONFIG,
)
from agents.sage.prompts import (
    SAGE_SYSTEM_PROMPT,
    MACRO_CALCULATION_PROMPT,
    NUTRITION_PERIODIZATION_PROMPT,
    PLAN_ADJUSTMENT_PROMPT,
)
from agents.sage.tools import (
    calculate_tdee,
    calculate_macros,
    suggest_meal_distribution,
    get_food_suggestions,
    evaluate_progress,
    ALL_TOOLS,
    FOOD_DATABASE,
    ACTIVITY_MULTIPLIERS,
    ActivityLevel,
    NutritionGoal,
    DietPreference,
)

__all__ = [
    # Agent
    "sage",
    "root_agent",
    "calculate_nutrition_plan",
    "get_status",
    "AGENT_CARD",
    "AGENT_CONFIG",
    # Prompts
    "SAGE_SYSTEM_PROMPT",
    "MACRO_CALCULATION_PROMPT",
    "NUTRITION_PERIODIZATION_PROMPT",
    "PLAN_ADJUSTMENT_PROMPT",
    # Tools
    "calculate_tdee",
    "calculate_macros",
    "suggest_meal_distribution",
    "get_food_suggestions",
    "evaluate_progress",
    "ALL_TOOLS",
    # Data
    "FOOD_DATABASE",
    "ACTIVITY_MULTIPLIERS",
    # Types
    "ActivityLevel",
    "NutritionGoal",
    "DietPreference",
]

__version__ = "1.0.0"
