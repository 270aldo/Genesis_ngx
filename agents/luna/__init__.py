"""LUNA - Agente especializado en Salud Femenina.

Uso:
    from agents.luna import luna, track_cycle, AGENT_CARD

    # Con ADK CLI
    $ adk web agents/luna
"""

from __future__ import annotations

from agents.luna.agent import (
    luna,
    root_agent,
    quick_phase_check,
    quick_recommendations,
    get_status,
    AGENT_CARD,
    AGENT_CONFIG,
)
from agents.luna.prompts import (
    LUNA_SYSTEM_PROMPT,
    CYCLE_TRACKING_PROMPT,
    PHASE_RECOMMENDATIONS_PROMPT,
    SYMPTOM_ANALYSIS_PROMPT,
    CYCLE_PLAN_PROMPT,
    HORMONAL_HEALTH_PROMPT,
)
from agents.luna.tools import (
    track_cycle,
    get_phase_recommendations,
    analyze_symptoms,
    create_cycle_plan,
    assess_hormonal_health,
    ALL_TOOLS,
    CYCLE_PHASES,
    SYMPTOMS_DATABASE,
    TRAINING_BY_PHASE,
    NUTRITION_BY_PHASE,
    PERIMENOPAUSE_INFO,
    CyclePhase,
    EnergyLevel,
    ContraceptionType,
    LifeStage,
)

__all__ = [
    # Agent
    "luna",
    "root_agent",
    "quick_phase_check",
    "quick_recommendations",
    "get_status",
    "AGENT_CARD",
    "AGENT_CONFIG",
    # Prompts
    "LUNA_SYSTEM_PROMPT",
    "CYCLE_TRACKING_PROMPT",
    "PHASE_RECOMMENDATIONS_PROMPT",
    "SYMPTOM_ANALYSIS_PROMPT",
    "CYCLE_PLAN_PROMPT",
    "HORMONAL_HEALTH_PROMPT",
    # Tools
    "track_cycle",
    "get_phase_recommendations",
    "analyze_symptoms",
    "create_cycle_plan",
    "assess_hormonal_health",
    "ALL_TOOLS",
    # Data
    "CYCLE_PHASES",
    "SYMPTOMS_DATABASE",
    "TRAINING_BY_PHASE",
    "NUTRITION_BY_PHASE",
    "PERIMENOPAUSE_INFO",
    # Types
    "CyclePhase",
    "EnergyLevel",
    "ContraceptionType",
    "LifeStage",
]

__version__ = "1.0.0"
