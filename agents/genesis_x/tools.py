"""Tools para GENESIS_X orquestador.

Define las FunctionTools que el agente puede usar para:
- Clasificar intents de usuarios
- Invocar agentes especializados
- Construir consenso de respuestas
- Persistir eventos a Supabase
- Obtener contexto del usuario
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from google.adk.tools import FunctionTool

from agents.shared.agent_engine_registry import (
    AgentNotFoundError,
    get_registry,
)
from agents.shared.cost_calculator import CostCalculator
from agents.shared.security import SecurityValidator
from agents.shared.supabase_client import (
    SupabaseError,
    get_supabase_client,
)

logger = logging.getLogger(__name__)

# =============================================================================
# Constants & Types
# =============================================================================


class AgentDomain(str, Enum):
    """Dominios de agentes especializados."""

    FITNESS_STRENGTH = "blaze"
    FITNESS_MOBILITY = "atlas"
    FITNESS_CARDIO = "tempo"
    FITNESS_RECOVERY = "wave"
    NUTRITION_STRATEGY = "sage"
    NUTRITION_METABOLISM = "metabol"
    NUTRITION_MACROS = "macro"
    NUTRITION_SUPPLEMENTS = "nova"
    BEHAVIOR = "spark"
    ANALYTICS = "stella"
    WOMENS_HEALTH = "luna"
    EDUCATION = "logos"


class IntentCategory(str, Enum):
    """Categorías de intent del usuario."""

    FITNESS_STRENGTH = "fitness_strength"
    FITNESS_CARDIO = "fitness_cardio"
    FITNESS_MOBILITY = "fitness_mobility"
    FITNESS_RECOVERY = "fitness_recovery"
    NUTRITION_STRATEGY = "nutrition_strategy"
    NUTRITION_MACROS = "nutrition_macros"
    NUTRITION_METABOLISM = "nutrition_metabolism"
    NUTRITION_SUPPLEMENTS = "nutrition_supplements"
    BEHAVIOR = "behavior"
    ANALYTICS = "analytics"
    WOMENS_HEALTH = "womens_health"
    EDUCATION = "education"
    SEASON_PLANNING = "season_planning"
    GENERAL_CHAT = "general_chat"
    EMERGENCY = "emergency"


# Mapeo de intent a agente(s) responsable(s)
INTENT_TO_AGENTS: dict[str, list[str]] = {
    IntentCategory.FITNESS_STRENGTH.value: ["blaze"],
    IntentCategory.FITNESS_CARDIO.value: ["tempo"],
    IntentCategory.FITNESS_MOBILITY.value: ["atlas"],
    IntentCategory.FITNESS_RECOVERY.value: ["wave"],
    IntentCategory.NUTRITION_STRATEGY.value: ["sage"],
    IntentCategory.NUTRITION_MACROS.value: ["macro"],
    IntentCategory.NUTRITION_METABOLISM.value: ["metabol"],
    IntentCategory.NUTRITION_SUPPLEMENTS.value: ["nova"],
    IntentCategory.BEHAVIOR.value: ["spark"],
    IntentCategory.ANALYTICS.value: ["stella"],
    IntentCategory.WOMENS_HEALTH.value: ["luna"],
    IntentCategory.EDUCATION.value: ["logos"],
    IntentCategory.SEASON_PLANNING.value: ["blaze", "sage", "stella"],
    IntentCategory.GENERAL_CHAT.value: [],
    IntentCategory.EMERGENCY.value: [],
}

# Modelos recomendados por agente
AGENT_MODELS: dict[str, str] = {
    "genesis_x": "gemini-2.5-pro",
    "blaze": "gemini-2.5-flash",
    "atlas": "gemini-2.5-flash",
    "tempo": "gemini-2.5-flash",
    "wave": "gemini-2.5-flash",
    "sage": "gemini-2.5-flash",
    "metabol": "gemini-2.5-flash",
    "macro": "gemini-2.5-flash",
    "nova": "gemini-2.5-flash",
    "spark": "gemini-2.5-flash",
    "stella": "gemini-2.5-flash",
    "luna": "gemini-2.5-flash",
    "logos": "gemini-2.5-pro",  # Pro para educación profunda
}


@dataclass
class IntentClassification:
    """Resultado de clasificación de intent."""

    primary_intent: str
    secondary_intents: list[str]
    confidence: float
    agents_needed: list[str]
    reasoning: str
    is_emergency: bool = False
    requires_human_handoff: bool = False


@dataclass
class AgentResponse:
    """Respuesta de un agente especializado."""

    agent_id: str
    method: str
    result: dict[str, Any]
    tokens_used: int
    cost_usd: float
    latency_ms: int


@dataclass
class ConsensusResult:
    """Resultado de construcción de consenso."""

    unified_response: str
    sources: list[str]
    confidence: float
    follow_up_suggested: Optional[str] = None


# =============================================================================
# Helper Functions
# =============================================================================


def _get_cost_calculator() -> CostCalculator:
    """Obtiene instancia del calculador de costos."""
    return CostCalculator()


def _get_security_validator() -> SecurityValidator:
    """Obtiene instancia del validador de seguridad."""
    return SecurityValidator()


# =============================================================================
# FunctionTools for GENESIS_X
# =============================================================================


def classify_intent(
    message: str,
    user_context: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Clasifica el intent del mensaje del usuario para routing.

    Analiza el mensaje y determina qué tipo de ayuda necesita el usuario,
    qué agentes especializados deberían intervenir, y si hay alguna
    situación que requiera atención especial (emergencia, handoff).

    Args:
        message: Mensaje del usuario a clasificar
        user_context: Contexto opcional del usuario (temporada activa,
                     preferencias, historial reciente)

    Returns:
        dict con:
        - primary_intent: El intent principal detectado
        - secondary_intents: Lista de intents secundarios
        - confidence: Nivel de confianza (0.0-1.0)
        - agents_needed: Lista de IDs de agentes a invocar
        - reasoning: Explicación de la clasificación
        - is_emergency: True si se detecta posible emergencia
        - requires_human_handoff: True si necesita coach humano
    """
    # Validar seguridad del input
    validator = _get_security_validator()
    is_safe, validation_result = validator.validate(message)

    if not is_safe:
        if validation_result == "PHI_DETECTED":
            return {
                "primary_intent": "emergency",
                "secondary_intents": [],
                "confidence": 0.95,
                "agents_needed": [],
                "reasoning": "Se detectó posible información médica protegida. "
                "No podemos procesar este tipo de información.",
                "is_emergency": False,
                "requires_human_handoff": True,
            }
        if validation_result == "PROMPT_INJECTION":
            return {
                "primary_intent": "general_chat",
                "secondary_intents": [],
                "confidence": 0.9,
                "agents_needed": [],
                "reasoning": "No entendí tu mensaje. ¿Puedes reformularlo?",
                "is_emergency": False,
                "requires_human_handoff": False,
            }

    # Palabras clave para clasificación básica (heurística inicial)
    # El modelo LLM refinará esto, pero ayuda a dar contexto
    message_lower = message.lower()

    # Detectar emergencias
    emergency_keywords = [
        "dolor de pecho",
        "no puedo respirar",
        "desmayo",
        "sangre",
        "emergencia",
        "urgente médico",
        "hospital",
    ]
    if any(kw in message_lower for kw in emergency_keywords):
        return {
            "primary_intent": "emergency",
            "secondary_intents": [],
            "confidence": 0.95,
            "agents_needed": [],
            "reasoning": "Detecté palabras que sugieren una posible emergencia médica.",
            "is_emergency": True,
            "requires_human_handoff": False,
        }

    # Heurística básica por keywords
    intent_keywords = {
        "fitness_strength": [
            "fuerza",
            "músculo",
            "hipertrofia",
            "pesas",
            "gym",
            "entrenamiento",
            "ejercicio",
            "workout",
            "repeticiones",
            "series",
        ],
        "fitness_cardio": [
            "cardio",
            "correr",
            "running",
            "hiit",
            "resistencia",
            "aeróbico",
            "frecuencia cardíaca",
            "zona",
        ],
        "fitness_mobility": [
            "movilidad",
            "flexibilidad",
            "estiramiento",
            "stretch",
            "articulación",
            "rango de movimiento",
            "postura",
        ],
        "fitness_recovery": [
            "recuperación",
            "descanso",
            "sueño",
            "dormir",
            "hrv",
            "deload",
            "fatiga",
            "cansancio",
        ],
        "nutrition_strategy": [
            "dieta",
            "alimentación",
            "comer",
            "nutrición",
            "plan nutricional",
        ],
        "nutrition_macros": [
            "macros",
            "proteína",
            "carbohidratos",
            "grasas",
            "calorías",
            "déficit",
            "superávit",
        ],
        "nutrition_metabolism": [
            "metabolismo",
            "tdee",
            "gasto calórico",
            "insulina",
            "timing",
        ],
        "nutrition_supplements": [
            "suplemento",
            "creatina",
            "proteína en polvo",
            "vitamina",
            "stack",
        ],
        "behavior": [
            "motivación",
            "hábito",
            "consistencia",
            "disciplina",
            "no puedo",
            "me cuesta",
        ],
        "analytics": [
            "progreso",
            "datos",
            "métricas",
            "tendencia",
            "gráfico",
            "histórico",
        ],
        "womens_health": [
            "ciclo",
            "menstruación",
            "periodo",
            "menopausia",
            "hormonal",
        ],
        "education": [
            "por qué",
            "explica",
            "cómo funciona",
            "ciencia",
            "evidencia",
            "estudios",
        ],
        "season_planning": [
            "temporada",
            "fase",
            "ciclo de entrenamiento",
            "periodización",
            "objetivo",
            "meta",
        ],
    }

    # Encontrar matches
    intent_scores: dict[str, int] = {}
    for intent, keywords in intent_keywords.items():
        score = sum(1 for kw in keywords if kw in message_lower)
        if score > 0:
            intent_scores[intent] = score

    if not intent_scores:
        # Default a general_chat si no hay matches
        return {
            "primary_intent": "general_chat",
            "secondary_intents": [],
            "confidence": 0.5,
            "agents_needed": [],
            "reasoning": "No se detectaron keywords específicos. Clasificado como chat general.",
            "is_emergency": False,
            "requires_human_handoff": False,
        }

    # Ordenar por score
    sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
    primary = sorted_intents[0][0]
    secondary = [intent for intent, _ in sorted_intents[1:3]]  # Top 2 secundarios

    # Determinar agentes necesarios
    agents = INTENT_TO_AGENTS.get(primary, []).copy()
    for sec_intent in secondary:
        for agent in INTENT_TO_AGENTS.get(sec_intent, []):
            if agent not in agents:
                agents.append(agent)

    # Calcular confidence basado en score
    max_score = sorted_intents[0][1]
    confidence = min(0.5 + (max_score * 0.1), 0.95)

    return {
        "primary_intent": primary,
        "secondary_intents": secondary,
        "confidence": round(confidence, 2),
        "agents_needed": agents[:3],  # Máximo 3 agentes
        "reasoning": f"Clasificado por keywords. Score principal: {max_score}",
        "is_emergency": False,
        "requires_human_handoff": False,
    }


async def invoke_specialist(
    agent_id: str,
    method: str,
    params: dict[str, Any],
    user_id: str,
    budget_usd: float = 0.01,
) -> dict[str, Any]:
    """Invoca un agente especializado para obtener información específica.

    Utiliza el AgentEngineRegistry para invocar agentes desplegados en
    Vertex AI Agent Engine. Actualmente soporta BLAZE; otros agentes
    retornan placeholder hasta PR #3c.

    Args:
        agent_id: ID del agente a invocar (blaze, sage, etc.)
        method: Método a invocar en el agente
        params: Parámetros para el método
        user_id: ID del usuario para contexto
        budget_usd: Presupuesto máximo para esta invocación

    Returns:
        dict con:
        - agent_id: ID del agente invocado
        - method: Método invocado
        - result: Resultado del agente
        - tokens_used: Tokens utilizados
        - cost_usd: Costo de la invocación
        - status: 'success', 'error', 'budget_exceeded'
    """
    # Validar que el agente existe
    if agent_id not in AGENT_MODELS:
        logger.warning(f"Agente desconocido: {agent_id}")
        return {
            "agent_id": agent_id,
            "method": method,
            "result": {"error": f"Agente {agent_id} no disponible"},
            "tokens_used": 0,
            "cost_usd": 0.0,
            "status": "error",
        }

    # Estimar costo antes de invocar
    calc = _get_cost_calculator()
    model_type = "flash" if "flash" in AGENT_MODELS[agent_id] else "pro"

    # Estimación conservadora: 500 tokens input, 200 output
    estimated_cost = calc.calculate_gemini_cost(
        model=model_type,
        input_tokens=500,
        output_tokens=200,
        cached_tokens=0,
    )

    if estimated_cost > budget_usd:
        logger.warning(
            f"Budget insuficiente para {agent_id}: "
            f"estimado ${estimated_cost:.4f} > budget ${budget_usd:.4f}"
        )
        return {
            "agent_id": agent_id,
            "method": method,
            "result": {"error": "Budget insuficiente para esta operación"},
            "tokens_used": 0,
            "cost_usd": 0.0,
            "status": "budget_exceeded",
        }

    logger.info(f"Invocando agente {agent_id}.{method} para user {user_id}")

    # BLAZE: Invoke via Agent Engine Registry
    if agent_id == "blaze":
        return await _invoke_via_registry(
            agent_id=agent_id,
            method=method,
            params=params,
            user_id=user_id,
            budget_usd=budget_usd,
        )

    # Otros agentes: placeholder hasta PR #3c
    return {
        "agent_id": agent_id,
        "method": method,
        "result": {
            "placeholder": True,
            "message": f"Agente {agent_id} respondería al método {method}",
            "params_received": params,
        },
        "tokens_used": 0,
        "cost_usd": 0.0,
        "status": "success",
    }


async def _invoke_via_registry(
    agent_id: str,
    method: str,
    params: dict[str, Any],
    user_id: str,
    budget_usd: float,
) -> dict[str, Any]:
    """Invoca un agente usando el AgentEngineRegistry.

    Args:
        agent_id: ID del agente a invocar
        method: Método/tool a ejecutar
        params: Parámetros para el método
        user_id: ID del usuario
        budget_usd: Presupuesto máximo

    Returns:
        dict con resultado de la invocación
    """
    try:
        registry = get_registry()

        # Construir mensaje para el agente basado en method y params
        message = _build_agent_message(method, params)

        # Invocar el agente via registry
        result = await registry.invoke(
            agent_id=agent_id,
            message=message,
            user_id=user_id,
            budget_usd=budget_usd,
        )

        return {
            "agent_id": result.agent_id,
            "method": method,
            "result": {
                "response": result.response,
                "events": result.events,
            },
            "tokens_used": result.tokens_used,
            "cost_usd": result.cost_usd,
            "latency_ms": result.latency_ms,
            "status": result.status,
        }

    except AgentNotFoundError as e:
        logger.error(f"Agent not found: {e}")
        return {
            "agent_id": agent_id,
            "method": method,
            "result": {"error": str(e)},
            "tokens_used": 0,
            "cost_usd": 0.0,
            "status": "error",
        }
    except Exception as e:
        logger.error(f"Error invoking agent {agent_id}: {e}")
        return {
            "agent_id": agent_id,
            "method": method,
            "result": {"error": f"Error de invocación: {e}"},
            "tokens_used": 0,
            "cost_usd": 0.0,
            "status": "error",
        }


def _build_agent_message(method: str, params: dict[str, Any]) -> str:
    """Construye el mensaje para enviar al agente basado en method y params.

    Args:
        method: Nombre del método/tool a invocar
        params: Parámetros del método

    Returns:
        Mensaje formateado para el agente
    """
    # Formatear parámetros como contexto natural
    params_str = ", ".join(f"{k}={v}" for k, v in params.items())

    # Mensajes específicos por método de BLAZE
    method_messages = {
        "generate_workout": f"Genera un workout con estos parámetros: {params_str}",
        "calculate_1rm": f"Calcula el 1RM con: {params_str}",
        "suggest_progression": f"Sugiere progresión con: {params_str}",
        "design_training_block": f"Diseña un bloque de entrenamiento con: {params_str}",
    }

    return method_messages.get(
        method,
        f"Ejecuta {method} con parámetros: {params_str}"
    )


def build_consensus(
    agent_responses: list[dict[str, Any]],
    user_message: str,
    user_context: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Construye una respuesta unificada a partir de múltiples agentes.

    Toma las respuestas de varios agentes especializados y las integra
    en una respuesta coherente para el usuario, resolviendo posibles
    conflictos y priorizando según el contexto.

    Args:
        agent_responses: Lista de respuestas de agentes especializados
        user_message: Mensaje original del usuario
        user_context: Contexto del usuario (temporada, preferencias, etc.)

    Returns:
        dict con:
        - unified_response: Respuesta integrada para el usuario
        - sources: Lista de agentes que contribuyeron
        - confidence: Confianza en la respuesta unificada
        - follow_up_suggested: Pregunta de seguimiento sugerida
        - conflicts_resolved: Lista de conflictos que se resolvieron
    """
    if not agent_responses:
        return {
            "unified_response": "No tengo suficiente información para responder "
            "a tu pregunta. ¿Podrías darme más detalles?",
            "sources": [],
            "confidence": 0.3,
            "follow_up_suggested": "¿Qué aspecto específico te gustaría explorar?",
            "conflicts_resolved": [],
        }

    # Filtrar respuestas exitosas
    successful_responses = [
        r for r in agent_responses if r.get("status") == "success"
    ]

    if not successful_responses:
        # Todos los agentes fallaron
        return {
            "unified_response": "Estoy teniendo dificultades técnicas para "
            "procesar tu solicitud. Por favor intenta de nuevo.",
            "sources": [],
            "confidence": 0.2,
            "follow_up_suggested": None,
            "conflicts_resolved": [],
        }

    # Extraer información de cada agente
    sources = [r["agent_id"] for r in successful_responses]

    # En producción, aquí el LLM integraría las respuestas
    # Por ahora, construimos una respuesta placeholder estructurada
    agents_summary = ", ".join(sources)

    unified_response = (
        f"Basándome en la consulta de los especialistas ({agents_summary}), "
        f"aquí está mi respuesta integrada a tu pregunta sobre: '{user_message[:50]}...'"
    )

    # Calcular confianza basada en número de fuentes y sus resultados
    confidence = min(0.5 + (len(successful_responses) * 0.15), 0.95)

    return {
        "unified_response": unified_response,
        "sources": sources,
        "confidence": round(confidence, 2),
        "follow_up_suggested": "¿Hay algo más específico que te gustaría saber?",
        "conflicts_resolved": [],
    }


def get_user_context(user_id: str) -> dict[str, Any]:
    """Obtiene el contexto del usuario desde Supabase.

    Recupera información relevante del usuario para personalizar
    las respuestas: temporada activa, preferencias, historial reciente.

    Args:
        user_id: ID del usuario (UUID)

    Returns:
        dict con:
        - user_id: ID del usuario
        - active_season: Temporada activa (si existe)
        - current_phase: Fase actual (si existe)
        - preferences: Preferencias del usuario
        - recent_checkins: Check-ins recientes
        - status: 'success' o 'error'
    """
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        logger.error(f"user_id inválido: {user_id}")
        return {
            "user_id": user_id,
            "status": "error",
            "error": "ID de usuario inválido",
        }

    try:
        supabase = get_supabase_client()

        # Obtener temporada activa
        # En producción, esto usaría el auth_token del usuario
        # Por ahora usamos service_client para testing
        season_response = (
            supabase.service_client.table("seasons")
            .select("*")
            .eq("user_id", str(user_uuid))
            .eq("status", "active")
            .maybe_single()
            .execute()
        )

        active_season = season_response.data if season_response.data else None

        # Obtener preferencias
        prefs_response = (
            supabase.service_client.table("user_preferences")
            .select("*")
            .eq("user_id", str(user_uuid))
            .maybe_single()
            .execute()
        )

        preferences = prefs_response.data if prefs_response.data else {}

        # Obtener check-ins recientes (últimos 7 días)
        from datetime import timedelta

        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()

        checkins_response = (
            supabase.service_client.table("daily_checkins")
            .select("*")
            .eq("user_id", str(user_uuid))
            .gte("checkin_date", week_ago)
            .order("checkin_date", desc=True)
            .limit(7)
            .execute()
        )

        recent_checkins = checkins_response.data if checkins_response.data else []

        return {
            "user_id": user_id,
            "active_season": active_season,
            "current_phase": None,  # TODO: obtener de phases table
            "preferences": preferences,
            "recent_checkins": recent_checkins,
            "status": "success",
        }

    except SupabaseError as e:
        logger.error(f"Error obteniendo contexto de usuario {user_id}: {e}")
        return {
            "user_id": user_id,
            "status": "error",
            "error": str(e),
        }


def persist_to_supabase(
    user_id: str,
    event_type: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Persiste un evento a Supabase para auditoría y tracking.

    Registra eventos importantes del orquestador para:
    - Auditoría de decisiones
    - Tracking de costos
    - Análisis de uso

    Args:
        user_id: ID del usuario
        event_type: Tipo de evento (intent_classified, specialist_invoked,
                   consensus_built, etc.)
        payload: Datos del evento

    Returns:
        dict con:
        - event_id: ID del evento creado
        - status: 'success' o 'error'
        - error: Mensaje de error si aplica
    """
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        logger.error(f"user_id inválido: {user_id}")
        return {
            "event_id": None,
            "status": "error",
            "error": "ID de usuario inválido",
        }

    try:
        supabase = get_supabase_client()

        # Usar el RPC agent_log_event que ya existe
        # Este RPC valida el agent_role y registra el evento
        response = supabase.service_client.rpc(
            "agent_log_event",
            {
                "p_user_id": str(user_uuid),
                "p_agent_type": "genesis_x",
                "p_event_type": event_type,
                "p_payload": payload,
            },
        ).execute()

        if response.data:
            return {
                "event_id": response.data,
                "status": "success",
            }
        else:
            return {
                "event_id": None,
                "status": "error",
                "error": "No se pudo crear el evento",
            }

    except SupabaseError as e:
        logger.error(f"Error persistiendo evento para user {user_id}: {e}")
        return {
            "event_id": None,
            "status": "error",
            "error": str(e),
        }


# =============================================================================
# Wrapped FunctionTools for ADK
# =============================================================================

# Estas son las versiones envueltas como FunctionTool para usar en el Agent
classify_intent_tool = FunctionTool(classify_intent)
invoke_specialist_tool = FunctionTool(invoke_specialist)
build_consensus_tool = FunctionTool(build_consensus)
get_user_context_tool = FunctionTool(get_user_context)
persist_to_supabase_tool = FunctionTool(persist_to_supabase)

# Lista de todas las tools disponibles
ALL_TOOLS = [
    classify_intent_tool,
    invoke_specialist_tool,
    build_consensus_tool,
    get_user_context_tool,
    persist_to_supabase_tool,
]
