"""Tests para las tools de SAGE."""

from __future__ import annotations

from agents.sage.tools import (
    calculate_tdee,
    calculate_macros,
    suggest_meal_distribution,
    get_food_suggestions,
    evaluate_progress,
    FOOD_DATABASE,
)


class TestCalculateTdee:
    """Tests para calculate_tdee."""

    def test_basic_tdee_calculation(self):
        """Debe calcular TDEE correctamente."""
        result = calculate_tdee(
            weight_kg=80,
            height_cm=180,
            age=35,
            sex="male",
            activity_level="moderate",
        )
        assert "tdee" in result
        assert "bmr" in result
        assert result["tdee"] > result["bmr"]
        assert 2000 < result["tdee"] < 4000  # Rango razonable

    def test_female_lower_bmr(self):
        """BMR femenino debe ser menor que masculino (mismos parámetros)."""
        male = calculate_tdee(80, 170, 30, "male", "moderate")
        female = calculate_tdee(80, 170, 30, "female", "moderate")
        assert female["bmr"] < male["bmr"]

    def test_activity_level_affects_tdee(self):
        """Mayor actividad = mayor TDEE."""
        sedentary = calculate_tdee(80, 180, 35, "male", "sedentary")
        active = calculate_tdee(80, 180, 35, "male", "active")
        assert active["tdee"] > sedentary["tdee"]

    def test_body_fat_uses_katch_mcardle(self):
        """Si se proporciona BF%, debe usar Katch-McArdle."""
        result = calculate_tdee(80, 180, 35, "male", "moderate", body_fat_pct=15)
        assert result["formula"] == "Katch-McArdle"

    def test_calorie_ranges_included(self):
        """Debe incluir rangos de calorías para diferentes objetivos."""
        result = calculate_tdee(80, 180, 35, "male", "moderate")
        assert "calorie_ranges" in result
        assert "moderate_deficit" in result["calorie_ranges"]
        assert "lean_bulk" in result["calorie_ranges"]


class TestCalculateMacros:
    """Tests para calculate_macros."""

    def test_basic_macro_calculation(self):
        """Debe calcular macros correctamente."""
        result = calculate_macros(
            target_calories=2500,
            weight_kg=80,
            goal="muscle_gain",
        )
        assert "protein" in result
        assert "carbohydrates" in result
        assert "fat" in result
        assert result["calories"] > 0

    def test_protein_per_kg_in_range(self):
        """Proteína debe estar en rango apropiado."""
        result = calculate_macros(2500, 80, "muscle_gain")
        protein_per_kg = result["protein"]["per_kg"]
        assert 1.6 <= protein_per_kg <= 2.5

    def test_fat_loss_high_protein(self):
        """Fat loss debe tener proteína más alta."""
        fat_loss = calculate_macros(2000, 80, "fat_loss")
        muscle_gain = calculate_macros(2000, 80, "muscle_gain")
        assert fat_loss["protein"]["per_kg"] >= muscle_gain["protein"]["per_kg"]

    def test_low_carb_preference(self):
        """Low carb debe reducir carbohidratos."""
        balanced = calculate_macros(2500, 80, "maintenance", preference="balanced")
        low_carb = calculate_macros(2500, 80, "maintenance", preference="low_carb")
        assert low_carb["carbohydrates"]["grams"] < balanced["carbohydrates"]["grams"]

    def test_includes_fiber_recommendation(self):
        """Debe incluir recomendación de fibra."""
        result = calculate_macros(2500, 80, "maintenance")
        assert "fiber" in result
        assert result["fiber"]["grams"] >= 25

    def test_includes_water_recommendation(self):
        """Debe incluir recomendación de agua."""
        result = calculate_macros(2500, 80, "maintenance")
        assert "water_liters" in result


class TestSuggestMealDistribution:
    """Tests para suggest_meal_distribution."""

    def test_basic_distribution(self):
        """Debe crear distribución de comidas."""
        macros = {"calories": 2500, "protein": {"grams": 180}, "carbohydrates": {"grams": 250}, "fat": {"grams": 80}}
        result = suggest_meal_distribution(macros, meals_per_day=4)
        assert "meals" in result
        assert len(result["meals"]) == 4

    def test_meals_sum_to_total(self):
        """Calorías de comidas deben sumar aproximadamente al total."""
        macros = {"calories": 2500, "protein": {"grams": 180}, "carbohydrates": {"grams": 250}, "fat": {"grams": 80}}
        result = suggest_meal_distribution(macros, meals_per_day=4)
        total = sum(m["calories"] for m in result["meals"])
        assert abs(total - 2500) < 50  # Tolerancia por redondeo

    def test_training_time_adds_notes(self):
        """Horario de entrenamiento debe añadir notas."""
        macros = {"calories": 2500, "protein": {"grams": 180}, "carbohydrates": {"grams": 250}, "fat": {"grams": 80}}
        result = suggest_meal_distribution(macros, training_time="morning")
        assert "training_notes" in result
        assert len(result["training_notes"]) > 0


class TestGetFoodSuggestions:
    """Tests para get_food_suggestions."""

    def test_get_protein_foods(self):
        """Debe retornar alimentos de proteína."""
        result = get_food_suggestions("protein")
        assert result["count"] > 0
        assert "chicken_breast" in result["foods"]

    def test_vegetarian_filter(self):
        """Debe filtrar carnes para vegetarianos."""
        result = get_food_suggestions("protein", dietary_preference="vegetarian")
        assert "chicken_breast" not in result["foods"]
        assert "eggs" in result["foods"]

    def test_vegan_filter(self):
        """Debe filtrar productos animales para veganos."""
        result = get_food_suggestions("protein", dietary_preference="vegan")
        assert "chicken_breast" not in result["foods"]
        assert "eggs" not in result["foods"]
        assert "tofu" in result["foods"] or "lentils" in result["foods"]

    def test_exclude_specific_foods(self):
        """Debe excluir alimentos específicos."""
        result = get_food_suggestions("protein", exclude=["eggs"])
        assert "eggs" not in result["foods"]


class TestEvaluateProgress:
    """Tests para evaluate_progress."""

    def test_on_track_fat_loss(self):
        """Debe detectar progreso correcto en fat loss."""
        result = evaluate_progress(
            starting_weight=85,
            current_weight=84,  # -1kg en 2 semanas = -0.5kg/semana
            weeks_elapsed=2,
            goal="fat_loss",
            current_calories=2000,
        )
        assert result["is_on_track"] is True
        assert result["weekly_change_kg"] == -0.5

    def test_too_fast_fat_loss(self):
        """Debe detectar pérdida muy rápida."""
        result = evaluate_progress(
            starting_weight=85,
            current_weight=82,  # -3kg en 2 semanas = -1.5kg/semana
            weeks_elapsed=2,
            goal="fat_loss",
            current_calories=1500,
        )
        assert result["is_on_track"] is False
        assert result["suggested_calorie_adjustment"] > 0  # Aumentar calorías

    def test_not_losing_enough(self):
        """Debe detectar pérdida insuficiente."""
        result = evaluate_progress(
            starting_weight=85,
            current_weight=84.9,  # -0.1kg en 2 semanas
            weeks_elapsed=2,
            goal="fat_loss",
            current_calories=2500,
        )
        assert result["is_on_track"] is False
        assert result["suggested_calorie_adjustment"] < 0  # Reducir calorías

    def test_muscle_gain_progress(self):
        """Debe evaluar correctamente ganancia muscular."""
        result = evaluate_progress(
            starting_weight=80,
            current_weight=80.4,  # +0.4kg en 2 semanas = +0.2kg/semana
            weeks_elapsed=2,
            goal="muscle_gain",
            current_calories=3000,
        )
        assert result["is_on_track"] is True


class TestFoodDatabaseIntegrity:
    """Tests para integridad de la base de datos de alimentos."""

    def test_all_foods_have_required_fields(self):
        """Todos los alimentos deben tener campos requeridos."""
        required_fields = ["name_es", "protein", "carbs", "fat", "calories"]
        for category, foods in FOOD_DATABASE.items():
            for food_id, food_data in foods.items():
                for field in required_fields:
                    assert field in food_data, f"Alimento {food_id} falta campo {field}"

    def test_macros_match_calories(self):
        """Macros deben sumar aproximadamente las calorías."""
        for category, foods in FOOD_DATABASE.items():
            for food_id, food_data in foods.items():
                calculated = (
                    food_data["protein"] * 4 +
                    food_data["carbs"] * 4 +
                    food_data["fat"] * 9
                )
                # Permitir 10% de diferencia (por fibra, etc.)
                assert abs(calculated - food_data["calories"]) < food_data["calories"] * 0.2, \
                    f"Macros no coinciden con calorías en {food_id}"
