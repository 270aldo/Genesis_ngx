"""BLAZE - Agente especializado en Fuerza e Hipertrofia.

Este módulo define el agente BLAZE usando Google ADK.
BLAZE diseña programas de entrenamiento de fuerza optimizados
para usuarios de 30-60 años.

Capabilities:
- Workout generation
- Exercise selection
- Progressive overload
- Periodization
- Form guidance

SLOs (de PRD Sección 4.2):
- Latency p95: ≤2.0s
- Cost per invoke: ≤$0.01
"""

from __future__ import annotations

import logging
from typing import Any

from google.adk import Agent

from agents.blaze.prompts import BLAZE_SYSTEM_PROMPT
from agents.blaze.tools import ALL_TOOLS

logger = logging.getLogger(__name__)

# =============================================================================
# Agent Configuration
# =============================================================================

AGENT_CONFIG = {
    "agent_id": "blaze",
    "display_name": "BLAZE",
    "domain": "fitness",
    "specialty": "strength_hypertrophy",
    "model": "gemini-2.5-flash",
    "thinking_level": "low",
    "capabilities": [
        "workout_generation",
        "exercise_selection",
        "progressive_overload",
        "periodization",
        "form_guidance",
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

blaze = Agent(
    name="blaze",
    model=AGENT_CONFIG["model"],
    description=(
        "Especialista en entrenamiento de fuerza e hipertrofia. "
        "Diseña workouts personalizados, selecciona ejercicios, "
        "y planifica progresión para usuarios de 30-60 años."
    ),
    instruction=BLAZE_SYSTEM_PROMPT,
    tools=ALL_TOOLS,
    output_key="blaze_response",
)

# =============================================================================
# Agent Card (A2A Protocol)
# =============================================================================

AGENT_CARD = {
    "name": AGENT_CONFIG["display_name"],
    "description": blaze.description,
    "version": "1.0.0",
    "protocol": "a2a/0.3",
    "domain": AGENT_CONFIG["domain"],
    "specialty": AGENT_CONFIG["specialty"],
    "capabilities": AGENT_CONFIG["capabilities"],
    "methods": [
        {
            "name": "generate_workout",
            "description": "Genera un workout personalizado",
            "params": {
                "user_id": {"type": "string", "required": True},
                "workout_type": {"type": "string", "required": True},
                "muscle_groups": {"type": "array", "required": True},
                "duration_minutes": {"type": "integer", "required": False},
                "equipment": {"type": "array", "required": False},
                "phase_config": {"type": "object", "required": False},
            },
        },
        {
            "name": "select_exercises",
            "description": "Selecciona ejercicios apropiados para objetivos específicos",
            "params": {
                "muscle_groups": {"type": "array", "required": True},
                "equipment": {"type": "array", "required": True},
                "goal": {"type": "string", "required": True},
                "limitations": {"type": "array", "required": False},
            },
        },
        {
            "name": "calculate_progression",
            "description": "Calcula progresión recomendada basada en rendimiento",
            "params": {
                "exercise": {"type": "string", "required": True},
                "current_weight": {"type": "number", "required": True},
                "current_reps": {"type": "integer", "required": True},
                "rpe": {"type": "integer", "required": True},
            },
        },
        {
            "name": "respond",
            "description": "Responde preguntas generales sobre fuerza e hipertrofia",
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
        "audience": "blaze-fitness-agent",
    },
}

# =============================================================================
# Helper Functions
# =============================================================================


def generate_workout(
    user_id: str,
    workout_type: str,
    muscle_groups: list[str],
    duration_minutes: int = 60,
    equipment: list[str] | None = None,
    phase_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Genera un workout personalizado.

    Args:
        user_id: ID del usuario
        workout_type: Tipo (strength, hypertrophy, mixed)
        muscle_groups: Grupos musculares a trabajar
        duration_minutes: Duración objetivo
        equipment: Equipo disponible
        phase_config: Configuración de la fase actual

    Returns:
        dict con workout generado
    """
    from agents.blaze.tools import (
        get_exercise_database,
    )

    # Valores por defecto
    equipment = equipment or ["barbell", "dumbbell", "cable", "machine"]
    phase_config = phase_config or {
        "volume": "moderate",
        "intensity_range": [70, 80],
        "rep_range": [8, 12],
    }

    # Obtener ejercicios para cada grupo muscular
    workout_exercises = []
    for mg in muscle_groups:
        exercises = get_exercise_database(muscle_group=mg)
        if exercises["count"] > 0:
            # Tomar los primeros 2 ejercicios por grupo
            for ex_id, ex_data in list(exercises["exercises"].items())[:2]:
                workout_exercises.append({
                    "exercise_id": ex_id,
                    "name": ex_data["name_es"],
                    "sets": 3 if workout_type == "strength" else 4,
                    "reps": "3-5" if workout_type == "strength" else "8-12",
                    "rest_seconds": 180 if workout_type == "strength" else 90,
                    "cues": ex_data["cues"],
                })

    return {
        "user_id": user_id,
        "workout_type": workout_type,
        "muscle_groups": muscle_groups,
        "estimated_duration_minutes": duration_minutes,
        "exercises": workout_exercises,
        "warmup": {
            "duration_minutes": 10,
            "components": ["5 min cardio ligero", "Movilidad específica", "Series de activación"],
        },
        "cooldown": {
            "duration_minutes": 5,
            "components": ["Stretching estático", "Respiración"],
        },
        "phase_config": phase_config,
    }


def get_status() -> dict[str, Any]:
    """Obtiene el estado actual del agente BLAZE."""
    from agents.blaze.tools import EXERCISE_DATABASE, SPLIT_TEMPLATES

    return {
        "status": "healthy",
        "version": AGENT_CARD["version"],
        "agent_id": AGENT_CONFIG["agent_id"],
        "model": AGENT_CONFIG["model"],
        "domain": AGENT_CONFIG["domain"],
        "specialty": AGENT_CONFIG["specialty"],
        "exercises_available": len(EXERCISE_DATABASE),
        "splits_available": list(SPLIT_TEMPLATES.keys()),
        "capabilities": AGENT_CONFIG["capabilities"],
    }


# =============================================================================
# ADK Entry Point
# =============================================================================

root_agent = blaze
