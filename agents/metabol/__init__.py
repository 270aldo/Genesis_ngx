"""METABOL - Agente especializado en Metabolismo.

Uso:
    from agents.metabol import metabol, calculate_user_tdee, AGENT_CARD

    # Con ADK CLI
    $ adk web agents/metabol
"""

from __future__ import annotations

from agents.metabol.agent import (
    metabol,
    root_agent,
    calculate_user_tdee,
    get_status,
    AGENT_CARD,
    AGENT_CONFIG,
)
from agents.metabol.prompts import (
    METABOL_SYSTEM_PROMPT,
    TDEE_CALCULATION_PROMPT,
    METABOLIC_ASSESSMENT_PROMPT,
    NUTRIENT_TIMING_PROMPT,
)
from agents.metabol.tools import (
    calculate_tdee,
    assess_metabolic_rate,
    plan_nutrient_timing,
    detect_metabolic_adaptation,
    assess_insulin_sensitivity,
    ALL_TOOLS,
    ACTIVITY_LEVELS,
    METABOLIC_FORMULAS,
    GOAL_ADJUSTMENTS,
    TIMING_WINDOWS,
    INSULIN_SENSITIVITY_INDICATORS,
    ActivityLevel,
    MetabolicGoal,
    BMRFormula,
    MealTiming,
)

__all__ = [
    # Agent
    "metabol",
    "root_agent",
    "calculate_user_tdee",
    "get_status",
    "AGENT_CARD",
    "AGENT_CONFIG",
    # Prompts
    "METABOL_SYSTEM_PROMPT",
    "TDEE_CALCULATION_PROMPT",
    "METABOLIC_ASSESSMENT_PROMPT",
    "NUTRIENT_TIMING_PROMPT",
    # Tools
    "calculate_tdee",
    "assess_metabolic_rate",
    "plan_nutrient_timing",
    "detect_metabolic_adaptation",
    "assess_insulin_sensitivity",
    "ALL_TOOLS",
    # Data
    "ACTIVITY_LEVELS",
    "METABOLIC_FORMULAS",
    "GOAL_ADJUSTMENTS",
    "TIMING_WINDOWS",
    "INSULIN_SENSITIVITY_INDICATORS",
    # Types
    "ActivityLevel",
    "MetabolicGoal",
    "BMRFormula",
    "MealTiming",
]

__version__ = "1.0.0"
