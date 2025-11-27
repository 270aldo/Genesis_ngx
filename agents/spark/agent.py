"""SPARK - Agente especializado en Conducta y Hábitos.

SPARK ayuda a formar hábitos sostenibles, identificar barreras,
diseñar sistemas de accountability y aplicar técnicas de cambio conductual.

Uso con ADK:
    $ adk web agents/spark
    $ adk run agents/spark --prompt "Ayúdame a formar el hábito de ejercicio"
"""

from __future__ import annotations

from google.adk import Agent

from agents.spark.prompts import SPARK_SYSTEM_PROMPT
from agents.spark.tools import (
    ALL_TOOLS,
    create_habit_plan,
    identify_barriers,
    design_accountability,
    assess_motivation,
    suggest_behavior_change,
    HABIT_FORMATION_STAGES,
    MOTIVATION_TYPES,
    COMMON_BARRIERS,
    BEHAVIOR_FRAMEWORKS,
    ACCOUNTABILITY_SYSTEMS,
)


# =============================================================================
# CONFIGURACIÓN DEL AGENTE
# =============================================================================


AGENT_CONFIG = {
    "domain": "behavior",
    "specialty": "habits_motivation",
    "capabilities": [
        "habit_formation",
        "motivation_strategies",
        "barrier_identification",
        "accountability_systems",
        "behavior_change_techniques",
    ],
    "model_tier": "flash",
    "cost_tier": "low",
    "latency_tier": "fast",
}


# =============================================================================
# AGENT CARD (A2A Protocol v0.3)
# =============================================================================


AGENT_CARD = {
    "name": "spark",
    "description": "Especialista en formación de hábitos, motivación y técnicas de cambio conductual",
    "version": "1.0.0",
    "protocol": "a2a/0.3",
    "domain": "behavior",
    "specialty": "habits_motivation",
    "capabilities": AGENT_CONFIG["capabilities"],
    "methods": [
        {
            "name": "create_habit_plan",
            "description": "Crea un plan de formación de hábito personalizado",
            "parameters": {
                "desired_habit": {"type": "string", "required": True},
                "current_routine": {"type": "string", "required": False},
                "available_time_minutes": {"type": "integer", "required": False, "default": 30},
                "difficulty_preference": {"type": "string", "required": False, "default": "small"},
                "previous_attempts": {"type": "array", "required": False},
            },
            "returns": "Plan de formación con versiones, anclas y métricas",
        },
        {
            "name": "identify_barriers",
            "description": "Identifica barreras que impiden alcanzar un objetivo",
            "parameters": {
                "goal": {"type": "string", "required": True},
                "current_obstacles": {"type": "array", "required": False},
                "lifestyle_context": {"type": "string", "required": False},
                "energy_level": {"type": "string", "required": False, "default": "moderate"},
                "support_system": {"type": "string", "required": False, "default": "limited"},
            },
            "returns": "Barreras identificadas con soluciones específicas",
        },
        {
            "name": "design_accountability",
            "description": "Diseña un sistema de accountability personalizado",
            "parameters": {
                "goal": {"type": "string", "required": True},
                "preferred_method": {"type": "string", "required": False, "default": "habit_tracking"},
                "has_partner": {"type": "boolean", "required": False, "default": False},
                "check_in_frequency": {"type": "string", "required": False, "default": "daily"},
                "consequence_tolerance": {"type": "string", "required": False, "default": "moderate"},
            },
            "returns": "Sistema de accountability con schedule y consecuencias",
        },
        {
            "name": "assess_motivation",
            "description": "Evalúa el tipo y nivel de motivación del usuario",
            "parameters": {
                "stated_goal": {"type": "string", "required": True},
                "reasons_for_goal": {"type": "array", "required": False},
                "past_attempts": {"type": "integer", "required": False, "default": 0},
                "external_pressure": {"type": "string", "required": False, "default": "none"},
                "personal_values": {"type": "array", "required": False},
            },
            "returns": "Evaluación de motivación con probabilidad de éxito",
        },
        {
            "name": "suggest_behavior_change",
            "description": "Sugiere técnicas de cambio conductual específicas",
            "parameters": {
                "target_behavior": {"type": "string", "required": True},
                "current_behavior": {"type": "string", "required": False},
                "preferred_framework": {"type": "string", "required": False, "default": "atomic_habits"},
                "time_available_weekly": {"type": "integer", "required": False, "default": 60},
                "learning_style": {"type": "string", "required": False, "default": "practical"},
            },
            "returns": "Estrategia de cambio con técnicas y plan de implementación",
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


spark = Agent(
    name="spark",
    model="gemini-2.5-flash",
    description="Especialista en formación de hábitos, motivación y técnicas de cambio conductual para mejorar adherencia",
    instruction=SPARK_SYSTEM_PROMPT,
    tools=ALL_TOOLS,
    output_key="spark_response",
)


# Root agent para ADK CLI
root_agent = spark


# =============================================================================
# FUNCIONES HELPER
# =============================================================================


def get_status() -> dict:
    """Retorna el estado del agente y sus capacidades.

    Returns:
        Dict con estado, frameworks disponibles y configuración.
    """
    return {
        "status": "healthy",
        "agent": "spark",
        "version": AGENT_CARD["version"],
        "frameworks_available": list(BEHAVIOR_FRAMEWORKS.keys()),
        "barrier_categories": list(COMMON_BARRIERS.keys()),
        "motivation_types": list(MOTIVATION_TYPES.keys()),
        "accountability_methods": list(ACCOUNTABILITY_SYSTEMS.keys()),
        "capabilities": AGENT_CONFIG["capabilities"],
        "model": "gemini-2.5-flash",
    }


def quick_habit_plan(
    habit: str,
    anchor: str | None = None,
    minutes: int = 10,
) -> dict:
    """Función helper para crear un plan de hábito rápido.

    Args:
        habit: El hábito deseado.
        anchor: Hábito existente para anclar.
        minutes: Minutos disponibles.

    Returns:
        Dict con plan simplificado.
    """
    return create_habit_plan(
        desired_habit=habit,
        current_routine=anchor,
        available_time_minutes=minutes,
        difficulty_preference="small",
    )


def quick_barrier_analysis(
    goal: str,
    obstacles: list[str] | None = None,
) -> dict:
    """Función helper para análisis rápido de barreras.

    Args:
        goal: El objetivo.
        obstacles: Lista de obstáculos conocidos.

    Returns:
        Dict con análisis de barreras.
    """
    return identify_barriers(
        goal=goal,
        current_obstacles=obstacles,
    )


__all__ = [
    "spark",
    "root_agent",
    "get_status",
    "quick_habit_plan",
    "quick_barrier_analysis",
    "AGENT_CARD",
    "AGENT_CONFIG",
]
