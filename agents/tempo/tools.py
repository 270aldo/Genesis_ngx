"""Tools para el agente TEMPO.

Herramientas especializadas en cardio, resistencia y entrenamiento de intervalos.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from google.adk.tools import FunctionTool


# =============================================================================
# Enums and Constants
# =============================================================================

class CardioType(Enum):
    """Tipos de entrenamiento cardiovascular."""

    HIIT = "hiit"
    LISS = "liss"
    FARTLEK = "fartlek"
    TEMPO_RUN = "tempo_run"
    INTERVALS = "intervals"
    CIRCUIT = "circuit"


class CardioModality(Enum):
    """Modalidades de cardio."""

    RUNNING = "running"
    CYCLING = "cycling"
    ROWING = "rowing"
    SWIMMING = "swimming"
    JUMP_ROPE = "jump_rope"
    STAIR_CLIMBER = "stair_climber"
    ELLIPTICAL = "elliptical"


# Heart rate zones (percentage of max HR)
HR_ZONES = {
    "zone_1": {
        "name": "Recovery",
        "name_es": "Recuperacion",
        "min_pct": 50,
        "max_pct": 60,
        "rpe": "2-3",
        "description": "Muy facil, conversacion normal",
    },
    "zone_2": {
        "name": "Aerobic Base",
        "name_es": "Base Aerobica",
        "min_pct": 60,
        "max_pct": 70,
        "rpe": "3-4",
        "description": "Facil, puede hablar en oraciones",
    },
    "zone_3": {
        "name": "Tempo",
        "name_es": "Tempo",
        "min_pct": 70,
        "max_pct": 80,
        "rpe": "5-6",
        "description": "Moderado, habla entrecortada",
    },
    "zone_4": {
        "name": "Threshold",
        "name_es": "Umbral",
        "min_pct": 80,
        "max_pct": 90,
        "rpe": "7-8",
        "description": "Dificil, solo palabras sueltas",
    },
    "zone_5": {
        "name": "VO2max",
        "name_es": "VO2max",
        "min_pct": 90,
        "max_pct": 100,
        "rpe": "9-10",
        "description": "Maximo esfuerzo, no puede hablar",
    },
}

# Session templates
SESSION_TEMPLATES = {
    "hiit_beginner": {
        "name_es": "HIIT Principiante",
        "type": "hiit",
        "duration_minutes": 20,
        "work_seconds": 20,
        "rest_seconds": 40,
        "rounds": 10,
        "work_zone": "zone_4",
        "rest_zone": "zone_2",
        "modalities": ["cycling", "rowing", "elliptical"],
    },
    "hiit_intermediate": {
        "name_es": "HIIT Intermedio",
        "type": "hiit",
        "duration_minutes": 25,
        "work_seconds": 30,
        "rest_seconds": 30,
        "rounds": 15,
        "work_zone": "zone_4",
        "rest_zone": "zone_2",
        "modalities": ["running", "cycling", "rowing"],
    },
    "hiit_advanced": {
        "name_es": "HIIT Avanzado",
        "type": "hiit",
        "duration_minutes": 30,
        "work_seconds": 40,
        "rest_seconds": 20,
        "rounds": 20,
        "work_zone": "zone_5",
        "rest_zone": "zone_2",
        "modalities": ["running", "cycling", "rowing"],
    },
    "liss_fat_burn": {
        "name_es": "LISS Quema Grasa",
        "type": "liss",
        "duration_minutes": 45,
        "target_zone": "zone_2",
        "modalities": ["walking", "cycling", "elliptical"],
    },
    "liss_endurance": {
        "name_es": "LISS Resistencia",
        "type": "liss",
        "duration_minutes": 60,
        "target_zone": "zone_2",
        "modalities": ["running", "cycling", "swimming"],
    },
    "tempo_run": {
        "name_es": "Carrera Tempo",
        "type": "tempo_run",
        "duration_minutes": 30,
        "warmup_minutes": 10,
        "tempo_minutes": 15,
        "cooldown_minutes": 5,
        "target_zone": "zone_3",
        "modalities": ["running"],
    },
    "fartlek": {
        "name_es": "Fartlek",
        "type": "fartlek",
        "duration_minutes": 35,
        "intervals": [
            {"type": "easy", "duration_minutes": 5, "zone": "zone_2"},
            {"type": "fast", "duration_minutes": 2, "zone": "zone_4"},
            {"type": "easy", "duration_minutes": 3, "zone": "zone_2"},
            {"type": "fast", "duration_minutes": 1, "zone": "zone_5"},
            {"type": "easy", "duration_minutes": 4, "zone": "zone_2"},
            {"type": "moderate", "duration_minutes": 5, "zone": "zone_3"},
            {"type": "easy", "duration_minutes": 3, "zone": "zone_2"},
            {"type": "fast", "duration_minutes": 2, "zone": "zone_4"},
            {"type": "easy", "duration_minutes": 5, "zone": "zone_2"},
        ],
        "modalities": ["running"],
    },
    "pyramid_intervals": {
        "name_es": "Intervalos Piramide",
        "type": "intervals",
        "duration_minutes": 35,
        "structure": [
            {"work_seconds": 30, "rest_seconds": 30},
            {"work_seconds": 60, "rest_seconds": 60},
            {"work_seconds": 90, "rest_seconds": 90},
            {"work_seconds": 120, "rest_seconds": 120},
            {"work_seconds": 90, "rest_seconds": 90},
            {"work_seconds": 60, "rest_seconds": 60},
            {"work_seconds": 30, "rest_seconds": 30},
        ],
        "work_zone": "zone_4",
        "rest_zone": "zone_2",
        "modalities": ["running", "cycling", "rowing"],
    },
    "metabolic_circuit": {
        "name_es": "Circuito Metabolico",
        "type": "circuit",
        "duration_minutes": 25,
        "exercises": [
            "burpees",
            "mountain_climbers",
            "jump_squats",
            "high_knees",
            "box_jumps",
        ],
        "work_seconds": 40,
        "rest_seconds": 20,
        "rounds": 4,
        "work_zone": "zone_4",
        "modalities": ["bodyweight"],
    },
}


# =============================================================================
# Tool Functions
# =============================================================================

def calculate_heart_rate_zones(
    age: int,
    resting_hr: int | None = None,
    method: str = "age_based",
) -> dict[str, Any]:
    """Calcula zonas de frecuencia cardiaca.

    Args:
        age: Edad del usuario
        resting_hr: Frecuencia cardiaca en reposo (opcional)
        method: Metodo de calculo (age_based, karvonen)

    Returns:
        dict con zonas de frecuencia cardiaca
    """
    # Calcular max HR usando formula de Tanaka
    max_hr = 208 - (0.7 * age)

    zones = {}

    if method == "karvonen" and resting_hr:
        # Metodo Karvonen (Heart Rate Reserve)
        hrr = max_hr - resting_hr
        for zone_id, zone_data in HR_ZONES.items():
            min_hr = round(resting_hr + (hrr * zone_data["min_pct"] / 100))
            max_hr_zone = round(resting_hr + (hrr * zone_data["max_pct"] / 100))
            zones[zone_id] = {
                "name": zone_data["name"],
                "name_es": zone_data["name_es"],
                "min_hr": min_hr,
                "max_hr": max_hr_zone,
                "rpe": zone_data["rpe"],
                "description": zone_data["description"],
            }
    else:
        # Metodo basado en edad (porcentaje de max HR)
        for zone_id, zone_data in HR_ZONES.items():
            min_hr = round(max_hr * zone_data["min_pct"] / 100)
            max_hr_zone = round(max_hr * zone_data["max_pct"] / 100)
            zones[zone_id] = {
                "name": zone_data["name"],
                "name_es": zone_data["name_es"],
                "min_hr": min_hr,
                "max_hr": max_hr_zone,
                "rpe": zone_data["rpe"],
                "description": zone_data["description"],
            }

    return {
        "age": age,
        "estimated_max_hr": round(max_hr),
        "resting_hr": resting_hr,
        "method": method,
        "zones": zones,
    }


def generate_cardio_session(
    session_type: str = "hiit_intermediate",
    duration_minutes: int | None = None,
    modality: str | None = None,
    age: int = 35,
) -> dict[str, Any]:
    """Genera una sesion de cardio estructurada.

    Args:
        session_type: Tipo de sesion (hiit_beginner, liss_fat_burn, etc.)
        duration_minutes: Duracion personalizada (opcional)
        modality: Modalidad preferida (running, cycling, etc.)
        age: Edad para calcular zonas HR

    Returns:
        dict con sesion estructurada
    """
    # Obtener template
    if session_type in SESSION_TEMPLATES:
        template = SESSION_TEMPLATES[session_type]
    else:
        template = SESSION_TEMPLATES["hiit_intermediate"]

    # Calcular zonas HR
    hr_zones = calculate_heart_rate_zones(age)

    # Determinar modalidad
    if modality and modality in template.get("modalities", []):
        selected_modality = modality
    else:
        selected_modality = template.get("modalities", ["running"])[0]

    # Duracion
    final_duration = duration_minutes or template["duration_minutes"]

    # Construir sesion segun tipo
    session = {
        "name": template["name_es"],
        "type": template["type"],
        "modality": selected_modality,
        "duration_minutes": final_duration,
        "warmup": {
            "duration_minutes": 5,
            "zone": "zone_1",
            "hr_range": f"{hr_zones['zones']['zone_1']['min_hr']}-{hr_zones['zones']['zone_1']['max_hr']} bpm",
            "instructions": "Comenzar muy suave, aumentar gradualmente",
        },
        "cooldown": {
            "duration_minutes": 3,
            "zone": "zone_1",
            "hr_range": f"{hr_zones['zones']['zone_1']['min_hr']}-{hr_zones['zones']['zone_1']['max_hr']} bpm",
            "instructions": "Reducir intensidad gradualmente hasta reposo",
        },
    }

    # Agregar detalles segun tipo
    if template["type"] == "hiit":
        work_zone = template["work_zone"]
        rest_zone = template["rest_zone"]
        session["main_work"] = {
            "rounds": template["rounds"],
            "work_seconds": template["work_seconds"],
            "rest_seconds": template["rest_seconds"],
            "work_zone": work_zone,
            "work_hr_range": f"{hr_zones['zones'][work_zone]['min_hr']}-{hr_zones['zones'][work_zone]['max_hr']} bpm",
            "rest_zone": rest_zone,
            "rest_hr_range": f"{hr_zones['zones'][rest_zone]['min_hr']}-{hr_zones['zones'][rest_zone]['max_hr']} bpm",
            "work_rpe": hr_zones["zones"][work_zone]["rpe"],
        }

    elif template["type"] == "liss":
        target_zone = template["target_zone"]
        session["main_work"] = {
            "duration_minutes": final_duration - 8,  # menos warmup y cooldown
            "target_zone": target_zone,
            "hr_range": f"{hr_zones['zones'][target_zone]['min_hr']}-{hr_zones['zones'][target_zone]['max_hr']} bpm",
            "rpe": hr_zones["zones"][target_zone]["rpe"],
            "instructions": "Mantener ritmo constante y sostenible",
        }

    elif template["type"] == "fartlek":
        session["main_work"] = {
            "intervals": template["intervals"],
            "instructions": "Variar intensidad segun como te sientas",
        }

    elif template["type"] == "tempo_run":
        target_zone = template["target_zone"]
        session["main_work"] = {
            "warmup_minutes": template["warmup_minutes"],
            "tempo_minutes": template["tempo_minutes"],
            "cooldown_minutes": template["cooldown_minutes"],
            "target_zone": target_zone,
            "hr_range": f"{hr_zones['zones'][target_zone]['min_hr']}-{hr_zones['zones'][target_zone]['max_hr']} bpm",
            "rpe": hr_zones["zones"][target_zone]["rpe"],
            "instructions": "Ritmo comfortablemente dificil",
        }

    elif template["type"] == "intervals":
        work_zone = template["work_zone"]
        rest_zone = template["rest_zone"]
        session["main_work"] = {
            "structure": template["structure"],
            "work_zone": work_zone,
            "rest_zone": rest_zone,
            "instructions": "Intervalos progresivos en piramide",
        }

    elif template["type"] == "circuit":
        session["main_work"] = {
            "exercises": template["exercises"],
            "work_seconds": template["work_seconds"],
            "rest_seconds": template["rest_seconds"],
            "rounds": template["rounds"],
            "instructions": "Moverse entre ejercicios sin descanso extra",
        }

    session["hr_zones"] = hr_zones["zones"]
    session["notes"] = [
        "Ajustar intensidad segun sensaciones del dia",
        "Hidratarse antes, durante y despues",
        "Si RPE es demasiado alto, reducir intensidad",
    ]

    return session


def suggest_cardio_for_goals(
    primary_goal: str,
    days_per_week: int = 3,
    experience_level: str = "intermediate",
    available_time_minutes: int = 30,
) -> dict[str, Any]:
    """Sugiere un plan de cardio basado en objetivos.

    Args:
        primary_goal: Objetivo principal (fat_loss, endurance, performance, general_fitness)
        days_per_week: Dias disponibles para cardio
        experience_level: Nivel de experiencia (beginner, intermediate, advanced)
        available_time_minutes: Tiempo disponible por sesion

    Returns:
        dict con plan de cardio semanal
    """
    recommendations = {
        "fat_loss": {
            "beginner": {
                "sessions": [
                    {"type": "liss_fat_burn", "days": [1, 3, 5]},
                ],
                "ratio": "100% LISS",
                "notes": "Enfocarse en crear habito y base aerobica",
            },
            "intermediate": {
                "sessions": [
                    {"type": "hiit_intermediate", "days": [1, 4]},
                    {"type": "liss_fat_burn", "days": [2, 6]},
                ],
                "ratio": "50% HIIT, 50% LISS",
                "notes": "Combinar HIIT para metabolismo y LISS para volumen",
            },
            "advanced": {
                "sessions": [
                    {"type": "hiit_advanced", "days": [1, 4]},
                    {"type": "liss_fat_burn", "days": [2, 5]},
                    {"type": "metabolic_circuit", "days": [6]},
                ],
                "ratio": "40% HIIT, 40% LISS, 20% Circuitos",
                "notes": "Alta variedad para evitar adaptacion",
            },
        },
        "endurance": {
            "beginner": {
                "sessions": [
                    {"type": "liss_fat_burn", "days": [1, 3, 5]},
                ],
                "ratio": "100% LISS",
                "notes": "Construir base aerobica solida",
            },
            "intermediate": {
                "sessions": [
                    {"type": "liss_endurance", "days": [1, 4]},
                    {"type": "tempo_run", "days": [2]},
                    {"type": "fartlek", "days": [6]},
                ],
                "ratio": "50% LISS, 25% Tempo, 25% Fartlek",
                "notes": "Modelo polarizado con variedad",
            },
            "advanced": {
                "sessions": [
                    {"type": "liss_endurance", "days": [1, 5]},
                    {"type": "tempo_run", "days": [2]},
                    {"type": "pyramid_intervals", "days": [4]},
                    {"type": "fartlek", "days": [6]},
                ],
                "ratio": "40% LISS, 20% Tempo, 20% Intervalos, 20% Fartlek",
                "notes": "Alta variedad y volumen",
            },
        },
        "performance": {
            "beginner": {
                "sessions": [
                    {"type": "hiit_beginner", "days": [1, 4]},
                    {"type": "liss_fat_burn", "days": [2]},
                ],
                "ratio": "60% HIIT, 40% LISS",
                "notes": "Desarrollar capacidad anaerobica",
            },
            "intermediate": {
                "sessions": [
                    {"type": "hiit_intermediate", "days": [1, 4]},
                    {"type": "pyramid_intervals", "days": [2]},
                    {"type": "liss_fat_burn", "days": [6]},
                ],
                "ratio": "50% HIIT, 25% Intervalos, 25% LISS",
                "notes": "Enfasis en trabajo de alta intensidad",
            },
            "advanced": {
                "sessions": [
                    {"type": "hiit_advanced", "days": [1, 4]},
                    {"type": "pyramid_intervals", "days": [2]},
                    {"type": "metabolic_circuit", "days": [5]},
                    {"type": "liss_fat_burn", "days": [6]},
                ],
                "ratio": "40% HIIT, 20% Intervalos, 20% Circuitos, 20% LISS",
                "notes": "Maxima intensidad con recuperacion activa",
            },
        },
        "general_fitness": {
            "beginner": {
                "sessions": [
                    {"type": "liss_fat_burn", "days": [1, 4]},
                    {"type": "hiit_beginner", "days": [2]},
                ],
                "ratio": "60% LISS, 40% HIIT",
                "notes": "Balance entre modalidades",
            },
            "intermediate": {
                "sessions": [
                    {"type": "hiit_intermediate", "days": [1]},
                    {"type": "liss_fat_burn", "days": [3]},
                    {"type": "fartlek", "days": [5]},
                ],
                "ratio": "33% HIIT, 33% LISS, 33% Fartlek",
                "notes": "Variedad para fitness general",
            },
            "advanced": {
                "sessions": [
                    {"type": "hiit_advanced", "days": [1]},
                    {"type": "tempo_run", "days": [2]},
                    {"type": "liss_endurance", "days": [4]},
                    {"type": "metabolic_circuit", "days": [6]},
                ],
                "ratio": "25% cada tipo",
                "notes": "Desarrollo completo de todas las capacidades",
            },
        },
    }

    # Obtener recomendacion
    goal_key = primary_goal.lower().replace(" ", "_")
    if goal_key not in recommendations:
        goal_key = "general_fitness"

    level_key = experience_level.lower()
    if level_key not in recommendations[goal_key]:
        level_key = "intermediate"

    plan = recommendations[goal_key][level_key]

    # Ajustar segun dias disponibles
    sessions_to_include = []
    for session_config in plan["sessions"]:
        session_type = session_config["type"]
        for day in session_config["days"]:
            if len(sessions_to_include) < days_per_week:
                sessions_to_include.append({
                    "day": day,
                    "session_type": session_type,
                    "template": SESSION_TEMPLATES.get(session_type, {}),
                })

    return {
        "goal": primary_goal,
        "experience_level": experience_level,
        "days_per_week": days_per_week,
        "time_per_session": available_time_minutes,
        "weekly_plan": sessions_to_include[:days_per_week],
        "training_ratio": plan["ratio"],
        "weekly_notes": plan["notes"],
        "general_tips": [
            "No hacer HIIT dos dias seguidos",
            "Permitir 48h de recuperacion entre sesiones intensas",
            "LISS puede hacerse mas frecuentemente",
            "Escuchar al cuerpo y ajustar segun fatiga",
        ],
    }


def calculate_calories_burned(
    duration_minutes: int,
    intensity: str = "moderate",
    body_weight_kg: float = 70.0,
    activity_type: str = "running",
) -> dict[str, Any]:
    """Calcula calorias quemadas aproximadas.

    Args:
        duration_minutes: Duracion del ejercicio
        intensity: Intensidad (low, moderate, high, very_high)
        body_weight_kg: Peso corporal en kg
        activity_type: Tipo de actividad

    Returns:
        dict con estimacion de calorias
    """
    # METs aproximados por actividad e intensidad
    mets_table = {
        "running": {"low": 6.0, "moderate": 9.0, "high": 11.0, "very_high": 14.0},
        "cycling": {"low": 4.0, "moderate": 6.5, "high": 10.0, "very_high": 12.0},
        "rowing": {"low": 4.5, "moderate": 7.0, "high": 10.0, "very_high": 12.0},
        "swimming": {"low": 5.0, "moderate": 7.0, "high": 10.0, "very_high": 11.0},
        "jump_rope": {"low": 8.0, "moderate": 10.0, "high": 12.0, "very_high": 14.0},
        "elliptical": {"low": 4.0, "moderate": 5.5, "high": 8.0, "very_high": 10.0},
        "walking": {"low": 2.5, "moderate": 3.5, "high": 5.0, "very_high": 6.5},
    }

    # Obtener MET
    activity = activity_type.lower()
    if activity not in mets_table:
        activity = "running"

    intensity_key = intensity.lower()
    if intensity_key not in mets_table[activity]:
        intensity_key = "moderate"

    met = mets_table[activity][intensity_key]

    # Calcular calorias: MET * peso (kg) * tiempo (horas)
    calories = met * body_weight_kg * (duration_minutes / 60)

    return {
        "duration_minutes": duration_minutes,
        "activity": activity,
        "intensity": intensity,
        "body_weight_kg": body_weight_kg,
        "met_value": met,
        "estimated_calories": round(calories),
        "calories_per_minute": round(calories / duration_minutes, 1),
        "note": "Estimacion aproximada. Valores reales varian segun individuo.",
    }


# =============================================================================
# FunctionTool Wrappers
# =============================================================================

calculate_heart_rate_zones_tool = FunctionTool(calculate_heart_rate_zones)
generate_cardio_session_tool = FunctionTool(generate_cardio_session)
suggest_cardio_for_goals_tool = FunctionTool(suggest_cardio_for_goals)
calculate_calories_burned_tool = FunctionTool(calculate_calories_burned)

# Lista de todas las tools para exportar
ALL_TOOLS = [
    calculate_heart_rate_zones_tool,
    generate_cardio_session_tool,
    suggest_cardio_for_goals_tool,
    calculate_calories_burned_tool,
]
