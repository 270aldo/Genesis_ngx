"""Tests para las tools de STELLA."""

from __future__ import annotations

from agents.stella.tools import (
    analyze_progress,
    calculate_trends,
    check_goal_status,
    interpret_biomarkers,
    generate_report,
    METRIC_TYPES,
    BIOMARKER_RANGES,
    GOAL_TEMPLATES,
    TREND_PERIODS,
)


class TestAnalyzeProgress:
    """Tests para analyze_progress."""

    def test_analyze_decreasing_values(self):
        """Debe detectar tendencia descendente."""
        result = analyze_progress(
            metric_values=[80.0, 79.5, 79.0, 78.5, 78.0],
            metric_name="weight_kg",
            period_days=30,
        )
        assert result["status"] == "analyzed"
        assert result["change"]["direction"] == "decreasing"
        assert result["change"]["absolute"] < 0

    def test_analyze_increasing_values(self):
        """Debe detectar tendencia ascendente."""
        result = analyze_progress(
            metric_values=[100.0, 110.0, 120.0, 130.0],
            metric_name="1rm_squat",
        )
        assert result["change"]["direction"] == "increasing"
        assert result["change"]["percent"] > 0

    def test_analyze_stable_values(self):
        """Debe detectar valores estables."""
        result = analyze_progress(
            metric_values=[75.0, 75.1, 74.9, 75.0, 75.1],
            metric_name="weight_kg",
        )
        assert result["change"]["direction"] == "stable"

    def test_analyze_with_goal_decrease(self):
        """Debe evaluar meta de disminucion."""
        result = analyze_progress(
            metric_values=[80.0, 78.0, 76.0],
            metric_name="weight_kg",
            goal_value=70.0,
            goal_type="decrease",
        )
        assert result["goal_analysis"] is not None
        assert result["goal_analysis"]["on_track"] is True

    def test_analyze_with_goal_increase(self):
        """Debe evaluar meta de aumento."""
        result = analyze_progress(
            metric_values=[100.0, 110.0, 120.0],
            metric_name="1rm_bench",
            goal_value=150.0,
            goal_type="increase",
        )
        assert result["goal_analysis"]["on_track"] is True
        assert result["goal_analysis"]["progress_percent"] > 0

    def test_analyze_insufficient_data_empty(self):
        """Debe manejar lista vacia."""
        result = analyze_progress(metric_values=[])
        assert result["status"] == "insufficient_data"

    def test_analyze_insufficient_data_single(self):
        """Debe manejar un solo valor."""
        result = analyze_progress(metric_values=[80.0])
        assert result["status"] == "insufficient_data"
        assert result["current_value"] == 80.0

    def test_analyze_includes_statistics(self):
        """Debe incluir estadisticas basicas."""
        result = analyze_progress(
            metric_values=[10.0, 20.0, 30.0, 40.0, 50.0],
        )
        assert "values" in result
        assert result["values"]["min"] == 10.0
        assert result["values"]["max"] == 50.0
        assert result["values"]["average"] == 30.0

    def test_analyze_includes_insights(self):
        """Debe incluir insights."""
        result = analyze_progress(
            metric_values=[80.0, 78.0, 76.0],
            goal_value=70.0,
            goal_type="decrease",
        )
        assert "insights" in result
        assert len(result["insights"]) > 0

    def test_analyze_consistency_metric(self):
        """Debe calcular consistencia."""
        result = analyze_progress(
            metric_values=[75.0, 75.1, 74.9, 75.0, 75.1, 75.0],
        )
        assert result["consistency"] == "very_consistent"


class TestCalculateTrends:
    """Tests para calculate_trends."""

    def test_calculate_ascending_trend(self):
        """Debe detectar tendencia ascendente."""
        data_points = [
            {"date": "2024-01-01", "value": 100},
            {"date": "2024-01-02", "value": 105},
            {"date": "2024-01-03", "value": 110},
            {"date": "2024-01-04", "value": 115},
        ]
        result = calculate_trends(data_points, metric_name="1rm_squat")
        assert result["trend"]["direction"] == "ascending"

    def test_calculate_descending_trend(self):
        """Debe detectar tendencia descendente."""
        data_points = [
            {"date": "2024-01-01", "value": 80},
            {"date": "2024-01-02", "value": 78},
            {"date": "2024-01-03", "value": 76},
            {"date": "2024-01-04", "value": 74},
        ]
        result = calculate_trends(data_points, metric_name="weight_kg")
        assert result["trend"]["direction"] == "descending"

    def test_calculate_stable_trend(self):
        """Debe detectar tendencia estable."""
        data_points = [
            {"date": "2024-01-01", "value": 75.0},
            {"date": "2024-01-02", "value": 75.1},
            {"date": "2024-01-03", "value": 74.9},
            {"date": "2024-01-04", "value": 75.0},
        ]
        result = calculate_trends(data_points)
        assert result["trend"]["direction"] == "stable"

    def test_calculate_volatile_trend(self):
        """Debe detectar alta volatilidad."""
        data_points = [
            {"date": "2024-01-01", "value": 100},
            {"date": "2024-01-02", "value": 50},
            {"date": "2024-01-03", "value": 120},
            {"date": "2024-01-04", "value": 40},
        ]
        result = calculate_trends(data_points)
        assert result["trend"]["direction"] == "volatile"

    def test_calculate_insufficient_data(self):
        """Debe manejar datos insuficientes."""
        data_points = [{"date": "2024-01-01", "value": 100}]
        result = calculate_trends(data_points)
        assert result["status"] == "insufficient_data"

    def test_calculate_includes_statistics(self):
        """Debe incluir estadisticas."""
        data_points = [
            {"date": f"2024-01-{i:02d}", "value": 100 + i}
            for i in range(1, 10)
        ]
        result = calculate_trends(data_points)
        assert "statistics" in result
        assert "mean" in result["statistics"]
        assert "std_dev" in result["statistics"]

    def test_calculate_detects_anomalies(self):
        """Debe detectar anomalias."""
        # Necesitamos mas puntos para que la deteccion de anomalias sea precisa
        # y un valor muy extremo para que sea detectado como anomalia (z-score > 2)
        data_points = [
            {"date": "2024-01-01", "value": 100},
            {"date": "2024-01-02", "value": 101},
            {"date": "2024-01-03", "value": 99},
            {"date": "2024-01-04", "value": 100},
            {"date": "2024-01-05", "value": 101},
            {"date": "2024-01-06", "value": 99},
            {"date": "2024-01-07", "value": 100},
            {"date": "2024-01-08", "value": 500},  # Anomalia extrema
        ]
        result = calculate_trends(data_points)
        assert len(result["anomalies"]) > 0

    def test_calculate_includes_projections(self):
        """Debe incluir proyecciones."""
        data_points = [
            {"date": f"2024-01-{i:02d}", "value": 100 + i * 2}
            for i in range(1, 10)
        ]
        result = calculate_trends(data_points)
        assert "projections" in result
        assert "7_days" in result["projections"]
        assert "30_days" in result["projections"]

    def test_calculate_includes_interpretation(self):
        """Debe incluir interpretacion."""
        data_points = [
            {"date": f"2024-01-{i:02d}", "value": 100 + i}
            for i in range(1, 5)
        ]
        result = calculate_trends(data_points)
        assert "interpretation" in result
        assert len(result["interpretation"]) > 0


class TestCheckGoalStatus:
    """Tests para check_goal_status."""

    def test_goal_completed(self):
        """Debe detectar meta completada."""
        result = check_goal_status(
            goal_category="strength",
            current_value=150.0,
            target_value=150.0,
            start_value=100.0,
        )
        assert result["status"] == "completed"
        assert result["progress"]["percent"] == 100.0

    def test_goal_near_completion(self):
        """Debe detectar meta cerca de completar."""
        result = check_goal_status(
            goal_category="strength",
            current_value=145.0,
            target_value=150.0,
            start_value=100.0,
        )
        assert result["status"] == "near_completion"
        assert result["progress"]["percent"] >= 75

    def test_goal_halfway(self):
        """Debe detectar meta a mitad de camino."""
        result = check_goal_status(
            goal_category="fat_loss",
            current_value=90.0,
            target_value=80.0,
            start_value=100.0,
        )
        assert result["status"] == "halfway"

    def test_goal_in_progress(self):
        """Debe detectar meta en progreso (25-50%)."""
        # 30% progreso = (73-70)/(80-70) = 3/10 = 30%
        result = check_goal_status(
            goal_category="muscle_gain",
            current_value=73.0,
            target_value=80.0,
            start_value=70.0,
        )
        assert result["status"] == "in_progress"

    def test_goal_starting(self):
        """Debe detectar meta en fase inicial."""
        result = check_goal_status(
            goal_category="endurance",
            current_value=101.0,
            target_value=150.0,
            start_value=100.0,
        )
        assert result["status"] == "starting"

    def test_goal_with_dates_on_track(self):
        """Debe evaluar progreso temporal - en camino."""
        # Usar fechas futuras para evitar problemas con fechas pasadas
        result = check_goal_status(
            goal_category="strength",
            current_value=125.0,
            target_value=150.0,
            start_value=100.0,
            start_date="2025-01-01",
            target_date="2025-12-31",
        )
        assert result["time_analysis"] is not None
        assert "pace" in result["time_analysis"]

    def test_goal_includes_recommendations(self):
        """Debe incluir recomendaciones."""
        result = check_goal_status(
            goal_category="recovery",
            current_value=70.0,
            target_value=90.0,
            start_value=60.0,
        )
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0

    def test_goal_invalid_category_defaults(self):
        """Debe usar categoria por defecto para invalida."""
        result = check_goal_status(
            goal_category="invalid_category",
            current_value=50.0,
            target_value=100.0,
            start_value=0.0,
        )
        assert result["status"] is not None


class TestInterpretBiomarkers:
    """Tests para interpret_biomarkers."""

    def test_interpret_optimal_biomarkers(self):
        """Debe interpretar biomarcadores optimos."""
        result = interpret_biomarkers(
            biomarkers={
                "resting_hr": 60,
                "hrv_ms": 70,
                "sleep_score": 85,
            }
        )
        assert result["status"] == "analyzed"
        assert result["summary"]["overall_health_score"] >= 80

    def test_interpret_concerning_biomarkers(self):
        """Debe detectar biomarcadores preocupantes."""
        result = interpret_biomarkers(
            biomarkers={
                "resting_hr": 110,
                "hrv_ms": 15,
                "sleep_score": 40,
            }
        )
        assert result["summary"]["overall_health_score"] < 70
        assert len(result["summary"]["concerns"]) > 0

    def test_interpret_with_age_and_sex(self):
        """Debe considerar edad y sexo."""
        # 15% body fat es optimo para hombres (rango optimo: 10-20%)
        result = interpret_biomarkers(
            biomarkers={"body_fat_pct": 15},
            user_age=45,
            user_sex="male",
        )
        assert result["interpretations"][0]["status"] in ["optimal", "normal"]

    def test_interpret_unknown_biomarker(self):
        """Debe manejar biomarcador desconocido."""
        result = interpret_biomarkers(
            biomarkers={"unknown_marker": 100}
        )
        assert result["interpretations"][0]["status"] == "unknown"

    def test_interpret_includes_recommendations(self):
        """Debe incluir recomendaciones por biomarcador."""
        result = interpret_biomarkers(
            biomarkers={"resting_hr": 95}
        )
        interp = result["interpretations"][0]
        assert "recommendations" in interp

    def test_interpret_includes_disclaimer(self):
        """Debe incluir disclaimer medico."""
        result = interpret_biomarkers(biomarkers={"hrv_ms": 50})
        assert "disclaimer" in result

    def test_interpret_with_history(self):
        """Debe analizar historial si se proporciona."""
        result = interpret_biomarkers(
            biomarkers={"resting_hr": 65},
            include_history=True,
            history={"resting_hr": [70, 68, 66, 65, 65]},
        )
        interp = result["interpretations"][0]
        assert "trend" in interp

    def test_interpret_glucose_high(self):
        """Debe alertar sobre glucosa alta."""
        result = interpret_biomarkers(biomarkers={"glucose_mg_dl": 130})
        assert result["interpretations"][0]["status"] == "high"

    def test_interpret_blood_pressure(self):
        """Debe interpretar presion arterial."""
        result = interpret_biomarkers(
            biomarkers={"blood_pressure_sys": 118}
        )
        assert result["interpretations"][0]["status"] == "optimal"


class TestGenerateReport:
    """Tests para generate_report."""

    def test_generate_weekly_report(self):
        """Debe generar reporte semanal."""
        result = generate_report(report_type="weekly")
        assert result["report_type"] == "weekly"
        assert result["period"]["days"] == 7

    def test_generate_monthly_report(self):
        """Debe generar reporte mensual."""
        result = generate_report(report_type="monthly")
        assert result["report_type"] == "monthly"
        assert result["period"]["days"] == 30

    def test_generate_quarterly_report(self):
        """Debe generar reporte trimestral."""
        result = generate_report(report_type="quarterly")
        assert result["report_type"] == "quarterly"
        assert result["period"]["days"] == 90

    def test_generate_with_metrics(self):
        """Debe incluir analisis de metricas."""
        result = generate_report(
            report_type="weekly",
            metrics_data={
                "weight_kg": [80.0, 79.5, 79.0, 78.5],
                "body_fat_pct": [20.0, 19.8, 19.5, 19.3],
            },
        )
        assert result["metrics_summary"]["total_tracked"] == 2
        assert len(result["metrics_summary"]["details"]) == 2

    def test_generate_with_goals(self):
        """Debe incluir analisis de metas."""
        result = generate_report(
            report_type="weekly",
            goals_data=[
                {"category": "strength", "name": "Squat PR", "current": 140, "target": 150, "start": 100},
                {"category": "fat_loss", "name": "Peso ideal", "current": 78, "target": 75, "start": 80},
            ],
        )
        assert result["goals_summary"]["total"] == 2

    def test_generate_includes_executive_summary(self):
        """Debe incluir resumen ejecutivo."""
        result = generate_report(
            report_type="weekly",
            user_name="Test User",
        )
        assert "executive_summary" in result
        assert len(result["executive_summary"]) > 0

    def test_generate_includes_action_items(self):
        """Debe incluir items de accion."""
        result = generate_report(report_type="weekly")
        assert "action_items" in result
        assert len(result["action_items"]) > 0

    def test_generate_includes_next_review(self):
        """Debe incluir fecha de proxima revision."""
        result = generate_report(report_type="weekly")
        assert "next_review" in result

    def test_generate_with_custom_period(self):
        """Debe manejar periodo personalizado."""
        result = generate_report(
            report_type="custom",
            period_start="2024-01-01",
            period_end="2024-01-15",
        )
        assert result["period"]["days"] == 14

    def test_generate_calculates_period_score(self):
        """Debe calcular puntuacion del periodo."""
        result = generate_report(
            report_type="weekly",
            metrics_data={"weight_kg": [80.0, 79.0, 78.0]},
        )
        assert "period_score" in result
        assert 0 <= result["period_score"] <= 100


class TestMetricTypesIntegrity:
    """Tests para integridad de METRIC_TYPES."""

    def test_all_categories_have_metrics(self):
        """Todas las categorias deben tener metricas."""
        for category, metrics in METRIC_TYPES.items():
            assert len(metrics) > 0, f"Categoria {category} sin metricas"

    def test_expected_categories_exist(self):
        """Deben existir categorias esperadas."""
        expected = ["body_composition", "performance", "recovery", "nutrition", "vitals"]
        for cat in expected:
            assert cat in METRIC_TYPES


class TestBiomarkerRangesIntegrity:
    """Tests para integridad de BIOMARKER_RANGES."""

    def test_all_biomarkers_have_required_fields(self):
        """Todos los biomarcadores deben tener campos requeridos."""
        required_fields = ["name_es", "unit", "interpretation"]
        for marker_id, marker_data in BIOMARKER_RANGES.items():
            for field in required_fields:
                assert field in marker_data, f"Biomarcador {marker_id} falta campo {field}"

    def test_all_biomarkers_have_ranges(self):
        """Todos los biomarcadores deben tener rangos."""
        for marker_id, marker_data in BIOMARKER_RANGES.items():
            has_optimal = "optimal_min" in marker_data or "optimal_min_male" in marker_data
            assert has_optimal, f"Biomarcador {marker_id} sin rango optimal"


class TestGoalTemplatesIntegrity:
    """Tests para integridad de GOAL_TEMPLATES."""

    def test_all_templates_have_required_fields(self):
        """Todos los templates deben tener campos requeridos."""
        required_fields = ["name_es", "metrics", "typical_timeline_weeks", "expected_progress_pct"]
        for template_id, template_data in GOAL_TEMPLATES.items():
            for field in required_fields:
                assert field in template_data, f"Template {template_id} falta campo {field}"

    def test_expected_categories_exist(self):
        """Deben existir categorias esperadas."""
        expected = ["strength", "fat_loss", "muscle_gain", "endurance", "recovery"]
        for cat in expected:
            assert cat in GOAL_TEMPLATES


class TestTrendPeriodsIntegrity:
    """Tests para integridad de TREND_PERIODS."""

    def test_expected_periods_exist(self):
        """Deben existir periodos esperados."""
        expected = ["7d", "14d", "30d", "90d"]
        for period in expected:
            assert period in TREND_PERIODS

    def test_periods_are_valid_days(self):
        """Todos los periodos deben ser dias validos."""
        for period_id, days in TREND_PERIODS.items():
            assert days > 0, f"Periodo {period_id} con dias invalidos"
