"""STELLA - Agente especializado en Analytics y Reportes.

Este modulo define el agente STELLA usando Google ADK.
STELLA analiza progreso, tendencias, biomarcadores y genera reportes
para usuarios de 30-60 años.

Capabilities:
- Progress tracking and analysis
- Trend calculation and pattern detection
- Goal monitoring and status
- Biomarker interpretation
- Report generation

SLOs (de PRD Seccion 4.2):
- Latency p95: ≤2.0s
- Cost per invoke: ≤$0.01
"""

from __future__ import annotations

import logging
from typing import Any

from google.adk import Agent

from agents.stella.prompts import STELLA_SYSTEM_PROMPT
from agents.stella.tools import ALL_TOOLS

logger = logging.getLogger(__name__)

# =============================================================================
# Agent Configuration
# =============================================================================

AGENT_CONFIG = {
    "agent_id": "stella",
    "display_name": "STELLA",
    "domain": "analytics",
    "specialty": "data_visualization",
    "model": "gemini-2.5-flash",
    "thinking_level": "low",
    "capabilities": [
        "progress_tracking",
        "trend_analysis",
        "goal_monitoring",
        "biomarker_interpretation",
        "report_generation",
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

stella = Agent(
    name="stella",
    model=AGENT_CONFIG["model"],
    description=(
        "Especialista en analytics, visualizacion de datos y reportes. "
        "Analiza progreso, identifica tendencias, monitorea metas, "
        "interpreta biomarcadores y genera reportes personalizados "
        "para usuarios de 30-60 años."
    ),
    instruction=STELLA_SYSTEM_PROMPT,
    tools=ALL_TOOLS,
    output_key="stella_response",
)

# =============================================================================
# Agent Card (A2A Protocol)
# =============================================================================

AGENT_CARD = {
    "name": AGENT_CONFIG["display_name"],
    "description": stella.description,
    "version": "1.0.0",
    "protocol": "a2a/0.3",
    "domain": AGENT_CONFIG["domain"],
    "specialty": AGENT_CONFIG["specialty"],
    "capabilities": AGENT_CONFIG["capabilities"],
    "methods": [
        {
            "name": "analyze_progress",
            "description": "Analiza el progreso de una metrica a lo largo del tiempo",
            "params": {
                "metric_values": {"type": "array", "required": True},
                "metric_name": {"type": "string", "required": False},
                "period_days": {"type": "integer", "required": False},
                "goal_value": {"type": "number", "required": False},
                "goal_type": {"type": "string", "required": False},
            },
        },
        {
            "name": "calculate_trends",
            "description": "Calcula tendencias en una serie de datos",
            "params": {
                "data_points": {"type": "array", "required": True},
                "metric_name": {"type": "string", "required": False},
                "period": {"type": "string", "required": False},
            },
        },
        {
            "name": "check_goal_status",
            "description": "Verifica el estado de cumplimiento de una meta",
            "params": {
                "goal_category": {"type": "string", "required": True},
                "current_value": {"type": "number", "required": True},
                "target_value": {"type": "number", "required": True},
                "start_value": {"type": "number", "required": False},
                "start_date": {"type": "string", "required": False},
                "target_date": {"type": "string", "required": False},
            },
        },
        {
            "name": "interpret_biomarkers",
            "description": "Interpreta biomarcadores de salud",
            "params": {
                "biomarkers": {"type": "object", "required": True},
                "user_age": {"type": "integer", "required": False},
                "user_sex": {"type": "string", "required": False},
            },
        },
        {
            "name": "generate_report",
            "description": "Genera un reporte de progreso personalizado",
            "params": {
                "report_type": {"type": "string", "required": True},
                "metrics_data": {"type": "object", "required": False},
                "goals_data": {"type": "array", "required": False},
                "user_name": {"type": "string", "required": False},
            },
        },
        {
            "name": "respond",
            "description": "Responde preguntas generales sobre analytics y reportes",
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
        "audience": "stella-analytics-agent",
    },
}

# =============================================================================
# Helper Functions
# =============================================================================


def analyze_user_progress(
    metric_values: list[float],
    metric_name: str = "weight_kg",
    period_days: int = 30,
    goal_value: float | None = None,
) -> dict[str, Any]:
    """Analiza el progreso del usuario en una metrica.

    Args:
        metric_values: Lista de valores de la metrica
        metric_name: Nombre de la metrica
        period_days: Dias del periodo
        goal_value: Valor objetivo (opcional)

    Returns:
        dict con analisis de progreso
    """
    from agents.stella.tools import analyze_progress

    return analyze_progress(
        metric_values=metric_values,
        metric_name=metric_name,
        period_days=period_days,
        goal_value=goal_value,
    )


def generate_user_report(
    report_type: str = "weekly",
    metrics_data: dict[str, list[float]] | None = None,
    goals_data: list[dict[str, Any]] | None = None,
    user_name: str = "Usuario",
) -> dict[str, Any]:
    """Genera un reporte para el usuario.

    Args:
        report_type: Tipo de reporte
        metrics_data: Datos de metricas
        goals_data: Datos de metas
        user_name: Nombre del usuario

    Returns:
        dict con reporte generado
    """
    from agents.stella.tools import generate_report

    return generate_report(
        report_type=report_type,
        metrics_data=metrics_data,
        goals_data=goals_data,
        user_name=user_name,
    )


def get_status() -> dict[str, Any]:
    """Obtiene el estado actual del agente STELLA."""
    from agents.stella.tools import METRIC_TYPES, BIOMARKER_RANGES, GOAL_TEMPLATES

    return {
        "status": "healthy",
        "version": AGENT_CARD["version"],
        "agent_id": AGENT_CONFIG["agent_id"],
        "model": AGENT_CONFIG["model"],
        "domain": AGENT_CONFIG["domain"],
        "specialty": AGENT_CONFIG["specialty"],
        "metric_categories": list(METRIC_TYPES.keys()),
        "biomarkers_supported": list(BIOMARKER_RANGES.keys()),
        "goal_templates": list(GOAL_TEMPLATES.keys()),
        "capabilities": AGENT_CONFIG["capabilities"],
    }


# =============================================================================
# ADK Entry Point
# =============================================================================

root_agent = stella
