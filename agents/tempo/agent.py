"""TEMPO - Agente especializado en Cardio y Resistencia.

Este modulo define el agente TEMPO usando Google ADK.
TEMPO diseña programas de cardio e intervalos para usuarios de 30-60 años.

Capabilities:
- Heart rate zone training
- HIIT programming
- LISS endurance
- Cardio periodization
- Calorie estimation

SLOs (de PRD Seccion 4.2):
- Latency p95: ≤2.0s
- Cost per invoke: ≤$0.01
"""

from __future__ import annotations

import logging
from typing import Any

from google.adk import Agent

from agents.tempo.prompts import TEMPO_SYSTEM_PROMPT
from agents.tempo.tools import ALL_TOOLS

logger = logging.getLogger(__name__)

# =============================================================================
# Agent Configuration
# =============================================================================

AGENT_CONFIG = {
    "agent_id": "tempo",
    "display_name": "TEMPO",
    "domain": "fitness",
    "specialty": "cardio_endurance",
    "model": "gemini-2.5-flash",
    "thinking_level": "low",
    "capabilities": [
        "heart_rate_zones",
        "hiit_programming",
        "liss_endurance",
        "cardio_periodization",
        "calorie_estimation",
    ],
    "limits": {
        "max_input_tokens": 20000,
        "max_output_tokens": 2000,
        "max_latency_ms": 2000,
        "max_cost_per_invoke": 0.01,
    },
}

# =============================================================================
# Agent Definition
# =============================================================================

tempo = Agent(
    name="tempo",
    model=AGENT_CONFIG["model"],
    description=(
        "Especialista en cardio, resistencia y entrenamiento de intervalos. "
        "Diseña programas HIIT, LISS, Fartlek y calcula zonas de frecuencia "
        "cardiaca para usuarios de 30-60 años."
    ),
    instruction=TEMPO_SYSTEM_PROMPT,
    tools=ALL_TOOLS,
    output_key="tempo_response",
)

# =============================================================================
# Agent Card (A2A Protocol)
# =============================================================================

AGENT_CARD = {
    "name": AGENT_CONFIG["display_name"],
    "description": tempo.description,
    "version": "1.0.0",
    "protocol": "a2a/0.3",
    "domain": AGENT_CONFIG["domain"],
    "specialty": AGENT_CONFIG["specialty"],
    "capabilities": AGENT_CONFIG["capabilities"],
    "methods": [
        {
            "name": "calculate_hr_zones",
            "description": "Calcula zonas de frecuencia cardiaca",
            "params": {
                "age": {"type": "integer", "required": True},
                "resting_hr": {"type": "integer", "required": False},
                "method": {"type": "string", "required": False},
            },
        },
        {
            "name": "generate_session",
            "description": "Genera una sesion de cardio",
            "params": {
                "session_type": {"type": "string", "required": True},
                "duration_minutes": {"type": "integer", "required": False},
                "modality": {"type": "string", "required": False},
            },
        },
        {
            "name": "suggest_cardio_plan",
            "description": "Sugiere un plan de cardio semanal",
            "params": {
                "primary_goal": {"type": "string", "required": True},
                "days_per_week": {"type": "integer", "required": False},
                "experience_level": {"type": "string", "required": False},
            },
        },
        {
            "name": "respond",
            "description": "Responde preguntas generales sobre cardio y resistencia",
            "params": {
                "message": {"type": "string", "required": True},
                "user_context": {"type": "object", "required": False},
            },
        },
    ],
    "limits": AGENT_CONFIG["limits"],
    "privacy": {
        "pii": False,
        "phi": False,
        "data_retention_days": 90,
    },
    "auth": {
        "method": "oidc",
        "audience": "tempo-cardio-agent",
    },
}

# =============================================================================
# Helper Functions
# =============================================================================


def generate_session(
    session_type: str = "hiit_intermediate",
    duration_minutes: int | None = None,
    modality: str | None = None,
    age: int = 35,
) -> dict[str, Any]:
    """Genera una sesion de cardio.

    Args:
        session_type: Tipo de sesion (hiit_beginner, liss_fat_burn, etc.)
        duration_minutes: Duracion personalizada
        modality: Modalidad preferida
        age: Edad para calcular zonas HR

    Returns:
        dict con sesion generada
    """
    from agents.tempo.tools import generate_cardio_session

    return generate_cardio_session(
        session_type=session_type,
        duration_minutes=duration_minutes,
        modality=modality,
        age=age,
    )


def get_status() -> dict[str, Any]:
    """Obtiene el estado actual del agente TEMPO."""
    from agents.tempo.tools import SESSION_TEMPLATES, HR_ZONES

    return {
        "status": "healthy",
        "version": AGENT_CARD["version"],
        "agent_id": AGENT_CONFIG["agent_id"],
        "model": AGENT_CONFIG["model"],
        "domain": AGENT_CONFIG["domain"],
        "specialty": AGENT_CONFIG["specialty"],
        "sessions_available": list(SESSION_TEMPLATES.keys()),
        "hr_zones_available": list(HR_ZONES.keys()),
        "capabilities": AGENT_CONFIG["capabilities"],
    }


# =============================================================================
# ADK Entry Point
# =============================================================================

root_agent = tempo
