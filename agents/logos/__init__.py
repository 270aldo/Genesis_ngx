"""LOGOS - Especialista en Educación.

LOGOS es el educador del sistema Genesis NGX. Usa el modelo Pro para
razonamiento profundo y adaptación al nivel del usuario.

Uso:
    from agents.logos import logos, explain_concept, AGENT_CARD

    # Con ADK CLI
    $ adk web agents/logos
"""

from __future__ import annotations

from agents.logos.agent import (
    logos,
    root_agent,
    get_status,
    quick_explain,
    quick_debunk,
    quick_quiz,
    AGENT_CARD,
    AGENT_CONFIG,
)
from agents.logos.prompts import (
    LOGOS_SYSTEM_PROMPT,
    CONCEPT_EXPLANATION_PROMPT,
    EVIDENCE_PRESENTATION_PROMPT,
    MYTH_DEBUNKING_PROMPT,
    DEEP_DIVE_PROMPT,
    QUIZ_GENERATION_PROMPT,
)
from agents.logos.tools import (
    explain_concept,
    present_evidence,
    debunk_myth,
    create_deep_dive,
    generate_quiz,
    ALL_TOOLS,
    CONCEPTS_DATABASE,
    EVIDENCE_DATABASE,
    MYTHS_DATABASE,
    QUIZ_TEMPLATES,
    QUIZ_TOPICS,
    LEARNING_LEVELS,
    Domain,
    LearningLevel,
    EvidenceGrade,
    QuestionType,
    Difficulty,
)

__all__ = [
    # Agent
    "logos",
    "root_agent",
    "get_status",
    "quick_explain",
    "quick_debunk",
    "quick_quiz",
    "AGENT_CARD",
    "AGENT_CONFIG",
    # Prompts
    "LOGOS_SYSTEM_PROMPT",
    "CONCEPT_EXPLANATION_PROMPT",
    "EVIDENCE_PRESENTATION_PROMPT",
    "MYTH_DEBUNKING_PROMPT",
    "DEEP_DIVE_PROMPT",
    "QUIZ_GENERATION_PROMPT",
    # Tools
    "explain_concept",
    "present_evidence",
    "debunk_myth",
    "create_deep_dive",
    "generate_quiz",
    "ALL_TOOLS",
    # Data
    "CONCEPTS_DATABASE",
    "EVIDENCE_DATABASE",
    "MYTHS_DATABASE",
    "QUIZ_TEMPLATES",
    "QUIZ_TOPICS",
    "LEARNING_LEVELS",
    # Types
    "Domain",
    "LearningLevel",
    "EvidenceGrade",
    "QuestionType",
    "Difficulty",
]

__version__ = "1.0.0"
