"""Tests para las tools de LUNA."""

from __future__ import annotations

from datetime import datetime, timedelta

from agents.luna.tools import (
    track_cycle,
    get_phase_recommendations,
    analyze_symptoms,
    create_cycle_plan,
    assess_hormonal_health,
    CYCLE_PHASES,
    SYMPTOMS_DATABASE,
    TRAINING_BY_PHASE,
    NUTRITION_BY_PHASE,
    PERIMENOPAUSE_INFO,
)


class TestTrackCycle:
    """Tests para track_cycle."""

    def test_track_basic_cycle(self):
        """Debe trackear ciclo básico."""
        today = datetime.now()
        last_period = (today - timedelta(days=10)).strftime("%Y-%m-%d")

        result = track_cycle(last_period_start=last_period)
        assert result["status"] == "tracked"
        assert "current_phase" in result

    def test_track_returns_cycle_day(self):
        """Debe retornar día del ciclo."""
        today = datetime.now()
        last_period = (today - timedelta(days=15)).strftime("%Y-%m-%d")

        result = track_cycle(last_period_start=last_period)
        assert result["cycle_day"] == 16  # 15 + 1

    def test_track_menstrual_phase(self):
        """Debe detectar fase menstrual correctamente."""
        today = datetime.now()
        last_period = (today - timedelta(days=2)).strftime("%Y-%m-%d")

        result = track_cycle(last_period_start=last_period)
        assert result["current_phase"] == "menstrual"

    def test_track_follicular_phase(self):
        """Debe detectar fase folicular correctamente."""
        today = datetime.now()
        last_period = (today - timedelta(days=8)).strftime("%Y-%m-%d")

        result = track_cycle(last_period_start=last_period)
        assert result["current_phase"] == "follicular"

    def test_track_ovulatory_phase(self):
        """Debe detectar fase ovulatoria correctamente."""
        today = datetime.now()
        last_period = (today - timedelta(days=13)).strftime("%Y-%m-%d")

        result = track_cycle(last_period_start=last_period)
        assert result["current_phase"] == "ovulatory"

    def test_track_luteal_phase(self):
        """Debe detectar fase lútea correctamente."""
        today = datetime.now()
        last_period = (today - timedelta(days=20)).strftime("%Y-%m-%d")

        result = track_cycle(last_period_start=last_period)
        assert result["current_phase"] == "luteal"

    def test_track_includes_predictions(self):
        """Debe incluir predicciones."""
        today = datetime.now()
        last_period = (today - timedelta(days=10)).strftime("%Y-%m-%d")

        result = track_cycle(last_period_start=last_period)
        assert "predictions" in result
        assert "next_period" in result["predictions"]
        assert "days_to_next_period" in result["predictions"]

    def test_track_includes_fertile_window_when_no_contraception(self):
        """Debe incluir ventana fértil si no hay anticoncepción."""
        today = datetime.now()
        last_period = (today - timedelta(days=10)).strftime("%Y-%m-%d")

        result = track_cycle(
            last_period_start=last_period,
            contraception="none",
        )
        assert "fertile_window" in result
        assert result["fertile_window"] is not None

    def test_track_no_fertile_window_with_hormonal_contraception(self):
        """No debe incluir ventana fértil con anticoncepción hormonal."""
        today = datetime.now()
        last_period = (today - timedelta(days=10)).strftime("%Y-%m-%d")

        result = track_cycle(
            last_period_start=last_period,
            contraception="hormonal_pill",
        )
        assert result["fertile_window"] is None

    def test_track_invalid_date_format(self):
        """Debe rechazar formato de fecha inválido."""
        result = track_cycle(last_period_start="10-01-2024")
        assert result["status"] == "error"

    def test_track_invalid_cycle_length(self):
        """Debe rechazar ciclo fuera de rango."""
        today = datetime.now()
        last_period = (today - timedelta(days=10)).strftime("%Y-%m-%d")

        result = track_cycle(
            last_period_start=last_period,
            cycle_length=15,  # Muy corto
        )
        assert result["status"] == "error"


class TestGetPhaseRecommendations:
    """Tests para get_phase_recommendations."""

    def test_get_menstrual_recommendations(self):
        """Debe dar recomendaciones para fase menstrual."""
        result = get_phase_recommendations(phase="menstrual")
        assert result["status"] == "recommended"
        assert result["phase"] == "menstrual"

    def test_get_follicular_recommendations(self):
        """Debe dar recomendaciones para fase folicular."""
        result = get_phase_recommendations(phase="follicular")
        assert result["status"] == "recommended"
        assert result["phase"] == "follicular"

    def test_includes_training_recommendations(self):
        """Debe incluir recomendaciones de entrenamiento."""
        result = get_phase_recommendations(phase="ovulatory")
        assert "training_recommendations" in result
        assert "recommended_activities" in result["training_recommendations"]

    def test_includes_nutrition_recommendations(self):
        """Debe incluir recomendaciones de nutrición."""
        result = get_phase_recommendations(phase="luteal")
        assert "nutrition_recommendations" in result
        assert "increase" in result["nutrition_recommendations"]

    def test_includes_intensity_modifier(self):
        """Debe incluir modificador de intensidad."""
        result = get_phase_recommendations(phase="menstrual")
        assert "intensity_modifier" in result["training_recommendations"]
        # Menstrual debería tener intensidad reducida
        assert result["training_recommendations"]["intensity_modifier"] < 1.0

    def test_adjusts_by_energy_level(self):
        """Debe ajustar por nivel de energía."""
        result = get_phase_recommendations(
            phase="follicular",
            energy_today="very_low",
        )
        assert "energy_adjustment" in result

    def test_includes_symptom_strategies(self):
        """Debe incluir estrategias para síntomas."""
        result = get_phase_recommendations(
            phase="luteal",
            has_symptoms=["bloating", "cravings"],
        )
        assert result["symptom_strategies"] is not None
        assert len(result["symptom_strategies"]) > 0

    def test_adjusts_by_goal(self):
        """Debe ajustar por objetivo."""
        result = get_phase_recommendations(
            phase="follicular",
            goal="performance",
        )
        assert "goal_specific_tips" in result

    def test_invalid_phase(self):
        """Debe rechazar fase inválida."""
        result = get_phase_recommendations(phase="invalid")
        assert result["status"] == "error"


class TestAnalyzeSymptoms:
    """Tests para analyze_symptoms."""

    def test_analyze_single_symptom(self):
        """Debe analizar un síntoma."""
        result = analyze_symptoms(symptoms=["cramps"])
        assert result["status"] == "analyzed"
        assert len(result["symptom_analysis"]) == 1

    def test_analyze_multiple_symptoms(self):
        """Debe analizar múltiples síntomas."""
        result = analyze_symptoms(symptoms=["cramps", "fatigue", "bloating"])
        assert result["status"] == "analyzed"
        assert len(result["symptom_analysis"]) == 3

    def test_includes_strategies(self):
        """Debe incluir estrategias para cada síntoma."""
        result = analyze_symptoms(symptoms=["headache"])
        symptom = result["symptom_analysis"][0]
        assert "strategies" in symptom
        assert len(symptom["strategies"]) > 0

    def test_includes_phase_association(self):
        """Debe asociar con fase si se proporciona día del ciclo."""
        result = analyze_symptoms(
            symptoms=["cramps"],
            cycle_day=3,
        )
        assert result["estimated_phase"] == "menstrual"

    def test_flags_severe_symptoms(self):
        """Debe marcar síntomas severos."""
        result = analyze_symptoms(
            symptoms=["cramps"],
            severity="severe",
        )
        assert result["see_doctor_if"] is not None

    def test_handles_recurring_symptoms(self):
        """Debe manejar síntomas recurrentes."""
        result = analyze_symptoms(
            symptoms=["bloating"],
            recurring=True,
        )
        assert result["recurring"] is True
        # Debería recomendar diario de síntomas
        assert any("diario" in r.lower() for r in result["general_recommendations"])

    def test_handles_unknown_symptom(self):
        """Debe manejar síntomas desconocidos."""
        result = analyze_symptoms(symptoms=["sintoma_inventado"])
        assert result["status"] == "analyzed"
        # Debe dar recomendaciones genéricas
        assert len(result["symptom_analysis"][0]["strategies"]) > 0

    def test_includes_disclaimer(self):
        """Debe incluir disclaimer médico."""
        result = analyze_symptoms(symptoms=["fatigue"])
        assert "disclaimer" in result

    def test_invalid_empty_symptoms(self):
        """Debe rechazar lista vacía de síntomas."""
        result = analyze_symptoms(symptoms=[])
        assert result["status"] == "error"


class TestCreateCyclePlan:
    """Tests para create_cycle_plan."""

    def test_create_basic_plan(self):
        """Debe crear plan básico."""
        result = create_cycle_plan()
        assert result["status"] == "created"
        assert "plan_by_phase" in result

    def test_plan_has_all_phases(self):
        """Plan debe tener todas las fases."""
        result = create_cycle_plan()
        phases = result["plan_by_phase"]
        assert "menstrual" in phases
        assert "follicular" in phases
        assert "ovulatory" in phases
        assert "luteal" in phases

    def test_plan_includes_training(self):
        """Plan debe incluir entrenamiento por fase."""
        result = create_cycle_plan()
        for phase_data in result["plan_by_phase"].values():
            assert "training" in phase_data
            assert "focus" in phase_data["training"]

    def test_plan_includes_nutrition(self):
        """Plan debe incluir nutrición por fase."""
        result = create_cycle_plan()
        for phase_data in result["plan_by_phase"].values():
            assert "nutrition" in phase_data
            assert "key_nutrients" in phase_data["nutrition"]

    def test_plan_adapts_to_goal(self):
        """Plan debe adaptarse al objetivo."""
        result = create_cycle_plan(goal="performance")
        assert result["goal"] == "performance"
        # Debería tener tips específicos
        for phase_data in result["plan_by_phase"].values():
            assert "goal_specific" in phase_data

    def test_plan_includes_daily_plan(self):
        """Plan debe incluir plan diario."""
        result = create_cycle_plan()
        for phase_data in result["plan_by_phase"].values():
            assert "daily_plan" in phase_data["training"]

    def test_plan_prepares_for_known_symptoms(self):
        """Plan debe preparar para síntomas conocidos."""
        result = create_cycle_plan(known_symptoms=["cramps", "bloating"])
        # Menstrual debería tener preparación para cramps
        assert result["plan_by_phase"]["menstrual"]["symptom_preparation"] is not None

    def test_plan_includes_principles(self):
        """Plan debe incluir principios generales."""
        result = create_cycle_plan()
        assert "general_principles" in result
        assert len(result["general_principles"]) > 0

    def test_plan_invalid_cycle_length(self):
        """Debe rechazar ciclo fuera de rango."""
        result = create_cycle_plan(cycle_length=15)
        assert result["status"] == "error"


class TestAssessHormonalHealth:
    """Tests para assess_hormonal_health."""

    def test_assess_healthy_signs(self):
        """Debe evaluar signos saludables."""
        result = assess_hormonal_health(
            cycle_regularity="regular",
            period_flow="moderate",
        )
        assert result["status"] == "assessed"
        assert len(result["positive_signs"]) > 0

    def test_assess_flags_irregularity(self):
        """Debe marcar ciclos muy irregulares."""
        result = assess_hormonal_health(
            cycle_regularity="very_irregular",
        )
        assert result["red_flags"] is not None
        assert len(result["red_flags"]) > 0

    def test_assess_flags_heavy_flow(self):
        """Debe marcar flujo muy abundante."""
        result = assess_hormonal_health(
            period_flow="very_heavy",
        )
        assert result["red_flags"] is not None

    def test_assess_calculates_health_score(self):
        """Debe calcular score de salud."""
        result = assess_hormonal_health()
        assert "hormonal_health_score" in result
        assert "score" in result["hormonal_health_score"]

    def test_assess_includes_recommendations(self):
        """Debe incluir recomendaciones."""
        result = assess_hormonal_health()
        assert "recommendations" in result or "general_guidance" in result

    def test_assess_perimenopause_stage(self):
        """Debe manejar etapa de perimenopausia."""
        result = assess_hormonal_health(
            life_stage="perimenopause",
        )
        assert result["life_stage_info"] is not None
        # Debería recomendar fuerza
        assert any("fuerza" in r.lower() for r in result["recommendations"])

    def test_assess_concerning_symptoms(self):
        """Debe evaluar síntomas preocupantes."""
        result = assess_hormonal_health(
            has_concerning_symptoms=["amenorrea"],
        )
        assert result["red_flags"] is not None

    def test_assess_includes_when_to_consult(self):
        """Debe incluir cuándo consultar médico si hay red flags."""
        result = assess_hormonal_health(
            cycle_regularity="very_irregular",
        )
        assert result["when_to_consult_doctor"] is not None

    def test_assess_includes_disclaimer(self):
        """Debe incluir disclaimer."""
        result = assess_hormonal_health()
        assert "disclaimer" in result


class TestCyclePhasesIntegrity:
    """Tests para integridad de CYCLE_PHASES."""

    def test_all_phases_have_required_fields(self):
        """Todas las fases deben tener campos requeridos."""
        required_fields = [
            "name_es", "typical_days", "hormones", "energy",
            "training_focus", "nutrition_focus", "intensity_modifier",
        ]
        for phase_id, phase_data in CYCLE_PHASES.items():
            for field in required_fields:
                assert field in phase_data, f"Fase {phase_id} falta campo {field}"

    def test_expected_phases_exist(self):
        """Deben existir fases esperadas."""
        expected = ["menstrual", "follicular", "ovulatory", "luteal"]
        for phase in expected:
            assert phase in CYCLE_PHASES

    def test_intensity_modifiers_valid(self):
        """Modificadores de intensidad deben ser válidos."""
        for phase_id, phase_data in CYCLE_PHASES.items():
            assert 0 < phase_data["intensity_modifier"] <= 1.5


class TestSymptomsDatabaseIntegrity:
    """Tests para integridad de SYMPTOMS_DATABASE."""

    def test_all_symptoms_have_required_fields(self):
        """Todos los síntomas deben tener campos requeridos."""
        required_fields = [
            "name_es", "typical_phase", "strategies", "when_to_see_doctor",
        ]
        for symptom_id, symptom_data in SYMPTOMS_DATABASE.items():
            for field in required_fields:
                assert field in symptom_data, f"Síntoma {symptom_id} falta campo {field}"

    def test_strategies_not_empty(self):
        """Estrategias no deben estar vacías."""
        for symptom_id, symptom_data in SYMPTOMS_DATABASE.items():
            assert len(symptom_data["strategies"]) > 0

    def test_expected_symptoms_exist(self):
        """Deben existir síntomas esperados."""
        expected = ["cramps", "fatigue", "bloating", "mood_swings", "cravings"]
        for symptom in expected:
            assert symptom in SYMPTOMS_DATABASE


class TestTrainingByPhaseIntegrity:
    """Tests para integridad de TRAINING_BY_PHASE."""

    def test_all_phases_have_training(self):
        """Todas las fases deben tener recomendaciones de entrenamiento."""
        for phase in CYCLE_PHASES.keys():
            assert phase in TRAINING_BY_PHASE

    def test_all_training_has_required_fields(self):
        """Todo entrenamiento debe tener campos requeridos."""
        required_fields = ["recommended", "duration_minutes", "intensity"]
        for phase_id, training_data in TRAINING_BY_PHASE.items():
            for field in required_fields:
                assert field in training_data, f"Training {phase_id} falta campo {field}"


class TestNutritionByPhaseIntegrity:
    """Tests para integridad de NUTRITION_BY_PHASE."""

    def test_all_phases_have_nutrition(self):
        """Todas las fases deben tener recomendaciones de nutrición."""
        for phase in CYCLE_PHASES.keys():
            assert phase in NUTRITION_BY_PHASE

    def test_all_nutrition_has_required_fields(self):
        """Toda nutrición debe tener campos requeridos."""
        required_fields = ["increase", "reduce", "calorie_adjustment"]
        for phase_id, nutrition_data in NUTRITION_BY_PHASE.items():
            for field in required_fields:
                assert field in nutrition_data, f"Nutrition {phase_id} falta campo {field}"


class TestPerimenopauseInfoIntegrity:
    """Tests para integridad de PERIMENOPAUSE_INFO."""

    def test_has_required_fields(self):
        """Debe tener campos requeridos."""
        required_fields = [
            "typical_age_range", "signs",
            "training_recommendations", "nutrition_recommendations",
        ]
        for field in required_fields:
            assert field in PERIMENOPAUSE_INFO

    def test_signs_not_empty(self):
        """Signos no deben estar vacíos."""
        assert len(PERIMENOPAUSE_INFO["signs"]) > 0

    def test_recommendations_not_empty(self):
        """Recomendaciones no deben estar vacías."""
        assert len(PERIMENOPAUSE_INFO["training_recommendations"]) > 0
        assert len(PERIMENOPAUSE_INFO["nutrition_recommendations"]) > 0
