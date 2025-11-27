"""ATLAS - Agente especializado en Movilidad y Flexibilidad.

Este modulo define el agente ATLAS usando Google ADK.
ATLAS disenha rutinas de movilidad y flexibilidad para usuarios de 30-60 años.

Capabilities:
- Mobility assessment
- Flexibility routines
- Movement patterns
- Injury prevention
- Workout mobility complement

SLOs (de PRD Seccion 4.2):
- Latency p95: ≤2.0s
- Cost per invoke: ≤$0.01
"""

from __future__ import annotations

import logging
from typing import Any

from google.adk import Agent

from agents.atlas.prompts import ATLAS_SYSTEM_PROMPT
from agents.atlas.tools import ALL_TOOLS

logger = logging.getLogger(__name__)

# =============================================================================
# Agent Configuration
# =============================================================================

AGENT_CONFIG = {
    "agent_id": "atlas",
    "display_name": "ATLAS",
    "domain": "fitness",
    "specialty": "mobility_flexibility",
    "model": "gemini-2.5-flash",
    "thinking_level": "low",
    "capabilities": [
        "mobility_assessment",
        "flexibility_routines",
        "movement_patterns",
        "injury_prevention",
        "warmup_cooldown",
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

atlas = Agent(
    name="atlas",
    model=AGENT_CONFIG["model"],
    description=(
        "Especialista en movilidad, flexibilidad y movimiento funcional. "
        "Evalua movilidad articular, diseña rutinas de stretching, "
        "y ayuda a prevenir lesiones para usuarios de 30-60 años."
    ),
    instruction=ATLAS_SYSTEM_PROMPT,
    tools=ALL_TOOLS,
    output_key="atlas_response",
)

# =============================================================================
# Agent Card (A2A Protocol)
# =============================================================================

AGENT_CARD = {
    "name": AGENT_CONFIG["display_name"],
    "description": atlas.description,
    "version": "1.0.0",
    "protocol": "a2a/0.3",
    "domain": AGENT_CONFIG["domain"],
    "specialty": AGENT_CONFIG["specialty"],
    "capabilities": AGENT_CONFIG["capabilities"],
    "methods": [
        {
            "name": "assess_mobility",
            "description": "Evalua la movilidad del usuario",
            "params": {
                "overhead_reach": {"type": "integer", "required": True},
                "deep_squat": {"type": "integer", "required": True},
                "hip_hinge": {"type": "integer", "required": True},
                "thoracic_rotation": {"type": "integer", "required": True},
            },
        },
        {
            "name": "generate_routine",
            "description": "Genera una rutina de movilidad",
            "params": {
                "focus": {"type": "string", "required": True},
                "duration_minutes": {"type": "integer", "required": False},
                "include_warmup": {"type": "boolean", "required": False},
            },
        },
        {
            "name": "suggest_mobility_for_workout",
            "description": "Sugiere movilidad para complementar un workout",
            "params": {
                "workout_type": {"type": "string", "required": True},
                "muscle_groups": {"type": "array", "required": True},
            },
        },
        {
            "name": "respond",
            "description": "Responde preguntas generales sobre movilidad y flexibilidad",
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
        "audience": "atlas-mobility-agent",
    },
}

# =============================================================================
# Helper Functions
# =============================================================================


def generate_routine(
    focus: str = "full_body",
    duration_minutes: int = 15,
    include_warmup: bool = True,
) -> dict[str, Any]:
    """Genera una rutina de movilidad.

    Args:
        focus: Area de enfoque (full_body, hip_focus, shoulder_focus, warmup, desk_worker)
        duration_minutes: Duracion objetivo
        include_warmup: Si incluir calentamiento

    Returns:
        dict con rutina generada
    """
    from agents.atlas.tools import generate_mobility_routine

    return generate_mobility_routine(
        focus=focus,
        duration_minutes=duration_minutes,
        include_warmup=include_warmup,
    )


def get_status() -> dict[str, Any]:
    """Obtiene el estado actual del agente ATLAS."""
    from agents.atlas.tools import MOBILITY_EXERCISES, ROUTINE_TEMPLATES

    return {
        "status": "healthy",
        "version": AGENT_CARD["version"],
        "agent_id": AGENT_CONFIG["agent_id"],
        "model": AGENT_CONFIG["model"],
        "domain": AGENT_CONFIG["domain"],
        "specialty": AGENT_CONFIG["specialty"],
        "exercises_available": len(MOBILITY_EXERCISES),
        "routines_available": list(ROUTINE_TEMPLATES.keys()),
        "capabilities": AGENT_CONFIG["capabilities"],
    }


# =============================================================================
# ADK Entry Point
# =============================================================================

root_agent = atlas
