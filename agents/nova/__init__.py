"""NOVA - Agente especializado en Suplementación.

Uso:
    from agents.nova import nova, recommend_supplements, AGENT_CARD

    # Con ADK CLI
    $ adk web agents/nova
"""

from __future__ import annotations

from agents.nova.agent import (
    nova,
    root_agent,
    quick_recommendation,
    quick_safety_check,
    get_status,
    AGENT_CARD,
    AGENT_CONFIG,
)
from agents.nova.prompts import (
    NOVA_SYSTEM_PROMPT,
    SUPPLEMENT_RECOMMENDATION_PROMPT,
    STACK_DESIGN_PROMPT,
    TIMING_PROTOCOL_PROMPT,
    INTERACTION_CHECK_PROMPT,
    EVIDENCE_GRADING_PROMPT,
)
from agents.nova.tools import (
    recommend_supplements,
    design_stack,
    create_timing_protocol,
    check_interactions,
    grade_evidence,
    ALL_TOOLS,
    SUPPLEMENTS_DATABASE,
    INTERACTIONS_DATABASE,
    GOAL_TO_SUPPLEMENTS,
    TIMING_WINDOWS,
    EvidenceLevel,
    InteractionSeverity,
    SupplementCategory,
    GoalType,
)

__all__ = [
    # Agent
    "nova",
    "root_agent",
    "quick_recommendation",
    "quick_safety_check",
    "get_status",
    "AGENT_CARD",
    "AGENT_CONFIG",
    # Prompts
    "NOVA_SYSTEM_PROMPT",
    "SUPPLEMENT_RECOMMENDATION_PROMPT",
    "STACK_DESIGN_PROMPT",
    "TIMING_PROTOCOL_PROMPT",
    "INTERACTION_CHECK_PROMPT",
    "EVIDENCE_GRADING_PROMPT",
    # Tools
    "recommend_supplements",
    "design_stack",
    "create_timing_protocol",
    "check_interactions",
    "grade_evidence",
    "ALL_TOOLS",
    # Data
    "SUPPLEMENTS_DATABASE",
    "INTERACTIONS_DATABASE",
    "GOAL_TO_SUPPLEMENTS",
    "TIMING_WINDOWS",
    # Types
    "EvidenceLevel",
    "InteractionSeverity",
    "SupplementCategory",
    "GoalType",
]

__version__ = "1.0.0"
