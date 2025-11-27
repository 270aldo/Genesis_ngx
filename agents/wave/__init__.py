"""WAVE - Agente especializado en Recuperacion y Descanso.

Uso:
    from agents.wave import wave, generate_protocol, AGENT_CARD

    # Con ADK CLI
    $ adk web agents/wave
"""

from __future__ import annotations

from agents.wave.agent import (
    wave,
    root_agent,
    generate_protocol,
    get_status,
    AGENT_CARD,
    AGENT_CONFIG,
)
from agents.wave.prompts import (
    WAVE_SYSTEM_PROMPT,
    RECOVERY_ASSESSMENT_PROMPT,
    PROTOCOL_GENERATION_PROMPT,
)
from agents.wave.tools import (
    assess_recovery_status,
    generate_recovery_protocol,
    recommend_deload,
    calculate_sleep_needs,
    ALL_TOOLS,
    RECOVERY_TECHNIQUES,
    DELOAD_PROTOCOLS,
    RecoveryType,
    FatigueLevel,
    RecoveryAssessment,
)

__all__ = [
    # Agent
    "wave",
    "root_agent",
    "generate_protocol",
    "get_status",
    "AGENT_CARD",
    "AGENT_CONFIG",
    # Prompts
    "WAVE_SYSTEM_PROMPT",
    "RECOVERY_ASSESSMENT_PROMPT",
    "PROTOCOL_GENERATION_PROMPT",
    # Tools
    "assess_recovery_status",
    "generate_recovery_protocol",
    "recommend_deload",
    "calculate_sleep_needs",
    "ALL_TOOLS",
    # Data
    "RECOVERY_TECHNIQUES",
    "DELOAD_PROTOCOLS",
    # Types
    "RecoveryType",
    "FatigueLevel",
    "RecoveryAssessment",
]

__version__ = "1.0.0"
