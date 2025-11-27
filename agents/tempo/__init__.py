"""TEMPO - Agente especializado en Cardio y Resistencia.

Uso:
    from agents.tempo import tempo, generate_session, AGENT_CARD

    # Con ADK CLI
    $ adk web agents/tempo
"""

from __future__ import annotations

from agents.tempo.agent import (
    tempo,
    root_agent,
    generate_session,
    get_status,
    AGENT_CARD,
    AGENT_CONFIG,
)
from agents.tempo.prompts import (
    TEMPO_SYSTEM_PROMPT,
    CARDIO_ASSESSMENT_PROMPT,
    SESSION_GENERATION_PROMPT,
)
from agents.tempo.tools import (
    calculate_heart_rate_zones,
    generate_cardio_session,
    suggest_cardio_for_goals,
    calculate_calories_burned,
    ALL_TOOLS,
    SESSION_TEMPLATES,
    HR_ZONES,
    CardioType,
    CardioModality,
)

__all__ = [
    # Agent
    "tempo",
    "root_agent",
    "generate_session",
    "get_status",
    "AGENT_CARD",
    "AGENT_CONFIG",
    # Prompts
    "TEMPO_SYSTEM_PROMPT",
    "CARDIO_ASSESSMENT_PROMPT",
    "SESSION_GENERATION_PROMPT",
    # Tools
    "calculate_heart_rate_zones",
    "generate_cardio_session",
    "suggest_cardio_for_goals",
    "calculate_calories_burned",
    "ALL_TOOLS",
    # Data
    "SESSION_TEMPLATES",
    "HR_ZONES",
    # Types
    "CardioType",
    "CardioModality",
]

__version__ = "1.0.0"
