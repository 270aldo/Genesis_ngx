"""Tests para las tools de MACRO."""

from __future__ import annotations

from agents.macro.tools import (
    calculate_macros,
    distribute_protein,
    plan_carb_cycling,
    optimize_fat_intake,
    compose_meal,
    MACRO_RATIOS,
    PROTEIN_TARGETS,
    CARB_CYCLING_PATTERNS,
    FAT_DISTRIBUTION,
    MEAL_TEMPLATES,
    PROTEIN_SOURCES,
)


class TestCalculateMacros:
    """Tests para calculate_macros."""

    def test_calculate_basic_macros(self):
        """Debe calcular macros básicos."""
        result = calculate_macros(daily_calories=2000)
        assert result["status"] == "calculated"
        assert "macros" in result
        assert result["macros"]["protein"]["grams"] > 0
        assert result["macros"]["carbs"]["grams"] > 0
        assert result["macros"]["fat"]["grams"] > 0

    def test_calculate_fat_loss_macros(self):
        """Macros para fat loss deben tener proteína alta."""
        result = calculate_macros(
            daily_calories=1800,
            goal="fat_loss",
        )
        assert result["status"] == "calculated"
        # Fat loss tiene mayor % de proteína
        assert result["macros"]["protein"]["percent"] >= 35

    def test_calculate_muscle_gain_macros(self):
        """Macros para muscle gain deben tener carbos altos."""
        result = calculate_macros(
            daily_calories=2500,
            goal="muscle_gain",
        )
        assert result["status"] == "calculated"
        # Muscle gain tiene más carbohidratos
        assert result["macros"]["carbs"]["percent"] >= 40

    def test_calculate_with_weight(self):
        """Debe calcular proteína por kg de peso."""
        result = calculate_macros(
            daily_calories=2000,
            weight_kg=75.0,
            activity_type="strength",
        )
        assert result["status"] == "calculated"
        assert result["summary"]["protein_per_kg"] is not None
        assert result["summary"]["protein_per_kg"] >= 1.4

    def test_calculate_with_custom_protein(self):
        """Debe usar proteína personalizada."""
        result = calculate_macros(
            daily_calories=2000,
            custom_protein_g=180.0,
        )
        assert result["status"] == "calculated"
        assert result["macros"]["protein"]["grams"] == 180.0

    def test_calories_balance_correctly(self):
        """Macros deben sumar las calorías objetivo."""
        result = calculate_macros(daily_calories=2000)
        total = (
            result["macros"]["protein"]["calories"]
            + result["macros"]["carbs"]["calories"]
            + result["macros"]["fat"]["calories"]
        )
        assert abs(total - 2000) < 10  # Tolerancia por redondeo

    def test_includes_ranges(self):
        """Debe incluir rangos flexibles."""
        result = calculate_macros(daily_calories=2000)
        assert "ranges" in result
        assert "protein" in result["ranges"]
        assert "low" in result["ranges"]["protein"]
        assert "high" in result["ranges"]["protein"]

    def test_includes_recommendations(self):
        """Debe incluir recomendaciones."""
        result = calculate_macros(daily_calories=2000)
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0

    def test_invalid_calories_low(self):
        """Debe rechazar calorías muy bajas."""
        result = calculate_macros(daily_calories=500)
        assert result["status"] == "error"

    def test_invalid_calories_high(self):
        """Debe rechazar calorías muy altas."""
        result = calculate_macros(daily_calories=15000)
        assert result["status"] == "error"

    def test_invalid_goal(self):
        """Debe rechazar objetivo inválido."""
        result = calculate_macros(daily_calories=2000, goal="invalid_goal")
        assert result["status"] == "error"

    def test_different_approaches(self):
        """Debe soportar diferentes enfoques."""
        standard = calculate_macros(
            daily_calories=2000, goal="fat_loss", approach="standard"
        )
        high_protein = calculate_macros(
            daily_calories=2000, goal="fat_loss", approach="high_protein"
        )
        assert standard["macros"]["protein"]["percent"] < high_protein["macros"]["protein"]["percent"]

    def test_minimum_fat_for_health(self):
        """Debe mantener mínimo 20% de grasas."""
        result = calculate_macros(
            daily_calories=2000,
            goal="performance",  # Tiene fat bajo en template
        )
        assert result["macros"]["fat"]["percent"] >= 20

    def test_low_carb_warning(self):
        """Debe advertir cuando carbos son muy bajos."""
        result = calculate_macros(
            daily_calories=1200,
            custom_protein_g=150,  # Fuerza proteína alta
        )
        # Puede generar warning si carbos quedan muy bajos
        if result["macros"]["carbs"]["grams"] < 50:
            assert result["warnings"] is not None


class TestDistributeProtein:
    """Tests para distribute_protein."""

    def test_distribute_basic(self):
        """Debe distribuir proteína básica."""
        result = distribute_protein(daily_protein_g=150, meals_per_day=4)
        assert result["status"] == "distributed"
        assert len(result["distribution"]) == 4

    def test_distribute_3_meals(self):
        """Debe distribuir en 3 comidas."""
        result = distribute_protein(daily_protein_g=120, meals_per_day=3)
        assert len(result["distribution"]) == 3
        total = sum(m["protein_g"] for m in result["distribution"])
        assert abs(total - 120) < 1

    def test_distribute_5_meals(self):
        """Debe distribuir en 5 comidas."""
        result = distribute_protein(daily_protein_g=180, meals_per_day=5)
        assert len(result["distribution"]) == 5

    def test_distribute_6_meals(self):
        """Debe distribuir en 6 comidas."""
        result = distribute_protein(daily_protein_g=200, meals_per_day=6)
        assert len(result["distribution"]) == 6

    def test_total_equals_daily(self):
        """Total debe igualar proteína diaria."""
        result = distribute_protein(daily_protein_g=160, meals_per_day=4)
        total = sum(m["protein_g"] for m in result["distribution"])
        assert abs(total - 160) < 1

    def test_includes_meal_names(self):
        """Debe incluir nombres de comidas."""
        result = distribute_protein(daily_protein_g=150, meals_per_day=4)
        for meal in result["distribution"]:
            assert "name" in meal
            assert len(meal["name"]) > 0

    def test_includes_source_suggestions(self):
        """Debe incluir sugerencias de fuentes."""
        result = distribute_protein(daily_protein_g=150, meals_per_day=4)
        for meal in result["distribution"]:
            assert "sources_suggestion" in meal

    def test_synthesis_analysis(self):
        """Debe incluir análisis de síntesis."""
        result = distribute_protein(daily_protein_g=150, meals_per_day=4)
        assert "synthesis_analysis" in result
        assert "optimal_per_meal" in result["synthesis_analysis"]

    def test_timing_recommendations(self):
        """Debe incluir recomendaciones de timing."""
        result = distribute_protein(daily_protein_g=150, meals_per_day=4)
        assert "timing_recommendations" in result

    def test_muscle_gain_distribution(self):
        """Fat loss debe tener distribución uniforme."""
        result = distribute_protein(
            daily_protein_g=180,
            meals_per_day=4,
            goal="fat_loss",
        )
        # Fat loss tiende a distribución uniforme
        proteins = [m["protein_g"] for m in result["distribution"]]
        variance = max(proteins) - min(proteins)
        assert variance < 10  # Relativamente uniforme

    def test_invalid_protein_low(self):
        """Debe rechazar proteína muy baja."""
        result = distribute_protein(daily_protein_g=20)
        assert result["status"] == "error"

    def test_invalid_protein_high(self):
        """Debe rechazar proteína muy alta."""
        result = distribute_protein(daily_protein_g=500)
        assert result["status"] == "error"

    def test_invalid_meals(self):
        """Debe rechazar comidas inválidas."""
        result = distribute_protein(daily_protein_g=150, meals_per_day=1)
        assert result["status"] == "error"


class TestPlanCarbCycling:
    """Tests para plan_carb_cycling."""

    def test_plan_basic_cycling(self):
        """Debe crear plan básico de ciclado."""
        result = plan_carb_cycling(
            base_carbs_g=200,
            training_days=["lunes", "miercoles", "viernes"],
        )
        assert result["status"] == "planned"
        assert "weekly_plan" in result
        assert len(result["weekly_plan"]) == 7

    def test_training_days_are_high(self):
        """Días de entrenamiento deben ser altos en carbos."""
        result = plan_carb_cycling(
            base_carbs_g=200,
            training_days=["lunes", "miercoles"],
        )
        # Lunes y miércoles deben ser high
        monday = result["weekly_plan"][0]
        wednesday = result["weekly_plan"][2]
        assert monday["carb_type"] == "high"
        assert wednesday["carb_type"] == "high"
        assert monday["is_training_day"] is True

    def test_high_carbs_greater_than_low(self):
        """Carbos altos deben ser mayores que bajos."""
        result = plan_carb_cycling(
            base_carbs_g=200,
            training_days=["lunes"],
        )
        high = result["carb_levels"]["high"]["grams"]
        low = result["carb_levels"]["low"]["grams"]
        assert high > low

    def test_different_patterns(self):
        """Debe soportar diferentes patrones."""
        classic = plan_carb_cycling(
            base_carbs_g=200,
            training_days=["lunes"],
            pattern="classic_3day",
        )
        alternating = plan_carb_cycling(
            base_carbs_g=200,
            training_days=["lunes"],
            pattern="alternating",
        )
        assert classic["pattern"] == "classic_3day"
        assert alternating["pattern"] == "alternating"

    def test_includes_summary(self):
        """Debe incluir resumen semanal."""
        result = plan_carb_cycling(
            base_carbs_g=200,
            training_days=["lunes", "miercoles", "viernes"],
        )
        assert "summary" in result
        assert "total_weekly_carbs" in result["summary"]
        assert "avg_daily_carbs" in result["summary"]

    def test_includes_carb_levels(self):
        """Debe incluir niveles de carbos."""
        result = plan_carb_cycling(
            base_carbs_g=200,
            training_days=["lunes"],
        )
        assert "carb_levels" in result
        assert "high" in result["carb_levels"]
        assert "moderate" in result["carb_levels"]
        assert "low" in result["carb_levels"]

    def test_includes_source_recommendations(self):
        """Debe incluir recomendaciones de fuentes."""
        result = plan_carb_cycling(
            base_carbs_g=200,
            training_days=["lunes"],
        )
        assert "carb_source_recommendations" in result

    def test_training_days_english(self):
        """Debe aceptar días en inglés."""
        result = plan_carb_cycling(
            base_carbs_g=200,
            training_days=["monday", "wednesday"],
        )
        assert result["status"] == "planned"
        assert result["weekly_plan"][0]["is_training_day"] is True
        assert result["weekly_plan"][2]["is_training_day"] is True

    def test_invalid_carbs_low(self):
        """Debe rechazar carbos muy bajos."""
        result = plan_carb_cycling(
            base_carbs_g=20,
            training_days=["lunes"],
        )
        assert result["status"] == "error"

    def test_invalid_pattern(self):
        """Debe rechazar patrón inválido."""
        result = plan_carb_cycling(
            base_carbs_g=200,
            training_days=["lunes"],
            pattern="invalid_pattern",
        )
        assert result["status"] == "error"


class TestOptimizeFatIntake:
    """Tests para optimize_fat_intake."""

    def test_optimize_basic(self):
        """Debe optimizar grasa básica."""
        result = optimize_fat_intake(daily_fat_g=70)
        assert result["status"] == "optimized"
        assert "distribution" in result

    def test_includes_all_fat_types(self):
        """Debe incluir todos los tipos de grasa."""
        result = optimize_fat_intake(daily_fat_g=70)
        assert "saturated" in result["distribution"]
        assert "monounsaturated" in result["distribution"]
        assert "polyunsaturated" in result["distribution"]
        assert "trans" in result["distribution"]

    def test_omega3_analysis(self):
        """Debe incluir análisis de omega-3."""
        result = optimize_fat_intake(daily_fat_g=70, current_omega3_g=0.5)
        assert "omega3_analysis" in result
        assert "deficit_g" in result["omega3_analysis"]

    def test_omega3_deficit_detected(self):
        """Debe detectar déficit de omega-3."""
        result = optimize_fat_intake(daily_fat_g=70, current_omega3_g=0.3)
        assert result["omega3_analysis"]["deficit_g"] > 0
        assert result["omega3_analysis"]["status"] in ["insuficiente", "mejorable"]

    def test_omega3_sufficient(self):
        """Debe reconocer omega-3 suficiente."""
        result = optimize_fat_intake(daily_fat_g=70, current_omega3_g=2.5)
        assert result["omega3_analysis"]["status"] == "óptimo"

    def test_vegan_sources(self):
        """Debe adaptar fuentes para veganos."""
        result = optimize_fat_intake(
            daily_fat_g=70,
            dietary_restrictions=["vegano"],
        )
        # No debe incluir pescado en fuentes omega-3
        omega3_sources = result["recommended_sources"]["omega3"]
        assert "salmón" not in omega3_sources
        assert "sardinas" not in omega3_sources

    def test_includes_daily_suggestions(self):
        """Debe incluir sugerencias diarias."""
        result = optimize_fat_intake(daily_fat_g=70)
        assert "daily_suggestions" in result
        assert len(result["daily_suggestions"]) > 0

    def test_includes_health_notes(self):
        """Debe incluir notas de salud."""
        result = optimize_fat_intake(daily_fat_g=70)
        assert "health_notes" in result

    def test_trans_fat_zero(self):
        """Grasas trans deben ser cero."""
        result = optimize_fat_intake(daily_fat_g=70)
        assert result["distribution"]["trans"]["max_g"] == 0

    def test_invalid_fat_low(self):
        """Debe rechazar grasa muy baja."""
        result = optimize_fat_intake(daily_fat_g=10)
        assert result["status"] == "error"

    def test_invalid_fat_high(self):
        """Debe rechazar grasa muy alta."""
        result = optimize_fat_intake(daily_fat_g=400)
        assert result["status"] == "error"


class TestComposeMeal:
    """Tests para compose_meal."""

    def test_compose_basic_meal(self):
        """Debe componer comida básica."""
        result = compose_meal(target_calories=500)
        assert result["status"] == "composed"
        assert "macro_targets" in result

    def test_compose_pre_workout(self):
        """Comida pre-entreno debe tener más carbos."""
        result = compose_meal(target_calories=500, meal_type="pre_workout")
        assert result["meal_type"] == "pre_workout"
        assert result["macro_targets"]["carbs"]["percent"] >= 50

    def test_compose_post_workout(self):
        """Comida post-entreno debe tener proteína alta."""
        result = compose_meal(target_calories=500, meal_type="post_workout")
        assert result["macro_targets"]["protein"]["percent"] >= 30

    def test_compose_low_carb(self):
        """Comida low carb debe tener pocos carbos."""
        result = compose_meal(target_calories=500, meal_type="low_carb")
        assert result["macro_targets"]["carbs"]["percent"] <= 20

    def test_compose_with_target_protein(self):
        """Debe respetar proteína objetivo."""
        result = compose_meal(target_calories=500, target_protein_g=40)
        assert result["macro_targets"]["protein"]["grams"] == 40

    def test_includes_suggested_foods(self):
        """Debe incluir alimentos sugeridos."""
        result = compose_meal(target_calories=500)
        assert "suggested_foods" in result
        assert "protein_sources" in result["suggested_foods"]
        assert "carb_sources" in result["suggested_foods"]

    def test_includes_portion_guide(self):
        """Debe incluir guía de porciones."""
        result = compose_meal(target_calories=500)
        assert "portion_guide" in result

    def test_vegan_options(self):
        """Debe adaptar para veganos."""
        result = compose_meal(
            target_calories=500,
            dietary_restrictions=["vegano"],
        )
        # Proteínas deben ser veganas
        protein_sources = result["suggested_foods"]["protein_sources"]
        assert any("tofu" in s.lower() for s in protein_sources)

    def test_invalid_calories_low(self):
        """Debe rechazar calorías muy bajas."""
        result = compose_meal(target_calories=50)
        assert result["status"] == "error"

    def test_invalid_calories_high(self):
        """Debe rechazar calorías muy altas."""
        result = compose_meal(target_calories=3000)
        assert result["status"] == "error"

    def test_invalid_meal_type_defaults(self):
        """Tipo inválido debe usar balanced."""
        result = compose_meal(target_calories=500, meal_type="invalid_type")
        assert result["meal_type"] == "balanced"

    def test_macros_sum_to_calories(self):
        """Macros deben sumar las calorías."""
        result = compose_meal(target_calories=500)
        total = (
            result["macro_targets"]["protein"]["calories"]
            + result["macro_targets"]["carbs"]["calories"]
            + result["macro_targets"]["fat"]["calories"]
        )
        assert abs(total - 500) < 20


class TestMacroRatiosIntegrity:
    """Tests para integridad de MACRO_RATIOS."""

    def test_all_goals_have_required_fields(self):
        """Todos los objetivos deben tener campos requeridos."""
        required_approaches = ["standard"]
        for goal_id, goal_data in MACRO_RATIOS.items():
            if goal_id in ["name_es", "description"]:
                continue
            for approach in required_approaches:
                if approach in goal_data:
                    ratios = goal_data[approach]
                    assert "protein" in ratios
                    assert "carbs" in ratios
                    assert "fat" in ratios

    def test_ratios_sum_to_one(self):
        """Proporciones deben sumar 1.0."""
        for goal_id, goal_data in MACRO_RATIOS.items():
            for key, value in goal_data.items():
                if isinstance(value, dict) and "protein" in value:
                    total = value["protein"] + value["carbs"] + value["fat"]
                    assert abs(total - 1.0) < 0.01, f"Ratios en {goal_id}.{key} no suman 1.0"

    def test_expected_goals_exist(self):
        """Deben existir objetivos esperados."""
        expected = ["fat_loss", "maintenance", "muscle_gain", "recomp", "performance"]
        for goal in expected:
            assert goal in MACRO_RATIOS


class TestProteinTargetsIntegrity:
    """Tests para integridad de PROTEIN_TARGETS."""

    def test_all_levels_have_required_fields(self):
        """Todos los niveles deben tener campos requeridos."""
        required_fields = ["g_per_kg", "name_es", "description"]
        for level_id, level_data in PROTEIN_TARGETS.items():
            for field in required_fields:
                assert field in level_data, f"Nivel {level_id} falta campo {field}"

    def test_g_per_kg_valid_range(self):
        """g_per_kg debe estar en rango válido."""
        for level_id, level_data in PROTEIN_TARGETS.items():
            g_per_kg = level_data["g_per_kg"]
            assert 0.5 <= g_per_kg <= 3.0, f"g_per_kg inválido en {level_id}"

    def test_expected_levels_exist(self):
        """Deben existir niveles esperados."""
        expected = ["sedentary", "light", "moderate", "strength", "endurance"]
        for level in expected:
            assert level in PROTEIN_TARGETS


class TestCarbCyclingPatternsIntegrity:
    """Tests para integridad de CARB_CYCLING_PATTERNS."""

    def test_all_patterns_have_required_fields(self):
        """Todos los patrones deben tener campos requeridos."""
        required_fields = ["pattern", "name_es", "description", "high_multiplier", "low_multiplier"]
        for pattern_id, pattern_data in CARB_CYCLING_PATTERNS.items():
            for field in required_fields:
                assert field in pattern_data, f"Patrón {pattern_id} falta campo {field}"

    def test_multipliers_valid(self):
        """Multiplicadores deben ser válidos."""
        for pattern_id, pattern_data in CARB_CYCLING_PATTERNS.items():
            assert pattern_data["high_multiplier"] > 1.0
            assert pattern_data["low_multiplier"] < 1.0

    def test_expected_patterns_exist(self):
        """Deben existir patrones esperados."""
        expected = ["classic_3day", "training_based", "alternating"]
        for pattern in expected:
            assert pattern in CARB_CYCLING_PATTERNS


class TestFatDistributionIntegrity:
    """Tests para integridad de FAT_DISTRIBUTION."""

    def test_all_types_have_required_fields(self):
        """Todos los tipos deben tener campos requeridos."""
        required_fields = ["name_es", "description"]
        for type_id, type_data in FAT_DISTRIBUTION.items():
            for field in required_fields:
                assert field in type_data, f"Tipo {type_id} falta campo {field}"

    def test_expected_types_exist(self):
        """Deben existir tipos esperados."""
        expected = ["saturated", "monounsaturated", "polyunsaturated", "omega3", "trans"]
        for fat_type in expected:
            assert fat_type in FAT_DISTRIBUTION


class TestMealTemplatesIntegrity:
    """Tests para integridad de MEAL_TEMPLATES."""

    def test_all_templates_have_required_fields(self):
        """Todos los templates deben tener campos requeridos."""
        required_fields = ["ratios", "name_es", "description"]
        for template_id, template_data in MEAL_TEMPLATES.items():
            for field in required_fields:
                assert field in template_data, f"Template {template_id} falta campo {field}"

    def test_ratios_sum_to_one(self):
        """Ratios deben sumar 1.0."""
        for template_id, template_data in MEAL_TEMPLATES.items():
            ratios = template_data["ratios"]
            total = ratios["protein"] + ratios["carbs"] + ratios["fat"]
            assert abs(total - 1.0) < 0.01, f"Ratios en {template_id} no suman 1.0"

    def test_expected_templates_exist(self):
        """Deben existir templates esperados."""
        expected = ["balanced", "pre_workout", "post_workout", "high_protein", "low_carb"]
        for template in expected:
            assert template in MEAL_TEMPLATES


class TestProteinSourcesIntegrity:
    """Tests para integridad de PROTEIN_SOURCES."""

    def test_all_sources_have_required_fields(self):
        """Todas las fuentes deben tener campos requeridos."""
        required_fields = ["protein_per_100g", "calories_per_100g", "name_es"]
        for source_id, source_data in PROTEIN_SOURCES.items():
            for field in required_fields:
                assert field in source_data, f"Fuente {source_id} falta campo {field}"

    def test_protein_values_valid(self):
        """Valores de proteína deben ser válidos."""
        for source_id, source_data in PROTEIN_SOURCES.items():
            protein = source_data["protein_per_100g"]
            assert 0 <= protein <= 100, f"Proteína inválida en {source_id}"

    def test_expected_sources_exist(self):
        """Deben existir fuentes esperadas."""
        expected = ["chicken_breast", "salmon", "eggs", "greek_yogurt"]
        for source in expected:
            assert source in PROTEIN_SOURCES
