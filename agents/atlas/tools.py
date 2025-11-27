"""Tools para el agente ATLAS.

Herramientas especializadas en movilidad, flexibilidad y movimiento funcional.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from google.adk.tools import FunctionTool


# =============================================================================
# Mobility Exercise Database
# =============================================================================

MOBILITY_EXERCISES = {
    # Hombros
    "shoulder_circles": {
        "name_es": "Circulos de Hombro",
        "joint": "shoulder",
        "type": "mobility",
        "duration_seconds": 30,
        "reps": None,
        "cues": [
            "Brazos extendidos a los lados",
            "Circulos pequenos, aumentar gradualmente",
            "Mantener core activado",
        ],
        "targets": ["deltoides", "manguito_rotador"],
        "difficulty": 1,
    },
    "wall_slides": {
        "name_es": "Deslizamientos en Pared",
        "joint": "shoulder",
        "type": "mobility",
        "duration_seconds": None,
        "reps": 10,
        "cues": [
            "Espalda pegada a la pared",
            "Codos y munecas contra la pared",
            "Deslizar arriba manteniendo contacto",
        ],
        "targets": ["escapula", "manguito_rotador"],
        "difficulty": 2,
    },
    "shoulder_dislocates": {
        "name_es": "Dislocaciones con Banda",
        "joint": "shoulder",
        "type": "mobility",
        "duration_seconds": None,
        "reps": 15,
        "cues": [
            "Agarre amplio con banda o palo",
            "Pasar por encima de la cabeza sin doblar codos",
            "Movimiento controlado",
        ],
        "targets": ["pectoral", "dorsal", "manguito_rotador"],
        "difficulty": 2,
    },
    # Caderas
    "hip_circles": {
        "name_es": "Circulos de Cadera",
        "joint": "hip",
        "type": "mobility",
        "duration_seconds": 30,
        "reps": None,
        "cues": [
            "Manos en la cadera",
            "Circulos amplios y controlados",
            "Ambas direcciones",
        ],
        "targets": ["cadera", "core"],
        "difficulty": 1,
    },
    "90_90_stretch": {
        "name_es": "Estiramiento 90/90",
        "joint": "hip",
        "type": "flexibility",
        "duration_seconds": 60,
        "reps": None,
        "cues": [
            "Ambas piernas en 90 grados",
            "Pecho hacia la rodilla frontal",
            "Mantener espalda recta",
        ],
        "targets": ["rotadores_externos", "rotadores_internos"],
        "difficulty": 2,
    },
    "pigeon_pose": {
        "name_es": "Postura de Paloma",
        "joint": "hip",
        "type": "flexibility",
        "duration_seconds": 90,
        "reps": None,
        "cues": [
            "Pierna frontal cruzada, rodilla hacia afuera",
            "Pierna trasera extendida",
            "Bajar gradualmente el torso",
        ],
        "targets": ["gluteo", "piriforme", "flexores_cadera"],
        "difficulty": 3,
    },
    "hip_flexor_stretch": {
        "name_es": "Estiramiento de Flexores de Cadera",
        "joint": "hip",
        "type": "flexibility",
        "duration_seconds": 60,
        "reps": None,
        "cues": [
            "Rodilla trasera en el suelo",
            "Pelvis en retroversion (meter cola)",
            "Mantener torso erguido",
        ],
        "targets": ["psoas", "recto_femoral"],
        "difficulty": 2,
    },
    "deep_squat_hold": {
        "name_es": "Sentadilla Profunda Sostenida",
        "joint": "hip",
        "type": "mobility",
        "duration_seconds": 60,
        "reps": None,
        "cues": [
            "Pies ligeramente mas anchos que hombros",
            "Rodillas siguiendo direccion de pies",
            "Pecho arriba, espalda recta",
        ],
        "targets": ["cadera", "tobillo", "columna"],
        "difficulty": 2,
    },
    # Columna
    "cat_cow": {
        "name_es": "Gato-Vaca",
        "joint": "spine",
        "type": "mobility",
        "duration_seconds": None,
        "reps": 10,
        "cues": [
            "Cuatro puntos (manos y rodillas)",
            "Arquear y redondear la espalda",
            "Coordinar con respiracion",
        ],
        "targets": ["columna_toracica", "columna_lumbar"],
        "difficulty": 1,
    },
    "thoracic_rotation": {
        "name_es": "Rotacion Toracica",
        "joint": "spine",
        "type": "mobility",
        "duration_seconds": None,
        "reps": 10,
        "cues": [
            "Cuatro puntos, una mano detras de la cabeza",
            "Rotar abriendo el codo hacia el techo",
            "Mantener cadera estable",
        ],
        "targets": ["columna_toracica"],
        "difficulty": 2,
    },
    "jefferson_curl": {
        "name_es": "Jefferson Curl",
        "joint": "spine",
        "type": "flexibility",
        "duration_seconds": None,
        "reps": 5,
        "cues": [
            "De pie en superficie elevada",
            "Bajar vertebra por vertebra",
            "Sin peso o peso muy ligero",
        ],
        "targets": ["columna", "isquiotibiales"],
        "difficulty": 3,
    },
    # Tobillos
    "ankle_circles": {
        "name_es": "Circulos de Tobillo",
        "joint": "ankle",
        "type": "mobility",
        "duration_seconds": 30,
        "reps": None,
        "cues": [
            "Levantar un pie del suelo",
            "Circulos amplios con el pie",
            "Ambas direcciones",
        ],
        "targets": ["tobillo"],
        "difficulty": 1,
    },
    "wall_ankle_stretch": {
        "name_es": "Estiramiento de Tobillo en Pared",
        "joint": "ankle",
        "type": "mobility",
        "duration_seconds": 60,
        "reps": None,
        "cues": [
            "Pie cerca de la pared, rodilla hacia adelante",
            "Talon pegado al suelo",
            "Empujar rodilla hacia la pared",
        ],
        "targets": ["tobillo", "soleo"],
        "difficulty": 2,
    },
    "calf_stretch": {
        "name_es": "Estiramiento de Pantorrilla",
        "joint": "ankle",
        "type": "flexibility",
        "duration_seconds": 45,
        "reps": None,
        "cues": [
            "Pierna trasera extendida",
            "Talon trasero en el suelo",
            "Inclinar hacia adelante",
        ],
        "targets": ["gastrocnemio", "soleo"],
        "difficulty": 1,
    },
}

# Plantillas de rutinas por objetivo
ROUTINE_TEMPLATES = {
    "warmup": {
        "name_es": "Calentamiento de Movilidad",
        "duration_minutes": 10,
        "exercises": ["hip_circles", "shoulder_circles", "cat_cow", "ankle_circles", "deep_squat_hold"],
        "description": "Preparacion articular antes del entrenamiento",
    },
    "hip_focus": {
        "name_es": "Movilidad de Cadera",
        "duration_minutes": 15,
        "exercises": ["hip_circles", "90_90_stretch", "hip_flexor_stretch", "pigeon_pose", "deep_squat_hold"],
        "description": "Enfoque en movilidad y flexibilidad de cadera",
    },
    "shoulder_focus": {
        "name_es": "Movilidad de Hombro",
        "duration_minutes": 12,
        "exercises": ["shoulder_circles", "wall_slides", "shoulder_dislocates", "thoracic_rotation"],
        "description": "Enfoque en movilidad de hombro y columna toracica",
    },
    "full_body": {
        "name_es": "Movilidad Cuerpo Completo",
        "duration_minutes": 20,
        "exercises": [
            "ankle_circles", "hip_circles", "cat_cow", "thoracic_rotation",
            "shoulder_circles", "deep_squat_hold", "hip_flexor_stretch", "wall_slides",
        ],
        "description": "Rutina completa de movilidad para todas las articulaciones",
    },
    "desk_worker": {
        "name_es": "Movilidad para Oficina",
        "duration_minutes": 10,
        "exercises": ["thoracic_rotation", "hip_flexor_stretch", "wall_slides", "cat_cow", "calf_stretch"],
        "description": "Contrarresta efectos de estar sentado mucho tiempo",
    },
}


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class MobilityAssessment:
    """Evaluacion de movilidad."""

    joint: str
    score: int  # 1-5
    notes: str
    priority: str  # low, medium, high


# =============================================================================
# Tool Functions
# =============================================================================

def get_mobility_exercises(
    joint: str | None = None,
    exercise_type: str | None = None,
    max_difficulty: int = 3,
) -> dict[str, Any]:
    """Obtiene ejercicios de movilidad filtrados.

    Args:
        joint: Articulacion objetivo (shoulder, hip, spine, ankle)
        exercise_type: Tipo de ejercicio (mobility, flexibility)
        max_difficulty: Dificultad maxima (1-3)

    Returns:
        dict con ejercicios filtrados
    """
    filtered = {}

    for ex_id, ex_data in MOBILITY_EXERCISES.items():
        # Filtrar por articulacion
        if joint and ex_data["joint"] != joint:
            continue

        # Filtrar por tipo
        if exercise_type and ex_data["type"] != exercise_type:
            continue

        # Filtrar por dificultad
        if ex_data["difficulty"] > max_difficulty:
            continue

        filtered[ex_id] = ex_data

    return {
        "exercises": filtered,
        "count": len(filtered),
        "filters_applied": {
            "joint": joint,
            "type": exercise_type,
            "max_difficulty": max_difficulty,
        },
    }


def assess_mobility(
    overhead_reach: int,
    deep_squat: int,
    hip_hinge: int,
    thoracic_rotation: int,
) -> dict[str, Any]:
    """Evalua la movilidad del usuario basandose en tests simples.

    Args:
        overhead_reach: Puntuacion 1-5 en alcance overhead
        deep_squat: Puntuacion 1-5 en sentadilla profunda
        hip_hinge: Puntuacion 1-5 en bisagra de cadera
        thoracic_rotation: Puntuacion 1-5 en rotacion toracica

    Returns:
        dict con evaluacion y recomendaciones
    """
    assessments = [
        MobilityAssessment(
            joint="shoulder",
            score=overhead_reach,
            notes="Alcance overhead" if overhead_reach >= 3 else "Limitacion en hombro/toracica",
            priority="high" if overhead_reach <= 2 else ("medium" if overhead_reach == 3 else "low"),
        ),
        MobilityAssessment(
            joint="hip",
            score=deep_squat,
            notes="Sentadilla profunda" if deep_squat >= 3 else "Limitacion en cadera/tobillo",
            priority="high" if deep_squat <= 2 else ("medium" if deep_squat == 3 else "low"),
        ),
        MobilityAssessment(
            joint="hip",
            score=hip_hinge,
            notes="Bisagra de cadera" if hip_hinge >= 3 else "Limitacion en isquiotibiales/cadera",
            priority="high" if hip_hinge <= 2 else ("medium" if hip_hinge == 3 else "low"),
        ),
        MobilityAssessment(
            joint="spine",
            score=thoracic_rotation,
            notes="Rotacion toracica" if thoracic_rotation >= 3 else "Rigidez en columna toracica",
            priority="high" if thoracic_rotation <= 2 else ("medium" if thoracic_rotation == 3 else "low"),
        ),
    ]

    # Calcular score promedio
    avg_score = (overhead_reach + deep_squat + hip_hinge + thoracic_rotation) / 4

    # Determinar areas prioritarias
    priority_areas = [a for a in assessments if a.priority == "high"]

    # Generar recomendaciones
    recommendations = []
    if overhead_reach <= 2:
        recommendations.append("Priorizar trabajo de movilidad de hombro y columna toracica")
    if deep_squat <= 2:
        recommendations.append("Trabajar movilidad de cadera y dorsiflexion de tobillo")
    if hip_hinge <= 2:
        recommendations.append("Enfocarse en flexibilidad de isquiotibiales y movilidad de cadera")
    if thoracic_rotation <= 2:
        recommendations.append("Incluir rotaciones toracicas diariamente")

    if not recommendations:
        recommendations.append("Buena movilidad general. Mantener con rutinas de mantenimiento.")

    return {
        "overall_score": round(avg_score, 1),
        "category": "excellent" if avg_score >= 4 else ("good" if avg_score >= 3 else ("fair" if avg_score >= 2 else "needs_work")),
        "assessments": [
            {
                "joint": a.joint,
                "score": a.score,
                "notes": a.notes,
                "priority": a.priority,
            }
            for a in assessments
        ],
        "priority_areas": [
            {"joint": a.joint, "score": a.score, "notes": a.notes}
            for a in priority_areas
        ],
        "recommendations": recommendations,
    }


def generate_mobility_routine(
    focus: str = "full_body",
    duration_minutes: int = 15,
    include_warmup: bool = True,
) -> dict[str, Any]:
    """Genera una rutina de movilidad personalizada.

    Args:
        focus: Area de enfoque (full_body, hip_focus, shoulder_focus, warmup, desk_worker)
        duration_minutes: Duracion objetivo en minutos
        include_warmup: Si incluir calentamiento articular

    Returns:
        dict con rutina estructurada
    """
    # Obtener template base
    if focus in ROUTINE_TEMPLATES:
        template = ROUTINE_TEMPLATES[focus]
        exercise_ids = template["exercises"]
    else:
        # Default a full body
        template = ROUTINE_TEMPLATES["full_body"]
        exercise_ids = template["exercises"]

    # Construir rutina
    routine_exercises = []
    total_duration = 0

    for ex_id in exercise_ids:
        if ex_id in MOBILITY_EXERCISES:
            ex = MOBILITY_EXERCISES[ex_id]

            # Calcular duracion del ejercicio
            if ex["duration_seconds"]:
                ex_duration = ex["duration_seconds"]
            else:
                ex_duration = (ex["reps"] or 10) * 3  # ~3 segundos por rep

            routine_exercises.append({
                "exercise_id": ex_id,
                "name": ex["name_es"],
                "joint": ex["joint"],
                "duration_seconds": ex_duration,
                "reps": ex["reps"],
                "cues": ex["cues"],
                "type": ex["type"],
            })
            total_duration += ex_duration

    return {
        "name": template["name_es"],
        "description": template["description"],
        "focus": focus,
        "estimated_duration_minutes": round(total_duration / 60, 1),
        "exercises": routine_exercises,
        "notes": [
            "Realizar cada ejercicio de forma controlada",
            "Respirar profundamente durante los estiramientos",
            "No forzar el rango de movimiento",
            "Escuchar al cuerpo y ajustar intensidad",
        ],
    }


def suggest_mobility_for_workout(
    workout_type: str,
    muscle_groups: list[str],
) -> dict[str, Any]:
    """Sugiere ejercicios de movilidad para complementar un workout.

    Args:
        workout_type: Tipo de entrenamiento (push, pull, legs, full_body)
        muscle_groups: Grupos musculares del workout

    Returns:
        dict con ejercicios de movilidad recomendados
    """
    # Mapeo de grupos musculares a articulaciones
    muscle_to_joint = {
        "chest": "shoulder",
        "pectoral": "shoulder",
        "shoulders": "shoulder",
        "deltoids": "shoulder",
        "back": "spine",
        "lats": "shoulder",
        "quads": "hip",
        "hamstrings": "hip",
        "glutes": "hip",
        "calves": "ankle",
    }

    # Determinar articulaciones a trabajar
    target_joints = set()
    for mg in muscle_groups:
        mg_lower = mg.lower()
        if mg_lower in muscle_to_joint:
            target_joints.add(muscle_to_joint[mg_lower])

    # Recomendaciones por tipo de workout
    warmup_exercises = []
    cooldown_exercises = []

    if workout_type.lower() in ["push", "upper", "chest"]:
        warmup_exercises = ["shoulder_circles", "wall_slides", "thoracic_rotation"]
        cooldown_exercises = ["shoulder_dislocates", "cat_cow"]

    elif workout_type.lower() in ["pull", "back"]:
        warmup_exercises = ["shoulder_circles", "thoracic_rotation", "cat_cow"]
        cooldown_exercises = ["wall_slides", "jefferson_curl"]

    elif workout_type.lower() in ["legs", "lower", "squat"]:
        warmup_exercises = ["hip_circles", "ankle_circles", "deep_squat_hold"]
        cooldown_exercises = ["hip_flexor_stretch", "pigeon_pose", "calf_stretch"]

    else:  # full body
        warmup_exercises = ["hip_circles", "shoulder_circles", "cat_cow", "ankle_circles"]
        cooldown_exercises = ["hip_flexor_stretch", "thoracic_rotation", "calf_stretch"]

    # Construir respuesta
    warmup = [
        {"exercise_id": ex_id, **MOBILITY_EXERCISES[ex_id]}
        for ex_id in warmup_exercises
        if ex_id in MOBILITY_EXERCISES
    ]

    cooldown = [
        {"exercise_id": ex_id, **MOBILITY_EXERCISES[ex_id]}
        for ex_id in cooldown_exercises
        if ex_id in MOBILITY_EXERCISES
    ]

    return {
        "workout_type": workout_type,
        "target_joints": list(target_joints),
        "warmup": {
            "duration_minutes": 5,
            "exercises": warmup,
        },
        "cooldown": {
            "duration_minutes": 5,
            "exercises": cooldown,
        },
        "notes": [
            "Realizar calentamiento antes del entrenamiento principal",
            "El cooldown ayuda a la recuperacion y mantiene la movilidad",
        ],
    }


# =============================================================================
# FunctionTool Wrappers
# =============================================================================

get_mobility_exercises_tool = FunctionTool(get_mobility_exercises)
assess_mobility_tool = FunctionTool(assess_mobility)
generate_mobility_routine_tool = FunctionTool(generate_mobility_routine)
suggest_mobility_for_workout_tool = FunctionTool(suggest_mobility_for_workout)

# Lista de todas las tools para exportar
ALL_TOOLS = [
    get_mobility_exercises_tool,
    assess_mobility_tool,
    generate_mobility_routine_tool,
    suggest_mobility_for_workout_tool,
]
