"""NOVA - Agente especializado en Suplementación.

NOVA ayuda a usuarios con recomendaciones de suplementos basadas en evidencia,
diseño de stacks, protocolos de timing, verificación de interacciones
y evaluación de nivel de evidencia científica.

Uso con ADK:
    $ adk web agents/nova
    $ adk run agents/nova --prompt "¿Qué suplementos para ganar músculo?"
"""

from __future__ import annotations

from google.adk import Agent

from agents.nova.prompts import NOVA_SYSTEM_PROMPT
from agents.nova.tools import (
    ALL_TOOLS,
    recommend_supplements,
    check_interactions,
    SUPPLEMENTS_DATABASE,
    GOAL_TO_SUPPLEMENTS,
    TIMING_WINDOWS,
)


# =============================================================================
# CONFIGURACIÓN DEL AGENTE
# =============================================================================


AGENT_CONFIG = {
    "domain": "nutrition",
    "specialty": "supplementation",
    "capabilities": [
        "supplement_recommendations",
        "stack_design",
        "timing_protocols",
        "interaction_checking",
        "evidence_grading",
    ],
    "model_tier": "flash",
    "cost_tier": "low",
    "latency_tier": "fast",
}


# =============================================================================
# AGENT CARD (A2A Protocol v0.3)
# =============================================================================


AGENT_CARD = {
    "name": "nova",
    "description": "Especialista en suplementación nutricional basada en evidencia científica",
    "version": "1.0.0",
    "protocol": "a2a/0.3",
    "domain": "nutrition",
    "specialty": "supplementation",
    "capabilities": AGENT_CONFIG["capabilities"],
    "methods": [
        {
            "name": "recommend_supplements",
            "description": "Recomienda suplementos basados en objetivos específicos",
            "parameters": {
                "goal": {"type": "string", "required": True},
                "current_supplements": {"type": "array", "required": False},
                "dietary_restrictions": {"type": "array", "required": False},
                "budget_monthly_usd": {"type": "integer", "required": False, "default": 50},
                "max_supplements": {"type": "integer", "required": False, "default": 5},
            },
            "returns": "Recomendaciones priorizadas con dosis y timing",
        },
        {
            "name": "design_stack",
            "description": "Diseña un stack completo de suplementos personalizado",
            "parameters": {
                "primary_goal": {"type": "string", "required": True},
                "secondary_goals": {"type": "array", "required": False},
                "experience_level": {"type": "string", "required": False, "default": "beginner"},
                "budget_monthly_usd": {"type": "integer", "required": False, "default": 75},
                "preferences": {"type": "object", "required": False},
            },
            "returns": "Stack por niveles con protocolo de introducción",
        },
        {
            "name": "create_timing_protocol",
            "description": "Crea un protocolo de timing y dosificación optimizado",
            "parameters": {
                "supplements": {"type": "array", "required": True},
                "workout_time": {"type": "string", "required": False},
                "wake_time": {"type": "string", "required": False, "default": "07:00"},
                "sleep_time": {"type": "string", "required": False, "default": "23:00"},
            },
            "returns": "Horario diario optimizado con separaciones",
        },
        {
            "name": "check_interactions",
            "description": "Verifica interacciones entre suplementos, medicamentos y condiciones",
            "parameters": {
                "supplements": {"type": "array", "required": True},
                "medications": {"type": "array", "required": False},
                "conditions": {"type": "array", "required": False},
            },
            "returns": "Interacciones por severidad y recomendaciones de seguridad",
        },
        {
            "name": "grade_evidence",
            "description": "Evalúa el nivel de evidencia científica de un suplemento",
            "parameters": {
                "supplement": {"type": "string", "required": True},
                "claim": {"type": "string", "required": False},
            },
            "returns": "Nivel de evidencia (A-D) con detalles de estudios",
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


nova = Agent(
    name="nova",
    model="gemini-2.5-flash",
    description="Especialista en suplementación nutricional basada en evidencia para optimizar salud y rendimiento",
    instruction=NOVA_SYSTEM_PROMPT,
    tools=ALL_TOOLS,
    output_key="nova_response",
)


# Root agent para ADK CLI
root_agent = nova


# =============================================================================
# FUNCIONES HELPER
# =============================================================================


def get_status() -> dict:
    """Retorna el estado del agente y sus capacidades.

    Returns:
        Dict con estado, suplementos disponibles y configuración.
    """
    return {
        "status": "healthy",
        "agent": "nova",
        "version": AGENT_CARD["version"],
        "supplements_in_database": len(SUPPLEMENTS_DATABASE),
        "goals_supported": list(GOAL_TO_SUPPLEMENTS.keys()),
        "timing_windows": list(TIMING_WINDOWS.keys()),
        "capabilities": AGENT_CONFIG["capabilities"],
        "model": "gemini-2.5-flash",
    }


def quick_recommendation(goal: str, budget: int = 50) -> dict:
    """Función helper para recomendación rápida de suplementos.

    Args:
        goal: Objetivo (muscle_gain, sleep, performance, etc.).
        budget: Presupuesto mensual en USD.

    Returns:
        Dict con recomendaciones simplificadas.
    """
    return recommend_supplements(
        goal=goal,
        budget_monthly_usd=budget,
        max_supplements=3,
    )


def quick_safety_check(supplements: list[str]) -> dict:
    """Función helper para verificación rápida de seguridad.

    Args:
        supplements: Lista de suplementos a verificar.

    Returns:
        Dict con resultado de seguridad.
    """
    return check_interactions(supplements=supplements)


__all__ = [
    "nova",
    "root_agent",
    "get_status",
    "quick_recommendation",
    "quick_safety_check",
    "AGENT_CARD",
    "AGENT_CONFIG",
]
