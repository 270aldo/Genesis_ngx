"""Tests para las tools de METABOL."""

from __future__ import annotations

from agents.metabol.tools import (
    calculate_tdee,
    assess_metabolic_rate,
    plan_nutrient_timing,
    detect_metabolic_adaptation,
    assess_insulin_sensitivity,
    ACTIVITY_LEVELS,
    METABOLIC_FORMULAS,
    GOAL_ADJUSTMENTS,
    TIMING_WINDOWS,
    INSULIN_SENSITIVITY_INDICATORS,
)


class TestCalculateTdee:
    """Tests para calculate_tdee."""

    def test_calculate_male_tdee(self):
        """Debe calcular TDEE para hombre."""
        result = calculate_tdee(
            weight_kg=75.0,
            height_cm=175,
            age=35,
            sex="male",
            activity_level="moderate",
        )
        assert result["status"] == "calculated"
        assert result["result"]["daily_calories"] > 2000

    def test_calculate_female_tdee(self):
        """Debe calcular TDEE para mujer."""
        result = calculate_tdee(
            weight_kg=60.0,
            height_cm=165,
            age=35,
            sex="female",
            activity_level="moderate",
        )
        assert result["status"] == "calculated"
        assert result["result"]["daily_calories"] > 1500

    def test_sedentary_less_than_active(self):
        """Sedentario debe tener menos calorias que activo."""
        sedentary = calculate_tdee(
            weight_kg=75.0, height_cm=175, age=35,
            activity_level="sedentary",
        )
        active = calculate_tdee(
            weight_kg=75.0, height_cm=175, age=35,
            activity_level="active",
        )
        assert sedentary["result"]["daily_calories"] < active["result"]["daily_calories"]

    def test_fat_loss_creates_deficit(self):
        """Fat loss debe crear deficit."""
        maintenance = calculate_tdee(
            weight_kg=75.0, height_cm=175, age=35,
            goal="maintenance",
        )
        fat_loss = calculate_tdee(
            weight_kg=75.0, height_cm=175, age=35,
            goal="fat_loss",
        )
        assert fat_loss["result"]["daily_calories"] < maintenance["result"]["daily_calories"]

    def test_muscle_gain_creates_surplus(self):
        """Muscle gain debe crear superavit."""
        maintenance = calculate_tdee(
            weight_kg=75.0, height_cm=175, age=35,
            goal="maintenance",
        )
        muscle_gain = calculate_tdee(
            weight_kg=75.0, height_cm=175, age=35,
            goal="muscle_gain",
        )
        assert muscle_gain["result"]["daily_calories"] > maintenance["result"]["daily_calories"]

    def test_katch_mcardle_with_body_fat(self):
        """Debe usar Katch-McArdle con body fat."""
        result = calculate_tdee(
            weight_kg=75.0,
            height_cm=175,
            age=35,
            body_fat_percent=15.0,
            formula="katch_mcardle",
        )
        assert result["formula_used"] == "katch_mcardle"

    def test_harris_benedict_formula(self):
        """Debe usar Harris-Benedict si se especifica."""
        result = calculate_tdee(
            weight_kg=75.0,
            height_cm=175,
            age=35,
            formula="harris_benedict",
        )
        assert result["formula_used"] == "harris_benedict"

    def test_invalid_inputs_return_error(self):
        """Inputs invalidos deben retornar error."""
        result = calculate_tdee(
            weight_kg=-75.0,
            height_cm=175,
            age=35,
        )
        assert result["status"] == "error"

    def test_includes_recommendations(self):
        """Debe incluir recomendaciones."""
        result = calculate_tdee(
            weight_kg=75.0,
            height_cm=175,
            age=35,
        )
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0

    def test_minimum_calories_for_fat_loss(self):
        """Debe respetar calorias minimas en fat loss."""
        result = calculate_tdee(
            weight_kg=50.0,
            height_cm=155,
            age=50,
            sex="female",
            activity_level="sedentary",
            goal="fat_loss",
        )
        assert result["result"]["daily_calories"] >= 1200


class TestAssessMetabolicRate:
    """Tests para assess_metabolic_rate."""

    def test_assess_basic_bmr(self):
        """Debe calcular BMR basico."""
        result = assess_metabolic_rate(
            weight_kg=75.0,
            height_cm=175,
            age=35,
            sex="male",
        )
        assert result["status"] == "assessed"
        assert "mifflin_st_jeor" in result["formulas"]
        assert "harris_benedict" in result["formulas"]

    def test_katch_mcardle_with_body_fat(self):
        """Debe incluir Katch-McArdle con body fat."""
        result = assess_metabolic_rate(
            weight_kg=75.0,
            height_cm=175,
            age=35,
            body_fat_percent=15.0,
        )
        assert "katch_mcardle" in result["formulas"]

    def test_includes_summary(self):
        """Debe incluir resumen."""
        result = assess_metabolic_rate(
            weight_kg=75.0,
            height_cm=175,
            age=35,
        )
        assert "summary" in result
        assert "average_bmr" in result["summary"]
        assert "recommended_formula" in result["summary"]

    def test_includes_metabolic_context(self):
        """Debe incluir contexto metabolico."""
        result = assess_metabolic_rate(
            weight_kg=75.0,
            height_cm=175,
            age=55,
        )
        assert "metabolic_context" in result
        assert len(result["metabolic_context"]) > 0

    def test_includes_composition_with_body_fat(self):
        """Debe incluir composicion con body fat."""
        result = assess_metabolic_rate(
            weight_kg=80.0,
            height_cm=175,
            age=35,
            body_fat_percent=20.0,
        )
        assert result["composition"] is not None
        assert "lean_mass_kg" in result["composition"]
        assert "fat_mass_kg" in result["composition"]

    def test_invalid_inputs_return_error(self):
        """Inputs invalidos deben retornar error."""
        result = assess_metabolic_rate(
            weight_kg=0,
            height_cm=175,
            age=35,
        )
        assert result["status"] == "error"


class TestPlanNutrientTiming:
    """Tests para plan_nutrient_timing."""

    def test_plan_basic_timing(self):
        """Debe generar plan basico de timing."""
        result = plan_nutrient_timing(
            training_time="18:00",
            wake_time="07:00",
            sleep_time="23:00",
        )
        assert result["status"] == "planned"
        assert "schedule" in result

    def test_generates_meal_schedule(self):
        """Debe generar horario de comidas."""
        result = plan_nutrient_timing(
            training_time="18:00",
            meals_per_day=4,
        )
        assert "meals" in result["schedule"]
        assert len(result["schedule"]["meals"]) == 4

    def test_includes_training_windows(self):
        """Debe incluir ventanas de entrenamiento."""
        result = plan_nutrient_timing(training_time="18:00")
        assert "training_day_windows" in result
        assert "pre_workout" in result["training_day_windows"]
        assert "post_workout" in result["training_day_windows"]

    def test_includes_timing_recommendations(self):
        """Debe incluir recomendaciones de timing."""
        result = plan_nutrient_timing(training_time="18:00")
        assert "timing_recommendations" in result
        assert "training_days" in result["timing_recommendations"]
        assert "rest_days" in result["timing_recommendations"]

    def test_goal_specific_notes(self):
        """Debe incluir notas especificas por objetivo."""
        result = plan_nutrient_timing(
            training_time="18:00",
            goal="fat_loss",
        )
        assert "goal_specific_notes" in result
        assert len(result["goal_specific_notes"]) > 0

    def test_invalid_time_format(self):
        """Debe manejar formato de hora invalido."""
        result = plan_nutrient_timing(training_time="invalid")
        assert result["status"] == "error"


class TestDetectMetabolicAdaptation:
    """Tests para detect_metabolic_adaptation."""

    def test_detect_no_adaptation(self):
        """Debe detectar sin adaptacion."""
        result = detect_metabolic_adaptation(
            weekly_weights=[80.0, 79.5, 79.0, 78.5],
            daily_calories=2000,
            weeks_in_deficit=4,
        )
        assert result["status"] == "analyzed"
        assert result["adaptation_assessment"]["level"] == "low"

    def test_detect_stalled_weight(self):
        """Debe detectar peso estancado."""
        result = detect_metabolic_adaptation(
            weekly_weights=[80.0, 80.0, 80.0, 80.0],
            daily_calories=1800,
            weeks_in_deficit=10,
        )
        assert result["weight_analysis"]["is_stalled"] is True

    def test_detect_high_adaptation(self):
        """Debe detectar alta adaptacion."""
        result = detect_metabolic_adaptation(
            weekly_weights=[80.0, 80.0, 80.0, 80.0, 80.0],
            daily_calories=1500,
            weeks_in_deficit=12,
            current_symptoms=["fatiga extrema", "frio constante", "libido baja"],
        )
        assert result["adaptation_assessment"]["level"] in ["moderate", "high"]

    def test_insufficient_data(self):
        """Debe manejar datos insuficientes."""
        result = detect_metabolic_adaptation(
            weekly_weights=[80.0],
            daily_calories=2000,
        )
        assert result["status"] == "insufficient_data"

    def test_includes_recommendations(self):
        """Debe incluir recomendaciones."""
        result = detect_metabolic_adaptation(
            weekly_weights=[80.0, 79.5, 79.0],
            daily_calories=2000,
        )
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0

    def test_calculates_weight_changes(self):
        """Debe calcular cambios de peso."""
        result = detect_metabolic_adaptation(
            weekly_weights=[80.0, 79.0, 78.0],
            daily_calories=2000,
        )
        assert "total_change_kg" in result["weight_analysis"]
        assert "avg_weekly_change_kg" in result["weight_analysis"]


class TestAssessInsulinSensitivity:
    """Tests para assess_insulin_sensitivity."""

    def test_assess_high_sensitivity(self):
        """Debe detectar alta sensibilidad."""
        result = assess_insulin_sensitivity(
            fasting_glucose_mg_dl=85,
            post_meal_energy="stable",
            body_fat_distribution="even",
            family_history_diabetes=False,
            exercise_frequency="high",
            carb_response="good",
        )
        assert result["status"] == "assessed"
        assert result["assessment"]["sensitivity_level"] == "high_sensitivity"

    def test_assess_low_sensitivity(self):
        """Debe detectar baja sensibilidad."""
        result = assess_insulin_sensitivity(
            fasting_glucose_mg_dl=115,
            post_meal_energy="crash",
            body_fat_distribution="central",
            family_history_diabetes=True,
            exercise_frequency="sedentary",
            carb_response="poor",
        )
        assert result["assessment"]["sensitivity_level"] in ["low_sensitivity", "moderate_sensitivity"]

    def test_includes_carb_recommendation(self):
        """Debe incluir recomendacion de carbohidratos."""
        result = assess_insulin_sensitivity()
        assert "carb_recommendation" in result
        assert "percent_of_calories" in result["carb_recommendation"]

    def test_includes_factors_analyzed(self):
        """Debe incluir factores analizados."""
        result = assess_insulin_sensitivity(
            fasting_glucose_mg_dl=90,
        )
        assert "factors_analyzed" in result
        assert len(result["factors_analyzed"]) > 0

    def test_includes_disclaimer(self):
        """Debe incluir disclaimer."""
        result = assess_insulin_sensitivity()
        assert "disclaimer" in result

    def test_glucose_status_detection(self):
        """Debe detectar status de glucosa."""
        normal = assess_insulin_sensitivity(fasting_glucose_mg_dl=90)
        assert normal["glucose_status"] == "normal"

        pre = assess_insulin_sensitivity(fasting_glucose_mg_dl=110)
        assert pre["glucose_status"] == "prediabetes_range"


class TestActivityLevelsIntegrity:
    """Tests para integridad de ACTIVITY_LEVELS."""

    def test_all_levels_have_required_fields(self):
        """Todos los niveles deben tener campos requeridos."""
        required_fields = ["name_es", "factor", "description"]
        for level_id, level_data in ACTIVITY_LEVELS.items():
            for field in required_fields:
                assert field in level_data, f"Nivel {level_id} falta campo {field}"

    def test_factors_are_valid(self):
        """Todos los factores deben ser validos."""
        for level_id, level_data in ACTIVITY_LEVELS.items():
            assert 1.0 <= level_data["factor"] <= 2.5, f"Factor invalido en {level_id}"

    def test_expected_levels_exist(self):
        """Deben existir niveles esperados."""
        expected = ["sedentary", "light", "moderate", "active", "very_active"]
        for level in expected:
            assert level in ACTIVITY_LEVELS


class TestMetabolicFormulasIntegrity:
    """Tests para integridad de METABOLIC_FORMULAS."""

    def test_all_formulas_have_required_fields(self):
        """Todas las formulas deben tener campos requeridos."""
        required_fields = ["name", "accuracy", "requires_body_fat"]
        for formula_id, formula_data in METABOLIC_FORMULAS.items():
            for field in required_fields:
                assert field in formula_data, f"Formula {formula_id} falta campo {field}"

    def test_expected_formulas_exist(self):
        """Deben existir formulas esperadas."""
        expected = ["mifflin_st_jeor", "harris_benedict", "katch_mcardle"]
        for formula in expected:
            assert formula in METABOLIC_FORMULAS


class TestGoalAdjustmentsIntegrity:
    """Tests para integridad de GOAL_ADJUSTMENTS."""

    def test_all_goals_have_required_fields(self):
        """Todos los objetivos deben tener campos requeridos."""
        required_fields = ["name_es"]
        for goal_id, goal_data in GOAL_ADJUSTMENTS.items():
            for field in required_fields:
                assert field in goal_data, f"Goal {goal_id} falta campo {field}"

    def test_expected_goals_exist(self):
        """Deben existir objetivos esperados."""
        expected = ["fat_loss", "maintenance", "muscle_gain", "recomp"]
        for goal in expected:
            assert goal in GOAL_ADJUSTMENTS


class TestTimingWindowsIntegrity:
    """Tests para integridad de TIMING_WINDOWS."""

    def test_all_windows_have_required_fields(self):
        """Todas las ventanas deben tener campos requeridos."""
        required_fields = ["name_es", "macro_focus", "recommendations"]
        for window_id, window_data in TIMING_WINDOWS.items():
            for field in required_fields:
                assert field in window_data, f"Window {window_id} falta campo {field}"

    def test_expected_windows_exist(self):
        """Deben existir ventanas esperadas."""
        expected = ["pre_workout", "post_workout", "before_sleep"]
        for window in expected:
            assert window in TIMING_WINDOWS


class TestInsulinSensitivityIndicatorsIntegrity:
    """Tests para integridad de INSULIN_SENSITIVITY_INDICATORS."""

    def test_all_levels_have_required_fields(self):
        """Todos los niveles deben tener campos requeridos."""
        required_fields = ["name_es", "description", "carb_tolerance", "recommended_carb_pct"]
        for level_id, level_data in INSULIN_SENSITIVITY_INDICATORS.items():
            for field in required_fields:
                assert field in level_data, f"Level {level_id} falta campo {field}"

    def test_expected_levels_exist(self):
        """Deben existir niveles esperados."""
        expected = ["high_sensitivity", "moderate_sensitivity", "low_sensitivity"]
        for level in expected:
            assert level in INSULIN_SENSITIVITY_INDICATORS
