"""Tools para STELLA - Agente de Analytics y Reportes.

Este modulo proporciona las herramientas de analisis de datos para STELLA:
- Analisis de progreso
- Calculo de tendencias
- Monitoreo de metas
- Interpretacion de biomarcadores
- Generacion de reportes
"""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from google.adk.tools import FunctionTool

# =============================================================================
# Enums y Constantes
# =============================================================================


class MetricCategory(str, Enum):
    """Categorias de metricas disponibles."""

    BODY_COMPOSITION = "body_composition"
    PERFORMANCE = "performance"
    RECOVERY = "recovery"
    NUTRITION = "nutrition"
    VITALS = "vitals"


class TrendDirection(str, Enum):
    """Direccion de tendencia."""

    ASCENDING = "ascending"
    DESCENDING = "descending"
    STABLE = "stable"
    VOLATILE = "volatile"


class GoalCategory(str, Enum):
    """Categorias de metas."""

    STRENGTH = "strength"
    FAT_LOSS = "fat_loss"
    MUSCLE_GAIN = "muscle_gain"
    ENDURANCE = "endurance"
    RECOVERY = "recovery"
    GENERAL_HEALTH = "general_health"


class ReportType(str, Enum):
    """Tipos de reporte."""

    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    CUSTOM = "custom"


# =============================================================================
# Estructuras de Datos
# =============================================================================

METRIC_TYPES: dict[str, list[str]] = {
    "body_composition": ["weight_kg", "body_fat_pct", "muscle_mass_kg", "bmi"],
    "performance": ["1rm_squat", "1rm_bench", "1rm_deadlift", "volume_total", "reps_completed"],
    "recovery": ["hrv_ms", "sleep_score", "resting_hr", "recovery_score"],
    "nutrition": ["calories", "protein_g", "carbs_g", "fat_g", "adherence_pct"],
    "vitals": ["blood_pressure_sys", "blood_pressure_dia", "glucose_mg_dl", "cholesterol_total"],
}

TREND_PERIODS: dict[str, int] = {
    "7d": 7,
    "14d": 14,
    "30d": 30,
    "90d": 90,
}

BIOMARKER_RANGES: dict[str, dict[str, Any]] = {
    "resting_hr": {
        "name_es": "Frecuencia cardiaca en reposo",
        "unit": "bpm",
        "optimal_min": 50,
        "optimal_max": 70,
        "normal_min": 60,
        "normal_max": 100,
        "interpretation": {
            "low": "Excelente condicion cardiovascular",
            "optimal": "Buena condicion cardiovascular",
            "high": "Considerar mejorar condicion aerobica",
            "very_high": "Consultar con medico si persiste elevada",
        },
    },
    "hrv_ms": {
        "name_es": "Variabilidad de frecuencia cardiaca",
        "unit": "ms",
        "optimal_min": 50,
        "optimal_max": 100,
        "normal_min": 20,
        "normal_max": 200,
        "interpretation": {
            "low": "Posible estres o fatiga acumulada",
            "optimal": "Buen equilibrio del sistema nervioso",
            "high": "Excelente capacidad de recuperacion",
        },
    },
    "sleep_score": {
        "name_es": "Puntuacion de sueno",
        "unit": "puntos",
        "optimal_min": 80,
        "optimal_max": 100,
        "normal_min": 60,
        "normal_max": 100,
        "interpretation": {
            "low": "Sueno de baja calidad, revisar higiene del sueno",
            "optimal": "Descanso adecuado",
            "high": "Excelente calidad de sueno",
        },
    },
    "body_fat_pct": {
        "name_es": "Porcentaje de grasa corporal",
        "unit": "%",
        "optimal_min_male": 10,
        "optimal_max_male": 20,
        "optimal_min_female": 18,
        "optimal_max_female": 28,
        "interpretation": {
            "low": "Nivel atletico, mantener nutricion adecuada",
            "optimal": "Rango saludable",
            "high": "Considerar ajustes en nutricion y ejercicio",
        },
    },
    "glucose_mg_dl": {
        "name_es": "Glucosa en sangre",
        "unit": "mg/dL",
        "optimal_min": 70,
        "optimal_max": 100,
        "normal_min": 70,
        "normal_max": 125,
        "interpretation": {
            "low": "Glucosa baja, considerar comer algo",
            "optimal": "Niveles normales de glucosa",
            "high": "Consultar con medico para evaluacion",
        },
    },
    "blood_pressure_sys": {
        "name_es": "Presion arterial sistolica",
        "unit": "mmHg",
        "optimal_min": 90,
        "optimal_max": 120,
        "normal_min": 90,
        "normal_max": 140,
        "interpretation": {
            "low": "Presion baja, monitorear sintomas",
            "optimal": "Presion arterial saludable",
            "high": "Considerar cambios de estilo de vida y consulta medica",
        },
    },
}

GOAL_TEMPLATES: dict[str, dict[str, Any]] = {
    "strength": {
        "name_es": "Fuerza",
        "metrics": ["1rm_squat", "1rm_bench", "1rm_deadlift"],
        "typical_timeline_weeks": 12,
        "expected_progress_pct": 10,
    },
    "fat_loss": {
        "name_es": "Perdida de grasa",
        "metrics": ["body_fat_pct", "weight_kg"],
        "typical_timeline_weeks": 12,
        "expected_progress_pct": 5,
    },
    "muscle_gain": {
        "name_es": "Ganancia muscular",
        "metrics": ["muscle_mass_kg", "weight_kg"],
        "typical_timeline_weeks": 16,
        "expected_progress_pct": 3,
    },
    "endurance": {
        "name_es": "Resistencia",
        "metrics": ["resting_hr", "hrv_ms", "recovery_score"],
        "typical_timeline_weeks": 8,
        "expected_progress_pct": 15,
    },
    "recovery": {
        "name_es": "Recuperacion",
        "metrics": ["sleep_score", "hrv_ms", "recovery_score"],
        "typical_timeline_weeks": 4,
        "expected_progress_pct": 20,
    },
}


# =============================================================================
# Funciones de Analytics
# =============================================================================


def analyze_progress(
    metric_values: list[float],
    metric_name: str = "weight_kg",
    period_days: int = 30,
    goal_value: float | None = None,
    goal_type: str = "decrease",
) -> dict[str, Any]:
    """Analiza el progreso de una metrica a lo largo del tiempo.

    Args:
        metric_values: Lista de valores de la metrica (ordenados del mas antiguo al mas reciente)
        metric_name: Nombre de la metrica
        period_days: Dias del periodo de analisis
        goal_value: Valor objetivo (opcional)
        goal_type: Tipo de meta ("increase", "decrease", "maintain")

    Returns:
        dict con analisis de progreso
    """
    if not metric_values:
        return {
            "metric_name": metric_name,
            "status": "insufficient_data",
            "message": "No hay datos suficientes para analizar",
        }

    if len(metric_values) < 2:
        return {
            "metric_name": metric_name,
            "status": "insufficient_data",
            "message": "Se necesitan al menos 2 mediciones para analizar progreso",
            "current_value": metric_values[0],
        }

    start_value = metric_values[0]
    end_value = metric_values[-1]
    min_value = min(metric_values)
    max_value = max(metric_values)
    avg_value = sum(metric_values) / len(metric_values)

    # Calcular cambio
    absolute_change = end_value - start_value
    percent_change = (absolute_change / start_value * 100) if start_value != 0 else 0

    # Determinar direccion
    if percent_change > 2:
        direction = "increasing"
    elif percent_change < -2:
        direction = "decreasing"
    else:
        direction = "stable"

    # Evaluar contra meta
    goal_progress = None
    on_track = None
    if goal_value is not None:
        distance_to_goal = abs(goal_value - end_value)
        initial_distance = abs(goal_value - start_value)

        if initial_distance > 0:
            goal_progress = ((initial_distance - distance_to_goal) / initial_distance) * 100
        else:
            goal_progress = 100.0

        # Determinar si esta en camino
        if goal_type == "decrease":
            on_track = end_value <= start_value and (goal_value is None or end_value <= start_value)
        elif goal_type == "increase":
            on_track = end_value >= start_value
        else:  # maintain
            on_track = abs(percent_change) <= 3

    # Calcular consistencia (desviacion estandar relativa)
    if len(metric_values) >= 3:
        mean = avg_value
        variance = sum((x - mean) ** 2 for x in metric_values) / len(metric_values)
        std_dev = variance**0.5
        coefficient_of_variation = (std_dev / mean * 100) if mean != 0 else 0

        if coefficient_of_variation < 5:
            consistency = "very_consistent"
        elif coefficient_of_variation < 10:
            consistency = "consistent"
        elif coefficient_of_variation < 20:
            consistency = "variable"
        else:
            consistency = "highly_variable"
    else:
        consistency = "insufficient_data"
        coefficient_of_variation = None

    # Generar insights
    insights = []

    if direction == "increasing" and goal_type == "decrease":
        insights.append("La metrica esta aumentando cuando deberia disminuir. Revisar estrategia.")
    elif direction == "decreasing" and goal_type == "increase":
        insights.append("La metrica esta disminuyendo cuando deberia aumentar. Revisar estrategia.")
    elif direction == "stable" and goal_type != "maintain":
        insights.append("La metrica se mantiene estable. Considerar ajustar intensidad.")

    if on_track is True:
        insights.append("Progreso en la direccion correcta hacia tu meta.")
    elif on_track is False:
        insights.append("El progreso actual no esta alineado con tu meta.")

    if consistency == "highly_variable":
        insights.append("Alta variabilidad en las mediciones. Considerar estandarizar condiciones de medicion.")

    return {
        "metric_name": metric_name,
        "status": "analyzed",
        "period_days": period_days,
        "data_points": len(metric_values),
        "values": {
            "start": round(start_value, 2),
            "end": round(end_value, 2),
            "min": round(min_value, 2),
            "max": round(max_value, 2),
            "average": round(avg_value, 2),
        },
        "change": {
            "absolute": round(absolute_change, 2),
            "percent": round(percent_change, 2),
            "direction": direction,
        },
        "consistency": consistency,
        "coefficient_of_variation": round(coefficient_of_variation, 2) if coefficient_of_variation else None,
        "goal_analysis": {
            "goal_value": goal_value,
            "goal_type": goal_type,
            "progress_percent": round(goal_progress, 2) if goal_progress is not None else None,
            "on_track": on_track,
        }
        if goal_value is not None
        else None,
        "insights": insights,
    }


def calculate_trends(
    data_points: list[dict[str, Any]],
    metric_name: str = "weight_kg",
    period: str = "30d",
) -> dict[str, Any]:
    """Calcula tendencias en una serie de datos.

    Args:
        data_points: Lista de dicts con 'date' y 'value'
        metric_name: Nombre de la metrica
        period: Periodo de analisis ("7d", "14d", "30d", "90d")

    Returns:
        dict con analisis de tendencia
    """
    if not data_points:
        return {
            "metric_name": metric_name,
            "status": "insufficient_data",
            "message": "No hay datos para analizar tendencia",
        }

    # Extraer valores
    values = [dp.get("value", 0) for dp in data_points if dp.get("value") is not None]

    if len(values) < 3:
        return {
            "metric_name": metric_name,
            "status": "insufficient_data",
            "message": "Se necesitan al menos 3 puntos para calcular tendencia",
            "data_points": len(values),
        }

    # Calcular tendencia usando regresion lineal simple
    n = len(values)
    x_values = list(range(n))
    x_mean = sum(x_values) / n
    y_mean = sum(values) / n

    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
    denominator = sum((x - x_mean) ** 2 for x in x_values)

    if denominator == 0:
        slope = 0
    else:
        slope = numerator / denominator

    # Determinar direccion de tendencia
    slope_normalized = slope / y_mean * 100 if y_mean != 0 else 0

    if slope_normalized > 1:
        trend_direction = TrendDirection.ASCENDING
    elif slope_normalized < -1:
        trend_direction = TrendDirection.DESCENDING
    else:
        trend_direction = TrendDirection.STABLE

    # Detectar volatilidad
    mean = y_mean
    variance = sum((v - mean) ** 2 for v in values) / n
    std_dev = variance**0.5
    cv = (std_dev / mean * 100) if mean != 0 else 0

    if cv > 15:
        trend_direction = TrendDirection.VOLATILE

    # Detectar patrones ciclicos (simplificado)
    has_weekly_pattern = False
    if len(values) >= 14:
        # Buscar patron semanal comparando medias
        week1_avg = sum(values[:7]) / 7
        week2_avg = sum(values[7:14]) / 7
        if abs(week1_avg - week2_avg) / mean * 100 < 5:
            has_weekly_pattern = True

    # Detectar anomalias (valores fuera de 2 desviaciones estandar)
    anomalies = []
    for i, v in enumerate(values):
        z_score = (v - mean) / std_dev if std_dev > 0 else 0
        if abs(z_score) > 2:
            anomalies.append({
                "index": i,
                "value": round(v, 2),
                "z_score": round(z_score, 2),
                "type": "above_normal" if z_score > 0 else "below_normal",
            })

    # Proyeccion simple (lineal)
    projected_7d = values[-1] + slope * 7
    projected_30d = values[-1] + slope * 30

    # Generar interpretacion
    interpretation = []

    if trend_direction == TrendDirection.ASCENDING:
        interpretation.append(f"{metric_name} muestra tendencia ascendente ({slope_normalized:.1f}% por punto)")
    elif trend_direction == TrendDirection.DESCENDING:
        interpretation.append(f"{metric_name} muestra tendencia descendente ({slope_normalized:.1f}% por punto)")
    elif trend_direction == TrendDirection.STABLE:
        interpretation.append(f"{metric_name} se mantiene estable con poca variacion")
    else:
        interpretation.append(f"{metric_name} muestra alta volatilidad (CV={cv:.1f}%)")

    if anomalies:
        interpretation.append(f"Se detectaron {len(anomalies)} valores atipicos")

    if has_weekly_pattern:
        interpretation.append("Se observa un patron semanal consistente")

    return {
        "metric_name": metric_name,
        "status": "analyzed",
        "period": period,
        "data_points": len(values),
        "trend": {
            "direction": trend_direction.value,
            "slope": round(slope, 4),
            "slope_normalized_pct": round(slope_normalized, 2),
            "strength": "strong" if abs(slope_normalized) > 3 else "moderate" if abs(slope_normalized) > 1 else "weak",
        },
        "statistics": {
            "mean": round(mean, 2),
            "std_dev": round(std_dev, 2),
            "coefficient_of_variation": round(cv, 2),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
        },
        "patterns": {
            "has_weekly_pattern": has_weekly_pattern,
            "is_volatile": trend_direction == TrendDirection.VOLATILE,
        },
        "anomalies": anomalies,
        "projections": {
            "7_days": round(projected_7d, 2),
            "30_days": round(projected_30d, 2),
            "note": "Proyeccion lineal simple, usar con precaucion",
        },
        "interpretation": interpretation,
    }


def check_goal_status(
    goal_category: str = "strength",
    current_value: float = 0,
    target_value: float = 0,
    start_value: float = 0,
    start_date: str | None = None,
    target_date: str | None = None,
) -> dict[str, Any]:
    """Verifica el estado de cumplimiento de una meta.

    Args:
        goal_category: Categoria de la meta
        current_value: Valor actual
        target_value: Valor objetivo
        start_value: Valor inicial
        start_date: Fecha de inicio (YYYY-MM-DD)
        target_date: Fecha objetivo (YYYY-MM-DD)

    Returns:
        dict con estado de la meta
    """
    # Validar categoria
    if goal_category not in GOAL_TEMPLATES:
        goal_category = "general_health"

    template = GOAL_TEMPLATES.get(goal_category, GOAL_TEMPLATES["recovery"])

    # Calcular progreso
    if target_value == start_value:
        progress_pct = 100.0 if current_value == target_value else 0.0
    else:
        progress_pct = ((current_value - start_value) / (target_value - start_value)) * 100

    progress_pct = max(0, min(100, progress_pct))  # Limitar entre 0 y 100

    # Calcular tiempo transcurrido y restante
    today = datetime.now()
    time_analysis = None

    if start_date and target_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            target_dt = datetime.strptime(target_date, "%Y-%m-%d")

            total_days = (target_dt - start_dt).days
            elapsed_days = (today - start_dt).days
            remaining_days = (target_dt - today).days

            time_progress_pct = (elapsed_days / total_days * 100) if total_days > 0 else 0

            # Calcular si esta on track
            expected_progress = time_progress_pct
            progress_vs_time = progress_pct - expected_progress

            if progress_vs_time >= 5:
                pace = "ahead"
                pace_description = "Por encima del progreso esperado"
            elif progress_vs_time <= -10:
                pace = "behind"
                pace_description = "Por debajo del progreso esperado"
            else:
                pace = "on_track"
                pace_description = "Progreso alineado con el tiempo"

            time_analysis = {
                "start_date": start_date,
                "target_date": target_date,
                "total_days": total_days,
                "elapsed_days": elapsed_days,
                "remaining_days": max(0, remaining_days),
                "time_progress_pct": round(time_progress_pct, 1),
                "pace": pace,
                "pace_description": pace_description,
                "is_overdue": remaining_days < 0,
            }
        except ValueError:
            time_analysis = {"error": "Formato de fecha invalido"}

    # Determinar estado
    if progress_pct >= 100:
        status = "completed"
        status_description = "Meta alcanzada"
    elif progress_pct >= 75:
        status = "near_completion"
        status_description = "Muy cerca de completar"
    elif progress_pct >= 50:
        status = "halfway"
        status_description = "A mitad de camino"
    elif progress_pct >= 25:
        status = "in_progress"
        status_description = "Progreso inicial"
    else:
        status = "starting"
        status_description = "Fase inicial"

    # Calcular velocidad de progreso necesaria
    velocity_needed = None
    if time_analysis and time_analysis.get("remaining_days", 0) > 0:
        remaining_progress = 100 - progress_pct
        velocity_needed = remaining_progress / time_analysis["remaining_days"]

    # Generar recomendaciones
    recommendations = []

    if status == "completed":
        recommendations.append("Celebra tu logro y considera establecer una nueva meta")
    elif time_analysis and time_analysis.get("pace") == "behind":
        recommendations.append("Considera intensificar esfuerzos o ajustar la meta")
        recommendations.append(f"Necesitas avanzar {velocity_needed:.2f}% por dia para cumplir")
    elif time_analysis and time_analysis.get("pace") == "ahead":
        recommendations.append("Excelente progreso, mantén el ritmo actual")
    else:
        recommendations.append("Mantén la consistencia para alcanzar tu meta")

    return {
        "goal_category": goal_category,
        "goal_name_es": template["name_es"],
        "status": status,
        "status_description": status_description,
        "values": {
            "start": round(start_value, 2),
            "current": round(current_value, 2),
            "target": round(target_value, 2),
        },
        "progress": {
            "percent": round(progress_pct, 1),
            "remaining_pct": round(100 - progress_pct, 1),
            "absolute_remaining": round(abs(target_value - current_value), 2),
        },
        "time_analysis": time_analysis,
        "velocity_needed_per_day": round(velocity_needed, 3) if velocity_needed else None,
        "recommendations": recommendations,
    }


def interpret_biomarkers(
    biomarkers: dict[str, float],
    user_age: int = 40,
    user_sex: str = "male",
    include_history: bool = False,
    history: dict[str, list[float]] | None = None,
) -> dict[str, Any]:
    """Interpreta biomarcadores de salud.

    Args:
        biomarkers: Dict con nombre de biomarcador y valor
        user_age: Edad del usuario
        user_sex: Sexo del usuario ("male", "female")
        include_history: Si incluir analisis de historial
        history: Dict con historial de cada biomarcador

    Returns:
        dict con interpretacion de biomarcadores
    """
    interpretations = []
    overall_health_score = 100
    concerns = []
    positive_indicators = []

    for marker_name, value in biomarkers.items():
        if marker_name not in BIOMARKER_RANGES:
            interpretations.append({
                "marker": marker_name,
                "value": value,
                "status": "unknown",
                "message": "Biomarcador no reconocido",
            })
            continue

        marker_info = BIOMARKER_RANGES[marker_name]

        # Obtener rangos (algunos ajustados por sexo)
        if "optimal_min_male" in marker_info and user_sex == "male":
            optimal_min = marker_info["optimal_min_male"]
            optimal_max = marker_info["optimal_max_male"]
        elif "optimal_min_female" in marker_info and user_sex == "female":
            optimal_min = marker_info["optimal_min_female"]
            optimal_max = marker_info["optimal_max_female"]
        else:
            optimal_min = marker_info.get("optimal_min", 0)
            optimal_max = marker_info.get("optimal_max", 100)

        normal_min = marker_info.get("normal_min", optimal_min)
        normal_max = marker_info.get("normal_max", optimal_max)

        # Determinar status
        if optimal_min <= value <= optimal_max:
            status = "optimal"
            score_impact = 0
        elif normal_min <= value <= normal_max:
            status = "normal"
            score_impact = -5
        elif value < normal_min:
            status = "low"
            score_impact = -15
        else:
            status = "high"
            score_impact = -15

        overall_health_score += score_impact

        # Obtener interpretacion
        interp_key = "optimal" if status == "optimal" else "low" if status == "low" else "high"
        interpretation_text = marker_info["interpretation"].get(interp_key, "")

        # Generar recomendaciones
        recommendations = []
        if status == "low":
            if marker_name == "hrv_ms":
                recommendations.append("Priorizar descanso y reducir estres")
            elif marker_name == "sleep_score":
                recommendations.append("Mejorar higiene del sueno")
        elif status == "high":
            if marker_name == "resting_hr":
                recommendations.append("Incorporar mas actividad aerobica")
            elif marker_name in ["blood_pressure_sys", "glucose_mg_dl"]:
                recommendations.append("Consultar con profesional de la salud")

        # Analisis de historial
        trend = None
        if include_history and history and marker_name in history:
            hist_values = history[marker_name]
            if len(hist_values) >= 3:
                recent_avg = sum(hist_values[-3:]) / 3
                older_avg = sum(hist_values[:3]) / 3 if len(hist_values) >= 6 else hist_values[0]

                if recent_avg > older_avg * 1.05:
                    trend = "increasing"
                elif recent_avg < older_avg * 0.95:
                    trend = "decreasing"
                else:
                    trend = "stable"

        interpretation_entry = {
            "marker": marker_name,
            "name_es": marker_info["name_es"],
            "value": round(value, 2),
            "unit": marker_info["unit"],
            "status": status,
            "ranges": {
                "optimal": f"{optimal_min}-{optimal_max}",
                "normal": f"{normal_min}-{normal_max}",
            },
            "interpretation": interpretation_text,
            "recommendations": recommendations,
        }

        if trend:
            interpretation_entry["trend"] = trend

        interpretations.append(interpretation_entry)

        # Categorizar para resumen
        if status == "optimal":
            positive_indicators.append(marker_info["name_es"])
        elif status in ["low", "high"]:
            concerns.append(marker_info["name_es"])

    # Limitar score entre 0 y 100
    overall_health_score = max(0, min(100, overall_health_score))

    # Determinar nivel general
    if overall_health_score >= 90:
        health_level = "excellent"
        health_level_es = "Excelente"
    elif overall_health_score >= 75:
        health_level = "good"
        health_level_es = "Bueno"
    elif overall_health_score >= 60:
        health_level = "moderate"
        health_level_es = "Moderado"
    else:
        health_level = "needs_attention"
        health_level_es = "Requiere atencion"

    # Generar resumen
    summary = []
    if positive_indicators:
        summary.append(f"Indicadores positivos: {', '.join(positive_indicators[:3])}")
    if concerns:
        summary.append(f"Areas de atencion: {', '.join(concerns)}")
    if not concerns:
        summary.append("Todos los biomarcadores en rangos saludables")

    return {
        "status": "analyzed",
        "markers_analyzed": len(biomarkers),
        "interpretations": interpretations,
        "summary": {
            "overall_health_score": overall_health_score,
            "health_level": health_level,
            "health_level_es": health_level_es,
            "positive_indicators": positive_indicators,
            "concerns": concerns,
            "summary_text": " | ".join(summary),
        },
        "general_recommendations": [
            "Mantener consistencia en las mediciones",
            "Consultar con profesional de salud para valores fuera de rango",
            "Repetir mediciones en condiciones similares para mejor precision",
        ],
        "disclaimer": "Esta interpretacion es educativa y no reemplaza una evaluacion medica profesional.",
    }


def generate_report(
    report_type: str = "weekly",
    metrics_data: dict[str, list[float]] | None = None,
    goals_data: list[dict[str, Any]] | None = None,
    period_start: str | None = None,
    period_end: str | None = None,
    user_name: str = "Usuario",
) -> dict[str, Any]:
    """Genera un reporte de progreso personalizado.

    Args:
        report_type: Tipo de reporte ("weekly", "monthly", "quarterly", "custom")
        metrics_data: Dict con metricas y sus valores
        goals_data: Lista de metas con su progreso
        period_start: Fecha inicio (YYYY-MM-DD)
        period_end: Fecha fin (YYYY-MM-DD)
        user_name: Nombre del usuario

    Returns:
        dict con reporte generado
    """
    # Determinar periodo
    today = datetime.now()
    if period_start and period_end:
        try:
            start_dt = datetime.strptime(period_start, "%Y-%m-%d")
            end_dt = datetime.strptime(period_end, "%Y-%m-%d")
        except ValueError:
            start_dt = today - timedelta(days=7)
            end_dt = today
    else:
        if report_type == "weekly":
            start_dt = today - timedelta(days=7)
        elif report_type == "monthly":
            start_dt = today - timedelta(days=30)
        elif report_type == "quarterly":
            start_dt = today - timedelta(days=90)
        else:
            start_dt = today - timedelta(days=7)
        end_dt = today

    period_days = (end_dt - start_dt).days

    # Analizar metricas
    metrics_analysis = []
    highlights = []
    areas_for_improvement = []

    if metrics_data:
        for metric_name, values in metrics_data.items():
            if not values:
                continue

            analysis = analyze_progress(
                metric_values=values,
                metric_name=metric_name,
                period_days=period_days,
            )

            metrics_analysis.append({
                "metric": metric_name,
                "start_value": analysis["values"]["start"] if "values" in analysis else None,
                "end_value": analysis["values"]["end"] if "values" in analysis else None,
                "change_pct": analysis["change"]["percent"] if "change" in analysis else None,
                "direction": analysis["change"]["direction"] if "change" in analysis else None,
            })

            # Categorizar para resumen
            if "change" in analysis:
                if abs(analysis["change"]["percent"]) > 5:
                    if analysis["change"]["percent"] > 0:
                        highlights.append(f"{metric_name}: +{analysis['change']['percent']:.1f}%")
                    else:
                        areas_for_improvement.append(f"{metric_name}: {analysis['change']['percent']:.1f}%")

    # Analizar metas
    goals_analysis = []
    goals_completed = 0
    goals_on_track = 0

    if goals_data:
        for goal in goals_data:
            goal_status = check_goal_status(
                goal_category=goal.get("category", "general_health"),
                current_value=goal.get("current", 0),
                target_value=goal.get("target", 0),
                start_value=goal.get("start", 0),
            )

            goals_analysis.append({
                "goal": goal.get("name", goal.get("category")),
                "progress_pct": goal_status["progress"]["percent"],
                "status": goal_status["status"],
            })

            if goal_status["status"] == "completed":
                goals_completed += 1
            elif goal_status["progress"]["percent"] >= 50:
                goals_on_track += 1

    # Calcular puntuacion general del periodo
    total_metrics = len(metrics_analysis)
    improving_metrics = sum(1 for m in metrics_analysis if m.get("change_pct", 0) > 0)
    period_score = (improving_metrics / total_metrics * 100) if total_metrics > 0 else 50

    if goals_data:
        goal_score = ((goals_completed + goals_on_track * 0.5) / len(goals_data) * 100) if goals_data else 50
        period_score = (period_score + goal_score) / 2

    # Generar resumen ejecutivo
    executive_summary = []

    if period_score >= 80:
        executive_summary.append(f"Excelente periodo, {user_name}. Progreso notable en multiples areas.")
    elif period_score >= 60:
        executive_summary.append(f"Buen periodo, {user_name}. Avances solidos con areas de oportunidad.")
    elif period_score >= 40:
        executive_summary.append(f"Periodo mixto, {user_name}. Algunos avances, pero hay areas que requieren atencion.")
    else:
        executive_summary.append(f"Periodo desafiante, {user_name}. Revisemos la estrategia juntos.")

    if goals_completed > 0:
        executive_summary.append(f"Metas completadas: {goals_completed}")
    if highlights:
        executive_summary.append(f"Mejoras destacadas: {', '.join(highlights[:2])}")

    # Generar recomendaciones
    action_items = []

    if areas_for_improvement:
        action_items.append(f"Enfocar en mejorar: {areas_for_improvement[0]}")
    if goals_on_track < len(goals_data or []):
        action_items.append("Revisar estrategia para metas atrasadas")
    action_items.append("Mantener consistencia en mediciones diarias")
    action_items.append("Programar revision de metas para el proximo periodo")

    return {
        "report_type": report_type,
        "generated_at": today.isoformat(),
        "period": {
            "start": start_dt.strftime("%Y-%m-%d"),
            "end": end_dt.strftime("%Y-%m-%d"),
            "days": period_days,
        },
        "user_name": user_name,
        "executive_summary": executive_summary,
        "period_score": round(period_score, 1),
        "metrics_summary": {
            "total_tracked": total_metrics,
            "improving": improving_metrics,
            "declining": total_metrics - improving_metrics,
            "details": metrics_analysis,
        },
        "goals_summary": {
            "total": len(goals_data or []),
            "completed": goals_completed,
            "on_track": goals_on_track,
            "needs_attention": len(goals_data or []) - goals_completed - goals_on_track,
            "details": goals_analysis,
        },
        "highlights": highlights,
        "areas_for_improvement": areas_for_improvement,
        "action_items": action_items,
        "next_review": (end_dt + timedelta(days=7 if report_type == "weekly" else 30)).strftime("%Y-%m-%d"),
    }


# =============================================================================
# FunctionTools para ADK
# =============================================================================

analyze_progress_tool = FunctionTool(analyze_progress)
calculate_trends_tool = FunctionTool(calculate_trends)
check_goal_status_tool = FunctionTool(check_goal_status)
interpret_biomarkers_tool = FunctionTool(interpret_biomarkers)
generate_report_tool = FunctionTool(generate_report)

ALL_TOOLS = [
    analyze_progress_tool,
    calculate_trends_tool,
    check_goal_status_tool,
    interpret_biomarkers_tool,
    generate_report_tool,
]
