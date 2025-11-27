"""WAVE - Agente especializado en Recuperacion y Descanso.

Este modulo define el agente WAVE usando Google ADK.
WAVE diseña protocolos de recuperacion para usuarios de 30-60 años.

Capabilities:
- Recovery assessment
- Sleep optimization
- Deload programming
- Fatigue management
- Recovery protocols

SLOs (de PRD Seccion 4.2):
- Latency p95: ≤2.0s
- Cost per invoke: ≤$0.01
"""

from __future__ import annotations

import logging
from typing import Any

from google.adk import Agent

from agents.wave.prompts import WAVE_SYSTEM_PROMPT
from agents.wave.tools import ALL_TOOLS

logger = logging.getLogger(__name__)

# =============================================================================
# Agent Configuration
# =============================================================================

AGENT_CONFIG = {
    "agent_id": "wave",
    "display_name": "WAVE",
    "domain": "fitness",
    "specialty": "recovery_rest",
    "model": "gemini-2.5-flash",
    "thinking_level": "low",
    "capabilities": [
        "recovery_assessment",
        "sleep_optimization",
        "deload_programming",
        "fatigue_management",
        "recovery_protocols",
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

wave = Agent(
    name="wave",
    model=AGENT_CONFIG["model"],
    description=(
        "Especialista en recuperacion, descanso y regeneracion. "
        "Evalua fatiga, optimiza sueno, diseña protocolos de deload "
        "y tecnicas de recuperacion para usuarios de 30-60 años."
    ),
    instruction=WAVE_SYSTEM_PROMPT,
    tools=ALL_TOOLS,
    output_key="wave_response",
)

# =============================================================================
# Agent Card (A2A Protocol)
# =============================================================================

AGENT_CARD = {
    "name": AGENT_CONFIG["display_name"],
    "description": wave.description,
    "version": "1.0.0",
    "protocol": "a2a/0.3",
    "domain": AGENT_CONFIG["domain"],
    "specialty": AGENT_CONFIG["specialty"],
    "capabilities": AGENT_CONFIG["capabilities"],
    "methods": [
        {
            "name": "assess_recovery",
            "description": "Evalua el estado de recuperacion del usuario",
            "params": {
                "sleep_quality": {"type": "integer", "required": True},
                "sleep_hours": {"type": "number", "required": True},
                "muscle_soreness": {"type": "integer", "required": True},
                "energy_level": {"type": "integer", "required": True},
                "motivation": {"type": "integer", "required": True},
            },
        },
        {
            "name": "generate_protocol",
            "description": "Genera un protocolo de recuperacion",
            "params": {
                "fatigue_level": {"type": "string", "required": True},
                "training_type": {"type": "string", "required": False},
                "time_available": {"type": "integer", "required": False},
            },
        },
        {
            "name": "recommend_deload",
            "description": "Recomienda protocolo de deload si es necesario",
            "params": {
                "weeks_training": {"type": "integer", "required": True},
                "current_fatigue": {"type": "string", "required": True},
            },
        },
        {
            "name": "respond",
            "description": "Responde preguntas generales sobre recuperacion",
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
        "audience": "wave-recovery-agent",
    },
}

# =============================================================================
# Helper Functions
# =============================================================================


def generate_protocol(
    fatigue_level: str = "moderate",
    training_type: str = "strength",
    time_available_minutes: int = 30,
) -> dict[str, Any]:
    """Genera un protocolo de recuperacion.

    Args:
        fatigue_level: Nivel de fatiga
        training_type: Tipo de entrenamiento reciente
        time_available_minutes: Tiempo disponible

    Returns:
        dict con protocolo generado
    """
    from agents.wave.tools import generate_recovery_protocol

    return generate_recovery_protocol(
        fatigue_level=fatigue_level,
        training_type=training_type,
        time_available_minutes=time_available_minutes,
    )


def get_status() -> dict[str, Any]:
    """Obtiene el estado actual del agente WAVE."""
    from agents.wave.tools import RECOVERY_TECHNIQUES, DELOAD_PROTOCOLS

    return {
        "status": "healthy",
        "version": AGENT_CARD["version"],
        "agent_id": AGENT_CONFIG["agent_id"],
        "model": AGENT_CONFIG["model"],
        "domain": AGENT_CONFIG["domain"],
        "specialty": AGENT_CONFIG["specialty"],
        "techniques_available": list(RECOVERY_TECHNIQUES.keys()),
        "deload_protocols_available": list(DELOAD_PROTOCOLS.keys()),
        "capabilities": AGENT_CONFIG["capabilities"],
    }


# =============================================================================
# ADK Entry Point
# =============================================================================

root_agent = wave
