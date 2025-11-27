"""Tests para las tools de ATLAS."""

from __future__ import annotations

from agents.atlas.tools import (
    get_mobility_exercises,
    assess_mobility,
    generate_mobility_routine,
    suggest_mobility_for_workout,
    MOBILITY_EXERCISES,
    ROUTINE_TEMPLATES,
)


class TestMobilityExerciseDatabase:
    """Tests para get_mobility_exercises."""

    def test_get_all_exercises(self):
        """Debe retornar todos los ejercicios sin filtros."""
        result = get_mobility_exercises()
        assert result["count"] > 0
        assert "exercises" in result

    def test_filter_by_joint(self):
        """Debe filtrar por articulacion."""
        result = get_mobility_exercises(joint="hip")
        assert result["count"] > 0
        for ex_data in result["exercises"].values():
            assert ex_data["joint"] == "hip"

    def test_filter_by_shoulder(self):
        """Debe filtrar ejercicios de hombro."""
        result = get_mobility_exercises(joint="shoulder")
        assert result["count"] > 0
        for ex_data in result["exercises"].values():
            assert ex_data["joint"] == "shoulder"

    def test_filter_by_type(self):
        """Debe filtrar por tipo de ejercicio."""
        result = get_mobility_exercises(exercise_type="mobility")
        assert result["count"] > 0
        for ex_data in result["exercises"].values():
            assert ex_data["type"] == "mobility"

    def test_filter_by_flexibility_type(self):
        """Debe filtrar ejercicios de flexibilidad."""
        result = get_mobility_exercises(exercise_type="flexibility")
        assert result["count"] > 0
        for ex_data in result["exercises"].values():
            assert ex_data["type"] == "flexibility"

    def test_filter_by_max_difficulty(self):
        """Debe filtrar por dificultad maxima."""
        result = get_mobility_exercises(max_difficulty=1)
        assert result["count"] > 0
        for ex_data in result["exercises"].values():
            assert ex_data["difficulty"] <= 1

    def test_combined_filters(self):
        """Debe aplicar multiples filtros."""
        result = get_mobility_exercises(
            joint="hip",
            exercise_type="mobility",
            max_difficulty=2,
        )
        assert result["count"] >= 1
        for ex_data in result["exercises"].values():
            assert ex_data["joint"] == "hip"
            assert ex_data["type"] == "mobility"
            assert ex_data["difficulty"] <= 2


class TestAssessMobility:
    """Tests para assess_mobility."""

    def test_excellent_mobility(self):
        """Debe retornar excellent para scores altos."""
        result = assess_mobility(
            overhead_reach=5,
            deep_squat=5,
            hip_hinge=5,
            thoracic_rotation=5,
        )
        assert result["category"] == "excellent"
        assert result["overall_score"] == 5.0
        assert len(result["priority_areas"]) == 0

    def test_needs_work_mobility(self):
        """Debe retornar needs_work para scores bajos."""
        result = assess_mobility(
            overhead_reach=1,
            deep_squat=1,
            hip_hinge=1,
            thoracic_rotation=1,
        )
        assert result["category"] == "needs_work"
        assert result["overall_score"] == 1.0
        assert len(result["priority_areas"]) > 0

    def test_mixed_scores(self):
        """Debe manejar scores mixtos correctamente."""
        result = assess_mobility(
            overhead_reach=5,
            deep_squat=2,
            hip_hinge=4,
            thoracic_rotation=3,
        )
        # Score promedio es 3.5, categoria good
        assert result["category"] == "good"
        # Debe identificar deep_squat como area prioritaria
        priority_joints = [a["joint"] for a in result["priority_areas"]]
        assert "hip" in priority_joints

    def test_recommendations_included(self):
        """Debe incluir recomendaciones."""
        result = assess_mobility(
            overhead_reach=2,
            deep_squat=3,
            hip_hinge=3,
            thoracic_rotation=2,
        )
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0

    def test_assessments_structure(self):
        """Debe incluir estructura de assessments."""
        result = assess_mobility(
            overhead_reach=3,
            deep_squat=3,
            hip_hinge=3,
            thoracic_rotation=3,
        )
        assert "assessments" in result
        assert len(result["assessments"]) == 4
        for assessment in result["assessments"]:
            assert "joint" in assessment
            assert "score" in assessment
            assert "notes" in assessment
            assert "priority" in assessment


class TestGenerateMobilityRoutine:
    """Tests para generate_mobility_routine."""

    def test_full_body_routine(self):
        """Debe generar rutina full body."""
        result = generate_mobility_routine(focus="full_body")
        assert result["focus"] == "full_body"
        assert "exercises" in result
        assert len(result["exercises"]) > 0

    def test_hip_focus_routine(self):
        """Debe generar rutina enfocada en cadera."""
        result = generate_mobility_routine(focus="hip_focus")
        assert result["focus"] == "hip_focus"
        # Debe tener ejercicios de cadera
        joints = [ex["joint"] for ex in result["exercises"]]
        assert "hip" in joints

    def test_shoulder_focus_routine(self):
        """Debe generar rutina enfocada en hombro."""
        result = generate_mobility_routine(focus="shoulder_focus")
        assert result["focus"] == "shoulder_focus"
        joints = [ex["joint"] for ex in result["exercises"]]
        assert "shoulder" in joints

    def test_warmup_routine(self):
        """Debe generar rutina de calentamiento."""
        result = generate_mobility_routine(focus="warmup")
        assert result["focus"] == "warmup"
        assert "exercises" in result

    def test_desk_worker_routine(self):
        """Debe generar rutina para trabajador de oficina."""
        result = generate_mobility_routine(focus="desk_worker")
        assert result["focus"] == "desk_worker"
        assert "exercises" in result

    def test_routine_includes_cues(self):
        """Rutina debe incluir cues de ejecucion."""
        result = generate_mobility_routine(focus="full_body")
        for ex in result["exercises"]:
            assert "cues" in ex
            assert len(ex["cues"]) > 0

    def test_routine_includes_notes(self):
        """Rutina debe incluir notas."""
        result = generate_mobility_routine(focus="full_body")
        assert "notes" in result
        assert len(result["notes"]) > 0

    def test_invalid_focus_defaults_to_full_body(self):
        """Focus invalido debe defaultear a full_body."""
        result = generate_mobility_routine(focus="invalid_focus")
        assert "exercises" in result
        assert len(result["exercises"]) > 0


class TestSuggestMobilityForWorkout:
    """Tests para suggest_mobility_for_workout."""

    def test_push_workout_mobility(self):
        """Debe sugerir movilidad para push."""
        result = suggest_mobility_for_workout(
            workout_type="push",
            muscle_groups=["chest", "shoulders"],
        )
        assert result["workout_type"] == "push"
        assert "warmup" in result
        assert "cooldown" in result
        assert len(result["warmup"]["exercises"]) > 0

    def test_pull_workout_mobility(self):
        """Debe sugerir movilidad para pull."""
        result = suggest_mobility_for_workout(
            workout_type="pull",
            muscle_groups=["back", "lats"],
        )
        assert result["workout_type"] == "pull"
        assert "warmup" in result
        assert "cooldown" in result

    def test_legs_workout_mobility(self):
        """Debe sugerir movilidad para legs."""
        result = suggest_mobility_for_workout(
            workout_type="legs",
            muscle_groups=["quads", "hamstrings", "glutes"],
        )
        assert result["workout_type"] == "legs"
        assert "hip" in result["target_joints"]

    def test_full_body_workout_mobility(self):
        """Debe sugerir movilidad para full body."""
        result = suggest_mobility_for_workout(
            workout_type="full_body",
            muscle_groups=["chest", "back", "quads"],
        )
        assert result["workout_type"] == "full_body"
        assert len(result["warmup"]["exercises"]) > 0
        assert len(result["cooldown"]["exercises"]) > 0

    def test_includes_duration(self):
        """Debe incluir duracion estimada."""
        result = suggest_mobility_for_workout(
            workout_type="push",
            muscle_groups=["chest"],
        )
        assert result["warmup"]["duration_minutes"] > 0
        assert result["cooldown"]["duration_minutes"] > 0

    def test_includes_notes(self):
        """Debe incluir notas."""
        result = suggest_mobility_for_workout(
            workout_type="legs",
            muscle_groups=["quads"],
        )
        assert "notes" in result
        assert len(result["notes"]) > 0


class TestMobilityExerciseDatabaseIntegrity:
    """Tests para integridad de la base de datos de ejercicios."""

    def test_all_exercises_have_required_fields(self):
        """Todos los ejercicios deben tener campos requeridos."""
        required_fields = ["name_es", "joint", "type", "cues", "targets", "difficulty"]
        for ex_id, ex_data in MOBILITY_EXERCISES.items():
            for field in required_fields:
                assert field in ex_data, f"Ejercicio {ex_id} falta campo {field}"

    def test_all_exercises_have_duration_or_reps(self):
        """Todos los ejercicios deben tener duration_seconds o reps."""
        for ex_id, ex_data in MOBILITY_EXERCISES.items():
            has_duration = ex_data.get("duration_seconds") is not None
            has_reps = ex_data.get("reps") is not None
            assert has_duration or has_reps, f"Ejercicio {ex_id} sin duration ni reps"

    def test_valid_joints(self):
        """Todos los joints deben ser validos."""
        valid_joints = {"shoulder", "hip", "spine", "ankle"}
        for ex_id, ex_data in MOBILITY_EXERCISES.items():
            assert ex_data["joint"] in valid_joints, f"Joint invalido en {ex_id}"

    def test_valid_types(self):
        """Todos los tipos deben ser validos."""
        valid_types = {"mobility", "flexibility"}
        for ex_id, ex_data in MOBILITY_EXERCISES.items():
            assert ex_data["type"] in valid_types, f"Tipo invalido en {ex_id}"

    def test_difficulty_in_range(self):
        """Dificultad debe estar entre 1 y 3."""
        for ex_id, ex_data in MOBILITY_EXERCISES.items():
            assert 1 <= ex_data["difficulty"] <= 3, f"Dificultad invalida en {ex_id}"


class TestRoutineTemplatesIntegrity:
    """Tests para integridad de las plantillas de rutinas."""

    def test_all_templates_have_required_fields(self):
        """Todas las plantillas deben tener campos requeridos."""
        required_fields = ["name_es", "duration_minutes", "exercises", "description"]
        for template_id, template_data in ROUTINE_TEMPLATES.items():
            for field in required_fields:
                assert field in template_data, f"Template {template_id} falta campo {field}"

    def test_all_template_exercises_exist(self):
        """Todos los ejercicios referenciados deben existir."""
        for template_id, template_data in ROUTINE_TEMPLATES.items():
            for ex_id in template_data["exercises"]:
                assert ex_id in MOBILITY_EXERCISES, f"Ejercicio {ex_id} no existe (template {template_id})"

    def test_template_durations_positive(self):
        """Todas las duraciones deben ser positivas."""
        for template_id, template_data in ROUTINE_TEMPLATES.items():
            assert template_data["duration_minutes"] > 0, f"Duracion invalida en {template_id}"
