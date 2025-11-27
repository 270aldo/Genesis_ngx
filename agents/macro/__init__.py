"""MACRO - Agente especializado en Macronutrientes.

Uso:
    from agents.macro import macro, calculate_user_macros, AGENT_CARD

    # Con ADK CLI
    $ adk web agents/macro
"""

from __future__ import annotations

from agents.macro.agent import (
    macro,
    root_agent,
    calculate_user_macros,
    create_meal_plan,
    get_status,
    AGENT_CARD,
    AGENT_CONFIG,
)
from agents.macro.prompts import (
    MACRO_SYSTEM_PROMPT,
    MACRO_CALCULATION_PROMPT,
    PROTEIN_DISTRIBUTION_PROMPT,
    CARB_CYCLING_PROMPT,
)
from agents.macro.tools import (
    calculate_macros,
    distribute_protein,
    plan_carb_cycling,
    optimize_fat_intake,
    compose_meal,
    ALL_TOOLS,
    MACRO_RATIOS,
    PROTEIN_TARGETS,
    CARB_CYCLING_PATTERNS,
    FAT_DISTRIBUTION,
    MEAL_TEMPLATES,
    PROTEIN_SOURCES,
    NutritionGoal,
    ActivityType,
    CarbCycleDay,
    FatSource,
)

__all__ = [
    # Agent
    "macro",
    "root_agent",
    "calculate_user_macros",
    "create_meal_plan",
    "get_status",
    "AGENT_CARD",
    "AGENT_CONFIG",
    # Prompts
    "MACRO_SYSTEM_PROMPT",
    "MACRO_CALCULATION_PROMPT",
    "PROTEIN_DISTRIBUTION_PROMPT",
    "CARB_CYCLING_PROMPT",
    # Tools
    "calculate_macros",
    "distribute_protein",
    "plan_carb_cycling",
    "optimize_fat_intake",
    "compose_meal",
    "ALL_TOOLS",
    # Data
    "MACRO_RATIOS",
    "PROTEIN_TARGETS",
    "CARB_CYCLING_PATTERNS",
    "FAT_DISTRIBUTION",
    "MEAL_TEMPLATES",
    "PROTEIN_SOURCES",
    # Types
    "NutritionGoal",
    "ActivityType",
    "CarbCycleDay",
    "FatSource",
]

__version__ = "1.0.0"
