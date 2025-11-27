"""Tools para BLAZE - Agente de Fuerza e Hipertrofia.

Define las FunctionTools que BLAZE usa para:
- Generar workouts personalizados
- Seleccionar ejercicios apropiados
- Calcular progresión de cargas
- Trackear volumen de entrenamiento
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)

# =============================================================================
# Constants & Types
# =============================================================================


class MuscleGroup(str, Enum):
    """Grupos musculares principales."""

    CHEST = "chest"
    BACK = "back"
    SHOULDERS = "shoulders"
    BICEPS = "biceps"
    TRICEPS = "triceps"
    QUADRICEPS = "quadriceps"
    HAMSTRINGS = "hamstrings"
    GLUTES = "glutes"
    CALVES = "calves"
    CORE = "core"
    FOREARMS = "forearms"


class ExerciseType(str, Enum):
    """Tipos de ejercicio."""

    COMPOUND = "compound"
    ISOLATION = "isolation"
    CARDIO = "cardio"
    MOBILITY = "mobility"


class Equipment(str, Enum):
    """Tipos de equipo."""

    BARBELL = "barbell"
    DUMBBELL = "dumbbell"
    CABLE = "cable"
    MACHINE = "machine"
    BODYWEIGHT = "bodyweight"
    KETTLEBELL = "kettlebell"
    BANDS = "bands"


# Base de datos de ejercicios (simplificada)
EXERCISE_DATABASE: dict[str, dict[str, Any]] = {
    # Pecho
    "bench_press": {
        "name": "Bench Press",
        "name_es": "Press de Banca",
        "muscle_groups": [MuscleGroup.CHEST, MuscleGroup.TRICEPS, MuscleGroup.SHOULDERS],
        "type": ExerciseType.COMPOUND,
        "equipment": [Equipment.BARBELL],
        "difficulty": 2,
        "cues": ["Retrae escápulas", "Pies firmes en el suelo", "Baja controlado al pecho"],
    },
    "incline_dumbbell_press": {
        "name": "Incline Dumbbell Press",
        "name_es": "Press Inclinado con Mancuernas",
        "muscle_groups": [MuscleGroup.CHEST, MuscleGroup.SHOULDERS],
        "type": ExerciseType.COMPOUND,
        "equipment": [Equipment.DUMBBELL],
        "difficulty": 2,
        "cues": ["Ángulo 30-45 grados", "Codos a 45 grados", "Squeeze arriba"],
    },
    "cable_fly": {
        "name": "Cable Fly",
        "name_es": "Aperturas en Polea",
        "muscle_groups": [MuscleGroup.CHEST],
        "type": ExerciseType.ISOLATION,
        "equipment": [Equipment.CABLE],
        "difficulty": 1,
        "cues": ["Ligera flexión de codos", "Controla el negativo", "Squeeze en el centro"],
    },
    # Espalda
    "barbell_row": {
        "name": "Barbell Row",
        "name_es": "Remo con Barra",
        "muscle_groups": [MuscleGroup.BACK, MuscleGroup.BICEPS],
        "type": ExerciseType.COMPOUND,
        "equipment": [Equipment.BARBELL],
        "difficulty": 2,
        "cues": ["Espalda neutra", "Tira hacia el ombligo", "Squeeze escápulas"],
    },
    "lat_pulldown": {
        "name": "Lat Pulldown",
        "name_es": "Jalón al Pecho",
        "muscle_groups": [MuscleGroup.BACK, MuscleGroup.BICEPS],
        "type": ExerciseType.COMPOUND,
        "equipment": [Equipment.CABLE],
        "difficulty": 1,
        "cues": ["Pecho arriba", "Codos hacia abajo y atrás", "Controla la subida"],
    },
    "deadlift": {
        "name": "Deadlift",
        "name_es": "Peso Muerto",
        "muscle_groups": [MuscleGroup.BACK, MuscleGroup.HAMSTRINGS, MuscleGroup.GLUTES],
        "type": ExerciseType.COMPOUND,
        "equipment": [Equipment.BARBELL],
        "difficulty": 3,
        "cues": ["Barra pegada al cuerpo", "Empuja el piso", "Bloquea cadera arriba"],
    },
    # Piernas
    "squat": {
        "name": "Barbell Squat",
        "name_es": "Sentadilla con Barra",
        "muscle_groups": [MuscleGroup.QUADRICEPS, MuscleGroup.GLUTES],
        "type": ExerciseType.COMPOUND,
        "equipment": [Equipment.BARBELL],
        "difficulty": 3,
        "cues": ["Rodillas en línea con pies", "Profundidad paralelo o más", "Core apretado"],
    },
    "leg_press": {
        "name": "Leg Press",
        "name_es": "Prensa de Piernas",
        "muscle_groups": [MuscleGroup.QUADRICEPS, MuscleGroup.GLUTES],
        "type": ExerciseType.COMPOUND,
        "equipment": [Equipment.MACHINE],
        "difficulty": 1,
        "cues": ["Espalda baja pegada", "No bloquear rodillas", "Rango completo"],
    },
    "romanian_deadlift": {
        "name": "Romanian Deadlift",
        "name_es": "Peso Muerto Rumano",
        "muscle_groups": [MuscleGroup.HAMSTRINGS, MuscleGroup.GLUTES],
        "type": ExerciseType.COMPOUND,
        "equipment": [Equipment.BARBELL, Equipment.DUMBBELL],
        "difficulty": 2,
        "cues": ["Rodillas ligeramente flexionadas", "Cadera hacia atrás", "Estira isquios"],
    },
    "leg_curl": {
        "name": "Leg Curl",
        "name_es": "Curl de Pierna",
        "muscle_groups": [MuscleGroup.HAMSTRINGS],
        "type": ExerciseType.ISOLATION,
        "equipment": [Equipment.MACHINE],
        "difficulty": 1,
        "cues": ["Controla el movimiento", "Squeeze arriba", "No uses impulso"],
    },
    # Hombros
    "overhead_press": {
        "name": "Overhead Press",
        "name_es": "Press Militar",
        "muscle_groups": [MuscleGroup.SHOULDERS, MuscleGroup.TRICEPS],
        "type": ExerciseType.COMPOUND,
        "equipment": [Equipment.BARBELL],
        "difficulty": 2,
        "cues": ["Core apretado", "Barra sobre hombros", "Bloquea arriba"],
    },
    "lateral_raise": {
        "name": "Lateral Raise",
        "name_es": "Elevaciones Laterales",
        "muscle_groups": [MuscleGroup.SHOULDERS],
        "type": ExerciseType.ISOLATION,
        "equipment": [Equipment.DUMBBELL],
        "difficulty": 1,
        "cues": ["Ligera inclinación adelante", "Codos ligeramente flexionados", "No subas de hombros"],
    },
    # Brazos
    "barbell_curl": {
        "name": "Barbell Curl",
        "name_es": "Curl con Barra",
        "muscle_groups": [MuscleGroup.BICEPS],
        "type": ExerciseType.ISOLATION,
        "equipment": [Equipment.BARBELL],
        "difficulty": 1,
        "cues": ["Codos fijos", "Sin balanceo", "Squeeze arriba"],
    },
    "tricep_pushdown": {
        "name": "Tricep Pushdown",
        "name_es": "Extensión de Tríceps en Polea",
        "muscle_groups": [MuscleGroup.TRICEPS],
        "type": ExerciseType.ISOLATION,
        "equipment": [Equipment.CABLE],
        "difficulty": 1,
        "cues": ["Codos pegados al cuerpo", "Extensión completa", "Controla subida"],
    },
}

# Plantillas de splits
SPLIT_TEMPLATES: dict[str, dict[str, Any]] = {
    "push_pull_legs": {
        "name": "Push/Pull/Legs",
        "days_required": 3,
        "frequency": "1x por grupo muscular",
        "days": {
            "push": [MuscleGroup.CHEST, MuscleGroup.SHOULDERS, MuscleGroup.TRICEPS],
            "pull": [MuscleGroup.BACK, MuscleGroup.BICEPS],
            "legs": [MuscleGroup.QUADRICEPS, MuscleGroup.HAMSTRINGS, MuscleGroup.GLUTES, MuscleGroup.CALVES],
        },
    },
    "push_pull_legs_6": {
        "name": "Push/Pull/Legs (2x semana)",
        "days_required": 6,
        "frequency": "2x por grupo muscular",
        "days": {
            "push_1": [MuscleGroup.CHEST, MuscleGroup.SHOULDERS, MuscleGroup.TRICEPS],
            "pull_1": [MuscleGroup.BACK, MuscleGroup.BICEPS],
            "legs_1": [MuscleGroup.QUADRICEPS, MuscleGroup.HAMSTRINGS, MuscleGroup.GLUTES],
            "push_2": [MuscleGroup.CHEST, MuscleGroup.SHOULDERS, MuscleGroup.TRICEPS],
            "pull_2": [MuscleGroup.BACK, MuscleGroup.BICEPS],
            "legs_2": [MuscleGroup.QUADRICEPS, MuscleGroup.HAMSTRINGS, MuscleGroup.GLUTES],
        },
    },
    "upper_lower": {
        "name": "Upper/Lower",
        "days_required": 4,
        "frequency": "2x por grupo muscular",
        "days": {
            "upper_1": [MuscleGroup.CHEST, MuscleGroup.BACK, MuscleGroup.SHOULDERS, MuscleGroup.BICEPS, MuscleGroup.TRICEPS],
            "lower_1": [MuscleGroup.QUADRICEPS, MuscleGroup.HAMSTRINGS, MuscleGroup.GLUTES, MuscleGroup.CALVES],
            "upper_2": [MuscleGroup.CHEST, MuscleGroup.BACK, MuscleGroup.SHOULDERS, MuscleGroup.BICEPS, MuscleGroup.TRICEPS],
            "lower_2": [MuscleGroup.QUADRICEPS, MuscleGroup.HAMSTRINGS, MuscleGroup.GLUTES, MuscleGroup.CALVES],
        },
    },
    "full_body": {
        "name": "Full Body",
        "days_required": 3,
        "frequency": "3x por grupo muscular (bajo volumen)",
        "days": {
            "day_1": [MuscleGroup.CHEST, MuscleGroup.BACK, MuscleGroup.QUADRICEPS, MuscleGroup.SHOULDERS],
            "day_2": [MuscleGroup.CHEST, MuscleGroup.BACK, MuscleGroup.HAMSTRINGS, MuscleGroup.BICEPS, MuscleGroup.TRICEPS],
            "day_3": [MuscleGroup.CHEST, MuscleGroup.BACK, MuscleGroup.GLUTES, MuscleGroup.SHOULDERS],
        },
    },
}


@dataclass
class ExerciseSet:
    """Representa una serie de un ejercicio."""

    reps: int
    weight_kg: Optional[float] = None
    rpe: Optional[int] = None  # 1-10
    rest_seconds: int = 120


@dataclass
class Exercise:
    """Representa un ejercicio en un workout."""

    exercise_id: str
    name: str
    sets: list[ExerciseSet]
    notes: Optional[str] = None


# =============================================================================
# FunctionTools
# =============================================================================


def get_exercise_database(
    muscle_group: Optional[str] = None,
    equipment: Optional[str] = None,
    exercise_type: Optional[str] = None,
) -> dict[str, Any]:
    """Consulta la base de datos de ejercicios con filtros opcionales.

    Args:
        muscle_group: Filtrar por grupo muscular (chest, back, legs, etc.)
        equipment: Filtrar por equipo (barbell, dumbbell, cable, etc.)
        exercise_type: Filtrar por tipo (compound, isolation)

    Returns:
        dict con ejercicios que coinciden con los filtros
    """
    results = {}

    for ex_id, ex_data in EXERCISE_DATABASE.items():
        # Filtro por grupo muscular
        if muscle_group:
            muscle_groups = [mg.value for mg in ex_data["muscle_groups"]]
            if muscle_group.lower() not in muscle_groups:
                continue

        # Filtro por equipo
        if equipment:
            equip_list = [eq.value for eq in ex_data["equipment"]]
            if equipment.lower() not in equip_list:
                continue

        # Filtro por tipo
        if exercise_type:
            if ex_data["type"].value != exercise_type.lower():
                continue

        results[ex_id] = {
            "name": ex_data["name"],
            "name_es": ex_data["name_es"],
            "muscle_groups": [mg.value for mg in ex_data["muscle_groups"]],
            "type": ex_data["type"].value,
            "equipment": [eq.value for eq in ex_data["equipment"]],
            "difficulty": ex_data["difficulty"],
            "cues": ex_data["cues"],
        }

    return {
        "count": len(results),
        "exercises": results,
    }


def calculate_one_rep_max(weight_kg: float, reps: int, formula: str = "brzycki") -> dict[str, Any]:
    """Calcula el 1RM estimado basándose en peso y repeticiones.

    Args:
        weight_kg: Peso utilizado en kg
        reps: Número de repeticiones realizadas (1-15)
        formula: Fórmula a usar (brzycki, epley, lombardi)

    Returns:
        dict con 1RM estimado y tabla de porcentajes
    """
    if reps < 1 or reps > 15:
        return {"error": "Reps debe estar entre 1 y 15 para estimación precisa"}

    if reps == 1:
        one_rm = weight_kg
    elif formula == "brzycki":
        one_rm = weight_kg * (36 / (37 - reps))
    elif formula == "epley":
        one_rm = weight_kg * (1 + 0.0333 * reps)
    elif formula == "lombardi":
        one_rm = weight_kg * (reps ** 0.10)
    else:
        one_rm = weight_kg * (36 / (37 - reps))  # Default: Brzycki

    one_rm = round(one_rm, 1)

    # Tabla de porcentajes
    percentages = {}
    for pct in [100, 95, 90, 85, 80, 75, 70, 65, 60]:
        percentages[f"{pct}%"] = round(one_rm * (pct / 100), 1)

    # Estimación de reps por porcentaje
    rep_ranges = {
        "100%": "1 rep",
        "95%": "2 reps",
        "90%": "3-4 reps",
        "85%": "5-6 reps",
        "80%": "7-8 reps",
        "75%": "9-10 reps",
        "70%": "11-12 reps",
        "65%": "13-15 reps",
        "60%": "16-20 reps",
    }

    return {
        "estimated_1rm_kg": one_rm,
        "input": {"weight_kg": weight_kg, "reps": reps},
        "formula": formula,
        "percentage_table": percentages,
        "rep_ranges": rep_ranges,
    }


def calculate_training_volume(
    exercises: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calcula el volumen total de entrenamiento.

    Args:
        exercises: Lista de ejercicios con sets, reps y peso
                  Formato: [{"name": "Bench Press", "sets": 4, "reps": 8, "weight_kg": 80}]

    Returns:
        dict con volumen total, por grupo muscular, y análisis
    """
    total_volume = 0
    total_sets = 0
    volume_by_muscle: dict[str, int] = {}
    sets_by_muscle: dict[str, int] = {}

    for ex in exercises:
        ex_name = ex.get("name", "").lower().replace(" ", "_")
        sets = ex.get("sets", 0)
        reps = ex.get("reps", 0)
        weight = ex.get("weight_kg", 0)

        # Volumen = sets * reps * peso
        volume = sets * reps * weight
        total_volume += volume
        total_sets += sets

        # Buscar grupos musculares
        ex_data = EXERCISE_DATABASE.get(ex_name)
        if ex_data:
            for mg in ex_data["muscle_groups"]:
                mg_name = mg.value
                volume_by_muscle[mg_name] = volume_by_muscle.get(mg_name, 0) + volume
                sets_by_muscle[mg_name] = sets_by_muscle.get(mg_name, 0) + sets

    # Análisis de volumen
    analysis = []
    for muscle, sets_count in sets_by_muscle.items():
        if sets_count < 10:
            analysis.append(f"{muscle}: {sets_count} sets - Bajo (considera añadir volumen)")
        elif sets_count > 20:
            analysis.append(f"{muscle}: {sets_count} sets - Alto (considera reducir si hay fatiga)")
        else:
            analysis.append(f"{muscle}: {sets_count} sets - Adecuado")

    return {
        "total_volume_kg": round(total_volume, 1),
        "total_sets": total_sets,
        "volume_by_muscle_group": volume_by_muscle,
        "sets_by_muscle_group": sets_by_muscle,
        "analysis": analysis,
    }


def suggest_progression(
    current_weight_kg: float,
    current_reps: int,
    target_reps_min: int,
    target_reps_max: int,
    rpe_last_set: int,
    weeks_at_current: int = 1,
) -> dict[str, Any]:
    """Sugiere progresión basada en rendimiento actual.

    Args:
        current_weight_kg: Peso actual usado
        current_reps: Reps alcanzados en última sesión
        target_reps_min: Mínimo de reps objetivo
        target_reps_max: Máximo de reps objetivo
        rpe_last_set: RPE de la última serie (1-10)
        weeks_at_current: Semanas usando el peso actual

    Returns:
        dict con recomendación de progresión
    """
    recommendation = {
        "current": {"weight_kg": current_weight_kg, "reps": current_reps, "rpe": rpe_last_set},
        "ready_to_progress": False,
        "progression_type": None,
        "new_weight_kg": current_weight_kg,
        "new_rep_target": f"{target_reps_min}-{target_reps_max}",
        "reasoning": "",
        "caution": None,
    }

    # Criterios para progresar
    hit_top_of_range = current_reps >= target_reps_max
    rpe_manageable = rpe_last_set <= 8
    sufficient_time = weeks_at_current >= 1

    if hit_top_of_range and rpe_manageable and sufficient_time:
        # Listo para progresar en peso
        recommendation["ready_to_progress"] = True
        recommendation["progression_type"] = "weight_increase"

        # Incremento típico: 2.5kg para upper, 5kg para lower
        increment = 2.5
        recommendation["new_weight_kg"] = current_weight_kg + increment
        recommendation["reasoning"] = (
            f"Alcanzaste {current_reps} reps (top del rango) con RPE {rpe_last_set}. "
            f"Incrementa a {current_weight_kg + increment}kg y apunta a {target_reps_min} reps."
        )

    elif current_reps < target_reps_min:
        # No alcanza mínimo - mantener peso
        recommendation["progression_type"] = "maintain"
        recommendation["reasoning"] = (
            f"Solo {current_reps} reps (debajo del mínimo {target_reps_min}). "
            f"Mantén {current_weight_kg}kg hasta alcanzar el rango objetivo."
        )

        if rpe_last_set >= 9:
            recommendation["caution"] = "RPE muy alto. Considera un deload si persiste."

    elif rpe_last_set >= 9:
        # RPE muy alto - no progresar aún
        recommendation["progression_type"] = "maintain"
        recommendation["reasoning"] = (
            f"Reps en rango ({current_reps}) pero RPE alto ({rpe_last_set}). "
            f"Consolida antes de añadir peso."
        )

    else:
        # En rango pero no en top - añadir reps
        recommendation["progression_type"] = "rep_increase"
        recommendation["reasoning"] = (
            f"Estás en rango ({current_reps} reps). "
            f"Intenta añadir 1-2 reps antes de subir peso."
        )

    return recommendation


def generate_workout_split(
    days_per_week: int,
    experience_level: str,
    primary_goal: str,
) -> dict[str, Any]:
    """Genera un split de entrenamiento recomendado.

    Args:
        days_per_week: Días disponibles para entrenar (2-6)
        experience_level: Nivel (beginner, intermediate, advanced)
        primary_goal: Objetivo (hypertrophy, strength, general_fitness)

    Returns:
        dict con split recomendado y estructura de días
    """
    # Seleccionar template basado en días
    if days_per_week <= 2:
        split = SPLIT_TEMPLATES["full_body"]
        recommendation = (
            "Con 2 días, Full Body es ideal. Entrena todos los grupos principales "
            "cada sesión con volumen moderado."
        )
    elif days_per_week == 3:
        if experience_level == "beginner":
            split = SPLIT_TEMPLATES["full_body"]
            recommendation = (
                "Para principiantes, Full Body 3x/semana permite alta frecuencia "
                "y práctica de movimientos."
            )
        else:
            split = SPLIT_TEMPLATES["push_pull_legs"]
            recommendation = (
                "Push/Pull/Legs es excelente para 3 días. Cada grupo muscular "
                "se trabaja 1x/semana con buen volumen."
            )
    elif days_per_week == 4:
        split = SPLIT_TEMPLATES["upper_lower"]
        recommendation = (
            "Upper/Lower 4x/semana ofrece buena frecuencia (2x/grupo) "
            "con suficiente recuperación."
        )
    elif days_per_week >= 5:
        split = SPLIT_TEMPLATES["push_pull_legs_6"]
        recommendation = (
            "PPL 2x/semana (6 días) maximiza frecuencia y volumen. "
            "Ideal para usuarios avanzados con buena recuperación."
        )
    else:
        split = SPLIT_TEMPLATES["upper_lower"]
        recommendation = "Upper/Lower es versátil para la mayoría de usuarios."

    # Ajustes por objetivo
    volume_recommendation = ""
    if primary_goal == "hypertrophy":
        volume_recommendation = "Para hipertrofia: 10-20 sets/grupo/semana, RPE 7-9."
    elif primary_goal == "strength":
        volume_recommendation = "Para fuerza: 6-12 sets/grupo/semana en compuestos principales, alta intensidad."
    else:
        volume_recommendation = "Para fitness general: 8-15 sets/grupo/semana, variedad de rangos de reps."

    return {
        "split_name": split["name"],
        "days_required": split["days_required"],
        "frequency": split["frequency"],
        "structure": {day: [mg.value for mg in muscles] for day, muscles in split["days"].items()},
        "recommendation": recommendation,
        "volume_recommendation": volume_recommendation,
        "experience_level": experience_level,
        "primary_goal": primary_goal,
    }


# =============================================================================
# Wrapped FunctionTools for ADK
# =============================================================================

get_exercise_database_tool = FunctionTool(get_exercise_database)
calculate_one_rep_max_tool = FunctionTool(calculate_one_rep_max)
calculate_training_volume_tool = FunctionTool(calculate_training_volume)
suggest_progression_tool = FunctionTool(suggest_progression)
generate_workout_split_tool = FunctionTool(generate_workout_split)

# Lista de todas las tools disponibles
ALL_TOOLS = [
    get_exercise_database_tool,
    calculate_one_rep_max_tool,
    calculate_training_volume_tool,
    suggest_progression_tool,
    generate_workout_split_tool,
]
