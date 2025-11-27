"""ATLAS - Agente especializado en Movilidad y Flexibilidad.

Uso:
    from agents.atlas import atlas, generate_routine, AGENT_CARD

    # Con ADK CLI
    $ adk web agents/atlas
"""

from __future__ import annotations

from agents.atlas.agent import (
    atlas,
    root_agent,
    generate_routine,
    get_status,
    AGENT_CARD,
    AGENT_CONFIG,
)
from agents.atlas.prompts import (
    ATLAS_SYSTEM_PROMPT,
    MOBILITY_ASSESSMENT_PROMPT,
    ROUTINE_GENERATION_PROMPT,
)
from agents.atlas.tools import (
    get_mobility_exercises,
    assess_mobility,
    generate_mobility_routine,
    suggest_mobility_for_workout,
    ALL_TOOLS,
    MOBILITY_EXERCISES,
    ROUTINE_TEMPLATES,
    MobilityAssessment,
)

__all__ = [
    # Agent
    "atlas",
    "root_agent",
    "generate_routine",
    "get_status",
    "AGENT_CARD",
    "AGENT_CONFIG",
    # Prompts
    "ATLAS_SYSTEM_PROMPT",
    "MOBILITY_ASSESSMENT_PROMPT",
    "ROUTINE_GENERATION_PROMPT",
    # Tools
    "get_mobility_exercises",
    "assess_mobility",
    "generate_mobility_routine",
    "suggest_mobility_for_workout",
    "ALL_TOOLS",
    # Data
    "MOBILITY_EXERCISES",
    "ROUTINE_TEMPLATES",
    # Types
    "MobilityAssessment",
]

__version__ = "1.0.0"
