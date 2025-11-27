"""Tools para el agente WAVE.

Herramientas especializadas en recuperacion, descanso y regeneracion.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from google.adk.tools import FunctionTool


# =============================================================================
# Enums and Constants
# =============================================================================

class RecoveryType(Enum):
    """Tipos de recuperacion."""

    SLEEP = "sleep"
    ACTIVE_RECOVERY = "active_recovery"
    PASSIVE_RECOVERY = "passive_recovery"
    DELOAD = "deload"
    NUTRITION = "nutrition"


class FatigueLevel(Enum):
    """Niveles de fatiga."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"


# Recovery techniques database
RECOVERY_TECHNIQUES = {
    "sleep_optimization": {
        "name_es": "Optimizacion del Sueno",
        "type": "sleep",
        "duration_minutes": None,
        "frequency": "daily",
        "techniques": [
            {"name": "Rutina pre-sueno", "description": "30 min sin pantallas antes de dormir"},
            {"name": "Ambiente oscuro", "description": "Bloquear toda luz artificial"},
            {"name": "Temperatura fresca", "description": "Mantener habitacion a 18-20C"},
            {"name": "Horario consistente", "description": "Dormir y despertar a la misma hora"},
        ],
        "priority": 1,
    },
    "foam_rolling": {
        "name_es": "Rodillo de Espuma",
        "type": "active_recovery",
        "duration_minutes": 15,
        "frequency": "post_workout",
        "techniques": [
            {"name": "Cuadriceps", "description": "30-60 seg por lado"},
            {"name": "IT Band", "description": "30-60 seg por lado"},
            {"name": "Espalda alta", "description": "60 seg"},
            {"name": "Gluteos", "description": "30-60 seg por lado"},
        ],
        "priority": 2,
    },
    "cold_shower": {
        "name_es": "Ducha Fria",
        "type": "active_recovery",
        "duration_minutes": 3,
        "frequency": "post_workout",
        "techniques": [
            {"name": "Contraste", "description": "Alternar frio-caliente"},
            {"name": "Final frio", "description": "Terminar con agua fria"},
            {"name": "Gradual", "description": "Comenzar con 30 seg e incrementar"},
        ],
        "priority": 3,
    },
    "stretching_routine": {
        "name_es": "Rutina de Estiramiento",
        "type": "active_recovery",
        "duration_minutes": 15,
        "frequency": "daily",
        "techniques": [
            {"name": "Estatico", "description": "30-60 seg por musculo"},
            {"name": "Respiracion", "description": "Exhalar al profundizar"},
            {"name": "Relajado", "description": "Sin forzar el rango"},
        ],
        "priority": 2,
    },
    "walking": {
        "name_es": "Caminata Ligera",
        "type": "active_recovery",
        "duration_minutes": 30,
        "frequency": "rest_days",
        "techniques": [
            {"name": "Ritmo conversacional", "description": "Poder hablar comodamente"},
            {"name": "Al aire libre", "description": "Preferiblemente en naturaleza"},
            {"name": "Sin objetivo", "description": "Disfrutar el movimiento"},
        ],
        "priority": 2,
    },
    "epsom_bath": {
        "name_es": "Bano con Sales Epsom",
        "type": "passive_recovery",
        "duration_minutes": 20,
        "frequency": "weekly",
        "techniques": [
            {"name": "Temperatura tibia", "description": "No muy caliente"},
            {"name": "Sales de Epsom", "description": "2 tazas por bano"},
            {"name": "Relajacion", "description": "Sin dispositivos"},
        ],
        "priority": 3,
    },
    "meditation": {
        "name_es": "Meditacion",
        "type": "passive_recovery",
        "duration_minutes": 10,
        "frequency": "daily",
        "techniques": [
            {"name": "Respiracion", "description": "Enfocarse en la respiracion"},
            {"name": "Body scan", "description": "Recorrer el cuerpo mentalmente"},
            {"name": "Guiada", "description": "Usar app si es necesario"},
        ],
        "priority": 2,
    },
    "nap": {
        "name_es": "Siesta Corta",
        "type": "sleep",
        "duration_minutes": 20,
        "frequency": "as_needed",
        "techniques": [
            {"name": "Power nap", "description": "10-20 minutos maximo"},
            {"name": "Antes de 3pm", "description": "No afectar sueno nocturno"},
            {"name": "Ambiente oscuro", "description": "Usar antifaz si es necesario"},
        ],
        "priority": 3,
    },
    "hydration_protocol": {
        "name_es": "Protocolo de Hidratacion",
        "type": "nutrition",
        "duration_minutes": None,
        "frequency": "daily",
        "techniques": [
            {"name": "Al despertar", "description": "500ml agua al levantarse"},
            {"name": "Pre-entreno", "description": "500ml 2h antes"},
            {"name": "Durante", "description": "150-250ml cada 15-20min"},
            {"name": "Post-entreno", "description": "Reponer 150% del peso perdido"},
        ],
        "priority": 1,
    },
    "nutrition_timing": {
        "name_es": "Timing Nutricional",
        "type": "nutrition",
        "duration_minutes": None,
        "frequency": "training_days",
        "techniques": [
            {"name": "Post-entreno", "description": "Proteina + carbos dentro de 2h"},
            {"name": "Pre-sueno", "description": "Evitar comidas pesadas 3h antes"},
            {"name": "Consistencia", "description": "Horarios regulares de comida"},
        ],
        "priority": 2,
    },
}

# Deload protocols
DELOAD_PROTOCOLS = {
    "volume_reduction": {
        "name_es": "Reduccion de Volumen",
        "description": "Mantener intensidad, reducir series/reps",
        "volume_reduction_pct": 50,
        "intensity_reduction_pct": 0,
        "duration_weeks": 1,
        "best_for": ["intermediate", "advanced"],
    },
    "intensity_reduction": {
        "name_es": "Reduccion de Intensidad",
        "description": "Mantener volumen, reducir peso",
        "volume_reduction_pct": 0,
        "intensity_reduction_pct": 20,
        "duration_weeks": 1,
        "best_for": ["beginner", "intermediate"],
    },
    "full_deload": {
        "name_es": "Deload Completo",
        "description": "Reducir volumen e intensidad",
        "volume_reduction_pct": 40,
        "intensity_reduction_pct": 15,
        "duration_weeks": 1,
        "best_for": ["all_levels"],
    },
    "active_rest": {
        "name_es": "Descanso Activo",
        "description": "Solo actividad ligera, sin entrenamiento formal",
        "activities": ["walking", "swimming", "yoga", "stretching"],
        "duration_weeks": 1,
        "best_for": ["high_fatigue", "injury_prevention"],
    },
}


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class RecoveryAssessment:
    """Evaluacion de recuperacion."""

    metric: str
    score: int  # 1-5
    notes: str
    priority: str  # low, medium, high


# =============================================================================
# Tool Functions
# =============================================================================

def assess_recovery_status(
    sleep_quality: int,
    sleep_hours: float,
    muscle_soreness: int,
    energy_level: int,
    motivation: int,
    resting_hr_elevated: bool = False,
) -> dict[str, Any]:
    """Evalua el estado de recuperacion del usuario.

    Args:
        sleep_quality: Calidad del sueno 1-5
        sleep_hours: Horas de sueno
        muscle_soreness: Nivel de dolor muscular 1-5 (1=ninguno, 5=severo)
        energy_level: Nivel de energia 1-5
        motivation: Nivel de motivacion 1-5
        resting_hr_elevated: Si la FC en reposo esta elevada

    Returns:
        dict con evaluacion de recuperacion
    """
    assessments = []

    # Evaluar sueno
    sleep_score = min(sleep_quality, int(sleep_hours / 1.5))  # 7.5h = 5
    sleep_priority = "high" if sleep_score <= 2 else ("medium" if sleep_score == 3 else "low")
    assessments.append(RecoveryAssessment(
        metric="sleep",
        score=sleep_score,
        notes=f"{sleep_hours}h, calidad {sleep_quality}/5",
        priority=sleep_priority,
    ))

    # Evaluar dolor muscular (invertido, 1 es bueno)
    soreness_score = 6 - muscle_soreness
    soreness_priority = "high" if soreness_score <= 2 else ("medium" if soreness_score == 3 else "low")
    assessments.append(RecoveryAssessment(
        metric="muscle_soreness",
        score=soreness_score,
        notes="DOMS severo" if muscle_soreness >= 4 else "Dolor manejable" if muscle_soreness >= 2 else "Sin dolor significativo",
        priority=soreness_priority,
    ))

    # Evaluar energia
    energy_priority = "high" if energy_level <= 2 else ("medium" if energy_level == 3 else "low")
    assessments.append(RecoveryAssessment(
        metric="energy",
        score=energy_level,
        notes="Energia baja" if energy_level <= 2 else "Energia normal" if energy_level <= 4 else "Energia alta",
        priority=energy_priority,
    ))

    # Evaluar motivacion
    motivation_priority = "high" if motivation <= 2 else ("medium" if motivation == 3 else "low")
    assessments.append(RecoveryAssessment(
        metric="motivation",
        score=motivation,
        notes="Motivacion baja - posible fatiga mental" if motivation <= 2 else "Motivacion normal",
        priority=motivation_priority,
    ))

    # Calcular score total
    total_score = sum(a.score for a in assessments) / len(assessments)

    # Ajustar por FC elevada
    if resting_hr_elevated:
        total_score -= 0.5
        assessments.append(RecoveryAssessment(
            metric="heart_rate",
            score=2,
            notes="FC en reposo elevada - signo de fatiga acumulada",
            priority="high",
        ))

    # Determinar nivel de fatiga
    if total_score >= 4:
        fatigue_level = "low"
        recommendation = "Listo para entrenar con intensidad normal"
    elif total_score >= 3:
        fatigue_level = "moderate"
        recommendation = "Entrenar con intensidad moderada o hacer recuperacion activa"
    elif total_score >= 2:
        fatigue_level = "high"
        recommendation = "Priorizar recuperacion. Si entrena, reducir volumen/intensidad"
    else:
        fatigue_level = "severe"
        recommendation = "Descanso obligatorio. Considerar deload si persiste"

    # Generar recomendaciones especificas
    specific_recs = []
    for assessment in assessments:
        if assessment.priority == "high":
            if assessment.metric == "sleep":
                specific_recs.append("Mejorar higiene del sueno urgentemente")
            elif assessment.metric == "muscle_soreness":
                specific_recs.append("Aplicar tecnicas de recuperacion muscular")
            elif assessment.metric == "energy":
                specific_recs.append("Evaluar nutricion y descanso")
            elif assessment.metric == "motivation":
                specific_recs.append("Posible fatiga mental - considerar variacion")

    return {
        "overall_score": round(total_score, 1),
        "fatigue_level": fatigue_level,
        "main_recommendation": recommendation,
        "assessments": [
            {
                "metric": a.metric,
                "score": a.score,
                "notes": a.notes,
                "priority": a.priority,
            }
            for a in assessments
        ],
        "specific_recommendations": specific_recs,
        "ready_to_train": fatigue_level in ["low", "moderate"],
    }


def generate_recovery_protocol(
    fatigue_level: str = "moderate",
    training_type: str = "strength",
    time_available_minutes: int = 30,
    has_equipment: bool = True,
) -> dict[str, Any]:
    """Genera un protocolo de recuperacion personalizado.

    Args:
        fatigue_level: Nivel de fatiga (low, moderate, high, severe)
        training_type: Tipo de entrenamiento reciente
        time_available_minutes: Tiempo disponible para recuperacion
        has_equipment: Si tiene acceso a equipo (rodillo, etc.)

    Returns:
        dict con protocolo de recuperacion
    """
    protocol_techniques = []
    total_time = 0

    # Priorizar tecnicas segun fatiga
    if fatigue_level == "severe":
        priorities = ["sleep_optimization", "hydration_protocol", "meditation", "nap"]
    elif fatigue_level == "high":
        priorities = ["sleep_optimization", "hydration_protocol", "stretching_routine", "walking"]
    elif fatigue_level == "moderate":
        priorities = ["foam_rolling", "stretching_routine", "cold_shower", "hydration_protocol"]
    else:
        priorities = ["foam_rolling", "cold_shower", "walking"]

    # Agregar tecnicas que quepan en el tiempo
    for tech_id in priorities:
        if tech_id in RECOVERY_TECHNIQUES:
            tech = RECOVERY_TECHNIQUES[tech_id]
            tech_duration = tech["duration_minutes"] or 10

            # Verificar si requiere equipo
            if tech_id == "foam_rolling" and not has_equipment:
                continue

            if total_time + tech_duration <= time_available_minutes:
                protocol_techniques.append({
                    "technique_id": tech_id,
                    "name": tech["name_es"],
                    "type": tech["type"],
                    "duration_minutes": tech_duration,
                    "details": tech["techniques"],
                })
                total_time += tech_duration

    # Agregar recomendaciones de sueno siempre
    sleep_recs = RECOVERY_TECHNIQUES["sleep_optimization"]["techniques"]

    return {
        "fatigue_level": fatigue_level,
        "training_type": training_type,
        "protocol_techniques": protocol_techniques,
        "total_duration_minutes": total_time,
        "sleep_recommendations": sleep_recs,
        "general_notes": [
            "La recuperacion es donde ocurre la adaptacion",
            "Priorizar sueno sobre cualquier otra tecnica",
            "Escuchar al cuerpo y ajustar intensidad",
            "Hidratacion constante durante el dia",
        ],
    }


def recommend_deload(
    weeks_training: int,
    current_fatigue: str,
    experience_level: str = "intermediate",
    upcoming_event: bool = False,
) -> dict[str, Any]:
    """Recomienda un protocolo de deload.

    Args:
        weeks_training: Semanas desde ultimo deload
        current_fatigue: Nivel de fatiga actual
        experience_level: Nivel de experiencia
        upcoming_event: Si hay un evento proximo

    Returns:
        dict con recomendacion de deload
    """
    # Determinar si necesita deload
    needs_deload = False
    reasons = []

    if weeks_training >= 6:
        needs_deload = True
        reasons.append(f"{weeks_training} semanas sin deload (recomendado cada 4-6)")

    if current_fatigue in ["high", "severe"]:
        needs_deload = True
        reasons.append(f"Fatiga {current_fatigue}")

    if not needs_deload:
        return {
            "needs_deload": False,
            "message": "No se necesita deload actualmente",
            "next_deload_in_weeks": max(0, 6 - weeks_training),
            "monitoring_tips": [
                "Monitorear calidad del sueno",
                "Atencion a motivacion decreciente",
                "Notar rendimiento estancado",
            ],
        }

    # Seleccionar tipo de deload
    if current_fatigue == "severe" or upcoming_event:
        deload_type = "active_rest"
    elif experience_level == "beginner":
        deload_type = "intensity_reduction"
    elif current_fatigue == "high":
        deload_type = "full_deload"
    else:
        deload_type = "volume_reduction"

    protocol = DELOAD_PROTOCOLS[deload_type]

    return {
        "needs_deload": True,
        "reasons": reasons,
        "recommended_protocol": deload_type,
        "protocol_details": {
            "name": protocol["name_es"],
            "description": protocol["description"],
            "duration_weeks": protocol["duration_weeks"],
            "volume_change": f"-{protocol.get('volume_reduction_pct', 0)}%" if "volume_reduction_pct" in protocol else "N/A",
            "intensity_change": f"-{protocol.get('intensity_reduction_pct', 0)}%" if "intensity_reduction_pct" in protocol else "N/A",
        },
        "post_deload_tips": [
            "Retomar entrenamiento gradualmente",
            "Esperar mejoras en rendimiento post-deload",
            "Mantener buenas practicas de recuperacion",
        ],
    }


def calculate_sleep_needs(
    age: int,
    training_volume: str = "moderate",
    stress_level: str = "moderate",
    goals: str = "general_fitness",
) -> dict[str, Any]:
    """Calcula necesidades de sueno personalizadas.

    Args:
        age: Edad del usuario
        training_volume: Volumen de entrenamiento (low, moderate, high)
        stress_level: Nivel de estres (low, moderate, high)
        goals: Objetivos (muscle_building, fat_loss, performance, general_fitness)

    Returns:
        dict con recomendaciones de sueno
    """
    # Base de sueno por edad
    if age < 26:
        base_hours = 8.0
    elif age < 40:
        base_hours = 7.5
    elif age < 55:
        base_hours = 7.0
    else:
        base_hours = 6.5

    # Ajustes por volumen de entrenamiento
    volume_adjustment = {"low": 0, "moderate": 0.5, "high": 1.0}
    base_hours += volume_adjustment.get(training_volume, 0.5)

    # Ajustes por estres
    stress_adjustment = {"low": 0, "moderate": 0.25, "high": 0.5}
    base_hours += stress_adjustment.get(stress_level, 0.25)

    # Ajustes por objetivos
    goal_adjustment = {
        "muscle_building": 0.5,
        "fat_loss": 0.25,
        "performance": 0.5,
        "general_fitness": 0,
    }
    base_hours += goal_adjustment.get(goals, 0)

    # Rango recomendado
    min_hours = round(base_hours - 0.5, 1)
    max_hours = round(base_hours + 0.5, 1)
    optimal_hours = round(base_hours, 1)

    # Horarios sugeridos
    wake_times = ["6:00", "6:30", "7:00", "7:30"]
    bed_times = []
    for wake in wake_times:
        wake_hour = int(wake.split(":")[0])
        bed_hour = wake_hour - int(optimal_hours)
        if bed_hour < 0:
            bed_hour += 24
        bed_minute = 30 if (optimal_hours % 1) >= 0.5 else 0
        bed_times.append(f"{bed_hour}:{bed_minute:02d}")

    return {
        "age": age,
        "training_volume": training_volume,
        "stress_level": stress_level,
        "goals": goals,
        "recommended_sleep": {
            "minimum_hours": min_hours,
            "optimal_hours": optimal_hours,
            "maximum_hours": max_hours,
        },
        "schedule_examples": [
            {"wake_time": w, "bed_time": b}
            for w, b in zip(wake_times, bed_times)
        ],
        "quality_tips": [
            "Consistencia en horarios (incluso fines de semana)",
            "Evitar pantallas 1h antes de dormir",
            "Habitacion fresca y oscura",
            "Evitar cafeina despues de las 2pm",
            "Limitar alcohol (afecta calidad del sueno)",
        ],
        "signs_of_poor_sleep": [
            "Despertar cansado",
            "Necesitar alarma para despertar",
            "Somnolencia durante el dia",
            "Dificultad para concentrarse",
            "Rendimiento deportivo disminuido",
        ],
    }


# =============================================================================
# FunctionTool Wrappers
# =============================================================================

assess_recovery_status_tool = FunctionTool(assess_recovery_status)
generate_recovery_protocol_tool = FunctionTool(generate_recovery_protocol)
recommend_deload_tool = FunctionTool(recommend_deload)
calculate_sleep_needs_tool = FunctionTool(calculate_sleep_needs)

# Lista de todas las tools para exportar
ALL_TOOLS = [
    assess_recovery_status_tool,
    generate_recovery_protocol_tool,
    recommend_deload_tool,
    calculate_sleep_needs_tool,
]
