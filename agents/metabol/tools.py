"""Tools para METABOL - Agente de Metabolismo.

Este modulo proporciona las herramientas de calculo metabolico para METABOL:
- Calculo de TDEE
- Evaluacion de tasa metabolica
- Timing nutricional
- Deteccion de adaptacion metabolica
- Evaluacion de sensibilidad a insulina
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from google.adk.tools import FunctionTool

# =============================================================================
# Enums y Constantes
# =============================================================================


class ActivityLevel(str, Enum):
    """Niveles de actividad fisica."""

    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"
    VERY_ACTIVE = "very_active"


class MetabolicGoal(str, Enum):
    """Objetivos metabolicos."""

    FAT_LOSS = "fat_loss"
    MAINTENANCE = "maintenance"
    MUSCLE_GAIN = "muscle_gain"
    RECOMP = "recomp"


class BMRFormula(str, Enum):
    """Formulas para calcular BMR."""

    MIFFLIN_ST_JEOR = "mifflin_st_jeor"
    HARRIS_BENEDICT = "harris_benedict"
    KATCH_MCARDLE = "katch_mcardle"


class MealTiming(str, Enum):
    """Momentos de comida."""

    PRE_WORKOUT = "pre_workout"
    POST_WORKOUT = "post_workout"
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    BEFORE_SLEEP = "before_sleep"


# =============================================================================
# Estructuras de Datos
# =============================================================================

ACTIVITY_LEVELS: dict[str, dict[str, Any]] = {
    "sedentary": {
        "name_es": "Sedentario",
        "factor": 1.2,
        "description": "Trabajo de oficina, poco o nada de ejercicio",
        "examples": ["Trabajo de escritorio", "Muy poco movimiento diario"],
    },
    "light": {
        "name_es": "Ligero",
        "factor": 1.375,
        "description": "Ejercicio ligero 1-3 dias/semana",
        "examples": ["Caminatas cortas", "Ejercicio ocasional"],
    },
    "moderate": {
        "name_es": "Moderado",
        "factor": 1.55,
        "description": "Ejercicio moderado 3-5 dias/semana",
        "examples": ["Gimnasio 3-4 veces", "Deportes recreativos"],
    },
    "active": {
        "name_es": "Activo",
        "factor": 1.725,
        "description": "Ejercicio intenso 6-7 dias/semana",
        "examples": ["Entrenamiento diario", "Trabajo fisico + ejercicio"],
    },
    "very_active": {
        "name_es": "Muy Activo",
        "factor": 1.9,
        "description": "Atleta o trabajo muy fisico + ejercicio",
        "examples": ["Atleta profesional", "Trabajo de construccion + gimnasio"],
    },
}

METABOLIC_FORMULAS: dict[str, dict[str, Any]] = {
    "mifflin_st_jeor": {
        "name": "Mifflin-St Jeor",
        "year": 1990,
        "accuracy": "high",
        "requires_body_fat": False,
        "description": "Formula mas precisa para poblacion general",
        "male_formula": "10 * peso_kg + 6.25 * altura_cm - 5 * edad + 5",
        "female_formula": "10 * peso_kg + 6.25 * altura_cm - 5 * edad - 161",
    },
    "harris_benedict": {
        "name": "Harris-Benedict (Revisada)",
        "year": 1984,
        "accuracy": "moderate",
        "requires_body_fat": False,
        "description": "Formula clasica, menos precisa en obesidad",
        "male_formula": "88.362 + 13.397*peso + 4.799*altura - 5.677*edad",
        "female_formula": "447.593 + 9.247*peso + 3.098*altura - 4.330*edad",
    },
    "katch_mcardle": {
        "name": "Katch-McArdle",
        "year": 1996,
        "accuracy": "very_high",
        "requires_body_fat": True,
        "description": "Mas precisa cuando se conoce % grasa corporal",
        "formula": "370 + 21.6 * masa_magra_kg",
    },
}

GOAL_ADJUSTMENTS: dict[str, dict[str, Any]] = {
    "fat_loss": {
        "name_es": "Perdida de grasa",
        "deficit_percent": 20,
        "deficit_range": {"min": 15, "max": 25},
        "min_calories_male": 1500,
        "min_calories_female": 1200,
        "protein_multiplier": 1.1,
        "notes": "Deficit moderado para preservar musculo",
    },
    "maintenance": {
        "name_es": "Mantenimiento",
        "deficit_percent": 0,
        "protein_multiplier": 1.0,
        "notes": "TDEE sin ajustes",
    },
    "muscle_gain": {
        "name_es": "Ganancia muscular",
        "surplus_percent": 15,
        "surplus_range": {"min": 10, "max": 20},
        "protein_multiplier": 1.0,
        "notes": "Superavit controlado para minimizar grasa",
    },
    "recomp": {
        "name_es": "Recomposicion",
        "adjustment_percent": 0,
        "protein_multiplier": 1.2,
        "notes": "Calorias en mantenimiento, proteina alta",
    },
}

TIMING_WINDOWS: dict[str, dict[str, Any]] = {
    "pre_workout": {
        "name_es": "Pre-entrenamiento",
        "hours_before": 2,
        "range_hours": {"min": 1, "max": 3},
        "macro_focus": "carbs",
        "protein_priority": "moderate",
        "carb_priority": "high",
        "fat_priority": "low",
        "recommendations": [
            "Comida moderada 2-3h antes",
            "Snack ligero 30-60min antes si es necesario",
            "Evitar grasas altas cerca del entrenamiento",
        ],
    },
    "post_workout": {
        "name_es": "Post-entrenamiento",
        "hours_after": 2,
        "range_hours": {"min": 0, "max": 2},
        "macro_focus": "protein+carbs",
        "protein_priority": "very_high",
        "carb_priority": "high",
        "fat_priority": "moderate",
        "recommendations": [
            "Proteina dentro de 2h post-entrenamiento",
            "Carbohidratos para reponer glucogeno",
            "No es necesario comer inmediatamente",
        ],
    },
    "before_sleep": {
        "name_es": "Antes de dormir",
        "hours_before_bed": 2,
        "macro_focus": "protein",
        "protein_priority": "high",
        "carb_priority": "low",
        "fat_priority": "moderate",
        "recommendations": [
            "Caseina o proteina de lenta digestion",
            "Evitar comidas muy grandes",
            "Mantener calorias moderadas",
        ],
    },
    "morning_fasted": {
        "name_es": "Manana en ayunas",
        "macro_focus": "protein+fat",
        "protein_priority": "high",
        "carb_priority": "variable",
        "fat_priority": "moderate",
        "recommendations": [
            "Primera comida del dia",
            "Proteina para romper catabolismo",
            "Carbohidratos segun actividad del dia",
        ],
    },
}

INSULIN_SENSITIVITY_INDICATORS: dict[str, dict[str, Any]] = {
    "high_sensitivity": {
        "name_es": "Alta sensibilidad",
        "description": "Buen manejo de carbohidratos",
        "carb_tolerance": "high",
        "recommended_carb_pct": {"min": 40, "max": 55},
        "indicators": [
            "Energia estable despues de comidas con carbos",
            "Buena composicion corporal con dieta moderada en carbos",
            "Sin antecedentes familiares de diabetes",
            "Ejercicio regular",
        ],
    },
    "moderate_sensitivity": {
        "name_es": "Sensibilidad moderada",
        "description": "Manejo normal de carbohidratos",
        "carb_tolerance": "moderate",
        "recommended_carb_pct": {"min": 30, "max": 45},
        "indicators": [
            "Energia variable con comidas altas en carbos",
            "Tendencia a acumular grasa con exceso de carbos",
            "Algunos antecedentes familiares",
        ],
    },
    "low_sensitivity": {
        "name_es": "Baja sensibilidad",
        "description": "Considerar reducir carbohidratos",
        "carb_tolerance": "low",
        "recommended_carb_pct": {"min": 20, "max": 35},
        "indicators": [
            "Fatiga despues de comidas con carbos",
            "Dificultad para perder grasa",
            "Antecedentes de prediabetes o resistencia",
            "Distribucion de grasa central",
        ],
        "recommendation": "Consultar medico para evaluacion completa",
    },
}

ADAPTATION_SIGNS: dict[str, dict[str, Any]] = {
    "metabolic_slowdown": {
        "name_es": "Desaceleracion metabolica",
        "signs": [
            "Perdida de peso estancada >3 semanas",
            "Hambre aumentada significativamente",
            "Fatiga y falta de energia",
            "Frio frecuente",
        ],
        "causes": [
            "Deficit calorico prolongado",
            "Deficit muy agresivo",
            "Perdida de masa muscular",
        ],
        "solutions": [
            "Diet break de 1-2 semanas a mantenimiento",
            "Refeed days estrategicos",
            "Aumentar calorias gradualmente",
            "Revisar ingesta de proteina",
        ],
    },
    "hormonal_adaptation": {
        "name_es": "Adaptacion hormonal",
        "signs": [
            "Libido disminuida",
            "Calidad de sueno afectada",
            "Rendimiento en entrenamiento reducido",
            "Irritabilidad aumentada",
        ],
        "causes": [
            "Restriccion calorica severa",
            "Falta de grasas en dieta",
            "Estres cronico + deficit",
        ],
        "solutions": [
            "Aumentar calorias a mantenimiento",
            "Asegurar ingesta minima de grasas (0.8g/kg)",
            "Priorizar recuperacion y sueno",
        ],
    },
}


# =============================================================================
# Funciones de Metabolismo
# =============================================================================


def calculate_tdee(
    weight_kg: float,
    height_cm: float,
    age: int,
    sex: str = "male",
    activity_level: str = "moderate",
    body_fat_percent: float | None = None,
    goal: str = "maintenance",
    formula: str = "mifflin_st_jeor",
) -> dict[str, Any]:
    """Calcula el Total Daily Energy Expenditure (TDEE).

    Args:
        weight_kg: Peso en kilogramos
        height_cm: Altura en centimetros
        age: Edad en años
        sex: Sexo ("male" o "female")
        activity_level: Nivel de actividad (sedentary, light, moderate, active, very_active)
        body_fat_percent: Porcentaje de grasa corporal (opcional, para Katch-McArdle)
        goal: Objetivo (fat_loss, maintenance, muscle_gain, recomp)
        formula: Formula a usar (mifflin_st_jeor, harris_benedict, katch_mcardle)

    Returns:
        dict con TDEE calculado y desglose
    """
    # Validar inputs
    if weight_kg <= 0 or height_cm <= 0 or age <= 0:
        return {
            "status": "error",
            "message": "Peso, altura y edad deben ser valores positivos",
        }

    if sex not in ["male", "female"]:
        sex = "male"

    if activity_level not in ACTIVITY_LEVELS:
        activity_level = "moderate"

    if goal not in GOAL_ADJUSTMENTS:
        goal = "maintenance"

    # Calcular BMR segun formula
    if formula == "katch_mcardle" and body_fat_percent is not None:
        lean_mass = weight_kg * (1 - body_fat_percent / 100)
        bmr = 370 + 21.6 * lean_mass
        formula_used = "katch_mcardle"
    elif formula == "harris_benedict":
        if sex == "male":
            bmr = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)
        formula_used = "harris_benedict"
    else:
        # Default: Mifflin-St Jeor
        if sex == "male":
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        else:
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
        formula_used = "mifflin_st_jeor"

    # Aplicar factor de actividad
    activity_factor = ACTIVITY_LEVELS[activity_level]["factor"]
    tdee_maintenance = bmr * activity_factor

    # Aplicar ajuste por objetivo
    goal_info = GOAL_ADJUSTMENTS[goal]
    if goal == "fat_loss":
        adjustment = goal_info["deficit_percent"] / 100
        tdee_adjusted = tdee_maintenance * (1 - adjustment)
        # Aplicar minimos de seguridad
        min_cal = goal_info["min_calories_male"] if sex == "male" else goal_info["min_calories_female"]
        tdee_adjusted = max(tdee_adjusted, min_cal)
        adjustment_type = "deficit"
    elif goal == "muscle_gain":
        adjustment = goal_info["surplus_percent"] / 100
        tdee_adjusted = tdee_maintenance * (1 + adjustment)
        adjustment_type = "surplus"
    else:
        tdee_adjusted = tdee_maintenance
        adjustment_type = "none"

    # Calcular rango util (+/- 10%)
    tdee_range = {
        "low": round(tdee_adjusted * 0.9),
        "target": round(tdee_adjusted),
        "high": round(tdee_adjusted * 1.1),
    }

    # Generar recomendaciones
    recommendations = []
    if goal == "fat_loss":
        recommendations.append(f"Deficit de {goal_info['deficit_percent']}% para perdida sostenible")
        recommendations.append("Monitorea tu peso semanalmente y ajusta si es necesario")
    elif goal == "muscle_gain":
        recommendations.append(f"Superavit de {goal_info['surplus_percent']}% para ganancia limpia")
        recommendations.append("Ajusta si ganas >0.5kg/semana (puede ser grasa excesiva)")

    recommendations.append("Este es un punto de partida - ajusta segun resultados reales")
    recommendations.append("Recalcula cada 4-6 semanas o tras cambios de peso >3kg")

    return {
        "status": "calculated",
        "formula_used": formula_used,
        "formula_info": METABOLIC_FORMULAS[formula_used],
        "inputs": {
            "weight_kg": weight_kg,
            "height_cm": height_cm,
            "age": age,
            "sex": sex,
            "activity_level": activity_level,
            "body_fat_percent": body_fat_percent,
            "goal": goal,
        },
        "calculations": {
            "bmr": round(bmr),
            "activity_factor": activity_factor,
            "tdee_maintenance": round(tdee_maintenance),
            "adjustment_type": adjustment_type,
            "adjustment_percent": goal_info.get("deficit_percent") or goal_info.get("surplus_percent") or 0,
            "tdee_adjusted": round(tdee_adjusted),
        },
        "result": {
            "daily_calories": round(tdee_adjusted),
            "range": tdee_range,
            "goal_name_es": goal_info["name_es"],
        },
        "activity_info": ACTIVITY_LEVELS[activity_level],
        "recommendations": recommendations,
    }


def assess_metabolic_rate(
    weight_kg: float,
    height_cm: float,
    age: int,
    sex: str = "male",
    body_fat_percent: float | None = None,
    lean_mass_kg: float | None = None,
) -> dict[str, Any]:
    """Evalua la tasa metabolica basal (BMR) con multiples formulas.

    Args:
        weight_kg: Peso en kilogramos
        height_cm: Altura en centimetros
        age: Edad en años
        sex: Sexo ("male" o "female")
        body_fat_percent: Porcentaje de grasa corporal
        lean_mass_kg: Masa magra en kg (alternativa a body_fat_percent)

    Returns:
        dict con evaluacion metabolica
    """
    if weight_kg <= 0 or height_cm <= 0 or age <= 0:
        return {
            "status": "error",
            "message": "Datos invalidos",
        }

    results = {}

    # Mifflin-St Jeor
    if sex == "male":
        bmr_mifflin = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr_mifflin = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

    results["mifflin_st_jeor"] = {
        "bmr": round(bmr_mifflin),
        "accuracy": "high",
        "note": "Recomendada para poblacion general",
    }

    # Harris-Benedict
    if sex == "male":
        bmr_harris = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
    else:
        bmr_harris = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)

    results["harris_benedict"] = {
        "bmr": round(bmr_harris),
        "accuracy": "moderate",
        "note": "Formula clasica, menos precisa en obesidad",
    }

    # Katch-McArdle (si tenemos datos de composicion corporal)
    if body_fat_percent is not None:
        lean_mass = weight_kg * (1 - body_fat_percent / 100)
        bmr_katch = 370 + 21.6 * lean_mass
        results["katch_mcardle"] = {
            "bmr": round(bmr_katch),
            "lean_mass_kg": round(lean_mass, 1),
            "accuracy": "very_high",
            "note": "Mas precisa con composicion corporal conocida",
        }
    elif lean_mass_kg is not None:
        bmr_katch = 370 + 21.6 * lean_mass_kg
        results["katch_mcardle"] = {
            "bmr": round(bmr_katch),
            "lean_mass_kg": lean_mass_kg,
            "accuracy": "very_high",
            "note": "Mas precisa con composicion corporal conocida",
        }

    # Calcular promedio y rango
    bmr_values = [r["bmr"] for r in results.values()]
    avg_bmr = sum(bmr_values) / len(bmr_values)

    # Determinar formula recomendada
    if "katch_mcardle" in results:
        recommended = "katch_mcardle"
        recommended_bmr = results["katch_mcardle"]["bmr"]
    else:
        recommended = "mifflin_st_jeor"
        recommended_bmr = results["mifflin_st_jeor"]["bmr"]

    # Composicion corporal estimada
    composition = {}
    if body_fat_percent is not None:
        composition = {
            "body_fat_percent": body_fat_percent,
            "lean_mass_kg": round(weight_kg * (1 - body_fat_percent / 100), 1),
            "fat_mass_kg": round(weight_kg * body_fat_percent / 100, 1),
        }

    # Contexto metabolico
    metabolic_context = []

    # BMR por kg de peso
    bmr_per_kg = recommended_bmr / weight_kg
    if bmr_per_kg < 20:
        metabolic_context.append("BMR relativamente bajo por kg - puede indicar metabolismo eficiente")
    elif bmr_per_kg > 25:
        metabolic_context.append("BMR relativamente alto por kg - buen potencial metabolico")
    else:
        metabolic_context.append("BMR en rango tipico para tu peso")

    # Factor edad
    if age > 50:
        metabolic_context.append("El metabolismo tiende a bajar ~2-4% por decada despues de los 30")
        metabolic_context.append("El entrenamiento de fuerza ayuda a mantener masa muscular y BMR")

    return {
        "status": "assessed",
        "inputs": {
            "weight_kg": weight_kg,
            "height_cm": height_cm,
            "age": age,
            "sex": sex,
            "body_fat_percent": body_fat_percent,
        },
        "formulas": results,
        "summary": {
            "average_bmr": round(avg_bmr),
            "recommended_formula": recommended,
            "recommended_bmr": recommended_bmr,
            "bmr_range": {
                "min": min(bmr_values),
                "max": max(bmr_values),
            },
            "bmr_per_kg": round(bmr_per_kg, 1),
        },
        "composition": composition if composition else None,
        "metabolic_context": metabolic_context,
    }


def plan_nutrient_timing(
    training_time: str = "18:00",
    wake_time: str = "07:00",
    sleep_time: str = "23:00",
    meals_per_day: int = 4,
    training_days_per_week: int = 4,
    goal: str = "muscle_gain",
) -> dict[str, Any]:
    """Planifica el timing nutricional optimo.

    Args:
        training_time: Hora de entrenamiento (HH:MM)
        wake_time: Hora de despertar (HH:MM)
        sleep_time: Hora de dormir (HH:MM)
        meals_per_day: Numero de comidas por dia
        training_days_per_week: Dias de entrenamiento por semana
        goal: Objetivo (fat_loss, maintenance, muscle_gain)

    Returns:
        dict con plan de timing nutricional
    """
    # Parsear horas
    def parse_time(time_str: str) -> tuple[int, int]:
        parts = time_str.split(":")
        return int(parts[0]), int(parts[1]) if len(parts) > 1 else 0

    try:
        train_h, train_m = parse_time(training_time)
        wake_h, wake_m = parse_time(wake_time)
        sleep_h, sleep_m = parse_time(sleep_time)
    except (ValueError, IndexError):
        return {
            "status": "error",
            "message": "Formato de hora invalido. Usa HH:MM",
        }

    # Calcular ventanas
    pre_workout_h = train_h - 2 if train_h >= 2 else train_h + 22
    post_workout_h = train_h + 1 if train_h < 23 else 0

    # Generar horario de comidas sugerido
    waking_hours = sleep_h - wake_h if sleep_h > wake_h else (24 - wake_h + sleep_h)
    meal_interval = waking_hours / meals_per_day

    meal_schedule = []
    current_h = wake_h + 1  # Primera comida 1h despues de despertar

    for i in range(meals_per_day):
        meal_hour = int((current_h + i * meal_interval) % 24)
        meal_minute = 0

        # Determinar tipo de comida
        if i == 0:
            meal_type = "breakfast"
            priority = "protein+carbs"
        elif abs(meal_hour - pre_workout_h) <= 1 and training_days_per_week > 0:
            meal_type = "pre_workout"
            priority = "carbs+protein"
        elif abs(meal_hour - post_workout_h) <= 1 and training_days_per_week > 0:
            meal_type = "post_workout"
            priority = "protein+carbs"
        elif i == meals_per_day - 1:
            meal_type = "dinner/before_sleep"
            priority = "protein+moderate_carbs"
        else:
            meal_type = "main_meal"
            priority = "balanced"

        meal_schedule.append({
            "meal_number": i + 1,
            "suggested_time": f"{meal_hour:02d}:{meal_minute:02d}",
            "type": meal_type,
            "macro_priority": priority,
        })

    # Distribucion de macros por momento
    timing_recommendations = {
        "training_days": {
            "pre_workout": TIMING_WINDOWS["pre_workout"],
            "post_workout": TIMING_WINDOWS["post_workout"],
            "other_meals": "Distribuir proteina uniformemente, carbos segun actividad restante",
        },
        "rest_days": {
            "morning": "Proteina + grasas saludables, carbos moderados",
            "afternoon": "Comida balanceada",
            "evening": "Proteina + vegetales, carbos bajos-moderados",
        },
    }

    # Ajustes por objetivo
    goal_notes = []
    if goal == "fat_loss":
        goal_notes.append("Concentra carbohidratos alrededor del entrenamiento")
        goal_notes.append("Dias de descanso: carbos mas bajos")
        goal_notes.append("Proteina alta y distribuida en todas las comidas")
    elif goal == "muscle_gain":
        goal_notes.append("Carbohidratos distribuidos a lo largo del dia")
        goal_notes.append("Comida post-entrenamiento especialmente importante")
        goal_notes.append("Considera un snack antes de dormir con caseina")
    else:
        goal_notes.append("Distribucion equilibrada de macros")
        goal_notes.append("Prioriza proteina post-entrenamiento")

    return {
        "status": "planned",
        "inputs": {
            "training_time": training_time,
            "wake_time": wake_time,
            "sleep_time": sleep_time,
            "meals_per_day": meals_per_day,
            "training_days_per_week": training_days_per_week,
            "goal": goal,
        },
        "schedule": {
            "waking_hours": waking_hours,
            "meal_interval_hours": round(meal_interval, 1),
            "meals": meal_schedule,
        },
        "training_day_windows": {
            "pre_workout": f"{pre_workout_h:02d}:00 - {train_h:02d}:00",
            "training": training_time,
            "post_workout": f"{train_h:02d}:00 - {(train_h + 2) % 24:02d}:00",
        },
        "timing_recommendations": timing_recommendations,
        "goal_specific_notes": goal_notes,
        "general_guidelines": [
            "El timing es secundario al total calorico y de macros",
            "La consistencia es mas importante que la perfeccion",
            "Adapta el plan a tu estilo de vida",
            "Escucha a tu cuerpo - hambre y energia son indicadores utiles",
        ],
    }


def detect_metabolic_adaptation(
    weekly_weights: list[float],
    daily_calories: int,
    weeks_in_deficit: int = 0,
    initial_weight: float | None = None,
    current_symptoms: list[str] | None = None,
) -> dict[str, Any]:
    """Detecta signos de adaptacion metabolica.

    Args:
        weekly_weights: Lista de pesos semanales (kg)
        daily_calories: Calorias diarias actuales
        weeks_in_deficit: Semanas en deficit calorico
        initial_weight: Peso inicial del plan
        current_symptoms: Lista de sintomas actuales

    Returns:
        dict con evaluacion de adaptacion metabolica
    """
    if not weekly_weights or len(weekly_weights) < 2:
        return {
            "status": "insufficient_data",
            "message": "Se necesitan al menos 2 semanas de datos de peso",
        }

    # Analizar tendencia de peso
    weight_changes = []
    for i in range(1, len(weekly_weights)):
        change = weekly_weights[i] - weekly_weights[i - 1]
        weight_changes.append(change)

    total_change = weekly_weights[-1] - weekly_weights[0]
    avg_weekly_change = total_change / (len(weekly_weights) - 1)

    # Detectar estancamiento
    recent_changes = weight_changes[-3:] if len(weight_changes) >= 3 else weight_changes
    is_stalled = all(abs(c) < 0.2 for c in recent_changes)
    weeks_stalled = sum(1 for c in recent_changes if abs(c) < 0.2)

    # Evaluar sintomas
    adaptation_signs = []
    symptom_score = 0

    if current_symptoms:
        for symptom in current_symptoms:
            symptom_lower = symptom.lower()
            if any(word in symptom_lower for word in ["fatiga", "cansancio", "energia"]):
                adaptation_signs.append("Fatiga/baja energia")
                symptom_score += 2
            if any(word in symptom_lower for word in ["hambre", "apetito"]):
                adaptation_signs.append("Hambre aumentada")
                symptom_score += 1
            if any(word in symptom_lower for word in ["frio", "temperatura"]):
                adaptation_signs.append("Sensacion de frio")
                symptom_score += 2
            if any(word in symptom_lower for word in ["rendimiento", "fuerza"]):
                adaptation_signs.append("Rendimiento reducido")
                symptom_score += 1
            if any(word in symptom_lower for word in ["sueno", "dormir"]):
                adaptation_signs.append("Problemas de sueno")
                symptom_score += 1
            if any(word in symptom_lower for word in ["libido", "sexual"]):
                adaptation_signs.append("Libido reducida")
                symptom_score += 2

    # Calcular score de adaptacion
    adaptation_score = 0

    if is_stalled and weeks_in_deficit > 8:
        adaptation_score += 3
    elif is_stalled and weeks_in_deficit > 4:
        adaptation_score += 2
    elif is_stalled:
        adaptation_score += 1

    adaptation_score += min(symptom_score, 5)  # Cap de sintomas

    if initial_weight and weekly_weights[-1]:
        total_lost = initial_weight - weekly_weights[-1]
        pct_lost = (total_lost / initial_weight) * 100
        if pct_lost > 10:
            adaptation_score += 1

    # Determinar nivel de adaptacion
    if adaptation_score >= 6:
        adaptation_level = "high"
        adaptation_level_es = "Alta"
    elif adaptation_score >= 3:
        adaptation_level = "moderate"
        adaptation_level_es = "Moderada"
    else:
        adaptation_level = "low"
        adaptation_level_es = "Baja"

    # Generar recomendaciones
    recommendations = []

    if adaptation_level == "high":
        recommendations.append("Considera un diet break de 1-2 semanas a calorias de mantenimiento")
        recommendations.append("Aumenta calorias gradualmente (+100-200/dia por semana)")
        recommendations.append("Prioriza descanso y calidad de sueno")
        recommendations.append("Reduce intensidad de entrenamiento temporalmente")
    elif adaptation_level == "moderate":
        recommendations.append("Considera 2-3 dias de refeed a mantenimiento")
        recommendations.append("Asegurate de dormir 7-9 horas")
        recommendations.append("Revisa que la proteina sea suficiente (>1.6g/kg)")
        recommendations.append("Incorpora un dia de descanso extra si es necesario")
    else:
        recommendations.append("Continua con el plan actual")
        recommendations.append("Monitorea peso y sintomas semanalmente")
        recommendations.append("Mantén la paciencia - la perdida de peso no es lineal")

    return {
        "status": "analyzed",
        "inputs": {
            "weeks_of_data": len(weekly_weights),
            "weeks_in_deficit": weeks_in_deficit,
            "daily_calories": daily_calories,
        },
        "weight_analysis": {
            "start_weight": weekly_weights[0],
            "current_weight": weekly_weights[-1],
            "total_change_kg": round(total_change, 2),
            "avg_weekly_change_kg": round(avg_weekly_change, 2),
            "is_stalled": is_stalled,
            "weeks_stalled": weeks_stalled,
        },
        "adaptation_assessment": {
            "level": adaptation_level,
            "level_es": adaptation_level_es,
            "score": adaptation_score,
            "max_score": 10,
            "signs_detected": adaptation_signs,
        },
        "recommendations": recommendations,
        "warning": "Si los sintomas persisten, consulta con un profesional de la salud" if adaptation_level == "high" else None,
    }


def assess_insulin_sensitivity(
    fasting_glucose_mg_dl: float | None = None,
    post_meal_energy: str = "stable",
    body_fat_distribution: str = "even",
    family_history_diabetes: bool = False,
    exercise_frequency: str = "moderate",
    carb_response: str = "normal",
) -> dict[str, Any]:
    """Evalua indicadores de sensibilidad a la insulina.

    Args:
        fasting_glucose_mg_dl: Glucosa en ayunas (opcional)
        post_meal_energy: Energia despues de comidas ("stable", "crash", "variable")
        body_fat_distribution: Distribucion de grasa ("even", "central", "peripheral")
        family_history_diabetes: Antecedentes familiares de diabetes
        exercise_frequency: Frecuencia de ejercicio ("sedentary", "light", "moderate", "high")
        carb_response: Respuesta a carbohidratos ("good", "normal", "poor")

    Returns:
        dict con evaluacion de sensibilidad a insulina
    """
    score = 0
    max_score = 10
    factors = []

    # Evaluar glucosa en ayunas
    glucose_status = None
    if fasting_glucose_mg_dl is not None:
        if fasting_glucose_mg_dl < 70:
            glucose_status = "low"
            factors.append({"factor": "Glucosa en ayunas baja", "impact": "neutral", "note": "Consultar medico"})
        elif fasting_glucose_mg_dl <= 99:
            glucose_status = "normal"
            score += 3
            factors.append({"factor": "Glucosa en ayunas normal", "impact": "positive", "note": "<100 mg/dL"})
        elif fasting_glucose_mg_dl <= 125:
            glucose_status = "prediabetes_range"
            score += 1
            factors.append({"factor": "Glucosa en rango prediabetes", "impact": "negative", "note": "100-125 mg/dL - consultar medico"})
        else:
            glucose_status = "high"
            factors.append({"factor": "Glucosa elevada", "impact": "very_negative", "note": ">125 mg/dL - requiere evaluacion medica"})

    # Evaluar energia post-comida
    if post_meal_energy == "stable":
        score += 2
        factors.append({"factor": "Energia estable post-comida", "impact": "positive", "note": "Buen manejo de carbohidratos"})
    elif post_meal_energy == "crash":
        factors.append({"factor": "Crash de energia post-comida", "impact": "negative", "note": "Posible respuesta insulinica exagerada"})
    else:
        score += 1
        factors.append({"factor": "Energia variable", "impact": "neutral", "note": "Respuesta normal"})

    # Evaluar distribucion de grasa
    if body_fat_distribution == "central":
        factors.append({"factor": "Grasa central/abdominal", "impact": "negative", "note": "Asociada con resistencia a insulina"})
    elif body_fat_distribution == "peripheral":
        score += 1
        factors.append({"factor": "Grasa periferica", "impact": "neutral", "note": "Distribucion mas favorable"})
    else:
        score += 1
        factors.append({"factor": "Distribucion uniforme", "impact": "neutral", "note": "Patron normal"})

    # Evaluar antecedentes familiares
    if family_history_diabetes:
        factors.append({"factor": "Antecedentes familiares diabetes", "impact": "negative", "note": "Mayor riesgo genetico"})
    else:
        score += 1
        factors.append({"factor": "Sin antecedentes familiares", "impact": "positive", "note": "Menor riesgo genetico"})

    # Evaluar ejercicio
    exercise_scores = {"sedentary": 0, "light": 1, "moderate": 2, "high": 3}
    ex_score = exercise_scores.get(exercise_frequency, 1)
    score += ex_score
    if exercise_frequency in ["moderate", "high"]:
        factors.append({"factor": f"Ejercicio {exercise_frequency}", "impact": "positive", "note": "Mejora sensibilidad a insulina"})
    else:
        factors.append({"factor": f"Ejercicio {exercise_frequency}", "impact": "neutral", "note": "Aumentar actividad beneficiaria"})

    # Evaluar respuesta a carbohidratos
    if carb_response == "good":
        score += 2
        factors.append({"factor": "Buena tolerancia a carbohidratos", "impact": "positive", "note": ""})
    elif carb_response == "poor":
        factors.append({"factor": "Mala tolerancia a carbohidratos", "impact": "negative", "note": "Considerar reducir carbohidratos"})
    else:
        score += 1
        factors.append({"factor": "Tolerancia normal", "impact": "neutral", "note": ""})

    # Determinar nivel de sensibilidad
    sensitivity_pct = (score / max_score) * 100

    if sensitivity_pct >= 70:
        sensitivity_level = "high_sensitivity"
    elif sensitivity_pct >= 40:
        sensitivity_level = "moderate_sensitivity"
    else:
        sensitivity_level = "low_sensitivity"

    sensitivity_info = INSULIN_SENSITIVITY_INDICATORS[sensitivity_level]

    # Recomendaciones de carbohidratos
    carb_recommendation = sensitivity_info["recommended_carb_pct"]

    # Recomendaciones generales
    recommendations = []

    if sensitivity_level == "low_sensitivity":
        recommendations.append("Considera reducir carbohidratos a 20-35% de calorias")
        recommendations.append("Prioriza carbohidratos complejos y fibra")
        recommendations.append("Aumenta actividad fisica, especialmente entrenamiento de fuerza")
        recommendations.append("Consulta con un medico para evaluacion completa")
    elif sensitivity_level == "moderate_sensitivity":
        recommendations.append("Carbohidratos moderados (30-45% de calorias)")
        recommendations.append("Distribuye carbohidratos alrededor del ejercicio")
        recommendations.append("Incluye fibra con cada comida de carbohidratos")
    else:
        recommendations.append("Puedes tolerar carbohidratos mas altos (40-55%)")
        recommendations.append("Mantén el ejercicio regular para preservar sensibilidad")
        recommendations.append("Prioriza fuentes de carbohidratos de calidad")

    return {
        "status": "assessed",
        "inputs": {
            "fasting_glucose_mg_dl": fasting_glucose_mg_dl,
            "post_meal_energy": post_meal_energy,
            "body_fat_distribution": body_fat_distribution,
            "family_history_diabetes": family_history_diabetes,
            "exercise_frequency": exercise_frequency,
            "carb_response": carb_response,
        },
        "glucose_status": glucose_status,
        "assessment": {
            "sensitivity_level": sensitivity_level,
            "sensitivity_name_es": sensitivity_info["name_es"],
            "description": sensitivity_info["description"],
            "score": score,
            "max_score": max_score,
            "score_percent": round(sensitivity_pct, 1),
        },
        "factors_analyzed": factors,
        "carb_recommendation": {
            "percent_of_calories": carb_recommendation,
            "tolerance": sensitivity_info["carb_tolerance"],
        },
        "recommendations": recommendations,
        "disclaimer": "Esta evaluacion es orientativa. Para un diagnostico preciso, consulta con un profesional de la salud.",
    }


# =============================================================================
# FunctionTools para ADK
# =============================================================================

calculate_tdee_tool = FunctionTool(calculate_tdee)
assess_metabolic_rate_tool = FunctionTool(assess_metabolic_rate)
plan_nutrient_timing_tool = FunctionTool(plan_nutrient_timing)
detect_metabolic_adaptation_tool = FunctionTool(detect_metabolic_adaptation)
assess_insulin_sensitivity_tool = FunctionTool(assess_insulin_sensitivity)

ALL_TOOLS = [
    calculate_tdee_tool,
    assess_metabolic_rate_tool,
    plan_nutrient_timing_tool,
    detect_metabolic_adaptation_tool,
    assess_insulin_sensitivity_tool,
]
