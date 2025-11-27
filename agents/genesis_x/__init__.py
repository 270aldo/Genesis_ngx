"""GENESIS_X - Orquestador principal del sistema NGX.

Este módulo expone el agente orquestador y sus componentes principales
para uso con Google ADK y el sistema A2A.

Usage:
    # Para ADK CLI
    $ adk web agents/genesis_x

    # Para importar el agente
    from agents.genesis_x import genesis_x, orchestrate, AGENT_CARD

    # Para usar las tools directamente
    from agents.genesis_x.tools import classify_intent, invoke_specialist
"""

from __future__ import annotations

from agents.genesis_x.agent import (
    genesis_x,
    root_agent,
    orchestrate,
    get_status,
    AGENT_CARD,
    AGENT_CONFIG,
)
from agents.genesis_x.prompts import (
    GENESIS_X_SYSTEM_PROMPT,
    INTENT_CLASSIFICATION_PROMPT,
    CONSENSUS_BUILDING_PROMPT,
)
from agents.genesis_x.tools import (
    classify_intent,
    invoke_specialist,
    build_consensus,
    get_user_context,
    persist_to_supabase,
    ALL_TOOLS,
    INTENT_TO_AGENTS,
    AGENT_MODELS,
    IntentCategory,
    AgentDomain,
)

__all__ = [
    # Agent
    "genesis_x",
    "root_agent",
    "orchestrate",
    "get_status",
    "AGENT_CARD",
    "AGENT_CONFIG",
    # Prompts
    "GENESIS_X_SYSTEM_PROMPT",
    "INTENT_CLASSIFICATION_PROMPT",
    "CONSENSUS_BUILDING_PROMPT",
    # Tools
    "classify_intent",
    "invoke_specialist",
    "build_consensus",
    "get_user_context",
    "persist_to_supabase",
    "ALL_TOOLS",
    # Constants
    "INTENT_TO_AGENTS",
    "AGENT_MODELS",
    "IntentCategory",
    "AgentDomain",
]

__version__ = "1.0.0"
