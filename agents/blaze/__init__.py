"""BLAZE - Agente especializado en Fuerza e Hipertrofia.

Uso:
    from agents.blaze import blaze, generate_workout, AGENT_CARD

    # Con ADK CLI
    $ adk web agents/blaze
"""

from __future__ import annotations

from agents.blaze.agent import (
    blaze,
    root_agent,
    generate_workout,
    get_status,
    AGENT_CARD,
    AGENT_CONFIG,
)
from agents.blaze.prompts import (
    BLAZE_SYSTEM_PROMPT,
    WORKOUT_GENERATION_PROMPT,
    EXERCISE_SELECTION_PROMPT,
    PROGRESSIVE_OVERLOAD_PROMPT,
)
from agents.blaze.tools import (
    get_exercise_database,
    calculate_one_rep_max,
    calculate_training_volume,
    suggest_progression,
    generate_workout_split,
    ALL_TOOLS,
    EXERCISE_DATABASE,
    SPLIT_TEMPLATES,
    MuscleGroup,
    ExerciseType,
    Equipment,
)

__all__ = [
    # Agent
    "blaze",
    "root_agent",
    "generate_workout",
    "get_status",
    "AGENT_CARD",
    "AGENT_CONFIG",
    # Prompts
    "BLAZE_SYSTEM_PROMPT",
    "WORKOUT_GENERATION_PROMPT",
    "EXERCISE_SELECTION_PROMPT",
    "PROGRESSIVE_OVERLOAD_PROMPT",
    # Tools
    "get_exercise_database",
    "calculate_one_rep_max",
    "calculate_training_volume",
    "suggest_progression",
    "generate_workout_split",
    "ALL_TOOLS",
    # Data
    "EXERCISE_DATABASE",
    "SPLIT_TEMPLATES",
    # Types
    "MuscleGroup",
    "ExerciseType",
    "Equipment",
]

__version__ = "1.0.0"
