"""NEXUS Orchestrator Agent using Google ADK.

Este agente coordina agentes especializados en fitness, nutrición y salud mental
para proporcionar experiencias de bienestar holísticas.
"""

from __future__ import annotations

import uuid
from typing import Any

from google.adk import Agent
from google.adk.tools import FunctionTool

from agents.shared.config import get_settings
from agents.shared.logging_config import get_logger
from agents.shared.supabase_client import get_supabase_client

from .prompt import INTENT_CLASSIFICATION_PROMPT, NEXUS_INSTRUCTION

# Configuración
settings = get_settings()
logger = get_logger(__name__)

# Modelo para NEXUS (orquestador usa Pro para síntesis y resolución de conflictos - ADR-004)
MODEL = "gemini-2.5-pro"


# =============================================================================
# Custom Tools for NEXUS
# =============================================================================

def classify_intent(message: str) -> dict[str, Any]:
    """Clasifica el intent del mensaje del usuario.

    Args:
        message: El mensaje del usuario a clasificar

    Returns:
        Un diccionario con 'intent' y 'confidence'
    """
    # TODO: Implementar clasificación real con Gemini Flash-Lite
    # Por ahora, clasificación simple basada en keywords
    message_lower = message.lower()

    intents = {
        "check_in": ["cómo estoy", "me siento", "hoy", "estado"],
        "plan": ["plan", "programa", "rutina", "planificar"],
        "track": ["trackear", "registrar", "medir", "progreso"],
        "advice": ["consejo", "recomendación", "ayuda", "qué debo"],
        "fitness": ["ejercicio", "entrenar", "gym", "correr", "workout"],
        "nutrition": ["comer", "comida", "dieta", "nutrición", "calorías"],
        "mental_health": ["estrés", "ansiedad", "mindfulness", "meditar", "dormir"],
    }

    for intent, keywords in intents.items():
        if any(keyword in message_lower for keyword in keywords):
            logger.info("intent_classified", intent=intent, confidence=0.85)
            return {
                "intent": intent,
                "confidence": 0.85,
                "suggested_agent": _intent_to_agent(intent)
            }

    return {
        "intent": "general_inquiry",
        "confidence": 0.7,
        "suggested_agent": "nexus"
    }


def _intent_to_agent(intent: str) -> str:
    """Mapea un intent a un agente especializado."""
    intent_map = {
        "check_in": "fitness",
        "plan": "nexus",  # NEXUS maneja planning multi-agente
        "track": "fitness",
        "advice": "nexus",  # Consulta a múltiples agentes
        "fitness": "fitness",
        "nutrition": "nutrition",
        "mental_health": "mental",
        "general_inquiry": "nexus",
    }
    return intent_map.get(intent, "nexus")


def persist_message(
    conversation_id: str,
    content: str,
    agent_type: str = "nexus",
    tokens_used: int | None = None,
    cost_usd: float | None = None,
) -> dict[str, Any]:
    """Persiste un mensaje de agente en Supabase.

    Args:
        conversation_id: UUID de la conversación
        content: Contenido del mensaje
        agent_type: Tipo de agente (nexus, fitness, nutrition, mental)
        tokens_used: Número de tokens utilizados (opcional)
        cost_usd: Costo en USD (opcional)

    Returns:
        Diccionario con 'message_id' del mensaje creado
    """
    try:
        supabase = get_supabase_client()

        # Usar el service client para bypass RLS
        # TODO: Implementar autenticación correcta con JWT de agente
        message_id = supabase.service_client.table("messages").insert({
            "conversation_id": conversation_id,
            "role": "agent",
            "agent_type": agent_type,
            "content": content,
            "tokens_used": tokens_used,
            "cost_usd": cost_usd,
        }).execute()

        logger.info(
            "message_persisted",
            conversation_id=conversation_id,
            message_id=str(message_id),
        )

        return {
            "status": "success",
            "message_id": str(message_id),
        }
    except Exception as exc:
        logger.error("persist_message_failed", error=str(exc))
        return {
            "status": "failed",
            "error": str(exc),
        }


# =============================================================================
# NEXUS Agent Definition (ADK)
# =============================================================================

nexus_agent = Agent(
    name="nexus",
    model=MODEL,
    description=(
        "NEXUS es el orquestador principal que coordina agentes especializados "
        "en fitness, nutrición y salud mental para proporcionar experiencias "
        "de bienestar holísticas y personalizadas."
    ),
    instruction=NEXUS_INSTRUCTION,
    output_key="nexus_response",
    tools=[
        FunctionTool(classify_intent),
        FunctionTool(persist_message),
    ],
    # TODO: Agregar sub_agents cuando estén implementados
    # sub_agents=[
    #     fitness_agent,
    #     nutrition_agent,
    #     mental_health_agent,
    # ],
)

# Root agent requerido por ADK
root_agent = nexus_agent
