"""STELLA - Agente especializado en Analytics y Reportes.

Uso:
    from agents.stella import stella, generate_user_report, AGENT_CARD

    # Con ADK CLI
    $ adk web agents/stella
"""

from __future__ import annotations

from agents.stella.agent import (
    stella,
    root_agent,
    analyze_user_progress,
    generate_user_report,
    get_status,
    AGENT_CARD,
    AGENT_CONFIG,
)
from agents.stella.prompts import (
    STELLA_SYSTEM_PROMPT,
    PROGRESS_ANALYSIS_PROMPT,
    TREND_ANALYSIS_PROMPT,
    BIOMARKER_INTERPRETATION_PROMPT,
    REPORT_GENERATION_PROMPT,
)
from agents.stella.tools import (
    analyze_progress,
    calculate_trends,
    check_goal_status,
    interpret_biomarkers,
    generate_report,
    ALL_TOOLS,
    METRIC_TYPES,
    BIOMARKER_RANGES,
    GOAL_TEMPLATES,
    TREND_PERIODS,
    MetricCategory,
    TrendDirection,
    GoalCategory,
    ReportType,
)

__all__ = [
    # Agent
    "stella",
    "root_agent",
    "analyze_user_progress",
    "generate_user_report",
    "get_status",
    "AGENT_CARD",
    "AGENT_CONFIG",
    # Prompts
    "STELLA_SYSTEM_PROMPT",
    "PROGRESS_ANALYSIS_PROMPT",
    "TREND_ANALYSIS_PROMPT",
    "BIOMARKER_INTERPRETATION_PROMPT",
    "REPORT_GENERATION_PROMPT",
    # Tools
    "analyze_progress",
    "calculate_trends",
    "check_goal_status",
    "interpret_biomarkers",
    "generate_report",
    "ALL_TOOLS",
    # Data
    "METRIC_TYPES",
    "BIOMARKER_RANGES",
    "GOAL_TEMPLATES",
    "TREND_PERIODS",
    # Types
    "MetricCategory",
    "TrendDirection",
    "GoalCategory",
    "ReportType",
]

__version__ = "1.0.0"
