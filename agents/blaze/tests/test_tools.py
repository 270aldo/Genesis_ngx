"""Tests para las tools de BLAZE."""

from __future__ import annotations

from agents.blaze.tools import (
    get_exercise_database,
    calculate_one_rep_max,
    calculate_training_volume,
    suggest_progression,
    generate_workout_split,
    MuscleGroup,
    EXERCISE_DATABASE,
)


class TestExerciseDatabase:
    """Tests para get_exercise_database."""

    def test_get_all_exercises(self):
        """Debe retornar todos los ejercicios sin filtros."""
        result = get_exercise_database()
        assert result["count"] > 0
        assert "exercises" in result

    def test_filter_by_muscle_group(self):
        """Debe filtrar por grupo muscular."""
        result = get_exercise_database(muscle_group="chest")
        assert result["count"] > 0
        for ex_data in result["exercises"].values():
            assert "chest" in ex_data["muscle_groups"]

    def test_filter_by_equipment(self):
        """Debe filtrar por equipo."""
        result = get_exercise_database(equipment="barbell")
        assert result["count"] > 0
        for ex_data in result["exercises"].values():
            assert "barbell" in ex_data["equipment"]

    def test_filter_by_type(self):
        """Debe filtrar por tipo de ejercicio."""
        result = get_exercise_database(exercise_type="compound")
        assert result["count"] > 0
        for ex_data in result["exercises"].values():
            assert ex_data["type"] == "compound"

    def test_combined_filters(self):
        """Debe aplicar múltiples filtros."""
        result = get_exercise_database(
            muscle_group="chest",
            equipment="barbell",
            exercise_type="compound",
        )
        assert result["count"] >= 1
        assert "bench_press" in result["exercises"]


class TestCalculateOneRepMax:
    """Tests para calculate_one_rep_max."""

    def test_single_rep_returns_same_weight(self):
        """1 rep debe retornar el mismo peso."""
        result = calculate_one_rep_max(weight_kg=100, reps=1)
        assert result["estimated_1rm_kg"] == 100

    def test_multiple_reps_increases_estimate(self):
        """Múltiples reps deben estimar 1RM mayor."""
        result = calculate_one_rep_max(weight_kg=100, reps=10)
        assert result["estimated_1rm_kg"] > 100

    def test_percentage_table_included(self):
        """Debe incluir tabla de porcentajes."""
        result = calculate_one_rep_max(weight_kg=100, reps=5)
        assert "percentage_table" in result
        assert "100%" in result["percentage_table"]
        assert "80%" in result["percentage_table"]

    def test_invalid_reps_returns_error(self):
        """Debe retornar error para reps inválidos."""
        result = calculate_one_rep_max(weight_kg=100, reps=20)
        assert "error" in result

    def test_different_formulas(self):
        """Debe soportar diferentes fórmulas."""
        brzycki = calculate_one_rep_max(weight_kg=100, reps=5, formula="brzycki")
        epley = calculate_one_rep_max(weight_kg=100, reps=5, formula="epley")
        # Diferentes fórmulas dan resultados ligeramente diferentes
        assert brzycki["estimated_1rm_kg"] != epley["estimated_1rm_kg"]


class TestCalculateTrainingVolume:
    """Tests para calculate_training_volume."""

    def test_basic_volume_calculation(self):
        """Debe calcular volumen correctamente."""
        exercises = [
            {"name": "bench_press", "sets": 4, "reps": 8, "weight_kg": 80},
        ]
        result = calculate_training_volume(exercises)
        expected_volume = 4 * 8 * 80
        assert result["total_volume_kg"] == expected_volume
        assert result["total_sets"] == 4

    def test_volume_by_muscle_group(self):
        """Debe desglosar volumen por grupo muscular."""
        exercises = [
            {"name": "bench_press", "sets": 4, "reps": 8, "weight_kg": 80},
            {"name": "lat_pulldown", "sets": 3, "reps": 10, "weight_kg": 60},
        ]
        result = calculate_training_volume(exercises)
        assert "volume_by_muscle_group" in result
        assert "sets_by_muscle_group" in result

    def test_empty_exercises(self):
        """Debe manejar lista vacía."""
        result = calculate_training_volume([])
        assert result["total_volume_kg"] == 0
        assert result["total_sets"] == 0


class TestSuggestProgression:
    """Tests para suggest_progression."""

    def test_ready_to_progress(self):
        """Debe recomendar progresión cuando está listo."""
        result = suggest_progression(
            current_weight_kg=80,
            current_reps=12,  # Top del rango
            target_reps_min=8,
            target_reps_max=12,
            rpe_last_set=7,  # RPE manejable
            weeks_at_current=2,
        )
        assert result["ready_to_progress"] is True
        assert result["progression_type"] == "weight_increase"
        assert result["new_weight_kg"] > 80

    def test_maintain_when_below_range(self):
        """Debe recomendar mantener cuando no alcanza rango."""
        result = suggest_progression(
            current_weight_kg=80,
            current_reps=6,  # Debajo del mínimo
            target_reps_min=8,
            target_reps_max=12,
            rpe_last_set=9,
        )
        assert result["ready_to_progress"] is False
        assert result["progression_type"] == "maintain"

    def test_maintain_when_rpe_too_high(self):
        """Debe recomendar mantener cuando RPE es muy alto."""
        result = suggest_progression(
            current_weight_kg=80,
            current_reps=12,
            target_reps_min=8,
            target_reps_max=12,
            rpe_last_set=10,  # RPE máximo
        )
        assert result["ready_to_progress"] is False

    def test_rep_increase_in_middle_of_range(self):
        """Debe recomendar más reps cuando está en medio del rango."""
        result = suggest_progression(
            current_weight_kg=80,
            current_reps=10,  # Medio del rango
            target_reps_min=8,
            target_reps_max=12,
            rpe_last_set=7,
        )
        assert result["progression_type"] == "rep_increase"


class TestGenerateWorkoutSplit:
    """Tests para generate_workout_split."""

    def test_3_day_beginner(self):
        """Debe recomendar full body para principiante 3 días."""
        result = generate_workout_split(
            days_per_week=3,
            experience_level="beginner",
            primary_goal="hypertrophy",
        )
        assert result["split_name"] == "Full Body"
        assert result["days_required"] == 3

    def test_3_day_intermediate(self):
        """Debe recomendar PPL para intermedio 3 días."""
        result = generate_workout_split(
            days_per_week=3,
            experience_level="intermediate",
            primary_goal="hypertrophy",
        )
        assert result["split_name"] == "Push/Pull/Legs"

    def test_4_day_split(self):
        """Debe recomendar Upper/Lower para 4 días."""
        result = generate_workout_split(
            days_per_week=4,
            experience_level="intermediate",
            primary_goal="strength",
        )
        assert result["split_name"] == "Upper/Lower"
        assert result["days_required"] == 4

    def test_6_day_split(self):
        """Debe recomendar PPL 2x para 6 días."""
        result = generate_workout_split(
            days_per_week=6,
            experience_level="advanced",
            primary_goal="hypertrophy",
        )
        assert "2x" in result["split_name"]

    def test_includes_volume_recommendation(self):
        """Debe incluir recomendación de volumen."""
        result = generate_workout_split(
            days_per_week=4,
            experience_level="intermediate",
            primary_goal="hypertrophy",
        )
        assert "volume_recommendation" in result
        assert "hipertrofia" in result["volume_recommendation"].lower()


class TestExerciseDatabaseIntegrity:
    """Tests para integridad de la base de datos de ejercicios."""

    def test_all_exercises_have_required_fields(self):
        """Todos los ejercicios deben tener campos requeridos."""
        required_fields = ["name", "name_es", "muscle_groups", "type", "equipment", "difficulty", "cues"]
        for ex_id, ex_data in EXERCISE_DATABASE.items():
            for field in required_fields:
                assert field in ex_data, f"Ejercicio {ex_id} falta campo {field}"

    def test_all_muscle_groups_valid(self):
        """Todos los grupos musculares deben ser válidos."""
        valid_groups = {mg.value for mg in MuscleGroup}
        for ex_id, ex_data in EXERCISE_DATABASE.items():
            for mg in ex_data["muscle_groups"]:
                assert mg.value in valid_groups, f"Grupo muscular inválido en {ex_id}"

    def test_difficulty_in_range(self):
        """Dificultad debe estar entre 1 y 5."""
        for ex_id, ex_data in EXERCISE_DATABASE.items():
            assert 1 <= ex_data["difficulty"] <= 5, f"Dificultad inválida en {ex_id}"
