"""LOGOS - Especialista en Educación.

LOGOS es el educador del sistema Genesis NGX. Su misión es empoderar a los usuarios
con conocimiento para que entiendan el "por qué" detrás de cada recomendación.

Es el ÚNICO agente especialista que usa el modelo Pro (gemini-2.5-pro) debido a
la complejidad del razonamiento educativo y la necesidad de adaptar explicaciones
al nivel de cada usuario.

Uso con ADK:
    $ adk web agents/logos
    $ adk run agents/logos --prompt "Explícame qué es la sobrecarga progresiva"
"""

from __future__ import annotations

from google.adk import Agent

from agents.logos.prompts import LOGOS_SYSTEM_PROMPT
from agents.logos.tools import (
    ALL_TOOLS,
    CONCEPTS_DATABASE,
    EVIDENCE_DATABASE,
    MYTHS_DATABASE,
    LEARNING_LEVELS,
)


# =============================================================================
# CONFIGURACIÓN DEL AGENTE (Pro Model)
# =============================================================================


AGENT_CONFIG = {
    "domain": "education",
    "specialty": "learning_knowledge",
    "capabilities": [
        "concept_explanation",
        "evidence_presentation",
        "myth_debunking",
        "deep_dives",
        "quiz_generation",
    ],
    "personality": {
        "style": "Socrático - guía con preguntas",
        "tone": "Curioso, empático, adaptable",
        "depth": "Ajusta según nivel del usuario",
    },
    # Pro model configuration
    "model_tier": "pro",
    "thinking_level": "high",
    "cost_tier": "medium",
    "latency_tier": "standard",
}


# =============================================================================
# AGENT CARD (A2A Protocol v0.3) - Pro Configuration
# =============================================================================


AGENT_CARD = {
    "name": "logos",
    "description": "Especialista en educación: explica conceptos, presenta evidencia, desmiente mitos y genera contenido educativo adaptado al nivel del usuario",
    "version": "1.0.0",
    "protocol": "a2a/0.3",
    "domain": "education",
    "specialty": "learning_knowledge",
    "capabilities": AGENT_CONFIG["capabilities"],
    "methods": [
        {
            "name": "explain_concept",
            "description": "Explica un concepto adaptado al nivel del usuario",
            "parameters": {
                "concept": {"type": "string", "required": True},
                "user_level": {"type": "string", "required": False, "default": "intermediate"},
                "include_examples": {"type": "boolean", "required": False, "default": True},
                "include_mistakes": {"type": "boolean", "required": False, "default": True},
            },
            "returns": "Explicación adaptada con ejemplos y conceptos relacionados",
        },
        {
            "name": "present_evidence",
            "description": "Presenta evidencia científica sobre un tema",
            "parameters": {
                "topic": {"type": "string", "required": True},
                "include_studies": {"type": "boolean", "required": False, "default": True},
                "max_studies": {"type": "integer", "required": False, "default": 3},
            },
            "returns": "Veredicto, grado de evidencia, estudios clave y aplicación práctica",
        },
        {
            "name": "debunk_myth",
            "description": "Corrige un mito común con empatía y evidencia",
            "parameters": {
                "myth": {"type": "string", "required": True},
                "empathetic": {"type": "boolean", "required": False, "default": True},
            },
            "returns": "Mito, verdad, por qué se cree, y qué funciona realmente",
        },
        {
            "name": "create_deep_dive",
            "description": "Crea un módulo educativo completo sobre un tema",
            "parameters": {
                "topic": {"type": "string", "required": True},
                "sections": {"type": "array", "required": False},
                "include_quiz": {"type": "boolean", "required": False, "default": True},
                "user_level": {"type": "string", "required": False, "default": "intermediate"},
            },
            "returns": "Módulo educativo estructurado con secciones y quiz opcional",
        },
        {
            "name": "generate_quiz",
            "description": "Genera un quiz educativo sobre un tema",
            "parameters": {
                "topic": {"type": "string", "required": True},
                "difficulty": {"type": "string", "required": False, "default": "medium"},
                "num_questions": {"type": "integer", "required": False, "default": 5},
                "question_types": {"type": "array", "required": False},
            },
            "returns": "Quiz con preguntas, respuestas correctas y explicaciones",
        },
    ],
    # Pro limits (higher than Flash)
    "limits": {
        "max_input_tokens": 50000,
        "max_output_tokens": 4000,
        "max_latency_ms": 6000,
        "max_cost_per_invoke": 0.05,
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
# DEFINICIÓN DEL AGENTE (Pro Model)
# =============================================================================


logos = Agent(
    name="logos",
    model="gemini-2.5-pro",  # Pro model for complex educational reasoning
    description="Especialista en educación: explica conceptos de fitness, nutrición y bienestar adaptados al nivel del usuario, presenta evidencia científica, y desmiente mitos comunes",
    instruction=LOGOS_SYSTEM_PROMPT,
    tools=ALL_TOOLS,
    output_key="logos_response",
)


# Root agent para ADK CLI
root_agent = logos


# =============================================================================
# FUNCIONES HELPER
# =============================================================================


def get_status() -> dict:
    """Retorna el estado del agente y sus capacidades.

    Returns:
        Dict con estado, dominios cubiertos, y estadísticas de contenido.
    """
    return {
        "status": "healthy",
        "agent": "logos",
        "version": AGENT_CARD["version"],
        "model": "gemini-2.5-pro",
        "model_tier": "pro",
        "thinking_level": "high",
        "capabilities": AGENT_CONFIG["capabilities"],
        "content_stats": {
            "concepts": len(CONCEPTS_DATABASE),
            "evidence_topics": len(EVIDENCE_DATABASE),
            "myths": len(MYTHS_DATABASE),
            "learning_levels": len(LEARNING_LEVELS),
        },
        "domains_covered": list(set(
            data["domain"] for data in CONCEPTS_DATABASE.values()
        )),
    }


def quick_explain(concept: str, level: str = "intermediate") -> dict:
    """Helper para explicación rápida de un concepto.

    Args:
        concept: Concepto a explicar.
        level: Nivel del usuario.

    Returns:
        Dict con explicación.
    """
    from agents.logos.tools import explain_concept
    return explain_concept(concept=concept, user_level=level)


def quick_debunk(myth: str) -> dict:
    """Helper para desmentir rápidamente un mito.

    Args:
        myth: Mito a desmentir.

    Returns:
        Dict con información sobre el mito.
    """
    from agents.logos.tools import debunk_myth
    return debunk_myth(myth=myth)


def quick_quiz(topic: str, num_questions: int = 3) -> dict:
    """Helper para generar un quiz rápido.

    Args:
        topic: Tema del quiz.
        num_questions: Número de preguntas.

    Returns:
        Dict con quiz generado.
    """
    from agents.logos.tools import generate_quiz
    return generate_quiz(topic=topic, num_questions=num_questions)


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    "logos",
    "root_agent",
    "get_status",
    "quick_explain",
    "quick_debunk",
    "quick_quiz",
    "AGENT_CARD",
    "AGENT_CONFIG",
]
