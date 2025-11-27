"""SPARK - Agente especializado en Conducta y Hábitos.

Uso:
    from agents.spark import spark, create_habit_plan, AGENT_CARD

    # Con ADK CLI
    $ adk web agents/spark
"""

from __future__ import annotations

from agents.spark.agent import (
    spark,
    root_agent,
    quick_habit_plan,
    quick_barrier_analysis,
    get_status,
    AGENT_CARD,
    AGENT_CONFIG,
)
from agents.spark.prompts import (
    SPARK_SYSTEM_PROMPT,
    HABIT_FORMATION_PROMPT,
    BARRIER_IDENTIFICATION_PROMPT,
    MOTIVATION_ASSESSMENT_PROMPT,
    ACCOUNTABILITY_DESIGN_PROMPT,
)
from agents.spark.tools import (
    create_habit_plan,
    identify_barriers,
    design_accountability,
    assess_motivation,
    suggest_behavior_change,
    ALL_TOOLS,
    HABIT_FORMATION_STAGES,
    MOTIVATION_TYPES,
    COMMON_BARRIERS,
    BEHAVIOR_FRAMEWORKS,
    ACCOUNTABILITY_SYSTEMS,
    MotivationType,
    BarrierCategory,
    HabitDifficulty,
    CommitmentLevel,
)

__all__ = [
    # Agent
    "spark",
    "root_agent",
    "quick_habit_plan",
    "quick_barrier_analysis",
    "get_status",
    "AGENT_CARD",
    "AGENT_CONFIG",
    # Prompts
    "SPARK_SYSTEM_PROMPT",
    "HABIT_FORMATION_PROMPT",
    "BARRIER_IDENTIFICATION_PROMPT",
    "MOTIVATION_ASSESSMENT_PROMPT",
    "ACCOUNTABILITY_DESIGN_PROMPT",
    # Tools
    "create_habit_plan",
    "identify_barriers",
    "design_accountability",
    "assess_motivation",
    "suggest_behavior_change",
    "ALL_TOOLS",
    # Data
    "HABIT_FORMATION_STAGES",
    "MOTIVATION_TYPES",
    "COMMON_BARRIERS",
    "BEHAVIOR_FRAMEWORKS",
    "ACCOUNTABILITY_SYSTEMS",
    # Types
    "MotivationType",
    "BarrierCategory",
    "HabitDifficulty",
    "CommitmentLevel",
]

__version__ = "1.0.0"
