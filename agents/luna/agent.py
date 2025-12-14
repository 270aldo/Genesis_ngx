"""LUNA - Agente especializado en Salud Femenina.

LUNA ayuda a mujeres a adaptar su entrenamiento y nutrición a su ciclo
menstrual, entender sus fluctuaciones hormonales y optimizar su bienestar.

Uso con ADK:
    $ adk web agents/luna
    $ adk run agents/luna --prompt "¿Cómo adapto mi entrenamiento al ciclo?"
"""

from __future__ import annotations

from google.adk import Agent

from agents.luna.prompts import LUNA_SYSTEM_PROMPT
from agents.luna.tools import (
    ALL_TOOLS,
    track_cycle,
    get_phase_recommendations,
    CYCLE_PHASES,
    SYMPTOMS_DATABASE,
    TRAINING_BY_PHASE,
)


# =============================================================================
# CONFIGURACIÓN DEL AGENTE
# =============================================================================


AGENT_CONFIG = {
    "domain": "womens_health",
    "specialty": "female_physiology",
    "capabilities": [
        "cycle_tracking",
        "hormonal_considerations",
        "perimenopause_support",
        "phase_optimization",
        "symptom_management",
    ],
    "model_tier": "flash",
    "cost_tier": "low",
    "latency_tier": "fast",
}


# =============================================================================
# AGENT CARD (A2A Protocol v0.3)
# =============================================================================


AGENT_CARD = {
    "name": "luna",
    "description": "Especialista en salud femenina, ciclo menstrual y adaptación hormonal",
    "version": "1.0.0",
    "protocol": "a2a/0.3",
    "domain": "womens_health",
    "specialty": "female_physiology",
    "capabilities": AGENT_CONFIG["capabilities"],
    "methods": [
        {
            "name": "track_cycle",
            "description": "Registra datos del ciclo y calcula fase actual",
            "parameters": {
                "last_period_start": {"type": "string", "required": True, "format": "YYYY-MM-DD"},
                "cycle_length": {"type": "integer", "required": False, "default": 28},
                "period_length": {"type": "integer", "required": False, "default": 5},
                "contraception": {"type": "string", "required": False, "default": "none"},
                "current_date": {"type": "string", "required": False},
            },
            "returns": "Fase actual, predicciones y ventana fértil",
        },
        {
            "name": "get_phase_recommendations",
            "description": "Obtiene recomendaciones de entrenamiento y nutrición para una fase",
            "parameters": {
                "phase": {"type": "string", "required": True},
                "goal": {"type": "string", "required": False, "default": "general"},
                "energy_today": {"type": "string", "required": False, "default": "moderate"},
                "has_symptoms": {"type": "array", "required": False},
            },
            "returns": "Recomendaciones de entrenamiento, nutrición y manejo de síntomas",
        },
        {
            "name": "analyze_symptoms",
            "description": "Analiza síntomas y proporciona estrategias de manejo",
            "parameters": {
                "symptoms": {"type": "array", "required": True},
                "cycle_day": {"type": "integer", "required": False},
                "severity": {"type": "string", "required": False, "default": "moderate"},
                "recurring": {"type": "boolean", "required": False, "default": False},
            },
            "returns": "Análisis de síntomas con estrategias y alertas",
        },
        {
            "name": "create_cycle_plan",
            "description": "Crea un plan de entrenamiento y nutrición adaptado al ciclo",
            "parameters": {
                "cycle_length": {"type": "integer", "required": False, "default": 28},
                "goal": {"type": "string", "required": False, "default": "general"},
                "activity_level": {"type": "string", "required": False, "default": "moderate"},
                "known_symptoms": {"type": "array", "required": False},
            },
            "returns": "Plan completo por fase del ciclo",
        },
        {
            "name": "assess_hormonal_health",
            "description": "Evalúa señales de salud hormonal y proporciona orientación",
            "parameters": {
                "cycle_regularity": {"type": "string", "required": False, "default": "regular"},
                "period_flow": {"type": "string", "required": False, "default": "moderate"},
                "energy_pattern": {"type": "string", "required": False, "default": "normal_fluctuation"},
                "has_concerning_symptoms": {"type": "array", "required": False},
                "life_stage": {"type": "string", "required": False, "default": "reproductive"},
                "recent_changes": {"type": "string", "required": False},
            },
            "returns": "Evaluación de salud hormonal con recomendaciones",
        },
    ],
    "limits": {
        "max_input_tokens": 4096,
        "max_output_tokens": 2048,
        "max_latency_ms": 2000,
        "max_cost_per_invoke": 0.01,
    },
    "privacy": {
        "pii": False,
        "phi": False,
        "data_retention_days": 0,
    },
    "auth": {
        "method": "bearer",
        "audience": "genesis-ngx",
    },
}


# =============================================================================
# DEFINICIÓN DEL AGENTE
# =============================================================================


luna = Agent(
    name="luna",
    model="gemini-2.5-flash",
    description="Especialista en salud femenina, ciclo menstrual y adaptación hormonal para optimizar entrenamiento y nutrición",
    instruction=LUNA_SYSTEM_PROMPT,
    tools=ALL_TOOLS,
    output_key="luna_response",
)


# Root agent para ADK CLI
root_agent = luna


# =============================================================================
# FUNCIONES HELPER
# =============================================================================


def get_status() -> dict:
    """Retorna el estado del agente y sus capacidades.

    Returns:
        Dict con estado, fases soportadas y configuración.
    """
    return {
        "status": "healthy",
        "agent": "luna",
        "version": AGENT_CARD["version"],
        "phases_supported": list(CYCLE_PHASES.keys()),
        "symptoms_tracked": list(SYMPTOMS_DATABASE.keys()),
        "training_phases": list(TRAINING_BY_PHASE.keys()),
        "capabilities": AGENT_CONFIG["capabilities"],
        "model": "gemini-2.5-flash",
    }


def quick_phase_check(last_period: str, cycle_length: int = 28) -> dict:
    """Función helper para verificación rápida de fase.

    Args:
        last_period: Fecha del último periodo (YYYY-MM-DD).
        cycle_length: Duración del ciclo.

    Returns:
        Dict con fase actual simplificada.
    """
    return track_cycle(
        last_period_start=last_period,
        cycle_length=cycle_length,
    )


def quick_recommendations(phase: str) -> dict:
    """Función helper para recomendaciones rápidas por fase.

    Args:
        phase: Fase del ciclo.

    Returns:
        Dict con recomendaciones básicas.
    """
    return get_phase_recommendations(phase=phase)


__all__ = [
    "luna",
    "root_agent",
    "get_status",
    "quick_phase_check",
    "quick_recommendations",
    "AGENT_CARD",
    "AGENT_CONFIG",
]
