"""GENESIS_X - Orquestador principal del sistema NGX.

Este módulo define el agente orquestador usando Google ADK.
GENESIS_X coordina 12 agentes especializados para ayudar a usuarios
de 30-60 años a optimizar performance y longevidad.

Capabilities:
- Intent classification
- Multi-agent routing
- Consensus building
- Session management
- Handoff to human (plan HYBRID)

SLOs (de ADR-001):
- Latency p95: ≤6.0s
- Availability: ≥99.5%
- Cost per invoke: ≤$0.05
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from google.adk import Agent

from agents.genesis_x.prompts import GENESIS_X_SYSTEM_PROMPT
from agents.genesis_x.tools import (
    ALL_TOOLS,
)

logger = logging.getLogger(__name__)

# =============================================================================
# Agent Configuration
# =============================================================================

# Configuración basada en PRD Sección 4.1
AGENT_CONFIG = {
    "agent_id": "genesis-x",
    "display_name": "GENESIS_X",
    "role": "orchestrator",
    "model": "gemini-2.5-pro",  # gemini-3-pro cuando esté disponible
    "thinking_level": "high",
    "capabilities": [
        "intent_classification",
        "multi_agent_routing",
        "consensus_building",
        "session_management",
        "handoff_to_human",
        "planning",
    ],
    "personality": {
        "tone": "Profesional pero cercano",
        "style": "Directo, basado en evidencia",
        "language": "Español (México), adaptable",
    },
    "limits": {
        "max_input_tokens": 50000,
        "max_output_tokens": 4000,
        "max_latency_ms": 6000,
        "max_cost_per_invoke": 0.05,
    },
}

# =============================================================================
# Agent Definition
# =============================================================================

# Definición del agente principal usando ADK
genesis_x = Agent(
    name="genesis_x",
    model=AGENT_CONFIG["model"],
    description=(
        "Orquestador principal de GENESIS NGX. "
        "Coordina agentes especializados para optimización de "
        "performance y longevidad en usuarios de 30-60 años."
    ),
    instruction=GENESIS_X_SYSTEM_PROMPT,
    tools=ALL_TOOLS,
    output_key="genesis_x_response",
)

# =============================================================================
# Agent Card (A2A Protocol)
# =============================================================================

# Agent Card compatible con A2A v0.3 y el schema definido en docs/
AGENT_CARD = {
    "name": AGENT_CONFIG["display_name"],
    "description": genesis_x.description,
    "version": "1.0.0",
    "protocol": "a2a/0.3",
    "capabilities": AGENT_CONFIG["capabilities"],
    "methods": [
        {
            "name": "orchestrate",
            "description": "Procesa un mensaje del usuario, coordina agentes y responde",
            "params": {
                "user_id": {"type": "string", "required": True},
                "message": {"type": "string", "required": True},
                "conversation_id": {"type": "string", "required": False},
                "context": {"type": "object", "required": False},
            },
            "returns": {
                "response": {"type": "string"},
                "agents_consulted": {"type": "array"},
                "tokens_used": {"type": "integer"},
                "cost_usd": {"type": "number"},
            },
        },
        {
            "name": "classify_intent",
            "description": "Clasifica el intent de un mensaje sin generar respuesta",
            "params": {
                "message": {"type": "string", "required": True},
                "user_context": {"type": "object", "required": False},
            },
            "returns": {
                "primary_intent": {"type": "string"},
                "secondary_intents": {"type": "array"},
                "confidence": {"type": "number"},
                "agents_needed": {"type": "array"},
            },
        },
        {
            "name": "get_status",
            "description": "Obtiene el estado del orquestador",
            "params": {},
            "returns": {
                "status": {"type": "string"},
                "version": {"type": "string"},
                "available_agents": {"type": "array"},
            },
        },
    ],
    "limits": {
        "max_input_tokens": AGENT_CONFIG["limits"]["max_input_tokens"],
        "max_output_tokens": AGENT_CONFIG["limits"]["max_output_tokens"],
        "max_latency_ms": AGENT_CONFIG["limits"]["max_latency_ms"],
        "max_cost_per_invoke": AGENT_CONFIG["limits"]["max_cost_per_invoke"],
    },
    "privacy": {
        "pii": False,
        "phi": False,
        "data_retention_days": 90,
    },
    "auth": {
        "method": "oidc",
        "audience": "genesis-x-orchestrator",
    },
}

# =============================================================================
# Helper Functions for Direct Invocation
# =============================================================================


async def orchestrate(
    user_id: str,
    message: str,
    conversation_id: Optional[str] = None,
    context: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Procesa un mensaje del usuario a través del orquestador.

    Este es el punto de entrada principal para interactuar con GENESIS_X.
    Coordina el flujo completo: clasificación → invocación → consenso → respuesta.

    Args:
        user_id: ID del usuario (UUID string)
        message: Mensaje del usuario
        conversation_id: ID de conversación existente (opcional)
        context: Contexto adicional (opcional)

    Returns:
        dict con response, agents_consulted, tokens_used, cost_usd

    Example:
        >>> result = await orchestrate(
        ...     user_id="123e4567-e89b-12d3-a456-426614174000",
        ...     message="¿Cómo puedo mejorar mi fuerza?"
        ... )
        >>> print(result["response"])
    """
    from agents.genesis_x.tools import (
        classify_intent,
        get_user_context,
        invoke_specialist,
        build_consensus,
        persist_to_supabase,
    )

    logger.info(f"Orchestrating for user {user_id}: {message[:50]}...")

    # 1. Obtener contexto del usuario si no se provee
    if not context:
        context = get_user_context(user_id)
        if context.get("status") == "error":
            logger.warning(f"No se pudo obtener contexto para {user_id}")
            context = {}

    # 2. Clasificar intent
    classification = classify_intent(message, context)

    # Loggear clasificación
    persist_to_supabase(
        user_id=user_id,
        event_type="intent_classified",
        payload={
            "message_preview": message[:100],
            "classification": classification,
        },
    )

    # 3. Manejar casos especiales
    if classification.get("is_emergency"):
        return {
            "response": (
                "Detecté que podrías estar experimentando una emergencia médica. "
                "Por favor, contacta a servicios de emergencia (911) o acude "
                "al hospital más cercano inmediatamente. Tu salud es lo primero."
            ),
            "agents_consulted": [],
            "tokens_used": 0,
            "cost_usd": 0.0,
            "classification": classification,
        }

    if classification.get("requires_human_handoff"):
        return {
            "response": (
                "Tu solicitud requiere atención personalizada. "
                "Te conectaré con un coach humano que podrá ayudarte mejor."
            ),
            "agents_consulted": [],
            "tokens_used": 0,
            "cost_usd": 0.0,
            "classification": classification,
            "handoff_required": True,
        }

    # 4. Si es chat general, responder directamente
    if classification["primary_intent"] == "general_chat":
        return {
            "response": (
                "¡Hola! Soy GENESIS_X, tu asistente de performance y longevidad. "
                "Puedo ayudarte con entrenamiento, nutrición, recuperación, "
                "hábitos y más. ¿En qué te puedo ayudar hoy?"
            ),
            "agents_consulted": [],
            "tokens_used": 0,
            "cost_usd": 0.0,
            "classification": classification,
        }

    # 5. Invocar agentes especializados
    agent_responses = []
    total_cost = 0.0
    total_tokens = 0

    agents_needed = classification.get("agents_needed", [])
    budget_per_agent = 0.01  # $0.01 por agente

    for agent_id in agents_needed:
        response = await invoke_specialist(
            agent_id=agent_id,
            method="respond",
            params={
                "message": message,
                "user_context": context,
                "intent": classification["primary_intent"],
            },
            user_id=user_id,
            budget_usd=budget_per_agent,
        )
        agent_responses.append(response)
        total_cost += response.get("cost_usd", 0)
        total_tokens += response.get("tokens_used", 0)

    # 6. Construir consenso (async con Gemini Pro)
    consensus = await build_consensus(
        agent_responses=agent_responses,
        user_message=message,
        user_context=context,
    )

    # 7. Loggear resultado
    persist_to_supabase(
        user_id=user_id,
        event_type="orchestration_complete",
        payload={
            "agents_consulted": [r["agent_id"] for r in agent_responses],
            "total_cost_usd": total_cost,
            "total_tokens": total_tokens,
            "consensus_confidence": consensus.get("confidence", 0),
        },
    )

    return {
        "response": consensus["unified_response"],
        "agents_consulted": consensus["sources"],
        "tokens_used": total_tokens,
        "cost_usd": total_cost,
        "classification": classification,
        "follow_up": consensus.get("follow_up_suggested"),
    }


def get_status() -> dict[str, Any]:
    """Obtiene el estado actual del orquestador.

    Returns:
        dict con status, version, available_agents
    """
    from agents.genesis_x.tools import AGENT_MODELS

    return {
        "status": "healthy",
        "version": AGENT_CARD["version"],
        "agent_id": AGENT_CONFIG["agent_id"],
        "model": AGENT_CONFIG["model"],
        "available_agents": list(AGENT_MODELS.keys()),
        "capabilities": AGENT_CONFIG["capabilities"],
    }


# =============================================================================
# ADK Entry Point
# =============================================================================

# El agente root para ADK (requerido para `adk web` y `adk deploy`)
root_agent = genesis_x
