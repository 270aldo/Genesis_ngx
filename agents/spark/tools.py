"""Tools para SPARK - Agente de Conducta y Hábitos.

Incluye funciones para:
- Creación de planes de formación de hábitos
- Identificación de barreras psicológicas
- Diseño de sistemas de accountability
- Evaluación de motivación
- Aplicación de técnicas de cambio conductual
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from google.adk.tools import FunctionTool


# =============================================================================
# ENUMS Y TIPOS
# =============================================================================


class MotivationType(str, Enum):
    """Tipos de motivación."""

    INTRINSIC = "intrinsic"
    EXTRINSIC = "extrinsic"
    IDENTIFIED = "identified"
    INTROJECTED = "introjected"


class BarrierCategory(str, Enum):
    """Categorías de barreras."""

    TIME = "time"
    ENERGY = "energy"
    MOTIVATION = "motivation"
    KNOWLEDGE = "knowledge"
    SOCIAL = "social"
    RESOURCES = "resources"
    ENVIRONMENT = "environment"


class HabitDifficulty(str, Enum):
    """Nivel de dificultad de un hábito."""

    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class CommitmentLevel(str, Enum):
    """Nivel de compromiso."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


# =============================================================================
# DATOS DE REFERENCIA
# =============================================================================


HABIT_FORMATION_STAGES: dict[str, dict[str, str | list[str]]] = {
    "cue": {
        "name_es": "Señal",
        "description": "El disparador que inicia el comportamiento",
        "types": ["tiempo", "ubicación", "estado emocional", "otras personas", "acción previa"],
        "tips": [
            "Hazla obvia y visible",
            "Conecta con un hábito existente",
            "Usa alarmas o recordatorios al inicio",
        ],
    },
    "craving": {
        "name_es": "Antojo",
        "description": "La motivación o deseo detrás del hábito",
        "types": ["placer", "alivio", "logro", "conexión", "control"],
        "tips": [
            "Identifica el beneficio real que buscas",
            "Hazlo atractivo",
            "Asocia emociones positivas",
        ],
    },
    "response": {
        "name_es": "Respuesta",
        "description": "El hábito o comportamiento en sí",
        "types": ["físico", "mental", "social", "creativo"],
        "tips": [
            "Hazlo fácil (reduce fricción)",
            "Empieza pequeño (2 minutos)",
            "Prepara tu ambiente",
        ],
    },
    "reward": {
        "name_es": "Recompensa",
        "description": "El beneficio que refuerza el comportamiento",
        "types": ["inmediata", "diferida", "intrínseca", "extrínseca"],
        "tips": [
            "Celebra inmediatamente después",
            "Hazlo satisfactorio",
            "Trackea tu progreso visualmente",
        ],
    },
}


MOTIVATION_TYPES: dict[str, dict[str, str | list[str] | float]] = {
    "intrinsic": {
        "name_es": "Intrínseca",
        "description": "Motivación por el placer o satisfacción de la actividad misma",
        "drivers": ["autonomía", "maestría", "propósito", "curiosidad", "disfrute"],
        "sustainability": 0.95,
        "examples": [
            "Hacer ejercicio porque te hace sentir bien",
            "Aprender algo nuevo por curiosidad",
            "Cocinar saludable porque disfrutas el proceso",
        ],
    },
    "identified": {
        "name_es": "Identificada",
        "description": "Motivación porque el comportamiento se alinea con tus valores",
        "drivers": ["valores personales", "identidad", "importancia percibida", "metas a largo plazo"],
        "sustainability": 0.85,
        "examples": [
            "Ejercitarte porque valoras tu salud",
            "Comer bien porque quieres ser un buen ejemplo",
            "Meditar porque crees en el autocuidado",
        ],
    },
    "introjected": {
        "name_es": "Introyectada",
        "description": "Motivación por evitar culpa o ganar aprobación",
        "drivers": ["evitar culpa", "evitar vergüenza", "ganar aprobación", "autoestima condicional"],
        "sustainability": 0.50,
        "examples": [
            "Ir al gym para no sentirte culpable",
            "Comer bien porque 'deberías'",
            "Hacer dieta para que otros te vean bien",
        ],
    },
    "extrinsic": {
        "name_es": "Extrínseca",
        "description": "Motivación por recompensas o consecuencias externas",
        "drivers": ["dinero", "premios", "reconocimiento", "evitar castigo"],
        "sustainability": 0.30,
        "examples": [
            "Ejercitarte solo para perder peso",
            "Seguir una dieta por una apuesta",
            "Ir al gym porque tu pareja te presiona",
        ],
    },
}


COMMON_BARRIERS: dict[str, dict[str, str | list[str] | int]] = {
    "time": {
        "name_es": "Falta de tiempo",
        "description": "Percepción de no tener tiempo suficiente",
        "frequency": 85,  # % de personas que lo reportan
        "solutions": [
            "Empezar con micro-hábitos (2-5 minutos)",
            "Auditar tu tiempo real vs. percibido",
            "Identificar 'ladrones de tiempo' (redes, TV)",
            "Anclar hábito a rutina existente (habit stacking)",
            "Despertar 15-30 min antes",
        ],
        "reframe": "No es falta de tiempo, es falta de prioridad. Si es importante, encuentra 5 minutos.",
    },
    "energy": {
        "name_es": "Falta de energía",
        "description": "Sentirse demasiado cansado para actuar",
        "frequency": 70,
        "solutions": [
            "Hacerlo temprano (antes de gastar energía)",
            "Optimizar sueño primero",
            "Reducir dificultad en días de baja energía",
            "Usar 'versión mínima' del hábito",
            "Revisar nutrición e hidratación",
        ],
        "reframe": "La energía viene de la acción, no al revés. Empieza pequeño y la energía aparece.",
    },
    "motivation": {
        "name_es": "Falta de motivación",
        "description": "No sentir ganas de hacer la actividad",
        "frequency": 75,
        "solutions": [
            "No depender de motivación (depende de sistemas)",
            "Conectar con valores profundos (por qué)",
            "Visualizar el yo futuro que quieres ser",
            "Eliminar fricción del hábito",
            "Crear accountability con otros",
        ],
        "reframe": "La motivación es un mito. Los profesionales actúan sin motivación. Crea sistemas.",
    },
    "knowledge": {
        "name_es": "Falta de conocimiento",
        "description": "No saber cómo hacer algo correctamente",
        "frequency": 45,
        "solutions": [
            "Empezar con lo básico (no perfecto)",
            "Un recurso confiable, no 100 opciones",
            "Aprender haciendo, no solo leyendo",
            "Pedir ayuda (coach, mentor, amigo)",
            "Iterar y ajustar sobre la marcha",
        ],
        "reframe": "No necesitas saber todo para empezar. Aprenderás en el camino.",
    },
    "social": {
        "name_es": "Falta de apoyo social",
        "description": "Entorno social que no apoya o sabotea",
        "frequency": 50,
        "solutions": [
            "Comunicar tus objetivos claramente",
            "Encontrar comunidad de personas similares",
            "Establecer límites firmes pero amables",
            "No depender de aprobación externa",
            "Ser el cambio que quieres ver",
        ],
        "reframe": "Puedes inspirar a otros con tu ejemplo. Tu cambio puede ser contagioso.",
    },
    "resources": {
        "name_es": "Falta de recursos",
        "description": "Percepción de no tener dinero, equipo o acceso",
        "frequency": 40,
        "solutions": [
            "Empezar con lo que tienes (cuerpo, espacio)",
            "Alternativas gratuitas (apps, YouTube)",
            "Creatividad antes que dinero",
            "Priorizar gasto (¿café o gym?)",
            "Intercambiar servicios o habilidades",
        ],
        "reframe": "Las excusas de recursos son a menudo excusas de creatividad.",
    },
    "environment": {
        "name_es": "Ambiente no favorable",
        "description": "Entorno físico que dificulta el hábito",
        "frequency": 55,
        "solutions": [
            "Diseñar tu ambiente para el éxito",
            "Eliminar fricciones (ropa lista, comida prep)",
            "Agregar fricciones a malos hábitos",
            "Crear 'zonas' para diferentes actividades",
            "Usar señales visuales como recordatorios",
        ],
        "reframe": "Tu ambiente moldea tu comportamiento. Diseña para el éxito.",
    },
}


BEHAVIOR_FRAMEWORKS: dict[str, dict[str, str | list[str]]] = {
    "atomic_habits": {
        "name_es": "Hábitos Atómicos",
        "author": "James Clear",
        "core_principle": "Mejorar 1% cada día. Pequeños cambios, grandes resultados.",
        "four_laws": [
            "Hazlo obvio (diseña señales claras)",
            "Hazlo atractivo (conecta con deseos)",
            "Hazlo fácil (reduce fricción)",
            "Hazlo satisfactorio (recompensa inmediata)",
        ],
        "key_concepts": [
            "Habit stacking (anclar a hábitos existentes)",
            "Environment design (diseñar ambiente)",
            "Identity-based habits (enfocarse en quién quieres ser)",
            "2-minute rule (empezar con 2 minutos)",
        ],
    },
    "tiny_habits": {
        "name_es": "Hábitos Diminutos",
        "author": "BJ Fogg",
        "core_principle": "Hacer el comportamiento ridículamente pequeño y celebrar.",
        "formula": ["Después de [ANCLA], voy a [HÁBITO TINY], y celebraré [CELEBRACIÓN]"],
        "key_concepts": [
            "Behavior = Motivation × Ability × Prompt",
            "Starter step (primer paso mínimo)",
            "Shine (celebrar inmediatamente)",
            "Pearl habits (expandir gradualmente)",
        ],
    },
    "habit_loop": {
        "name_es": "El Bucle del Hábito",
        "author": "Charles Duhigg",
        "core_principle": "Entender el ciclo Señal-Rutina-Recompensa para modificarlo.",
        "steps": [
            "Identificar la rutina (el comportamiento)",
            "Experimentar con recompensas (qué buscas realmente)",
            "Aislar la señal (cuándo, dónde, con quién, qué emoción)",
            "Tener un plan (sustituir la rutina)",
        ],
        "key_concepts": [
            "Keystone habits (hábitos piedra angular)",
            "Golden rule (cambiar rutina, mantener señal y recompensa)",
            "Belief (creer que el cambio es posible)",
        ],
    },
    "self_determination": {
        "name_es": "Teoría de la Autodeterminación",
        "author": "Deci & Ryan",
        "core_principle": "La motivación intrínseca viene de satisfacer 3 necesidades básicas.",
        "three_needs": [
            "Autonomía (sentir control sobre tus acciones)",
            "Competencia (sentir que puedes lograr cosas)",
            "Conexión (sentir pertenencia y relación con otros)",
        ],
        "key_concepts": [
            "Motivación autónoma vs. controlada",
            "Internalización de valores",
            "Soporte de autonomía (no presión)",
        ],
    },
}


ACCOUNTABILITY_SYSTEMS: dict[str, dict[str, str | list[str] | int]] = {
    "habit_tracking": {
        "name_es": "Rastreo de Hábitos",
        "description": "Registrar diariamente si completaste el hábito",
        "effectiveness": 85,
        "tools": ["Habitica", "Streaks", "Loop Habit Tracker", "papel y pluma"],
        "tips": [
            "Mantén la racha visible",
            "No rompas la cadena 2 días seguidos",
            "Celebra visualmente cada check",
        ],
    },
    "accountability_partner": {
        "name_es": "Compañero de Accountability",
        "description": "Persona que revisa tu progreso regularmente",
        "effectiveness": 90,
        "requirements": [
            "Alguien que respetes",
            "Check-ins regulares (semanal mínimo)",
            "Honestidad total",
            "Sin juicios, solo hechos",
        ],
        "tips": [
            "Establece consecuencias claras",
            "Celebra juntos los logros",
            "Sé tú también su partner",
        ],
    },
    "public_commitment": {
        "name_es": "Compromiso Público",
        "description": "Declarar tu objetivo a otros",
        "effectiveness": 70,
        "platforms": ["Redes sociales", "Familia/amigos", "Grupo de apoyo", "Blog"],
        "tips": [
            "Ser específico con el compromiso",
            "Actualizar regularmente",
            "Cuidado con la satisfacción prematura",
        ],
    },
    "implementation_intentions": {
        "name_es": "Intenciones de Implementación",
        "description": "Planes específicos de cuándo, dónde y cómo actuar",
        "effectiveness": 80,
        "formula": ["Cuando [SITUACIÓN], voy a [COMPORTAMIENTO]"],
        "tips": [
            "Ser muy específico",
            "Incluir plan B",
            "Visualizar haciendo la acción",
        ],
    },
    "consequence_contracts": {
        "name_es": "Contratos con Consecuencias",
        "description": "Acuerdos formales con premios y castigos",
        "effectiveness": 75,
        "components": [
            "Objetivo claro y medible",
            "Plazo específico",
            "Consecuencia positiva (lograr)",
            "Consecuencia negativa (no lograr)",
            "Testigo o árbitro",
        ],
        "tips": [
            "Consecuencias significativas pero no destructivas",
            "Usar Stickk.com o similares",
            "Dinero funciona bien como consecuencia",
        ],
    },
}


# =============================================================================
# FUNCIONES DE CÁLCULO
# =============================================================================


def create_habit_plan(
    desired_habit: str,
    current_routine: str | None = None,
    available_time_minutes: int = 30,
    difficulty_preference: str = "small",
    previous_attempts: list[str] | None = None,
) -> dict:
    """Crea un plan de formación de hábito personalizado.

    Args:
        desired_habit: El hábito que el usuario quiere formar.
        current_routine: Rutina actual del usuario para anclar.
        available_time_minutes: Tiempo disponible por día.
        difficulty_preference: Preferencia de dificultad (tiny, small, medium, large).
        previous_attempts: Intentos anteriores fallidos.

    Returns:
        Dict con plan de formación de hábito.
    """
    # Validaciones
    if not desired_habit or len(desired_habit.strip()) < 3:
        return {
            "status": "error",
            "error": "Describe el hábito deseado con más detalle",
        }

    if available_time_minutes < 2:
        return {
            "status": "error",
            "error": "Necesitas al menos 2 minutos disponibles",
        }

    if difficulty_preference not in ["tiny", "small", "medium", "large"]:
        difficulty_preference = "small"

    # Determinar versión del hábito según dificultad
    habit_versions = _create_habit_versions(desired_habit, available_time_minutes)

    # Seleccionar versión recomendada
    recommended_version = habit_versions.get(difficulty_preference, habit_versions["small"])

    # Crear anclas sugeridas
    anchors = _suggest_anchors(current_routine)

    # Analizar intentos previos
    lessons_learned = []
    if previous_attempts:
        lessons_learned = _analyze_previous_attempts(previous_attempts)

    # Construir el loop del hábito
    habit_loop = {
        "cue": {
            "type": "anchor",
            "description": f"Después de {anchors[0]['anchor']}",
            "alternatives": [a["anchor"] for a in anchors[1:3]],
        },
        "craving": {
            "make_attractive": [
                "Visualiza cómo te sentirás después",
                "Conecta con tu identidad deseada",
                f"Recuerda por qué quieres {desired_habit}",
            ],
        },
        "response": {
            "habit": recommended_version["description"],
            "duration": recommended_version["duration_minutes"],
            "low_energy_version": habit_versions["tiny"]["description"],
        },
        "reward": {
            "immediate": "Celebra con un 'yes!' o pequeño baile",
            "tracking": "Marca el día en tu tracker",
            "progress": "Nota cómo te sientes después",
        },
    }

    # Plan semanal
    weekly_plan = _create_weekly_plan(recommended_version, difficulty_preference)

    return {
        "status": "created",
        "desired_habit": desired_habit,
        "recommended_version": recommended_version,
        "all_versions": habit_versions,
        "habit_loop": habit_loop,
        "anchors": anchors[:3],
        "weekly_plan": weekly_plan,
        "lessons_from_past": lessons_learned if lessons_learned else None,
        "success_metrics": {
            "short_term": "Completar 7 días seguidos",
            "medium_term": "Completar 21 días (formación inicial)",
            "long_term": "Completar 66 días (automatización)",
        },
        "tips": [
            "Empieza más pequeño de lo que crees necesario",
            "Nunca falles 2 días seguidos",
            "Celebra CADA vez que completes",
            "Si fallas, reduce la dificultad",
        ],
    }


def identify_barriers(
    goal: str,
    current_obstacles: list[str] | None = None,
    lifestyle_context: str | None = None,
    energy_level: str = "moderate",
    support_system: str = "limited",
) -> dict:
    """Identifica las barreras que impiden al usuario alcanzar su objetivo.

    Args:
        goal: El objetivo que el usuario quiere lograr.
        current_obstacles: Obstáculos que el usuario ya identifica.
        lifestyle_context: Contexto de vida (trabajo, familia, etc.).
        energy_level: Nivel de energía general (low, moderate, high).
        support_system: Sistema de apoyo (none, limited, moderate, strong).

    Returns:
        Dict con barreras identificadas y soluciones.
    """
    if not goal or len(goal.strip()) < 3:
        return {
            "status": "error",
            "error": "Describe tu objetivo con más detalle",
        }

    # Analizar obstáculos declarados
    identified_barriers = []
    if current_obstacles:
        for obstacle in current_obstacles:
            barrier_match = _match_barrier_category(obstacle)
            if barrier_match:
                identified_barriers.append(barrier_match)

    # Inferir barreras adicionales del contexto
    inferred_barriers = _infer_barriers_from_context(
        lifestyle_context, energy_level, support_system
    )

    # Combinar y deduplicar
    all_barriers = {b["category"]: b for b in identified_barriers + inferred_barriers}

    # Priorizar barreras
    prioritized = _prioritize_barriers(list(all_barriers.values()))

    # Generar soluciones específicas
    solutions_by_barrier = {}
    for barrier in prioritized[:3]:  # Top 3 barreras
        category = barrier["category"]
        if category in COMMON_BARRIERS:
            barrier_data = COMMON_BARRIERS[category]
            solutions_by_barrier[category] = {
                "name_es": barrier_data["name_es"],
                "impact_score": barrier["impact_score"],
                "solutions": barrier_data["solutions"][:3],
                "reframe": barrier_data["reframe"],
            }

    return {
        "status": "analyzed",
        "goal": goal,
        "barriers_identified": len(all_barriers),
        "top_barriers": prioritized[:3],
        "solutions": solutions_by_barrier,
        "priority_action": {
            "barrier": prioritized[0]["category"] if prioritized else None,
            "first_step": (
                COMMON_BARRIERS[prioritized[0]["category"]]["solutions"][0]
                if prioritized
                else "Define un objetivo más específico"
            ),
        },
        "context_insights": {
            "energy_level": energy_level,
            "support_system": support_system,
            "recommendation": _get_context_recommendation(energy_level, support_system),
        },
    }


def design_accountability(
    goal: str,
    preferred_method: str = "habit_tracking",
    has_partner: bool = False,
    check_in_frequency: str = "daily",
    consequence_tolerance: str = "moderate",
) -> dict:
    """Diseña un sistema de accountability personalizado.

    Args:
        goal: El objetivo para el cual crear accountability.
        preferred_method: Método preferido (habit_tracking, partner, public, contracts).
        has_partner: Si tiene compañero de accountability disponible.
        check_in_frequency: Frecuencia de check-ins (daily, weekly, biweekly).
        consequence_tolerance: Tolerancia a consecuencias (low, moderate, high).

    Returns:
        Dict con sistema de accountability diseñado.
    """
    if not goal or len(goal.strip()) < 3:
        return {
            "status": "error",
            "error": "Define un objetivo específico",
        }

    # Mapear preferencia a sistema
    if preferred_method not in ACCOUNTABILITY_SYSTEMS:
        preferred_method = "habit_tracking"

    primary_system = ACCOUNTABILITY_SYSTEMS[preferred_method]

    # Agregar sistemas complementarios
    complementary = []
    if has_partner and preferred_method != "accountability_partner":
        complementary.append(ACCOUNTABILITY_SYSTEMS["accountability_partner"])
    if consequence_tolerance in ["moderate", "high"]:
        complementary.append(ACCOUNTABILITY_SYSTEMS["consequence_contracts"])
    complementary.append(ACCOUNTABILITY_SYSTEMS["implementation_intentions"])

    # Crear check-in schedule
    schedule = _create_checkin_schedule(check_in_frequency)

    # Diseñar consecuencias
    consequences = _design_consequences(goal, consequence_tolerance)

    # Crear implementation intentions
    intentions = _create_implementation_intentions(goal)

    return {
        "status": "designed",
        "goal": goal,
        "primary_system": {
            "method": preferred_method,
            "name_es": primary_system["name_es"],
            "description": primary_system["description"],
            "effectiveness": primary_system["effectiveness"],
            "setup_steps": primary_system.get("tips", primary_system.get("requirements", [])),
        },
        "complementary_systems": [
            {
                "method": list(ACCOUNTABILITY_SYSTEMS.keys())[
                    list(ACCOUNTABILITY_SYSTEMS.values()).index(s)
                ],
                "name_es": s["name_es"],
            }
            for s in complementary[:2]
        ],
        "check_in_schedule": schedule,
        "consequences": consequences,
        "implementation_intentions": intentions,
        "success_tips": [
            "Revisa tu progreso a la misma hora cada día",
            "Celebra las pequeñas victorias",
            "Si fallas, analiza por qué sin juzgarte",
            "Ajusta el sistema si no funciona",
        ],
    }


def assess_motivation(
    stated_goal: str,
    reasons_for_goal: list[str] | None = None,
    past_attempts: int = 0,
    external_pressure: str = "none",
    personal_values: list[str] | None = None,
) -> dict:
    """Evalúa el tipo y nivel de motivación del usuario.

    Args:
        stated_goal: El objetivo declarado por el usuario.
        reasons_for_goal: Razones por las que quiere el objetivo.
        past_attempts: Número de intentos anteriores.
        external_pressure: Nivel de presión externa (none, low, moderate, high).
        personal_values: Valores personales del usuario.

    Returns:
        Dict con evaluación de motivación y recomendaciones.
    """
    if not stated_goal or len(stated_goal.strip()) < 3:
        return {
            "status": "error",
            "error": "Describe tu objetivo con más detalle",
        }

    # Analizar razones para determinar tipo de motivación
    motivation_scores = _analyze_motivation_type(reasons_for_goal, external_pressure)

    # Determinar tipo dominante
    dominant_type = max(motivation_scores, key=motivation_scores.get)
    dominant_data = MOTIVATION_TYPES[dominant_type]

    # Calcular nivel de compromiso
    commitment_factors = {
        "past_attempts": min(past_attempts / 5, 1) * 0.3,  # Más intentos = más comprometido
        "has_reasons": (0.3 if reasons_for_goal and len(reasons_for_goal) >= 2 else 0.1),
        "has_values": (0.2 if personal_values and len(personal_values) >= 2 else 0.1),
        "pressure_factor": {
            "none": 0.2,
            "low": 0.15,
            "moderate": 0.1,
            "high": 0.05,
        }.get(external_pressure, 0.1),
    }
    commitment_score = sum(commitment_factors.values())
    commitment_level = _score_to_commitment_level(commitment_score)

    # Calcular probabilidad de éxito
    sustainability = float(dominant_data["sustainability"])
    success_probability = round(sustainability * commitment_score * 100, 1)

    # Generar recomendaciones para mejorar motivación
    recommendations = _generate_motivation_recommendations(
        dominant_type, commitment_level, personal_values
    )

    return {
        "status": "assessed",
        "goal": stated_goal,
        "motivation_analysis": {
            "dominant_type": dominant_type,
            "dominant_name_es": dominant_data["name_es"],
            "description": dominant_data["description"],
            "sustainability_rating": sustainability,
            "all_scores": motivation_scores,
        },
        "commitment_analysis": {
            "level": commitment_level,
            "score": round(commitment_score, 2),
            "factors": commitment_factors,
        },
        "success_prediction": {
            "probability_percent": min(success_probability, 95),
            "risk_factors": _identify_motivation_risks(dominant_type, commitment_level),
        },
        "recommendations": recommendations,
        "motivation_boosters": dominant_data["examples"],
    }


def suggest_behavior_change(
    target_behavior: str,
    current_behavior: str | None = None,
    preferred_framework: str = "atomic_habits",
    time_available_weekly: int = 60,
    learning_style: str = "practical",
) -> dict:
    """Sugiere técnicas de cambio conductual específicas.

    Args:
        target_behavior: El comportamiento objetivo.
        current_behavior: El comportamiento actual a cambiar.
        preferred_framework: Framework preferido (atomic_habits, tiny_habits, habit_loop).
        time_available_weekly: Minutos disponibles por semana.
        learning_style: Estilo de aprendizaje (practical, theoretical, social).

    Returns:
        Dict con técnicas y estrategias de cambio conductual.
    """
    if not target_behavior or len(target_behavior.strip()) < 3:
        return {
            "status": "error",
            "error": "Describe el comportamiento objetivo con más detalle",
        }

    if preferred_framework not in BEHAVIOR_FRAMEWORKS:
        preferred_framework = "atomic_habits"

    framework = BEHAVIOR_FRAMEWORKS[preferred_framework]

    # Generar estrategia específica según framework
    strategy = _generate_framework_strategy(
        framework, target_behavior, current_behavior
    )

    # Crear plan de implementación
    implementation_plan = _create_implementation_plan(
        target_behavior, time_available_weekly
    )

    # Técnicas específicas
    techniques = _select_techniques_for_style(learning_style, preferred_framework)

    # Anticipar obstáculos
    anticipated_obstacles = _anticipate_obstacles(target_behavior)

    return {
        "status": "suggested",
        "target_behavior": target_behavior,
        "current_behavior": current_behavior,
        "framework": {
            "name": preferred_framework,
            "name_es": framework["name_es"],
            "author": framework["author"],
            "core_principle": framework["core_principle"],
        },
        "strategy": strategy,
        "implementation_plan": implementation_plan,
        "techniques": techniques,
        "anticipated_obstacles": anticipated_obstacles,
        "weekly_commitment": {
            "total_minutes": time_available_weekly,
            "sessions_recommended": max(3, time_available_weekly // 20),
            "minutes_per_session": min(20, time_available_weekly // 3),
        },
        "progress_markers": [
            {"day": 7, "milestone": "Primera semana completada"},
            {"day": 21, "milestone": "Hábito en formación"},
            {"day": 66, "milestone": "Hábito automatizado"},
            {"day": 90, "milestone": "Hábito consolidado"},
        ],
    }


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================


def _create_habit_versions(habit: str, max_minutes: int) -> dict:
    """Crea versiones del hábito de diferentes tamaños."""
    return {
        "tiny": {
            "description": f"{habit} por 2 minutos",
            "duration_minutes": 2,
            "difficulty": "tiny",
        },
        "small": {
            "description": f"{habit} por {min(10, max_minutes)} minutos",
            "duration_minutes": min(10, max_minutes),
            "difficulty": "small",
        },
        "medium": {
            "description": f"{habit} por {min(20, max_minutes)} minutos",
            "duration_minutes": min(20, max_minutes),
            "difficulty": "medium",
        },
        "large": {
            "description": f"{habit} por {max_minutes} minutos",
            "duration_minutes": max_minutes,
            "difficulty": "large",
        },
    }


def _suggest_anchors(current_routine: str | None) -> list[dict]:
    """Sugiere anclas para el nuevo hábito."""
    default_anchors = [
        {"anchor": "despertar", "time": "mañana", "reliability": "high"},
        {"anchor": "terminar el desayuno", "time": "mañana", "reliability": "high"},
        {"anchor": "regresar del trabajo", "time": "tarde", "reliability": "medium"},
        {"anchor": "preparar la cena", "time": "noche", "reliability": "medium"},
        {"anchor": "antes de dormir", "time": "noche", "reliability": "high"},
    ]

    if current_routine:
        custom_anchor = {
            "anchor": current_routine,
            "time": "personalizado",
            "reliability": "high",
        }
        return [custom_anchor] + default_anchors[:4]

    return default_anchors


def _analyze_previous_attempts(attempts: list[str]) -> list[str]:
    """Analiza intentos previos para extraer lecciones."""
    lessons = []
    for attempt in attempts:
        attempt_lower = attempt.lower()
        if "tiempo" in attempt_lower:
            lessons.append("Considera empezar con micro-hábitos de 2 minutos")
        if "motivación" in attempt_lower or "ganas" in attempt_lower:
            lessons.append("No dependas de motivación, crea sistemas")
        if "olvidé" in attempt_lower or "recordar" in attempt_lower:
            lessons.append("Usa anclas fuertes y recordatorios visuales")
        if "cansado" in attempt_lower or "energía" in attempt_lower:
            lessons.append("Hazlo temprano o ten versión de baja energía")

    return lessons if lessons else ["Empieza más pequeño de lo que intentaste antes"]


def _create_weekly_plan(version: dict, difficulty: str) -> dict:
    """Crea un plan semanal basado en la versión del hábito."""
    if difficulty == "tiny":
        return {
            "frequency": "diario",
            "rest_days": 0,
            "progression": "Mantén 2 min por 2 semanas, luego aumenta a 5",
        }
    elif difficulty == "small":
        return {
            "frequency": "6 días/semana",
            "rest_days": 1,
            "progression": "Mantén 2 semanas, luego aumenta 5 min",
        }
    elif difficulty == "medium":
        return {
            "frequency": "5 días/semana",
            "rest_days": 2,
            "progression": "Alterna días hasta que sea fácil",
        }
    else:
        return {
            "frequency": "4-5 días/semana",
            "rest_days": 2,
            "progression": "No aumentes hasta que sea consistente",
        }


def _match_barrier_category(obstacle: str) -> dict | None:
    """Clasifica un obstáculo en una categoría de barrera."""
    obstacle_lower = obstacle.lower()

    keywords = {
        "time": ["tiempo", "agenda", "ocupado", "horario", "trabajo"],
        "energy": ["cansado", "energía", "fatiga", "agotado", "sueño"],
        "motivation": ["motivación", "ganas", "flojera", "quiero", "difícil"],
        "knowledge": ["sé cómo", "aprender", "entiendo", "confundido"],
        "social": ["familia", "pareja", "amigos", "apoyo", "solo"],
        "resources": ["dinero", "equipo", "gym", "caro", "comprar"],
        "environment": ["casa", "espacio", "lugar", "ambiente", "clima"],
    }

    for category, words in keywords.items():
        if any(word in obstacle_lower for word in words):
            return {
                "category": category,
                "original": obstacle,
                "impact_score": 0.7,
            }

    return None


def _infer_barriers_from_context(
    lifestyle: str | None, energy: str, support: str
) -> list[dict]:
    """Infiere barreras del contexto."""
    barriers = []

    if energy == "low":
        barriers.append({"category": "energy", "impact_score": 0.9, "inferred": True})

    if support in ["none", "limited"]:
        barriers.append({"category": "social", "impact_score": 0.6, "inferred": True})

    if lifestyle:
        if "hijos" in lifestyle.lower() or "niños" in lifestyle.lower():
            barriers.append({"category": "time", "impact_score": 0.8, "inferred": True})

    return barriers


def _prioritize_barriers(barriers: list[dict]) -> list[dict]:
    """Prioriza barreras por impacto."""
    return sorted(barriers, key=lambda x: x.get("impact_score", 0.5), reverse=True)


def _get_context_recommendation(energy: str, support: str) -> str:
    """Genera recomendación basada en contexto."""
    if energy == "low":
        return "Prioriza descanso y hábitos de energía antes de agregar más"
    if support == "none":
        return "Considera encontrar una comunidad online de apoyo"
    return "Tu contexto es favorable para formar nuevos hábitos"


def _create_checkin_schedule(frequency: str) -> dict:
    """Crea un horario de check-ins."""
    schedules = {
        "daily": {
            "frequency": "diario",
            "best_time": "misma hora cada día (ej. 9 PM)",
            "duration": "2-5 minutos",
            "format": "¿Completé? Sí/No + nota breve",
        },
        "weekly": {
            "frequency": "semanal",
            "best_time": "domingo por la tarde",
            "duration": "15-20 minutos",
            "format": "Revisión de semana + plan siguiente",
        },
        "biweekly": {
            "frequency": "cada 2 semanas",
            "best_time": "fin de semana",
            "duration": "30 minutos",
            "format": "Análisis profundo + ajustes",
        },
    }
    return schedules.get(frequency, schedules["daily"])


def _design_consequences(goal: str, tolerance: str) -> dict:
    """Diseña consecuencias según tolerancia."""
    consequences = {
        "positive": {
            "daily": "Celebración verbal ('¡Sí!')",
            "weekly": "Actividad favorita (película, salida)",
            "monthly": "Recompensa significativa (compra, experiencia)",
        },
        "negative": {
            "low": "Solo pérdida de streak visual",
            "moderate": "Donación a causa neutral ($5-20)",
            "high": "Donación a causa que no te gusta ($20-50)",
        }[tolerance],
    }
    return consequences


def _create_implementation_intentions(goal: str) -> list[str]:
    """Crea intenciones de implementación."""
    return [
        f"Cuando suene mi alarma de las 7 AM, voy a [acción para {goal}]",
        f"Si me siento tentado a saltarme, voy a hacer la versión de 2 minutos",
        f"Cuando sea [día difícil], voy a hacer la versión mínima",
    ]


def _analyze_motivation_type(reasons: list[str] | None, pressure: str) -> dict[str, float]:
    """Analiza el tipo de motivación basado en razones."""
    scores = {
        "intrinsic": 0.25,
        "identified": 0.25,
        "introjected": 0.25,
        "extrinsic": 0.25,
    }

    if not reasons:
        return scores

    for reason in reasons:
        reason_lower = reason.lower()

        # Intrinsic keywords
        if any(w in reason_lower for w in ["disfruto", "me gusta", "divertido", "curioso"]):
            scores["intrinsic"] += 0.2

        # Identified keywords
        if any(w in reason_lower for w in ["valor", "importante", "creo", "identidad"]):
            scores["identified"] += 0.2

        # Introjected keywords
        if any(w in reason_lower for w in ["debería", "culpa", "vergüenza", "otros piensan"]):
            scores["introjected"] += 0.2

        # Extrinsic keywords
        if any(w in reason_lower for w in ["perder peso", "dinero", "premio", "ganar"]):
            scores["extrinsic"] += 0.2

    # Ajustar por presión externa
    if pressure in ["moderate", "high"]:
        scores["extrinsic"] += 0.15
        scores["intrinsic"] -= 0.1

    # Normalizar
    total = sum(scores.values())
    return {k: round(v / total, 2) for k, v in scores.items()}


def _score_to_commitment_level(score: float) -> str:
    """Convierte score a nivel de compromiso."""
    if score >= 0.8:
        return "very_high"
    elif score >= 0.6:
        return "high"
    elif score >= 0.4:
        return "moderate"
    return "low"


def _generate_motivation_recommendations(
    dominant_type: str, commitment: str, values: list[str] | None
) -> list[str]:
    """Genera recomendaciones para mejorar motivación."""
    recommendations = []

    if dominant_type == "extrinsic":
        recommendations.append("Conecta tu objetivo con valores más profundos")
        recommendations.append("Pregúntate: ¿Quién quiero ser, no solo qué quiero lograr?")

    if dominant_type == "introjected":
        recommendations.append("Suelta el 'debería' y encuentra el 'quiero'")
        recommendations.append("Tu valor no depende de lograr este objetivo")

    if commitment in ["low", "moderate"]:
        recommendations.append("Define tu 'por qué' con más claridad")
        recommendations.append("Visualiza tu yo futuro si logras vs. si no logras")

    if not values:
        recommendations.append("Identifica tus 3-5 valores más importantes")

    return recommendations[:4]


def _identify_motivation_risks(dominant_type: str, commitment: str) -> list[str]:
    """Identifica riesgos en la motivación."""
    risks = []

    if dominant_type in ["extrinsic", "introjected"]:
        risks.append("Motivación menos sostenible a largo plazo")

    if commitment in ["low", "moderate"]:
        risks.append("Probabilidad de abandono ante obstáculos")

    if dominant_type == "extrinsic":
        risks.append("Puede perder interés al lograr resultado externo")

    return risks if risks else ["Sin riesgos significativos identificados"]


def _generate_framework_strategy(
    framework: dict, target: str, current: str | None
) -> dict:
    """Genera estrategia basada en el framework."""
    strategy = {
        "core_principle": framework["core_principle"],
        "steps": [],
    }

    if "four_laws" in framework:
        strategy["steps"] = [
            f"1. Hazlo obvio: Define cuándo y dónde harás {target}",
            f"2. Hazlo atractivo: Conecta con beneficio inmediato",
            f"3. Hazlo fácil: Empieza con versión de 2 minutos",
            f"4. Hazlo satisfactorio: Celebra cada vez",
        ]
    elif "formula" in framework:
        strategy["steps"] = [
            f"1. Elige tu ancla: 'Después de [hábito existente]'",
            f"2. Define hábito tiny: '{target} por 30 segundos'",
            f"3. Celebra inmediatamente: 'Shine!'",
        ]
    else:
        strategy["steps"] = framework.get("steps", [])

    if current:
        strategy["replacement_strategy"] = (
            f"Mantén la señal de '{current}', cambia solo la rutina"
        )

    return strategy


def _create_implementation_plan(target: str, weekly_minutes: int) -> dict:
    """Crea plan de implementación."""
    daily_minutes = weekly_minutes // 7

    return {
        "phase_1": {
            "duration": "Semanas 1-2",
            "focus": "Consistencia > Duración",
            "daily_commitment": f"{max(2, daily_minutes // 3)} minutos",
        },
        "phase_2": {
            "duration": "Semanas 3-4",
            "focus": "Expandir gradualmente",
            "daily_commitment": f"{max(5, daily_minutes // 2)} minutos",
        },
        "phase_3": {
            "duration": "Semanas 5-8",
            "focus": "Objetivo completo",
            "daily_commitment": f"{daily_minutes} minutos",
        },
    }


def _select_techniques_for_style(style: str, framework: str) -> list[dict]:
    """Selecciona técnicas según estilo de aprendizaje."""
    techniques = {
        "practical": [
            {"name": "2-Minute Rule", "description": "Empieza con solo 2 minutos"},
            {"name": "Habit Stacking", "description": "Conecta con hábito existente"},
            {"name": "Environment Design", "description": "Prepara tu espacio"},
        ],
        "theoretical": [
            {"name": "Understanding Why", "description": "Entiende la ciencia detrás"},
            {"name": "Journaling", "description": "Reflexiona por escrito"},
            {"name": "Data Tracking", "description": "Mide y analiza tu progreso"},
        ],
        "social": [
            {"name": "Accountability Partner", "description": "Compañero de apoyo"},
            {"name": "Public Commitment", "description": "Comparte tu objetivo"},
            {"name": "Community Join", "description": "Únete a grupo similar"},
        ],
    }
    return techniques.get(style, techniques["practical"])


def _anticipate_obstacles(target: str) -> list[dict]:
    """Anticipa obstáculos comunes."""
    return [
        {
            "obstacle": "Falta de tiempo",
            "solution": "Ten versión de 2 minutos lista",
        },
        {
            "obstacle": "Olvido",
            "solution": "Usa anclas y recordatorios visuales",
        },
        {
            "obstacle": "Pérdida de motivación",
            "solution": "Recuerda tu 'por qué' y haz versión mínima",
        },
        {
            "obstacle": "Interrupción de rutina (viaje, enfermedad)",
            "solution": "Ten plan adaptado para situaciones especiales",
        },
    ]


# =============================================================================
# EXPORTACIÓN DE TOOLS
# =============================================================================


create_habit_plan_tool = FunctionTool(create_habit_plan)
identify_barriers_tool = FunctionTool(identify_barriers)
design_accountability_tool = FunctionTool(design_accountability)
assess_motivation_tool = FunctionTool(assess_motivation)
suggest_behavior_change_tool = FunctionTool(suggest_behavior_change)


ALL_TOOLS = [
    create_habit_plan_tool,
    identify_barriers_tool,
    design_accountability_tool,
    assess_motivation_tool,
    suggest_behavior_change_tool,
]


__all__ = [
    # Functions
    "create_habit_plan",
    "identify_barriers",
    "design_accountability",
    "assess_motivation",
    "suggest_behavior_change",
    # Tools
    "create_habit_plan_tool",
    "identify_barriers_tool",
    "design_accountability_tool",
    "assess_motivation_tool",
    "suggest_behavior_change_tool",
    "ALL_TOOLS",
    # Data
    "HABIT_FORMATION_STAGES",
    "MOTIVATION_TYPES",
    "COMMON_BARRIERS",
    "BEHAVIOR_FRAMEWORKS",
    "ACCOUNTABILITY_SYSTEMS",
    # Enums
    "MotivationType",
    "BarrierCategory",
    "HabitDifficulty",
    "CommitmentLevel",
]
