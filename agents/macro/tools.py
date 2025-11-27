"""Tools para MACRO - Agente de Macronutrientes.

Incluye funciones para:
- Cálculo de macronutrientes diarios
- Distribución óptima de proteína
- Planificación de ciclado de carbohidratos
- Optimización de ingesta de grasas
- Composición de comidas balanceadas
"""

from __future__ import annotations

from enum import Enum

from google.adk.tools import FunctionTool


# =============================================================================
# ENUMS Y TIPOS
# =============================================================================


class NutritionGoal(str, Enum):
    """Objetivos nutricionales."""

    FAT_LOSS = "fat_loss"
    MAINTENANCE = "maintenance"
    MUSCLE_GAIN = "muscle_gain"
    RECOMP = "recomp"
    PERFORMANCE = "performance"


class ActivityType(str, Enum):
    """Tipos de actividad física."""

    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    STRENGTH = "strength"
    ENDURANCE = "endurance"
    HYBRID = "hybrid"


class CarbCycleDay(str, Enum):
    """Tipos de día en ciclado de carbohidratos."""

    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    REFEED = "refeed"


class FatSource(str, Enum):
    """Fuentes de grasas."""

    SATURATED = "saturated"
    MONOUNSATURATED = "monounsaturated"
    POLYUNSATURATED = "polyunsaturated"
    OMEGA3 = "omega3"
    OMEGA6 = "omega6"


# =============================================================================
# DATOS DE REFERENCIA
# =============================================================================


MACRO_RATIOS: dict[str, dict[str, dict[str, float]]] = {
    "fat_loss": {
        "standard": {"protein": 0.40, "carbs": 0.25, "fat": 0.35},
        "high_protein": {"protein": 0.45, "carbs": 0.20, "fat": 0.35},
        "moderate_carb": {"protein": 0.35, "carbs": 0.35, "fat": 0.30},
        "name_es": "Pérdida de grasa",
        "description": "Mayor proteína para preservar músculo en déficit",
    },
    "maintenance": {
        "standard": {"protein": 0.30, "carbs": 0.40, "fat": 0.30},
        "balanced": {"protein": 0.30, "carbs": 0.35, "fat": 0.35},
        "performance": {"protein": 0.25, "carbs": 0.45, "fat": 0.30},
        "name_es": "Mantenimiento",
        "description": "Balance para sostener peso y rendimiento",
    },
    "muscle_gain": {
        "standard": {"protein": 0.30, "carbs": 0.45, "fat": 0.25},
        "lean_bulk": {"protein": 0.35, "carbs": 0.40, "fat": 0.25},
        "aggressive": {"protein": 0.25, "carbs": 0.50, "fat": 0.25},
        "name_es": "Ganancia muscular",
        "description": "Carbohidratos elevados para síntesis y energía",
    },
    "recomp": {
        "standard": {"protein": 0.40, "carbs": 0.30, "fat": 0.30},
        "carb_cycling": {"protein": 0.40, "carbs": 0.35, "fat": 0.25},
        "name_es": "Recomposición",
        "description": "Alta proteína con carbos periódicos",
    },
    "performance": {
        "standard": {"protein": 0.25, "carbs": 0.50, "fat": 0.25},
        "endurance": {"protein": 0.20, "carbs": 0.55, "fat": 0.25},
        "strength": {"protein": 0.30, "carbs": 0.45, "fat": 0.25},
        "name_es": "Rendimiento",
        "description": "Optimizado para máximo rendimiento atlético",
    },
}


PROTEIN_TARGETS: dict[str, dict[str, float | str]] = {
    "sedentary": {
        "g_per_kg": 0.8,
        "g_per_kg_range_low": 0.8,
        "g_per_kg_range_high": 1.0,
        "name_es": "Sedentario",
        "description": "Mínimo para mantener masa muscular",
    },
    "light": {
        "g_per_kg": 1.0,
        "g_per_kg_range_low": 0.8,
        "g_per_kg_range_high": 1.2,
        "name_es": "Actividad ligera",
        "description": "Actividad recreativa ocasional",
    },
    "moderate": {
        "g_per_kg": 1.2,
        "g_per_kg_range_low": 1.0,
        "g_per_kg_range_high": 1.4,
        "name_es": "Actividad moderada",
        "description": "Ejercicio regular 3-4 días/semana",
    },
    "strength": {
        "g_per_kg": 1.6,
        "g_per_kg_range_low": 1.4,
        "g_per_kg_range_high": 2.2,
        "name_es": "Entrenamiento de fuerza",
        "description": "Enfoque en hipertrofia o fuerza",
    },
    "endurance": {
        "g_per_kg": 1.4,
        "g_per_kg_range_low": 1.2,
        "g_per_kg_range_high": 1.8,
        "name_es": "Resistencia",
        "description": "Deportes de resistencia (running, ciclismo)",
    },
    "hybrid": {
        "g_per_kg": 1.6,
        "g_per_kg_range_low": 1.4,
        "g_per_kg_range_high": 2.0,
        "name_es": "Híbrido",
        "description": "Combinación fuerza + resistencia",
    },
    "fat_loss": {
        "g_per_kg": 2.0,
        "g_per_kg_range_low": 1.8,
        "g_per_kg_range_high": 2.4,
        "name_es": "Déficit calórico",
        "description": "Proteína alta para preservar músculo",
    },
}


CARB_CYCLING_PATTERNS: dict[str, dict[str, list[str] | str | float]] = {
    "classic_3day": {
        "pattern": ["high", "moderate", "low"],
        "name_es": "Clásico 3 días",
        "description": "Rotación simple: alto-moderado-bajo",
        "high_multiplier": 1.3,
        "moderate_multiplier": 1.0,
        "low_multiplier": 0.5,
    },
    "training_based": {
        "pattern": ["high", "high", "moderate", "low", "moderate", "low", "refeed"],
        "name_es": "Basado en entrenamiento",
        "description": "Altos en días de entrenamiento intenso",
        "high_multiplier": 1.4,
        "moderate_multiplier": 1.0,
        "low_multiplier": 0.4,
    },
    "weekend_refeed": {
        "pattern": ["low", "low", "low", "low", "low", "high", "high"],
        "name_es": "Recarga fin de semana",
        "description": "Bajos entre semana, recargas el fin de semana",
        "high_multiplier": 1.5,
        "moderate_multiplier": 1.0,
        "low_multiplier": 0.3,
    },
    "alternating": {
        "pattern": ["high", "low"],
        "name_es": "Alternado",
        "description": "Días alternados alto-bajo",
        "high_multiplier": 1.4,
        "moderate_multiplier": 1.0,
        "low_multiplier": 0.5,
    },
    "5_2": {
        "pattern": ["moderate", "moderate", "moderate", "moderate", "moderate", "low", "low"],
        "name_es": "5:2 modificado",
        "description": "5 días normales, 2 días bajos",
        "high_multiplier": 1.2,
        "moderate_multiplier": 1.0,
        "low_multiplier": 0.4,
    },
}


FAT_DISTRIBUTION: dict[str, dict[str, float | str | list[str]]] = {
    "saturated": {
        "max_percent": 0.10,
        "ideal_percent": 0.07,
        "name_es": "Saturadas",
        "description": "Limitar, asociadas a riesgo cardiovascular",
        "sources": ["carne roja", "lácteos enteros", "aceite de coco"],
    },
    "monounsaturated": {
        "min_percent": 0.10,
        "ideal_percent": 0.15,
        "name_es": "Monoinsaturadas",
        "description": "Base de grasas saludables",
        "sources": ["aceite de oliva", "aguacate", "nueces", "almendras"],
    },
    "polyunsaturated": {
        "min_percent": 0.05,
        "ideal_percent": 0.08,
        "name_es": "Poliinsaturadas",
        "description": "Esenciales, incluyen omega-3 y omega-6",
        "sources": ["pescado graso", "semillas", "nueces"],
    },
    "omega3": {
        "min_g_daily": 1.0,
        "ideal_g_daily": 2.5,
        "epa_dha_min_mg": 250,
        "epa_dha_ideal_mg": 500,
        "name_es": "Omega-3",
        "description": "Antiinflamatorio, salud cardiovascular y cerebral",
        "sources": ["salmón", "sardinas", "caballa", "linaza", "chía", "nueces"],
    },
    "omega6": {
        "max_ratio_to_omega3": 4.0,
        "ideal_ratio_to_omega3": 2.0,
        "name_es": "Omega-6",
        "description": "Esencial pero balancear con omega-3",
        "sources": ["aceites vegetales", "semillas", "frutos secos"],
    },
    "trans": {
        "max_percent": 0.0,
        "name_es": "Trans",
        "description": "EVITAR completamente - dañinas",
        "sources": ["alimentos ultraprocesados", "margarinas hidrogenadas"],
    },
}


MEAL_TEMPLATES: dict[str, dict[str, dict[str, float] | str | list[str]]] = {
    "balanced": {
        "ratios": {"protein": 0.30, "carbs": 0.40, "fat": 0.30},
        "name_es": "Balanceado",
        "description": "Distribución equilibrada estándar",
        "best_for": ["mantenimiento", "comidas principales"],
    },
    "pre_workout": {
        "ratios": {"protein": 0.25, "carbs": 0.55, "fat": 0.20},
        "name_es": "Pre-entrenamiento",
        "description": "Énfasis en carbohidratos para energía",
        "best_for": ["1-2 horas antes de entrenar"],
        "timing": "1-2 horas antes",
    },
    "post_workout": {
        "ratios": {"protein": 0.35, "carbs": 0.50, "fat": 0.15},
        "name_es": "Post-entrenamiento",
        "description": "Alto en proteína y carbos para recuperación",
        "best_for": ["30-60 min después de entrenar"],
        "timing": "30-60 minutos después",
    },
    "high_protein": {
        "ratios": {"protein": 0.45, "carbs": 0.30, "fat": 0.25},
        "name_es": "Alta proteína",
        "description": "Enfocado en síntesis proteica",
        "best_for": ["déficit calórico", "ganancia muscular"],
    },
    "low_carb": {
        "ratios": {"protein": 0.40, "carbs": 0.15, "fat": 0.45},
        "name_es": "Bajo en carbohidratos",
        "description": "Para días de descanso o bajos en carbs",
        "best_for": ["días de descanso", "ciclado de carbos"],
    },
    "before_sleep": {
        "ratios": {"protein": 0.40, "carbs": 0.20, "fat": 0.40},
        "name_es": "Antes de dormir",
        "description": "Digestión lenta, sin picos de insulina",
        "best_for": ["última comida del día"],
        "timing": "1-2 horas antes de dormir",
    },
}


PROTEIN_SOURCES: dict[str, dict[str, float | str | bool]] = {
    "chicken_breast": {
        "protein_per_100g": 31.0,
        "fat_per_100g": 3.6,
        "carbs_per_100g": 0.0,
        "calories_per_100g": 165,
        "name_es": "Pechuga de pollo",
        "quality": "high",
        "complete": True,
    },
    "salmon": {
        "protein_per_100g": 25.0,
        "fat_per_100g": 13.0,
        "carbs_per_100g": 0.0,
        "calories_per_100g": 208,
        "name_es": "Salmón",
        "quality": "high",
        "complete": True,
        "omega3": True,
    },
    "beef_lean": {
        "protein_per_100g": 26.0,
        "fat_per_100g": 15.0,
        "carbs_per_100g": 0.0,
        "calories_per_100g": 250,
        "name_es": "Res magra",
        "quality": "high",
        "complete": True,
    },
    "eggs": {
        "protein_per_100g": 13.0,
        "fat_per_100g": 11.0,
        "carbs_per_100g": 1.1,
        "calories_per_100g": 155,
        "name_es": "Huevos",
        "quality": "high",
        "complete": True,
    },
    "greek_yogurt": {
        "protein_per_100g": 10.0,
        "fat_per_100g": 0.7,
        "carbs_per_100g": 3.6,
        "calories_per_100g": 59,
        "name_es": "Yogur griego",
        "quality": "high",
        "complete": True,
    },
    "whey_protein": {
        "protein_per_100g": 80.0,
        "fat_per_100g": 5.0,
        "carbs_per_100g": 8.0,
        "calories_per_100g": 400,
        "name_es": "Proteína de suero",
        "quality": "high",
        "complete": True,
        "supplement": True,
    },
    "tofu": {
        "protein_per_100g": 8.0,
        "fat_per_100g": 4.8,
        "carbs_per_100g": 1.9,
        "calories_per_100g": 76,
        "name_es": "Tofu",
        "quality": "moderate",
        "complete": True,
        "vegan": True,
    },
    "lentils": {
        "protein_per_100g": 9.0,
        "fat_per_100g": 0.4,
        "carbs_per_100g": 20.0,
        "calories_per_100g": 116,
        "name_es": "Lentejas",
        "quality": "moderate",
        "complete": False,
        "vegan": True,
    },
}


# =============================================================================
# FUNCIONES DE CÁLCULO
# =============================================================================


def calculate_macros(
    daily_calories: int,
    goal: str = "maintenance",
    approach: str = "standard",
    weight_kg: float | None = None,
    activity_type: str = "moderate",
    custom_protein_g: float | None = None,
) -> dict:
    """Calcula los macronutrientes diarios según objetivo y calorías.

    Args:
        daily_calories: Calorías totales diarias (TDEE ajustado).
        goal: Objetivo nutricional (fat_loss, maintenance, muscle_gain, recomp, performance).
        approach: Enfoque dentro del objetivo (standard, high_protein, lean_bulk, etc.).
        weight_kg: Peso en kg (opcional, para cálculo por kg de peso).
        activity_type: Tipo de actividad para ajuste de proteína.
        custom_protein_g: Proteína personalizada en gramos (override).

    Returns:
        Dict con macros calculados, gramos y porcentajes.
    """
    # Validaciones
    if daily_calories < 800 or daily_calories > 10000:
        return {
            "status": "error",
            "error": "Calorías deben estar entre 800 y 10000",
        }

    if goal not in MACRO_RATIOS:
        return {
            "status": "error",
            "error": f"Objetivo no válido. Opciones: {list(MACRO_RATIOS.keys())}",
        }

    goal_data = MACRO_RATIOS[goal]
    if approach not in goal_data or approach in ["name_es", "description"]:
        approach = "standard"

    ratios = goal_data[approach]

    # Calcular proteína
    if custom_protein_g is not None and custom_protein_g > 0:
        protein_g = custom_protein_g
        protein_kcal = protein_g * 4
        protein_pct = protein_kcal / daily_calories
    elif weight_kg is not None and weight_kg > 0:
        # Calcular por peso corporal según actividad
        activity_data = PROTEIN_TARGETS.get(activity_type, PROTEIN_TARGETS["moderate"])
        if goal == "fat_loss":
            activity_data = PROTEIN_TARGETS["fat_loss"]
        g_per_kg = float(activity_data["g_per_kg"])
        protein_g = round(weight_kg * g_per_kg, 1)
        protein_kcal = protein_g * 4
        protein_pct = protein_kcal / daily_calories
    else:
        protein_pct = ratios["protein"]
        protein_kcal = daily_calories * protein_pct
        protein_g = round(protein_kcal / 4, 1)

    # Calcular grasas (mínimo 20% para salud hormonal)
    fat_pct = max(ratios["fat"], 0.20)
    fat_kcal = daily_calories * fat_pct
    fat_g = round(fat_kcal / 9, 1)

    # Calcular carbohidratos (lo que resta)
    remaining_kcal = daily_calories - protein_kcal - fat_kcal
    carbs_kcal = max(remaining_kcal, 0)
    carbs_g = round(carbs_kcal / 4, 1)
    carbs_pct = carbs_kcal / daily_calories if daily_calories > 0 else 0

    # Recalcular porcentajes finales
    actual_protein_pct = round(protein_pct * 100, 1)
    actual_fat_pct = round(fat_pct * 100, 1)
    actual_carbs_pct = round(carbs_pct * 100, 1)

    # Verificar mínimos de carbohidratos para rendimiento
    warnings = []
    if carbs_g < 50:
        warnings.append(
            "Carbohidratos muy bajos (<50g). Puede afectar energía y rendimiento."
        )
    if fat_g < 0.5 * (weight_kg or 70):
        warnings.append(
            "Grasas bajas pueden afectar hormonas. Considere aumentar."
        )

    return {
        "status": "calculated",
        "daily_calories": daily_calories,
        "goal": goal,
        "goal_name_es": goal_data.get("name_es", goal),
        "approach": approach,
        "macros": {
            "protein": {
                "grams": protein_g,
                "calories": round(protein_kcal),
                "percent": actual_protein_pct,
            },
            "carbs": {
                "grams": carbs_g,
                "calories": round(carbs_kcal),
                "percent": actual_carbs_pct,
            },
            "fat": {
                "grams": fat_g,
                "calories": round(fat_kcal),
                "percent": actual_fat_pct,
            },
        },
        "summary": {
            "total_calories": round(protein_kcal + carbs_kcal + fat_kcal),
            "protein_per_kg": round(protein_g / weight_kg, 2) if weight_kg else None,
            "caloric_balance": round(
                protein_kcal + carbs_kcal + fat_kcal - daily_calories
            ),
        },
        "ranges": {
            "protein": {
                "low": round(protein_g * 0.9, 1),
                "high": round(protein_g * 1.1, 1),
            },
            "carbs": {
                "low": round(carbs_g * 0.85, 1),
                "high": round(carbs_g * 1.15, 1),
            },
            "fat": {
                "low": round(fat_g * 0.9, 1),
                "high": round(fat_g * 1.1, 1),
            },
        },
        "warnings": warnings if warnings else None,
        "recommendations": [
            f"Distribuye la proteína ({protein_g}g) en 4-5 comidas de ~{round(protein_g/4)}g",
            "Prioriza carbohidratos alrededor del entrenamiento",
            "Incluye grasas saludables: aguacate, aceite de oliva, frutos secos",
            "Ajusta según tu respuesta individual después de 2-3 semanas",
        ],
    }


def distribute_protein(
    daily_protein_g: float,
    meals_per_day: int = 4,
    training_time: str | None = None,
    weight_kg: float | None = None,
    goal: str = "maintenance",
) -> dict:
    """Distribuye la proteína diaria entre comidas de forma óptima.

    Args:
        daily_protein_g: Gramos totales de proteína diaria.
        meals_per_day: Número de comidas principales (3-6).
        training_time: Hora de entrenamiento (HH:MM) para priorizar.
        weight_kg: Peso corporal para calcular por comida óptimo.
        goal: Objetivo para ajustar distribución.

    Returns:
        Dict con distribución de proteína por comida.
    """
    # Validaciones
    if daily_protein_g < 30 or daily_protein_g > 400:
        return {
            "status": "error",
            "error": "Proteína diaria debe estar entre 30g y 400g",
        }

    if meals_per_day < 2 or meals_per_day > 8:
        return {
            "status": "error",
            "error": "Número de comidas debe estar entre 2 y 8",
        }

    # Calcular proteína óptima por comida (20-40g para máxima síntesis)
    optimal_per_meal = min(max(daily_protein_g / meals_per_day, 20), 50)

    # Ajustar según objetivo
    if goal == "muscle_gain":
        # Más énfasis en post-entreno y antes de dormir
        distribution_weights = _get_muscle_gain_distribution(meals_per_day)
    elif goal == "fat_loss":
        # Distribución más uniforme, proteína alta en cada comida
        distribution_weights = _get_fat_loss_distribution(meals_per_day)
    else:
        distribution_weights = _get_balanced_distribution(meals_per_day)

    # Calcular gramos por comida
    meals = []
    total_distributed = 0

    meal_names = _get_meal_names(meals_per_day)

    for i, (name, weight) in enumerate(zip(meal_names, distribution_weights)):
        protein_g = round(daily_protein_g * weight, 1)
        total_distributed += protein_g

        meal = {
            "meal_number": i + 1,
            "name": name,
            "protein_g": protein_g,
            "percent_of_daily": round(weight * 100, 1),
            "sources_suggestion": _suggest_protein_sources(protein_g),
        }

        # Marcar comidas especiales
        if "entrenamiento" in name.lower():
            meal["priority"] = "high"
            meal["note"] = "Ventana anabólica - proteína de rápida absorción"
        elif "dormir" in name.lower() or "cena" in name.lower():
            meal["note"] = "Caseína o proteína de digestión lenta recomendada"

        meals.append(meal)

    # Ajustar redondeo
    diff = round(daily_protein_g - total_distributed, 1)
    if abs(diff) > 0.5:
        meals[-1]["protein_g"] = round(meals[-1]["protein_g"] + diff, 1)

    # Verificar síntesis proteica óptima
    synthesis_optimal = all(m["protein_g"] >= 20 for m in meals)
    leucine_threshold_note = (
        "Cada comida alcanza ~3g de leucina (umbral de síntesis)"
        if synthesis_optimal
        else "Considera reducir comidas para alcanzar 20g+ por comida"
    )

    return {
        "status": "distributed",
        "daily_protein_g": daily_protein_g,
        "meals_per_day": meals_per_day,
        "goal": goal,
        "distribution": meals,
        "synthesis_analysis": {
            "optimal_per_meal": round(optimal_per_meal, 1),
            "all_meals_optimal": synthesis_optimal,
            "note": leucine_threshold_note,
        },
        "timing_recommendations": {
            "pre_workout": "20-30g proteína 1-2h antes de entrenar",
            "post_workout": "25-40g proteína dentro de 2h post-entreno",
            "before_sleep": "30-40g caseína o proteína de lenta absorción",
        },
        "protein_quality_tips": [
            "Prioriza fuentes completas (carne, huevo, lácteos, soya)",
            "Combina legumbres + cereales si es dieta vegetal",
            "Espacía comidas 3-4 horas para optimizar síntesis",
        ],
    }


def plan_carb_cycling(
    base_carbs_g: float,
    training_days: list[str],
    pattern: str = "training_based",
    goal: str = "fat_loss",
    daily_calories: int | None = None,
) -> dict:
    """Planifica el ciclado de carbohidratos semanal.

    Args:
        base_carbs_g: Carbohidratos base (promedio diario).
        training_days: Lista de días de entrenamiento (lunes, martes, etc.).
        pattern: Patrón de ciclado a usar.
        goal: Objetivo del ciclado.
        daily_calories: Calorías totales para calcular porcentajes.

    Returns:
        Dict con plan de ciclado semanal.
    """
    # Validaciones
    if base_carbs_g < 30 or base_carbs_g > 600:
        return {
            "status": "error",
            "error": "Carbohidratos base deben estar entre 30g y 600g",
        }

    if pattern not in CARB_CYCLING_PATTERNS:
        return {
            "status": "error",
            "error": f"Patrón no válido. Opciones: {list(CARB_CYCLING_PATTERNS.keys())}",
        }

    pattern_data = CARB_CYCLING_PATTERNS[pattern]
    high_mult = float(pattern_data["high_multiplier"])
    mod_mult = float(pattern_data["moderate_multiplier"])
    low_mult = float(pattern_data["low_multiplier"])

    # Calcular carbos para cada tipo de día
    carbs_high = round(base_carbs_g * high_mult)
    carbs_moderate = round(base_carbs_g * mod_mult)
    carbs_low = round(base_carbs_g * low_mult)

    # Normalizar días de entrenamiento
    days_map = {
        "lunes": 0, "monday": 0,
        "martes": 1, "tuesday": 1,
        "miercoles": 2, "miércoles": 2, "wednesday": 2,
        "jueves": 3, "thursday": 3,
        "viernes": 4, "friday": 4,
        "sabado": 5, "sábado": 5, "saturday": 5,
        "domingo": 6, "sunday": 6,
    }

    training_indices = set()
    for day in training_days:
        day_lower = day.lower().strip()
        if day_lower in days_map:
            training_indices.add(days_map[day_lower])

    # Crear plan semanal
    week_days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    weekly_plan = []
    total_carbs_week = 0

    for i, day_name in enumerate(week_days):
        is_training = i in training_indices

        if is_training:
            day_type = "high"
            carbs = carbs_high
        elif i == 6:  # Domingo como posible refeed
            day_type = "moderate" if goal == "muscle_gain" else "low"
            carbs = carbs_moderate if goal == "muscle_gain" else carbs_low
        else:
            day_type = "low" if goal == "fat_loss" else "moderate"
            carbs = carbs_low if goal == "fat_loss" else carbs_moderate

        total_carbs_week += carbs

        day_plan = {
            "day": day_name,
            "day_index": i,
            "is_training_day": is_training,
            "carb_type": day_type,
            "carbs_g": carbs,
            "calories_from_carbs": carbs * 4,
        }

        if is_training:
            day_plan["timing_note"] = "Mayoría de carbos pre y post entrenamiento"
        elif day_type == "low":
            day_plan["timing_note"] = "Carbos principalmente en desayuno y almuerzo"

        weekly_plan.append(day_plan)

    # Calcular promedios
    avg_daily_carbs = round(total_carbs_week / 7, 1)

    return {
        "status": "planned",
        "pattern": pattern,
        "pattern_name_es": pattern_data["name_es"],
        "goal": goal,
        "base_carbs_g": base_carbs_g,
        "carb_levels": {
            "high": {"grams": carbs_high, "calories": carbs_high * 4},
            "moderate": {"grams": carbs_moderate, "calories": carbs_moderate * 4},
            "low": {"grams": carbs_low, "calories": carbs_low * 4},
        },
        "weekly_plan": weekly_plan,
        "summary": {
            "total_weekly_carbs": total_carbs_week,
            "avg_daily_carbs": avg_daily_carbs,
            "training_days_count": len(training_indices),
            "high_days": sum(1 for d in weekly_plan if d["carb_type"] == "high"),
            "low_days": sum(1 for d in weekly_plan if d["carb_type"] == "low"),
        },
        "carb_source_recommendations": {
            "high_days": ["avena", "arroz", "papa", "frutas", "pan integral"],
            "moderate_days": ["arroz", "legumbres", "verduras con almidón"],
            "low_days": ["verduras verdes", "bayas", "legumbres en pequeñas cantidades"],
        },
        "adjustment_notes": [
            "Ajusta después de 2 semanas según energía y resultados",
            "En días bajos, aumenta verduras y grasas para saciedad",
            "Los días altos deben coincidir con entrenamientos intensos",
        ],
    }


def optimize_fat_intake(
    daily_fat_g: float,
    current_omega3_g: float = 0.0,
    has_health_conditions: bool = False,
    dietary_restrictions: list[str] | None = None,
) -> dict:
    """Optimiza la ingesta de grasas según tipo y fuentes.

    Args:
        daily_fat_g: Gramos totales de grasa diaria.
        current_omega3_g: Ingesta actual estimada de omega-3.
        has_health_conditions: Si tiene condiciones de salud relevantes.
        dietary_restrictions: Restricciones dietéticas (vegano, etc.).

    Returns:
        Dict con distribución óptima de tipos de grasa.
    """
    # Validaciones
    if daily_fat_g < 20 or daily_fat_g > 300:
        return {
            "status": "error",
            "error": "Grasa diaria debe estar entre 20g y 300g",
        }

    restrictions = dietary_restrictions or []
    is_vegan = "vegano" in [r.lower() for r in restrictions]
    is_pescetarian = "pescetariano" in [r.lower() for r in restrictions]

    # Calcular distribución ideal
    total_calories_from_fat = daily_fat_g * 9

    # Saturadas: máximo 7-10%
    saturated_max_g = round(daily_fat_g * 0.10, 1)
    saturated_ideal_g = round(daily_fat_g * 0.07, 1)

    # Monoinsaturadas: 10-15% de calorías totales
    mono_ideal_g = round(daily_fat_g * 0.40, 1)  # ~40% de grasas totales
    mono_min_g = round(daily_fat_g * 0.30, 1)

    # Poliinsaturadas: ~25-30% de grasas totales
    poly_ideal_g = round(daily_fat_g * 0.25, 1)

    # Omega-3 específico
    omega3_data = FAT_DISTRIBUTION["omega3"]
    omega3_ideal_g = float(omega3_data["ideal_g_daily"])
    omega3_deficit = max(0, omega3_ideal_g - current_omega3_g)

    # Construir recomendaciones de fuentes
    sources = _get_fat_sources(is_vegan, is_pescetarian)

    # Evaluar balance omega-6/omega-3
    omega_balance = "óptimo" if current_omega3_g >= 1.5 else "mejorable"
    if current_omega3_g < 0.5:
        omega_balance = "insuficiente"

    return {
        "status": "optimized",
        "daily_fat_g": daily_fat_g,
        "calories_from_fat": round(total_calories_from_fat),
        "distribution": {
            "saturated": {
                "max_g": saturated_max_g,
                "ideal_g": saturated_ideal_g,
                "note": "Limitar, preferir fuentes naturales (coco, lácteos)",
            },
            "monounsaturated": {
                "ideal_g": mono_ideal_g,
                "min_g": mono_min_g,
                "note": "Base principal de grasas - aceite de oliva, aguacate",
            },
            "polyunsaturated": {
                "ideal_g": poly_ideal_g,
                "note": "Incluir omega-3 y omega-6 en balance",
            },
            "trans": {
                "max_g": 0,
                "note": "EVITAR completamente",
            },
        },
        "omega3_analysis": {
            "current_g": current_omega3_g,
            "ideal_g": omega3_ideal_g,
            "deficit_g": round(omega3_deficit, 1),
            "epa_dha_ideal_mg": omega3_data["epa_dha_ideal_mg"],
            "status": omega_balance,
            "recommendation": (
                "Aumentar consumo de pescado graso o suplementar"
                if omega3_deficit > 0.5
                else "Ingesta adecuada"
            ),
        },
        "recommended_sources": sources,
        "daily_suggestions": [
            f"1-2 cucharadas de aceite de oliva extra virgen (~{round(14*2)}g)",
            f"1/2 aguacate (~{round(15)}g de grasa saludable)",
            "Un puñado de nueces o almendras (~15-20g)",
            "Pescado graso 2-3 veces por semana" if not is_vegan else "Semillas de chía/linaza diario",
        ],
        "health_notes": [
            "Grasas saludables son esenciales para hormonas y absorción de vitaminas",
            "No eliminar grasas - mínimo 0.5g por kg de peso corporal",
            "Evitar frituras y aceites vegetales refinados en exceso",
        ] + (
            ["Considere omega-3 de algas si es vegano"]
            if is_vegan
            else []
        ),
    }


def compose_meal(
    target_calories: int,
    target_protein_g: float | None = None,
    meal_type: str = "balanced",
    available_foods: list[str] | None = None,
    dietary_restrictions: list[str] | None = None,
) -> dict:
    """Compone una comida que cumpla con los objetivos de macros.

    Args:
        target_calories: Calorías objetivo para la comida.
        target_protein_g: Proteína objetivo en gramos (opcional).
        meal_type: Tipo de comida (balanced, pre_workout, post_workout, etc.).
        available_foods: Lista de alimentos disponibles (opcional).
        dietary_restrictions: Restricciones dietéticas.

    Returns:
        Dict con composición de comida sugerida.
    """
    # Validaciones
    if target_calories < 100 or target_calories > 2000:
        return {
            "status": "error",
            "error": "Calorías por comida deben estar entre 100 y 2000",
        }

    if meal_type not in MEAL_TEMPLATES:
        meal_type = "balanced"

    template = MEAL_TEMPLATES[meal_type]
    ratios = template["ratios"]

    # Calcular macros objetivo
    protein_kcal = target_calories * ratios["protein"]
    carbs_kcal = target_calories * ratios["carbs"]
    fat_kcal = target_calories * ratios["fat"]

    # Si hay proteína específica, ajustar
    if target_protein_g is not None and target_protein_g > 0:
        protein_kcal = target_protein_g * 4
        # Redistribuir el resto
        remaining = target_calories - protein_kcal
        carbs_kcal = remaining * (ratios["carbs"] / (ratios["carbs"] + ratios["fat"]))
        fat_kcal = remaining - carbs_kcal

    protein_g = round(protein_kcal / 4, 1)
    carbs_g = round(carbs_kcal / 4, 1)
    fat_g = round(fat_kcal / 9, 1)

    # Generar sugerencia de alimentos
    restrictions = dietary_restrictions or []
    is_vegan = "vegano" in [r.lower() for r in restrictions]

    suggested_foods = _suggest_meal_foods(
        protein_g=protein_g,
        carbs_g=carbs_g,
        fat_g=fat_g,
        is_vegan=is_vegan,
        meal_type=meal_type,
    )

    return {
        "status": "composed",
        "meal_type": meal_type,
        "meal_name_es": template["name_es"],
        "target_calories": target_calories,
        "macro_targets": {
            "protein": {
                "grams": protein_g,
                "calories": round(protein_kcal),
                "percent": round(ratios["protein"] * 100),
            },
            "carbs": {
                "grams": carbs_g,
                "calories": round(carbs_kcal),
                "percent": round(ratios["carbs"] * 100),
            },
            "fat": {
                "grams": fat_g,
                "calories": round(fat_kcal),
                "percent": round(ratios["fat"] * 100),
            },
        },
        "suggested_foods": suggested_foods,
        "portion_guide": {
            "protein_portion": f"~{round(protein_g * 3)}g de carne/pescado o {round(protein_g / 25 * 100)}g de tofu",
            "carb_portion": f"~{round(carbs_g / 30 * 100)}g de arroz/pasta cocidos",
            "fat_portion": f"~{round(fat_g / 14)}cucharadas de aceite o {round(fat_g / 15 * 0.5)} aguacate",
        },
        "meal_timing": template.get("timing", "Flexible según tu horario"),
        "best_for": template.get("best_for", []),
        "preparation_tips": [
            "Prepara proteína y carbos en batch para la semana",
            "Ten verduras lavadas y cortadas listas",
            "Mide porciones hasta tener práctica visual",
        ],
    }


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================


def _get_muscle_gain_distribution(meals: int) -> list[float]:
    """Distribución de proteína para ganancia muscular."""
    if meals == 3:
        return [0.30, 0.35, 0.35]  # Más en post-entreno y cena
    elif meals == 4:
        return [0.25, 0.25, 0.25, 0.25]
    elif meals == 5:
        return [0.20, 0.15, 0.25, 0.20, 0.20]  # Snack post-entreno
    else:
        base = 1.0 / meals
        return [round(base, 2)] * meals


def _get_fat_loss_distribution(meals: int) -> list[float]:
    """Distribución de proteína para pérdida de grasa - uniforme."""
    return [round(1.0 / meals, 2)] * meals


def _get_balanced_distribution(meals: int) -> list[float]:
    """Distribución balanceada de proteína."""
    if meals == 3:
        return [0.30, 0.35, 0.35]
    elif meals == 4:
        return [0.25, 0.25, 0.25, 0.25]
    elif meals == 5:
        return [0.20, 0.20, 0.20, 0.20, 0.20]
    else:
        return [round(1.0 / meals, 2)] * meals


def _get_meal_names(meals: int) -> list[str]:
    """Obtiene nombres de comidas según cantidad."""
    if meals == 3:
        return ["Desayuno", "Almuerzo", "Cena"]
    elif meals == 4:
        return ["Desayuno", "Almuerzo", "Merienda", "Cena"]
    elif meals == 5:
        return ["Desayuno", "Media mañana", "Almuerzo", "Merienda", "Cena"]
    elif meals == 6:
        return ["Desayuno", "Media mañana", "Almuerzo", "Merienda", "Cena", "Pre-dormir"]
    else:
        return [f"Comida {i+1}" for i in range(meals)]


def _suggest_protein_sources(protein_g: float) -> list[str]:
    """Sugiere fuentes de proteína para alcanzar gramos objetivo."""
    suggestions = []

    if protein_g >= 30:
        suggestions.append(f"150g pechuga de pollo (~{round(150 * 0.31)}g proteína)")
        suggestions.append(f"170g salmón (~{round(170 * 0.25)}g proteína)")
    elif protein_g >= 20:
        suggestions.append(f"100g pechuga de pollo + 2 huevos (~{round(100 * 0.31 + 2 * 6.5)}g)")
        suggestions.append(f"150g pescado blanco (~{round(150 * 0.20)}g proteína)")
    else:
        suggestions.append(f"2-3 huevos (~{round(2.5 * 6.5)}g proteína)")
        suggestions.append(f"150g yogur griego (~{round(150 * 0.10)}g proteína)")

    return suggestions


def _get_fat_sources(is_vegan: bool, is_pescetarian: bool) -> dict:
    """Obtiene fuentes de grasa según restricciones."""
    sources = {
        "monounsaturated": ["aceite de oliva extra virgen", "aguacate", "almendras", "nueces de macadamia"],
        "polyunsaturated": ["nueces", "semillas de girasol", "semillas de calabaza"],
        "omega3": ["semillas de chía", "semillas de linaza", "nueces"],
    }

    if not is_vegan:
        sources["omega3"].extend(["salmón", "sardinas", "caballa"])
        sources["monounsaturated"].append("aceitunas")

    if is_pescetarian or (not is_vegan):
        sources["omega3"].insert(0, "pescado graso (salmón, caballa, sardinas)")

    return sources


def _suggest_meal_foods(
    protein_g: float,
    carbs_g: float,
    fat_g: float,
    is_vegan: bool,
    meal_type: str,
) -> dict:
    """Sugiere alimentos específicos para la comida."""
    suggestions = {
        "protein_sources": [],
        "carb_sources": [],
        "fat_sources": [],
        "vegetables": ["espinacas", "brócoli", "pimientos", "tomates"],
    }

    # Proteínas
    if is_vegan:
        suggestions["protein_sources"] = [
            f"~{round(protein_g * 10)}g tofu firme",
            f"~{round(protein_g * 5)}g tempeh",
            f"~{round(protein_g * 4)}g seitan",
        ]
    else:
        suggestions["protein_sources"] = [
            f"~{round(protein_g * 3.2)}g pechuga de pollo",
            f"~{round(protein_g * 4)}g pescado blanco",
            f"~{round(protein_g / 6.5)}huevos",
        ]

    # Carbohidratos según tipo de comida
    if meal_type in ["pre_workout", "post_workout"]:
        suggestions["carb_sources"] = [
            f"~{round(carbs_g * 4)}g arroz cocido",
            f"~{round(carbs_g * 3)}g avena",
            f"~{round(carbs_g / 25 * 100)}g plátano",
        ]
    else:
        suggestions["carb_sources"] = [
            f"~{round(carbs_g * 4)}g arroz integral",
            f"~{round(carbs_g * 4)}g quinoa cocida",
            f"~{round(carbs_g * 2)}g camote",
        ]

    # Grasas
    suggestions["fat_sources"] = [
        f"~{round(fat_g / 14)}cucharada(s) aceite de oliva",
        f"~{round(fat_g * 7)}g aguacate",
        f"~{round(fat_g * 4)}g nueces/almendras",
    ]

    return suggestions


# =============================================================================
# EXPORTACIÓN DE TOOLS
# =============================================================================


calculate_macros_tool = FunctionTool(calculate_macros)
distribute_protein_tool = FunctionTool(distribute_protein)
plan_carb_cycling_tool = FunctionTool(plan_carb_cycling)
optimize_fat_intake_tool = FunctionTool(optimize_fat_intake)
compose_meal_tool = FunctionTool(compose_meal)


ALL_TOOLS = [
    calculate_macros_tool,
    distribute_protein_tool,
    plan_carb_cycling_tool,
    optimize_fat_intake_tool,
    compose_meal_tool,
]


__all__ = [
    # Functions
    "calculate_macros",
    "distribute_protein",
    "plan_carb_cycling",
    "optimize_fat_intake",
    "compose_meal",
    # Tools
    "calculate_macros_tool",
    "distribute_protein_tool",
    "plan_carb_cycling_tool",
    "optimize_fat_intake_tool",
    "compose_meal_tool",
    "ALL_TOOLS",
    # Data
    "MACRO_RATIOS",
    "PROTEIN_TARGETS",
    "CARB_CYCLING_PATTERNS",
    "FAT_DISTRIBUTION",
    "MEAL_TEMPLATES",
    "PROTEIN_SOURCES",
    # Enums
    "NutritionGoal",
    "ActivityType",
    "CarbCycleDay",
    "FatSource",
]
