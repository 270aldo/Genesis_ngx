"""Tools para SAGE - Agente de Estrategia Nutricional.

Define las FunctionTools que SAGE usa para:
- Calcular requerimientos calóricos (TDEE)
- Calcular macronutrientes
- Crear planes de comidas
- Ajustar según progreso
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


class ActivityLevel(str, Enum):
    """Niveles de actividad física."""

    SEDENTARY = "sedentary"  # Trabajo de escritorio, poco ejercicio
    LIGHT = "light"  # Ejercicio ligero 1-3 días/semana
    MODERATE = "moderate"  # Ejercicio moderado 3-5 días/semana
    ACTIVE = "active"  # Ejercicio intenso 6-7 días/semana
    VERY_ACTIVE = "very_active"  # Atleta o trabajo físico + ejercicio


class NutritionGoal(str, Enum):
    """Objetivos nutricionales."""

    FAT_LOSS = "fat_loss"
    MUSCLE_GAIN = "muscle_gain"
    RECOMPOSITION = "recomposition"
    MAINTENANCE = "maintenance"
    PERFORMANCE = "performance"


class DietPreference(str, Enum):
    """Preferencias dietéticas."""

    OMNIVORE = "omnivore"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    PESCATARIAN = "pescatarian"
    KETO = "keto"
    LOW_CARB = "low_carb"
    MEDITERRANEAN = "mediterranean"


# Multiplicadores de actividad para TDEE
ACTIVITY_MULTIPLIERS = {
    ActivityLevel.SEDENTARY.value: 1.2,
    ActivityLevel.LIGHT.value: 1.375,
    ActivityLevel.MODERATE.value: 1.55,
    ActivityLevel.ACTIVE.value: 1.725,
    ActivityLevel.VERY_ACTIVE.value: 1.9,
}

# Alimentos por categoría
FOOD_DATABASE: dict[str, dict[str, Any]] = {
    "protein": {
        "chicken_breast": {"name_es": "Pechuga de Pollo", "protein": 31, "carbs": 0, "fat": 3.6, "calories": 165},
        "salmon": {"name_es": "Salmón", "protein": 25, "carbs": 0, "fat": 13, "calories": 208},
        "eggs": {"name_es": "Huevos", "protein": 13, "carbs": 1, "fat": 11, "calories": 155},
        "greek_yogurt": {"name_es": "Yogurt Griego", "protein": 10, "carbs": 4, "fat": 0.7, "calories": 59},
        "lean_beef": {"name_es": "Carne de Res Magra", "protein": 26, "carbs": 0, "fat": 15, "calories": 250},
        "tofu": {"name_es": "Tofu", "protein": 8, "carbs": 2, "fat": 4, "calories": 76},
        "lentils": {"name_es": "Lentejas", "protein": 9, "carbs": 20, "fat": 0.4, "calories": 116},
        "whey_protein": {"name_es": "Proteína de Suero", "protein": 80, "carbs": 10, "fat": 5, "calories": 400},
    },
    "carbs": {
        "rice": {"name_es": "Arroz", "protein": 2.7, "carbs": 28, "fat": 0.3, "calories": 130},
        "oats": {"name_es": "Avena", "protein": 17, "carbs": 66, "fat": 7, "calories": 389},
        "sweet_potato": {"name_es": "Camote", "protein": 2, "carbs": 20, "fat": 0, "calories": 86},
        "quinoa": {"name_es": "Quinoa", "protein": 4, "carbs": 21, "fat": 2, "calories": 120},
        "banana": {"name_es": "Plátano", "protein": 1, "carbs": 23, "fat": 0.3, "calories": 89},
        "bread_whole": {"name_es": "Pan Integral", "protein": 13, "carbs": 43, "fat": 3, "calories": 247},
        "pasta": {"name_es": "Pasta", "protein": 5, "carbs": 25, "fat": 1, "calories": 131},
    },
    "fats": {
        "olive_oil": {"name_es": "Aceite de Oliva", "protein": 0, "carbs": 0, "fat": 100, "calories": 884},
        "avocado": {"name_es": "Aguacate", "protein": 2, "carbs": 9, "fat": 15, "calories": 160},
        "almonds": {"name_es": "Almendras", "protein": 21, "carbs": 22, "fat": 49, "calories": 579},
        "peanut_butter": {"name_es": "Crema de Cacahuate", "protein": 25, "carbs": 20, "fat": 50, "calories": 588},
        "chia_seeds": {"name_es": "Semillas de Chía", "protein": 17, "carbs": 42, "fat": 31, "calories": 486},
    },
    "vegetables": {
        "broccoli": {"name_es": "Brócoli", "protein": 2.8, "carbs": 7, "fat": 0.4, "calories": 43},
        "spinach": {"name_es": "Espinaca", "protein": 2.9, "carbs": 3.6, "fat": 0.4, "calories": 30},
        "bell_pepper": {"name_es": "Pimiento", "protein": 1, "carbs": 6, "fat": 0.3, "calories": 31},
        "tomato": {"name_es": "Tomate", "protein": 0.9, "carbs": 3.9, "fat": 0.2, "calories": 21},
        "cucumber": {"name_es": "Pepino", "protein": 0.7, "carbs": 3.6, "fat": 0.1, "calories": 18},
    },
}


@dataclass
class MacroTargets:
    """Objetivos de macronutrientes."""

    calories: int
    protein_g: int
    carbs_g: int
    fat_g: int
    fiber_g: int = 30


@dataclass
class MealPlan:
    """Plan de comidas diario."""

    meals: list[dict[str, Any]]
    total_calories: int
    total_protein: int
    total_carbs: int
    total_fat: int


# =============================================================================
# FunctionTools
# =============================================================================


def calculate_tdee(
    weight_kg: float,
    height_cm: float,
    age: int,
    sex: str,
    activity_level: str,
    body_fat_pct: Optional[float] = None,
) -> dict[str, Any]:
    """Calcula el Total Daily Energy Expenditure (TDEE).

    Args:
        weight_kg: Peso en kilogramos
        height_cm: Altura en centímetros
        age: Edad en años
        sex: Sexo ('male' o 'female')
        activity_level: Nivel de actividad (sedentary, light, moderate, active, very_active)
        body_fat_pct: Porcentaje de grasa corporal (opcional, para fórmula Katch-McArdle)

    Returns:
        dict con BMR, TDEE y metodología usada
    """
    # Calcular BMR usando Mifflin-St Jeor (más precisa para población general)
    if sex.lower() == "male":
        bmr_mifflin = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr_mifflin = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

    # Si tenemos grasa corporal, usar Katch-McArdle
    bmr_katch = None
    if body_fat_pct is not None and 0 < body_fat_pct < 100:
        lean_mass = weight_kg * (1 - body_fat_pct / 100)
        bmr_katch = 370 + (21.6 * lean_mass)

    # Usar Katch-McArdle si disponible, sino Mifflin-St Jeor
    bmr = bmr_katch if bmr_katch else bmr_mifflin
    formula_used = "Katch-McArdle" if bmr_katch else "Mifflin-St Jeor"

    # Aplicar multiplicador de actividad
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    tdee = round(bmr * multiplier)

    # Rangos para diferentes objetivos
    ranges = {
        "aggressive_deficit": round(tdee * 0.75),  # -25%
        "moderate_deficit": round(tdee * 0.85),  # -15%
        "maintenance": tdee,
        "lean_bulk": round(tdee * 1.10),  # +10%
        "aggressive_bulk": round(tdee * 1.20),  # +20%
    }

    return {
        "bmr": round(bmr),
        "tdee": tdee,
        "formula": formula_used,
        "activity_level": activity_level,
        "activity_multiplier": multiplier,
        "calorie_ranges": ranges,
        "input": {
            "weight_kg": weight_kg,
            "height_cm": height_cm,
            "age": age,
            "sex": sex,
            "body_fat_pct": body_fat_pct,
        },
    }


def calculate_macros(
    target_calories: int,
    weight_kg: float,
    goal: str,
    training_days: int = 4,
    preference: str = "balanced",
) -> dict[str, Any]:
    """Calcula los macronutrientes basados en calorías y objetivo.

    Args:
        target_calories: Calorías diarias objetivo
        weight_kg: Peso corporal en kg
        goal: Objetivo (fat_loss, muscle_gain, recomposition, maintenance)
        training_days: Días de entrenamiento por semana
        preference: Preferencia de distribución (balanced, high_carb, low_carb, high_fat)

    Returns:
        dict con macros en gramos y porcentajes
    """
    # Proteína basada en objetivo y peso
    protein_per_kg = {
        "fat_loss": 2.2,  # Alta para preservar músculo
        "muscle_gain": 2.0,
        "recomposition": 2.0,
        "maintenance": 1.8,
        "performance": 1.8,
    }

    protein_g = round(weight_kg * protein_per_kg.get(goal, 1.8))
    protein_cal = protein_g * 4

    # Grasas mínimas para salud hormonal
    fat_min_g = round(weight_kg * 0.8)
    fat_min_cal = fat_min_g * 9

    # Calorías restantes para carbohidratos
    remaining_cal = target_calories - protein_cal - fat_min_cal

    # Ajustar según preferencia
    if preference == "low_carb":
        fat_g = round((target_calories * 0.40) / 9)
        carbs_g = round((target_calories - protein_cal - (fat_g * 9)) / 4)
    elif preference == "high_carb":
        fat_g = fat_min_g
        carbs_g = round(remaining_cal / 4)
    elif preference == "high_fat":
        fat_g = round((target_calories * 0.45) / 9)
        carbs_g = round((target_calories - protein_cal - (fat_g * 9)) / 4)
    else:  # balanced
        # 25-30% de calorías de grasa
        fat_g = round((target_calories * 0.28) / 9)
        carbs_g = round((target_calories - protein_cal - (fat_g * 9)) / 4)

    # Asegurar mínimos
    fat_g = max(fat_g, fat_min_g)
    carbs_g = max(carbs_g, 50)  # Mínimo 50g para función cerebral

    # Recalcular calorías reales
    actual_calories = (protein_g * 4) + (carbs_g * 4) + (fat_g * 9)

    # Porcentajes
    protein_pct = round((protein_g * 4 / actual_calories) * 100)
    carbs_pct = round((carbs_g * 4 / actual_calories) * 100)
    fat_pct = round((fat_g * 9 / actual_calories) * 100)

    # Fibra recomendada
    fiber_g = min(round(actual_calories / 1000 * 14), 40)  # 14g por 1000 kcal

    return {
        "calories": actual_calories,
        "protein": {
            "grams": protein_g,
            "per_kg": round(protein_g / weight_kg, 1),
            "percentage": protein_pct,
            "calories": protein_g * 4,
        },
        "carbohydrates": {
            "grams": carbs_g,
            "per_kg": round(carbs_g / weight_kg, 1),
            "percentage": carbs_pct,
            "calories": carbs_g * 4,
        },
        "fat": {
            "grams": fat_g,
            "per_kg": round(fat_g / weight_kg, 1),
            "percentage": fat_pct,
            "calories": fat_g * 9,
        },
        "fiber": {"grams": fiber_g},
        "goal": goal,
        "preference": preference,
        "water_liters": round(weight_kg * 0.035, 1),
    }


def suggest_meal_distribution(
    macros: dict[str, Any],
    meals_per_day: int = 4,
    training_time: Optional[str] = None,
) -> dict[str, Any]:
    """Sugiere distribución de comidas según macros y horario.

    Args:
        macros: Macros calculados (output de calculate_macros)
        meals_per_day: Número de comidas (3-6)
        training_time: Horario de entrenamiento ('morning', 'afternoon', 'evening', None)

    Returns:
        dict con distribución de comidas y timing de macros
    """
    calories = macros.get("calories", 2000)
    protein_g = macros.get("protein", {}).get("grams", 150)
    carbs_g = macros.get("carbohydrates", {}).get("grams", 200)
    fat_g = macros.get("fat", {}).get("grams", 70)

    meals_per_day = max(3, min(6, meals_per_day))

    # Distribución base por comida
    if meals_per_day == 3:
        distribution = [0.30, 0.40, 0.30]  # Desayuno, Almuerzo, Cena
        meal_names = ["Desayuno", "Almuerzo", "Cena"]
    elif meals_per_day == 4:
        distribution = [0.25, 0.30, 0.20, 0.25]
        meal_names = ["Desayuno", "Almuerzo", "Snack", "Cena"]
    elif meals_per_day == 5:
        distribution = [0.20, 0.10, 0.25, 0.20, 0.25]
        meal_names = ["Desayuno", "Snack AM", "Almuerzo", "Snack PM", "Cena"]
    else:  # 6
        distribution = [0.18, 0.10, 0.22, 0.10, 0.22, 0.18]
        meal_names = ["Desayuno", "Snack AM", "Almuerzo", "Snack PM", "Cena", "Snack Nocturno"]

    meals = []
    for i, (name, pct) in enumerate(zip(meal_names, distribution)):
        meals.append({
            "meal": name,
            "time_suggestion": _suggest_meal_time(i, meals_per_day, training_time),
            "calories": round(calories * pct),
            "protein_g": round(protein_g * pct),
            "carbs_g": round(carbs_g * pct),
            "fat_g": round(fat_g * pct),
        })

    # Ajustes para timing de entrenamiento
    training_notes = []
    if training_time:
        if training_time == "morning":
            training_notes = [
                "Desayuno: Mayor proporción de carbohidratos para energía",
                "Post-entrenamiento: Incluir proteína rápida + carbohidratos",
            ]
        elif training_time == "afternoon":
            training_notes = [
                "Almuerzo: Carbohidratos moderados pre-entreno",
                "Snack PM: Proteína + carbohidratos post-entreno",
            ]
        elif training_time == "evening":
            training_notes = [
                "Snack PM: Carbohidratos pre-entreno",
                "Cena: Proteína alta post-entreno, carbohidratos moderados",
            ]

    return {
        "meals_per_day": meals_per_day,
        "meals": meals,
        "training_time": training_time,
        "training_notes": training_notes,
        "protein_distribution_note": f"Distribuir {protein_g}g proteína en {meals_per_day} comidas = ~{round(protein_g/meals_per_day)}g por comida",
    }


def _suggest_meal_time(meal_index: int, total_meals: int, training_time: Optional[str]) -> str:
    """Sugiere horario para una comida."""
    base_times = {
        3: ["7:00-8:00", "13:00-14:00", "19:00-20:00"],
        4: ["7:00-8:00", "13:00-14:00", "16:00-17:00", "20:00-21:00"],
        5: ["7:00", "10:00", "13:00", "16:00", "20:00"],
        6: ["6:30", "9:30", "12:30", "15:30", "18:30", "21:00"],
    }
    times = base_times.get(total_meals, base_times[4])
    return times[meal_index] if meal_index < len(times) else "Variable"


def get_food_suggestions(
    category: str,
    dietary_preference: str = "omnivore",
    exclude: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Obtiene sugerencias de alimentos por categoría.

    Args:
        category: Categoría (protein, carbs, fats, vegetables)
        dietary_preference: Preferencia dietética
        exclude: Lista de alimentos a excluir

    Returns:
        dict con alimentos sugeridos y sus macros
    """
    exclude = exclude or []
    exclude_lower = [e.lower() for e in exclude]

    foods = FOOD_DATABASE.get(category, {})
    suggestions = {}

    for food_id, food_data in foods.items():
        # Filtrar por preferencia dietética
        if dietary_preference == "vegetarian":
            if food_id in ["chicken_breast", "salmon", "lean_beef"]:
                continue
        elif dietary_preference == "vegan":
            if food_id in ["chicken_breast", "salmon", "lean_beef", "eggs", "greek_yogurt", "whey_protein"]:
                continue

        # Filtrar excluidos
        if food_id in exclude_lower or food_data["name_es"].lower() in exclude_lower:
            continue

        suggestions[food_id] = food_data

    return {
        "category": category,
        "dietary_preference": dietary_preference,
        "foods": suggestions,
        "count": len(suggestions),
    }


def evaluate_progress(
    starting_weight: float,
    current_weight: float,
    weeks_elapsed: int,
    goal: str,
    current_calories: int,
) -> dict[str, Any]:
    """Evalúa el progreso y sugiere ajustes.

    Args:
        starting_weight: Peso inicial en kg
        current_weight: Peso actual en kg
        weeks_elapsed: Semanas transcurridas
        goal: Objetivo (fat_loss, muscle_gain, etc.)
        current_calories: Calorías actuales

    Returns:
        dict con evaluación y recomendaciones
    """
    weight_change = current_weight - starting_weight
    weekly_change = weight_change / max(weeks_elapsed, 1)

    # Rangos óptimos de cambio semanal
    optimal_ranges = {
        "fat_loss": (-0.75, -0.25),  # Perder 0.25-0.75 kg/semana
        "muscle_gain": (0.1, 0.3),  # Ganar 0.1-0.3 kg/semana
        "recomposition": (-0.2, 0.2),  # Cambio mínimo
        "maintenance": (-0.1, 0.1),
    }

    optimal = optimal_ranges.get(goal, (-0.3, 0.3))
    is_on_track = optimal[0] <= weekly_change <= optimal[1]

    # Generar recomendaciones
    recommendations = []
    calorie_adjustment = 0

    if goal == "fat_loss":
        if weekly_change > optimal[1]:  # No perdiendo suficiente
            recommendations.append("Considera reducir 100-200 kcal")
            calorie_adjustment = -150
        elif weekly_change < optimal[0]:  # Perdiendo muy rápido
            recommendations.append("Pérdida muy rápida. Considera aumentar 100-200 kcal")
            calorie_adjustment = 150
            recommendations.append("Riesgo de pérdida muscular. Asegura proteína alta.")
    elif goal == "muscle_gain":
        if weekly_change < optimal[0]:  # No ganando suficiente
            recommendations.append("Considera aumentar 150-250 kcal")
            calorie_adjustment = 200
        elif weekly_change > optimal[1]:  # Ganando muy rápido
            recommendations.append("Ganancia rápida puede incluir grasa. Reduce 100 kcal.")
            calorie_adjustment = -100

    if not recommendations:
        recommendations.append("Progreso en línea con el objetivo. Mantener plan actual.")

    return {
        "starting_weight": starting_weight,
        "current_weight": current_weight,
        "total_change_kg": round(weight_change, 2),
        "weekly_change_kg": round(weekly_change, 2),
        "weeks_elapsed": weeks_elapsed,
        "goal": goal,
        "is_on_track": is_on_track,
        "optimal_weekly_range": optimal,
        "recommendations": recommendations,
        "suggested_calorie_adjustment": calorie_adjustment,
        "new_calorie_target": current_calories + calorie_adjustment if calorie_adjustment else current_calories,
    }


# =============================================================================
# Wrapped FunctionTools for ADK
# =============================================================================

calculate_tdee_tool = FunctionTool(calculate_tdee)
calculate_macros_tool = FunctionTool(calculate_macros)
suggest_meal_distribution_tool = FunctionTool(suggest_meal_distribution)
get_food_suggestions_tool = FunctionTool(get_food_suggestions)
evaluate_progress_tool = FunctionTool(evaluate_progress)

# Lista de todas las tools disponibles
ALL_TOOLS = [
    calculate_tdee_tool,
    calculate_macros_tool,
    suggest_meal_distribution_tool,
    get_food_suggestions_tool,
    evaluate_progress_tool,
]
