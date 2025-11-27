"""Tools para LUNA - Agente de Salud Femenina.

Incluye funciones para:
- Seguimiento del ciclo menstrual
- Recomendaciones por fase del ciclo
- Análisis de síntomas
- Planes adaptados al ciclo
- Evaluación de salud hormonal
"""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from typing import Literal

from google.adk.tools import FunctionTool


# =============================================================================
# ENUMS Y TIPOS
# =============================================================================


class CyclePhase(str, Enum):
    """Fases del ciclo menstrual."""

    MENSTRUAL = "menstrual"
    FOLLICULAR = "follicular"
    OVULATORY = "ovulatory"
    LUTEAL = "luteal"


class EnergyLevel(str, Enum):
    """Nivel de energía."""

    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class ContraceptionType(str, Enum):
    """Tipo de anticoncepción."""

    NONE = "none"
    HORMONAL_PILL = "hormonal_pill"
    IUD_HORMONAL = "iud_hormonal"
    IUD_COPPER = "iud_copper"
    IMPLANT = "implant"
    OTHER = "other"


class LifeStage(str, Enum):
    """Etapa de vida reproductiva."""

    REPRODUCTIVE = "reproductive"
    PERIMENOPAUSE = "perimenopause"
    MENOPAUSE = "menopause"


# =============================================================================
# DATOS DE REFERENCIA
# =============================================================================


CYCLE_PHASES: dict[str, dict] = {
    "menstrual": {
        "name_es": "Fase Menstrual",
        "typical_days": "1-5",
        "hormones": "Estrógeno y progesterona bajos",
        "energy": "low",
        "mood": "introspectivo, necesidad de descanso",
        "training_focus": "recuperación, movilidad, yoga",
        "nutrition_focus": "hierro, antiinflamatorios, magnesio",
        "intensity_modifier": 0.6,  # 60% de intensidad normal
    },
    "follicular": {
        "name_es": "Fase Folicular",
        "typical_days": "6-13",
        "hormones": "Estrógeno en aumento",
        "energy": "high",
        "mood": "optimista, energético, sociable",
        "training_focus": "fuerza, HIIT, nuevos desafíos",
        "nutrition_focus": "proteína, carbohidratos, fibra",
        "intensity_modifier": 1.0,  # 100% intensidad
    },
    "ovulatory": {
        "name_es": "Fase Ovulatoria",
        "typical_days": "14-17",
        "hormones": "Pico de estrógeno, surge LH",
        "energy": "very_high",
        "mood": "confiado, comunicativo, máxima energía",
        "training_focus": "máxima intensidad, competencias, PRs",
        "nutrition_focus": "proteína, antioxidantes, hidratación",
        "intensity_modifier": 1.1,  # 110% intensidad permitida
    },
    "luteal": {
        "name_es": "Fase Lútea",
        "typical_days": "18-28",
        "hormones": "Progesterona dominante, luego cae",
        "energy": "moderate_declining",
        "mood": "más interno, posibles cambios de humor",
        "training_focus": "resistencia moderada, steady-state",
        "nutrition_focus": "más calorías, menos carbos simples, magnesio",
        "intensity_modifier": 0.8,  # 80% intensidad
    },
}


SYMPTOMS_DATABASE: dict[str, dict] = {
    "cramps": {
        "name_es": "Calambres menstruales",
        "typical_phase": "menstrual",
        "strategies": [
            "Aplicar calor en abdomen",
            "Magnesio (300-400mg/día)",
            "Ejercicio suave (caminata, yoga)",
            "Té de jengibre o manzanilla",
            "Omega-3 (antiinflamatorio)",
        ],
        "when_to_see_doctor": "Dolor que impide actividades normales",
    },
    "fatigue": {
        "name_es": "Fatiga",
        "typical_phase": "menstrual",
        "strategies": [
            "Priorizar sueño (7-9 horas)",
            "Hierro si sangrado abundante",
            "No forzar entrenamientos intensos",
            "Hidratación adecuada",
            "Snacks con hierro + vitamina C",
        ],
        "when_to_see_doctor": "Fatiga extrema o persistente fuera de periodo",
    },
    "bloating": {
        "name_es": "Hinchazón",
        "typical_phase": "luteal",
        "strategies": [
            "Reducir sodio",
            "Aumentar potasio (plátano, aguacate)",
            "Beber más agua (paradójicamente ayuda)",
            "Ejercicio suave",
            "Evitar bebidas carbonatadas",
        ],
        "when_to_see_doctor": "Hinchazón severa o constante",
    },
    "mood_swings": {
        "name_es": "Cambios de humor",
        "typical_phase": "luteal",
        "strategies": [
            "Ejercicio regular (libera endorfinas)",
            "Sueño suficiente",
            "Vitamina B6 (50-100mg)",
            "Magnesio",
            "Reducir cafeína y alcohol",
        ],
        "when_to_see_doctor": "Cambios severos que afectan relaciones",
    },
    "cravings": {
        "name_es": "Antojos",
        "typical_phase": "luteal",
        "strategies": [
            "No ignorar completamente (causa restricción)",
            "Elegir versiones más saludables",
            "Chocolate oscuro OK (hierro, magnesio)",
            "Comer suficiente en general",
            "Proteína en cada comida (saciedad)",
        ],
        "when_to_see_doctor": "Antojos extremos o compulsivos",
    },
    "headache": {
        "name_es": "Dolor de cabeza",
        "typical_phase": "menstrual",
        "strategies": [
            "Hidratación",
            "Magnesio preventivo",
            "Regularidad en comidas",
            "Descanso en cuarto oscuro",
            "Cafeína moderada (puede ayudar o empeorar)",
        ],
        "when_to_see_doctor": "Migrañas severas o nuevos patrones",
    },
    "breast_tenderness": {
        "name_es": "Sensibilidad mamaria",
        "typical_phase": "luteal",
        "strategies": [
            "Reducir cafeína",
            "Reducir sal",
            "Sujetador deportivo cómodo",
            "Aceite de onagra (evidencia limitada)",
            "Vitamina E",
        ],
        "when_to_see_doctor": "Bultos nuevos o dolor unilateral",
    },
    "acne": {
        "name_es": "Acné",
        "typical_phase": "luteal",
        "strategies": [
            "Limpieza facial consistente",
            "Reducir lácteos (para algunas)",
            "Zinc (15-30mg)",
            "No tocar la cara",
            "Cambiar funda de almohada frecuentemente",
        ],
        "when_to_see_doctor": "Acné severo o persistente",
    },
    "insomnia": {
        "name_es": "Problemas de sueño",
        "typical_phase": "luteal",
        "strategies": [
            "Magnesio antes de dormir",
            "Rutina de sueño consistente",
            "Evitar pantallas 1h antes",
            "Cuarto fresco y oscuro",
            "Limitar cafeína después de mediodía",
        ],
        "when_to_see_doctor": "Insomnio crónico que afecta función",
    },
}


TRAINING_BY_PHASE: dict[str, dict] = {
    "menstrual": {
        "recommended": [
            "Yoga restaurativo",
            "Caminatas suaves",
            "Estiramientos",
            "Natación suave",
            "Pilates modificado",
        ],
        "avoid": [
            "HIIT intenso",
            "Levantamiento máximo",
            "Entrenamientos extenuantes",
        ],
        "duration_minutes": "20-45",
        "intensity": "baja a moderada",
        "note": "Escuchar al cuerpo; OK si tiene energía para más",
    },
    "follicular": {
        "recommended": [
            "Entrenamiento de fuerza",
            "HIIT",
            "Intervalos de velocidad",
            "Nuevos ejercicios/deportes",
            "Entrenamientos grupales",
        ],
        "avoid": [
            "Sobreentrenamiento",
        ],
        "duration_minutes": "45-75",
        "intensity": "moderada a alta",
        "note": "Aprovechar la energía creciente",
    },
    "ovulatory": {
        "recommended": [
            "Entrenamientos más intensos",
            "Competencias",
            "Tests de fuerza/velocidad",
            "Actividades sociales/grupales",
        ],
        "avoid": [
            "Movimientos de alto riesgo sin calentamiento",
        ],
        "duration_minutes": "45-90",
        "intensity": "alta",
        "note": "Mayor riesgo de lesión ligamentosa - calentar bien",
    },
    "luteal": {
        "recommended": [
            "Cardio steady-state",
            "Fuerza con cargas moderadas",
            "Yoga",
            "Caminatas",
            "Ejercicios de bajo impacto",
        ],
        "avoid": [
            "Intentar PRs",
            "Entrenamientos muy largos",
            "Presionarse cuando no hay energía",
        ],
        "duration_minutes": "30-60",
        "intensity": "moderada, reduciendo hacia el final",
        "note": "Primera mitad aún buena energía, segunda mitad reducir",
    },
}


NUTRITION_BY_PHASE: dict[str, dict] = {
    "menstrual": {
        "increase": [
            {"nutrient": "Hierro", "sources": "carne roja, espinacas, legumbres", "why": "compensar pérdida por sangrado"},
            {"nutrient": "Magnesio", "sources": "chocolate oscuro, nueces, semillas", "why": "calambres y humor"},
            {"nutrient": "Omega-3", "sources": "pescado graso, semillas", "why": "antiinflamatorio"},
            {"nutrient": "Vitamina C", "sources": "cítricos, pimiento", "why": "ayuda absorción de hierro"},
        ],
        "reduce": [
            {"item": "Cafeína excesiva", "why": "puede empeorar calambres"},
            {"item": "Alcohol", "why": "deshidrata, afecta sueño"},
        ],
        "calorie_adjustment": "normal o ligeramente reducido si apetito bajo",
    },
    "follicular": {
        "increase": [
            {"nutrient": "Proteína", "sources": "carnes, huevos, legumbres", "why": "síntesis muscular óptima"},
            {"nutrient": "Carbohidratos complejos", "sources": "avena, arroz, papa", "why": "energía para entrenar"},
            {"nutrient": "Fibra", "sources": "vegetales, granos enteros", "why": "metabolismo de estrógeno"},
        ],
        "reduce": [
            {"item": "Alimentos procesados", "why": "aprovechar buena sensibilidad a insulina"},
        ],
        "calorie_adjustment": "normal, puede aumentar si entrenamiento intenso",
    },
    "ovulatory": {
        "increase": [
            {"nutrient": "Proteína", "sources": "variedad de fuentes", "why": "mantener músculo"},
            {"nutrient": "Antioxidantes", "sources": "frutas, vegetales coloridos", "why": "protección celular"},
            {"nutrient": "Hidratación", "sources": "agua, electrolitos", "why": "rendimiento óptimo"},
        ],
        "reduce": [
            {"item": "Nada específico", "why": "fase de mayor flexibilidad"},
        ],
        "calorie_adjustment": "normal",
    },
    "luteal": {
        "increase": [
            {"nutrient": "Calorías totales", "sources": "todas", "why": "metabolismo sube 2-10%"},
            {"nutrient": "Magnesio", "sources": "chocolate oscuro, nueces", "why": "SPM, antojos"},
            {"nutrient": "Vitamina B6", "sources": "pollo, pescado, plátano", "why": "síntomas premenstruales"},
            {"nutrient": "Proteína y grasas", "sources": "variedad", "why": "saciedad con menor sensibilidad a insulina"},
        ],
        "reduce": [
            {"item": "Carbohidratos simples", "why": "sensibilidad a insulina reducida"},
            {"item": "Sodio", "why": "reduce hinchazón"},
            {"item": "Alcohol", "why": "empeora síntomas y sueño"},
        ],
        "calorie_adjustment": "+100-300 kcal/día",
    },
}


PERIMENOPAUSE_INFO: dict = {
    "typical_age_range": "45-55 años",
    "duration": "4-10 años típicamente",
    "signs": [
        "Ciclos irregulares (más cortos o largos)",
        "Sofocos y sudores nocturnos",
        "Cambios en el sueño",
        "Cambios de humor",
        "Sequedad vaginal",
        "Cambios en distribución de grasa",
        "Pérdida de masa muscular acelerada",
        "Cambios en densidad ósea",
    ],
    "training_recommendations": [
        "Priorizar entrenamiento de fuerza (2-3x/semana mínimo)",
        "Incluir ejercicios de impacto para huesos",
        "HIIT cortos para metabolismo",
        "Yoga/pilates para flexibilidad y estrés",
        "No abandonar ejercicio aunque energía fluctúe",
    ],
    "nutrition_recommendations": [
        "Proteína aumentada (1.2-1.6g/kg)",
        "Calcio (1200mg/día)",
        "Vitamina D (2000-4000 IU)",
        "Omega-3 para inflamación y cognición",
        "Fitoestrógenos (soja) - evidencia mixta",
        "Reducir alcohol (empeora sofocos)",
    ],
}


# =============================================================================
# FUNCIONES DE CÁLCULO
# =============================================================================


def track_cycle(
    last_period_start: str,
    cycle_length: int = 28,
    period_length: int = 5,
    contraception: str = "none",
    current_date: str | None = None,
) -> dict:
    """Registra datos del ciclo y calcula la fase actual.

    Args:
        last_period_start: Fecha del primer día del último periodo (YYYY-MM-DD).
        cycle_length: Duración típica del ciclo en días (21-35 normal).
        period_length: Duración típica del sangrado en días (3-7 normal).
        contraception: Tipo de anticoncepción usada.
        current_date: Fecha actual (default: hoy).

    Returns:
        Dict con fase actual y predicciones.
    """
    # Validaciones
    try:
        last_period = datetime.strptime(last_period_start, "%Y-%m-%d")
    except ValueError:
        return {
            "status": "error",
            "error": "Formato de fecha inválido. Usa YYYY-MM-DD",
        }

    if cycle_length < 21 or cycle_length > 35:
        return {
            "status": "error",
            "error": "Duración de ciclo fuera de rango normal (21-35 días)",
            "recommendation": "Consulta con ginecólogo si ciclos muy irregulares",
        }

    if period_length < 2 or period_length > 10:
        return {
            "status": "error",
            "error": "Duración de periodo fuera de rango típico (2-10 días)",
        }

    # Fecha actual
    if current_date:
        try:
            today = datetime.strptime(current_date, "%Y-%m-%d")
        except ValueError:
            today = datetime.now()
    else:
        today = datetime.now()

    # Calcular día del ciclo
    days_since_period = (today - last_period).days
    cycle_day = (days_since_period % cycle_length) + 1

    # Determinar fase
    phase = _calculate_phase(cycle_day, cycle_length, period_length)
    phase_info = CYCLE_PHASES[phase]

    # Calcular fechas importantes
    ovulation_day = cycle_length - 14  # Ovulación ~14 días antes del siguiente periodo
    next_period = last_period + timedelta(days=cycle_length)

    # Si ya pasó, calcular el siguiente
    while next_period <= today:
        next_period += timedelta(days=cycle_length)

    days_to_next_period = (next_period - today).days

    # Ventana fértil (si no usa anticoncepción hormonal)
    fertile_window = None
    if contraception in ["none", "iud_copper"]:
        fertile_start = ovulation_day - 5
        fertile_end = ovulation_day + 1
        fertile_window = {
            "start_day": fertile_start,
            "end_day": fertile_end,
            "note": "Ventana aproximada; usa otros métodos para precisión",
        }

    return {
        "status": "tracked",
        "current_date": today.strftime("%Y-%m-%d"),
        "last_period_start": last_period_start,
        "cycle_day": cycle_day,
        "cycle_length": cycle_length,
        "current_phase": phase,
        "phase_name_es": phase_info["name_es"],
        "phase_info": {
            "typical_days": phase_info["typical_days"],
            "hormones": phase_info["hormones"],
            "energy_level": phase_info["energy"],
            "mood": phase_info["mood"],
        },
        "predictions": {
            "next_period": next_period.strftime("%Y-%m-%d"),
            "days_to_next_period": days_to_next_period,
            "estimated_ovulation_day": ovulation_day,
        },
        "fertile_window": fertile_window,
        "contraception": contraception,
        "note": "Estas son estimaciones. El ciclo real puede variar." if contraception == "none" else "Anticoncepción hormonal suprime ciclo natural.",
    }


def get_phase_recommendations(
    phase: str,
    goal: str = "general",
    energy_today: str = "moderate",
    has_symptoms: list[str] | None = None,
) -> dict:
    """Obtiene recomendaciones de entrenamiento y nutrición para una fase.

    Args:
        phase: Fase del ciclo (menstrual, follicular, ovulatory, luteal).
        goal: Objetivo (general, performance, weight_loss, muscle_gain).
        energy_today: Nivel de energía hoy.
        has_symptoms: Síntomas actuales.

    Returns:
        Dict con recomendaciones completas.
    """
    phase_normalized = phase.lower()
    if phase_normalized not in CYCLE_PHASES:
        return {
            "status": "error",
            "error": f"Fase '{phase}' no reconocida. Usa: menstrual, follicular, ovulatory, luteal",
        }

    phase_info = CYCLE_PHASES[phase_normalized]
    training = TRAINING_BY_PHASE[phase_normalized]
    nutrition = NUTRITION_BY_PHASE[phase_normalized]

    # Ajustar por energía actual
    energy_adjustment = _get_energy_adjustment(energy_today, phase_info["energy"])

    # Ajustar por síntomas
    symptom_modifications = []
    if has_symptoms:
        for symptom in has_symptoms:
            if symptom.lower() in SYMPTOMS_DATABASE:
                symptom_info = SYMPTOMS_DATABASE[symptom.lower()]
                symptom_modifications.append({
                    "symptom": symptom_info["name_es"],
                    "strategies": symptom_info["strategies"][:3],
                })

    # Ajustar por objetivo
    goal_modifications = _get_goal_modifications(goal, phase_normalized)

    return {
        "status": "recommended",
        "phase": phase_normalized,
        "phase_name_es": phase_info["name_es"],
        "training_recommendations": {
            "recommended_activities": training["recommended"],
            "activities_to_avoid": training.get("avoid", []),
            "duration": training["duration_minutes"],
            "intensity": training["intensity"],
            "intensity_modifier": phase_info["intensity_modifier"],
            "note": training["note"],
        },
        "nutrition_recommendations": {
            "increase": nutrition["increase"],
            "reduce": nutrition["reduce"],
            "calorie_adjustment": nutrition["calorie_adjustment"],
        },
        "energy_adjustment": energy_adjustment,
        "symptom_strategies": symptom_modifications if symptom_modifications else None,
        "goal_specific_tips": goal_modifications,
        "general_advice": [
            "Escucha a tu cuerpo - estas son guías, no reglas",
            "La variabilidad individual es normal",
            "Si te sientes bien, puedes hacer más; si no, descansa",
        ],
    }


def analyze_symptoms(
    symptoms: list[str],
    cycle_day: int | None = None,
    severity: str = "moderate",
    recurring: bool = False,
) -> dict:
    """Analiza síntomas y proporciona estrategias de manejo.

    Args:
        symptoms: Lista de síntomas a analizar.
        cycle_day: Día del ciclo (para contextualizar).
        severity: Severidad (mild, moderate, severe).
        recurring: Si los síntomas son recurrentes cada ciclo.

    Returns:
        Dict con análisis y recomendaciones.
    """
    if not symptoms:
        return {
            "status": "error",
            "error": "Proporciona al menos un síntoma a analizar",
        }

    analyzed = []
    see_doctor_flags = []
    phase_association = None

    # Determinar fase si se proporciona día del ciclo
    if cycle_day:
        if 1 <= cycle_day <= 5:
            phase_association = "menstrual"
        elif 6 <= cycle_day <= 13:
            phase_association = "follicular"
        elif 14 <= cycle_day <= 17:
            phase_association = "ovulatory"
        else:
            phase_association = "luteal"

    for symptom in symptoms:
        symptom_lower = symptom.lower().replace(" ", "_")

        # Buscar en base de datos
        if symptom_lower in SYMPTOMS_DATABASE:
            symptom_info = SYMPTOMS_DATABASE[symptom_lower]
            analysis = {
                "symptom": symptom,
                "name_es": symptom_info["name_es"],
                "typical_phase": symptom_info["typical_phase"],
                "phase_match": symptom_info["typical_phase"] == phase_association if phase_association else None,
                "strategies": symptom_info["strategies"],
                "when_to_see_doctor": symptom_info["when_to_see_doctor"],
            }

            if severity == "severe":
                see_doctor_flags.append({
                    "symptom": symptom_info["name_es"],
                    "reason": symptom_info["when_to_see_doctor"],
                })
        else:
            analysis = {
                "symptom": symptom,
                "name_es": symptom,
                "typical_phase": "variable",
                "strategies": [
                    "Descanso adecuado",
                    "Hidratación",
                    "Ejercicio suave",
                    "Consultar si persiste",
                ],
                "when_to_see_doctor": "Si el síntoma es nuevo, severo o persistente",
            }

        analyzed.append(analysis)

    # Recomendaciones generales basadas en análisis
    general_recs = _generate_symptom_recommendations(analyzed, severity, recurring)

    return {
        "status": "analyzed",
        "symptoms_count": len(analyzed),
        "cycle_day": cycle_day,
        "estimated_phase": phase_association,
        "severity": severity,
        "recurring": recurring,
        "symptom_analysis": analyzed,
        "see_doctor_if": see_doctor_flags if see_doctor_flags else None,
        "general_recommendations": general_recs,
        "disclaimer": "Esta información es educativa. Consulta con un profesional de salud para síntomas severos o preocupantes.",
    }


def create_cycle_plan(
    cycle_length: int = 28,
    goal: str = "general",
    activity_level: str = "moderate",
    known_symptoms: list[str] | None = None,
) -> dict:
    """Crea un plan de entrenamiento y nutrición adaptado al ciclo.

    Args:
        cycle_length: Duración del ciclo en días.
        goal: Objetivo (general, performance, weight_loss, muscle_gain).
        activity_level: Nivel de actividad (low, moderate, high).
        known_symptoms: Síntomas conocidos que suele experimentar.

    Returns:
        Dict con plan semanal por fase.
    """
    if cycle_length < 21 or cycle_length > 35:
        return {
            "status": "error",
            "error": "Duración de ciclo fuera de rango normal",
        }

    # Calcular días por fase
    phases_days = _calculate_phase_days(cycle_length)

    # Crear plan por fase
    plan = {}

    for phase_name, days_info in phases_days.items():
        phase_info = CYCLE_PHASES[phase_name]
        training = TRAINING_BY_PHASE[phase_name]
        nutrition = NUTRITION_BY_PHASE[phase_name]

        # Ajustar por objetivo
        goal_mods = _get_goal_modifications(goal, phase_name)

        # Ajustar por nivel de actividad
        activity_mods = _get_activity_modifications(activity_level, phase_name)

        # Crear plan de días
        daily_plan = _create_daily_plan(
            phase_name, days_info["duration"], training, activity_level
        )

        plan[phase_name] = {
            "phase_name_es": phase_info["name_es"],
            "days": f"{days_info['start']}-{days_info['end']}",
            "duration_days": days_info["duration"],
            "energy_expectation": phase_info["energy"],
            "training": {
                "focus": phase_info["training_focus"],
                "intensity_modifier": phase_info["intensity_modifier"],
                "recommended_activities": training["recommended"][:4],
                "avoid": training.get("avoid", []),
                "daily_plan": daily_plan,
            },
            "nutrition": {
                "focus": phase_info["nutrition_focus"],
                "key_nutrients": [n["nutrient"] for n in nutrition["increase"][:3]],
                "calorie_adjustment": nutrition["calorie_adjustment"],
            },
            "goal_specific": goal_mods,
            "symptom_preparation": _prepare_for_symptoms(phase_name, known_symptoms) if known_symptoms else None,
        }

    return {
        "status": "created",
        "cycle_length": cycle_length,
        "goal": goal,
        "activity_level": activity_level,
        "plan_by_phase": plan,
        "general_principles": [
            "Este plan es una guía - escucha a tu cuerpo",
            "Si te sientes bien, puedes hacer más",
            "Si estás cansada, reduce la intensidad",
            "Consistencia > perfección",
            "Trackea cómo te sientes para ajustar",
        ],
        "disclaimer": "Plan general. Ajusta según tu respuesta individual.",
    }


def assess_hormonal_health(
    cycle_regularity: str = "regular",
    period_flow: str = "moderate",
    energy_pattern: str = "normal_fluctuation",
    has_concerning_symptoms: list[str] | None = None,
    life_stage: str = "reproductive",
    recent_changes: str | None = None,
) -> dict:
    """Evalúa señales de salud hormonal y proporciona orientación.

    Args:
        cycle_regularity: Regularidad del ciclo (regular, somewhat_irregular, very_irregular).
        period_flow: Flujo del periodo (light, moderate, heavy, very_heavy).
        energy_pattern: Patrón de energía (stable, normal_fluctuation, extreme_fluctuation).
        has_concerning_symptoms: Síntomas preocupantes.
        life_stage: Etapa de vida (reproductive, perimenopause, menopause).
        recent_changes: Cambios recientes relevantes.

    Returns:
        Dict con evaluación y recomendaciones.
    """
    red_flags = []
    yellow_flags = []
    positive_signs = []
    recommendations = []

    # Evaluar regularidad
    if cycle_regularity == "regular":
        positive_signs.append("Ciclos regulares indican buena función hormonal")
    elif cycle_regularity == "somewhat_irregular":
        yellow_flags.append("Ciclos algo irregulares - monitorear")
        recommendations.append("Trackear ciclos por 3+ meses para identificar patrón")
    elif cycle_regularity == "very_irregular":
        red_flags.append("Ciclos muy irregulares pueden indicar desequilibrio hormonal")
        recommendations.append("Consulta con ginecólogo para evaluación")

    # Evaluar flujo
    if period_flow == "moderate":
        positive_signs.append("Flujo menstrual normal")
    elif period_flow == "light":
        yellow_flags.append("Flujo ligero - puede ser normal o indicar bajo estrógeno")
    elif period_flow == "heavy":
        yellow_flags.append("Flujo abundante - considerar niveles de hierro")
        recommendations.append("Considerar suplemento de hierro, verificar con médico")
    elif period_flow == "very_heavy":
        red_flags.append("Flujo muy abundante requiere evaluación médica")
        recommendations.append("Consultar médico; posible anemia")

    # Evaluar energía
    if energy_pattern == "normal_fluctuation":
        positive_signs.append("Fluctuación normal de energía con el ciclo")
    elif energy_pattern == "extreme_fluctuation":
        yellow_flags.append("Fluctuaciones extremas de energía")
        recommendations.append("Evaluar sueño, nutrición, estrés")

    # Evaluar síntomas preocupantes
    if has_concerning_symptoms:
        for symptom in has_concerning_symptoms:
            symptom_lower = symptom.lower()
            if "amenorrea" in symptom_lower or "sin periodo" in symptom_lower:
                red_flags.append("Ausencia de periodo requiere evaluación")
                recommendations.append("Consultar médico - descartar causas")
            elif "sangrado" in symptom_lower and "entre" in symptom_lower:
                red_flags.append("Sangrado intermenstrual debe evaluarse")
            elif "dolor" in symptom_lower and "severo" in symptom_lower:
                red_flags.append("Dolor severo puede indicar condición subyacente")
            else:
                yellow_flags.append(f"Síntoma a monitorear: {symptom}")

    # Evaluar etapa de vida
    life_stage_info = None
    if life_stage == "perimenopause":
        life_stage_info = PERIMENOPAUSE_INFO
        recommendations.extend([
            "Priorizar entrenamiento de fuerza",
            "Aumentar proteína a 1.2-1.6g/kg",
            "Considerar vitamina D y calcio",
        ])

    # Calcular score general
    health_score = _calculate_hormonal_health_score(
        len(positive_signs), len(yellow_flags), len(red_flags)
    )

    return {
        "status": "assessed",
        "hormonal_health_score": health_score,
        "positive_signs": positive_signs,
        "yellow_flags": yellow_flags if yellow_flags else None,
        "red_flags": red_flags if red_flags else None,
        "recommendations": recommendations,
        "life_stage": life_stage,
        "life_stage_info": life_stage_info,
        "recent_changes_noted": recent_changes,
        "general_guidance": [
            "Comer suficiente (no déficit crónico severo)",
            "Dormir 7-9 horas",
            "Manejar estrés",
            "Ejercicio moderado (ni muy poco ni excesivo)",
            "Grasas saludables en la dieta",
        ],
        "when_to_consult_doctor": [
            "Ausencia de periodo por más de 3 meses",
            "Sangrado muy abundante o entre periodos",
            "Dolor incapacitante",
            "Síntomas que afectan calidad de vida",
            "Cambios súbitos en el patrón menstrual",
        ] if red_flags else None,
        "disclaimer": "Esta evaluación es orientativa. No reemplaza diagnóstico médico.",
    }


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================


def _calculate_phase(cycle_day: int, cycle_length: int, period_length: int) -> str:
    """Calcula la fase del ciclo basada en el día."""
    ovulation_day = cycle_length - 14

    if cycle_day <= period_length:
        return "menstrual"
    elif cycle_day <= ovulation_day - 3:
        return "follicular"
    elif cycle_day <= ovulation_day + 2:
        return "ovulatory"
    else:
        return "luteal"


def _calculate_phase_days(cycle_length: int) -> dict:
    """Calcula los días de cada fase según duración del ciclo."""
    ovulation_day = cycle_length - 14

    return {
        "menstrual": {"start": 1, "end": 5, "duration": 5},
        "follicular": {"start": 6, "end": ovulation_day - 3, "duration": ovulation_day - 8},
        "ovulatory": {"start": ovulation_day - 2, "end": ovulation_day + 2, "duration": 5},
        "luteal": {"start": ovulation_day + 3, "end": cycle_length, "duration": cycle_length - ovulation_day - 2},
    }


def _get_energy_adjustment(current_energy: str, expected_energy: str) -> dict:
    """Genera ajustes basados en energía actual vs esperada."""
    adjustments = {
        "very_low": {
            "recommendation": "Reduce intensidad significativamente",
            "suggested_activities": ["yoga restaurativo", "caminata suave", "descanso"],
        },
        "low": {
            "recommendation": "Reduce intensidad, enfócate en movimiento suave",
            "suggested_activities": ["yoga", "caminata", "natación suave"],
        },
        "moderate": {
            "recommendation": "Sigue el plan normal con atención a señales del cuerpo",
            "suggested_activities": ["actividades planificadas"],
        },
        "high": {
            "recommendation": "Aprovecha la energía, puedes aumentar intensidad",
            "suggested_activities": ["entrenamientos más desafiantes"],
        },
        "very_high": {
            "recommendation": "Excelente día para entrenamientos intensos o PRs",
            "suggested_activities": ["HIIT", "fuerza máxima", "competencias"],
        },
    }

    return adjustments.get(current_energy, adjustments["moderate"])


def _get_goal_modifications(goal: str, phase: str) -> list[str]:
    """Genera modificaciones específicas por objetivo."""
    mods = {
        "performance": {
            "menstrual": ["Usa esta fase para recuperación activa"],
            "follicular": ["Período óptimo para PR y tests"],
            "ovulatory": ["Máximo rendimiento - aprovecha"],
            "luteal": ["Mantén, no intentes batir récords"],
        },
        "weight_loss": {
            "menstrual": ["Déficit calórico muy moderado"],
            "follicular": ["Déficit bien tolerado"],
            "ovulatory": ["Mantén nutrición para rendimiento"],
            "luteal": ["Cuidado con restricción - puede empeorar síntomas"],
        },
        "muscle_gain": {
            "menstrual": ["Prioriza recuperación y proteína"],
            "follicular": ["Óptimo para estímulo de hipertrofia"],
            "ovulatory": ["Máxima síntesis proteica potencial"],
            "luteal": ["Mantén proteína alta, volumen moderado"],
        },
        "general": {
            "menstrual": ["Escucha a tu cuerpo, descansa si necesitas"],
            "follicular": ["Buen momento para nuevos hábitos"],
            "ovulatory": ["Aprovecha la energía alta"],
            "luteal": ["Sé amable contigo misma"],
        },
    }

    return mods.get(goal, mods["general"]).get(phase, [])


def _get_activity_modifications(activity_level: str, phase: str) -> dict:
    """Genera modificaciones por nivel de actividad."""
    if activity_level == "low":
        return {"note": "Comienza gradualmente, incluso movimiento suave cuenta"}
    elif activity_level == "high":
        return {"note": "Atención a recuperación, especialmente en fase menstrual"}
    return {"note": "Nivel moderado es ideal para adaptación"}


def _create_daily_plan(phase: str, duration: int, training: dict, activity_level: str) -> list[dict]:
    """Crea plan diario para la fase."""
    plans = []
    activities = training["recommended"]

    for day in range(1, min(duration + 1, 8)):  # Máximo 7 días
        if phase == "menstrual":
            if day <= 2:
                activity = "Descanso activo o yoga suave"
            else:
                activity = activities[(day - 3) % len(activities)]
        else:
            activity = activities[(day - 1) % len(activities)]

        plans.append({
            "day": day,
            "activity": activity,
            "duration": training["duration_minutes"],
        })

    return plans


def _prepare_for_symptoms(phase: str, known_symptoms: list[str]) -> list[str]:
    """Prepara estrategias para síntomas conocidos."""
    preparations = []

    for symptom in known_symptoms:
        symptom_lower = symptom.lower()
        if symptom_lower in SYMPTOMS_DATABASE:
            symptom_info = SYMPTOMS_DATABASE[symptom_lower]
            if symptom_info["typical_phase"] == phase:
                preparations.append(f"Prepárate para {symptom_info['name_es']}: {symptom_info['strategies'][0]}")

    return preparations if preparations else ["No hay síntomas específicos a preparar para esta fase"]


def _generate_symptom_recommendations(analyzed: list, severity: str, recurring: bool) -> list[str]:
    """Genera recomendaciones generales basadas en análisis de síntomas."""
    recs = []

    if severity == "severe":
        recs.append("Síntomas severos requieren atención médica")

    if recurring:
        recs.append("Síntomas recurrentes - considera llevar un diario de síntomas")
        recs.append("Habla con tu médico sobre manejo preventivo")

    # Recomendaciones generales
    recs.extend([
        "Prioriza descanso y autocuidado",
        "Mantén hidratación adecuada",
        "No te presiones con entrenamientos intensos",
    ])

    return recs


def _calculate_hormonal_health_score(positive: int, yellow: int, red: int) -> dict:
    """Calcula score de salud hormonal."""
    if red > 0:
        return {
            "level": "attention_needed",
            "score": "LOW",
            "message": "Se detectaron señales que requieren evaluación médica",
        }
    elif yellow > 2:
        return {
            "level": "monitor",
            "score": "MODERATE",
            "message": "Algunas señales a monitorear",
        }
    elif positive >= 2:
        return {
            "level": "good",
            "score": "GOOD",
            "message": "Señales positivas de salud hormonal",
        }
    else:
        return {
            "level": "neutral",
            "score": "MODERATE",
            "message": "Información insuficiente para evaluación completa",
        }


# =============================================================================
# EXPORTACIÓN DE TOOLS
# =============================================================================


track_cycle_tool = FunctionTool(track_cycle)
get_phase_recommendations_tool = FunctionTool(get_phase_recommendations)
analyze_symptoms_tool = FunctionTool(analyze_symptoms)
create_cycle_plan_tool = FunctionTool(create_cycle_plan)
assess_hormonal_health_tool = FunctionTool(assess_hormonal_health)


ALL_TOOLS = [
    track_cycle_tool,
    get_phase_recommendations_tool,
    analyze_symptoms_tool,
    create_cycle_plan_tool,
    assess_hormonal_health_tool,
]


__all__ = [
    # Functions
    "track_cycle",
    "get_phase_recommendations",
    "analyze_symptoms",
    "create_cycle_plan",
    "assess_hormonal_health",
    # Tools
    "track_cycle_tool",
    "get_phase_recommendations_tool",
    "analyze_symptoms_tool",
    "create_cycle_plan_tool",
    "assess_hormonal_health_tool",
    "ALL_TOOLS",
    # Data
    "CYCLE_PHASES",
    "SYMPTOMS_DATABASE",
    "TRAINING_BY_PHASE",
    "NUTRITION_BY_PHASE",
    "PERIMENOPAUSE_INFO",
    # Enums
    "CyclePhase",
    "EnergyLevel",
    "ContraceptionType",
    "LifeStage",
]
