"""Tests para las tools de NOVA."""

from __future__ import annotations

from agents.nova.tools import (
    recommend_supplements,
    design_stack,
    create_timing_protocol,
    check_interactions,
    grade_evidence,
    SUPPLEMENTS_DATABASE,
    INTERACTIONS_DATABASE,
    GOAL_TO_SUPPLEMENTS,
    TIMING_WINDOWS,
)


class TestRecommendSupplements:
    """Tests para recommend_supplements."""

    def test_recommend_for_muscle_gain(self):
        """Debe recomendar suplementos para ganancia muscular."""
        result = recommend_supplements(goal="muscle_gain")
        assert result["status"] == "recommended"
        assert result["goal"] == "muscle_gain"
        assert len(result["recommendations"]) > 0

    def test_recommend_for_sleep(self):
        """Debe recomendar suplementos para sueño."""
        result = recommend_supplements(goal="sleep")
        assert result["status"] == "recommended"
        assert result["goal"] == "sleep"

    def test_recommend_with_budget(self):
        """Debe respetar presupuesto."""
        result = recommend_supplements(
            goal="performance",
            budget_monthly_usd=30,
        )
        assert result["status"] == "recommended"
        assert result["estimated_monthly_cost_usd"] <= 30

    def test_recommend_max_supplements(self):
        """Debe respetar límite de suplementos."""
        result = recommend_supplements(
            goal="health",
            max_supplements=3,
        )
        assert len(result["recommendations"]) <= 3

    def test_recommend_excludes_current(self):
        """Debe excluir suplementos actuales."""
        result = recommend_supplements(
            goal="muscle_gain",
            current_supplements=["creatine", "vitamin_d3"],
        )
        rec_ids = [r["id"] for r in result["recommendations"]]
        assert "creatine" not in rec_ids
        assert "vitamin_d3" not in rec_ids

    def test_recommend_includes_evidence_level(self):
        """Recomendaciones deben incluir nivel de evidencia."""
        result = recommend_supplements(goal="performance")
        for rec in result["recommendations"]:
            assert "evidence_level" in rec
            assert rec["evidence_level"] in ["A", "B", "C", "D"]

    def test_recommend_includes_by_tier(self):
        """Debe organizar por tier de evidencia."""
        result = recommend_supplements(goal="health")
        assert "by_tier" in result
        assert "tier_1_essential" in result["by_tier"]
        assert "tier_2_beneficial" in result["by_tier"]

    def test_recommend_includes_disclaimer(self):
        """Debe incluir disclaimer médico."""
        result = recommend_supplements(goal="sleep")
        assert "disclaimer" in result
        assert "médico" in result["disclaimer"].lower()

    def test_recommend_invalid_empty_goal(self):
        """Debe rechazar objetivo vacío."""
        result = recommend_supplements(goal="")
        assert result["status"] == "error"

    def test_recommend_maps_spanish_goals(self):
        """Debe mapear objetivos en español."""
        result = recommend_supplements(goal="ganar_musculo")
        assert result["status"] == "recommended"
        assert result["goal"] == "muscle_gain"


class TestDesignStack:
    """Tests para design_stack."""

    def test_design_basic_stack(self):
        """Debe diseñar stack básico."""
        result = design_stack(primary_goal="muscle_gain")
        assert result["status"] == "designed"
        assert "stack" in result

    def test_stack_has_levels(self):
        """Stack debe tener niveles base, goal, optimization."""
        result = design_stack(primary_goal="performance")
        assert "base" in result["stack"]
        assert "goal_specific" in result["stack"]
        assert "optimization" in result["stack"]

    def test_stack_respects_budget(self):
        """Debe respetar presupuesto."""
        result = design_stack(
            primary_goal="health",
            budget_monthly_usd=40,
        )
        assert result["estimated_monthly_cost_usd"] <= 40

    def test_stack_includes_introduction_protocol(self):
        """Debe incluir protocolo de introducción."""
        result = design_stack(primary_goal="sleep")
        assert "introduction_protocol" in result
        assert len(result["introduction_protocol"]) > 0

    def test_stack_with_secondary_goals(self):
        """Debe incluir suplementos de objetivos secundarios."""
        result = design_stack(
            primary_goal="muscle_gain",
            secondary_goals=["sleep"],
        )
        assert result["status"] == "designed"
        assert result["secondary_goals"] == ["sleep"]

    def test_stack_identifies_synergies(self):
        """Debe identificar sinergias."""
        result = design_stack(primary_goal="health")
        assert "synergies_included" in result

    def test_stack_beginner_vs_advanced(self):
        """Stack avanzado puede tener más suplementos."""
        beginner = design_stack(
            primary_goal="performance",
            experience_level="beginner",
        )
        advanced = design_stack(
            primary_goal="performance",
            experience_level="advanced",
        )
        # Ambos deben ser válidos
        assert beginner["status"] == "designed"
        assert advanced["status"] == "designed"

    def test_stack_with_preferences(self):
        """Debe respetar preferencias."""
        result = design_stack(
            primary_goal="health",
            preferences={"no_caffeine": True},
        )
        all_supps = []
        for level in ["base", "goal_specific", "optimization"]:
            all_supps.extend([s["id"] for s in result["stack"].get(level, [])])
        assert "caffeine" not in all_supps

    def test_stack_invalid_empty_goal(self):
        """Debe rechazar objetivo vacío."""
        result = design_stack(primary_goal="")
        assert result["status"] == "error"


class TestCreateTimingProtocol:
    """Tests para create_timing_protocol."""

    def test_create_basic_protocol(self):
        """Debe crear protocolo básico."""
        result = create_timing_protocol(
            supplements=["vitamin_d3", "magnesium", "omega3"]
        )
        assert result["status"] == "created"
        assert "schedule_by_window" in result

    def test_protocol_includes_daily_schedule(self):
        """Debe incluir horario diario."""
        result = create_timing_protocol(
            supplements=["creatine", "caffeine", "magnesium"]
        )
        assert "daily_schedule" in result

    def test_protocol_with_workout_time(self):
        """Debe ajustar para hora de entrenamiento."""
        result = create_timing_protocol(
            supplements=["caffeine", "citrulline"],
            workout_time="18:00",
        )
        assert result["workout_time"] == "18:00"
        # Pre-workout debe tener suplementos
        assert len(result["schedule_by_window"]["pre_workout"]) > 0

    def test_protocol_separates_supplements(self):
        """Debe identificar separaciones necesarias."""
        result = create_timing_protocol(
            supplements=["zinc", "magnesium", "caffeine"]
        )
        assert "required_separations" in result

    def test_protocol_respects_wake_sleep(self):
        """Debe usar horarios proporcionados."""
        result = create_timing_protocol(
            supplements=["vitamin_d3"],
            wake_time="06:00",
            sleep_time="22:00",
        )
        assert result["wake_time"] == "06:00"
        assert result["sleep_time"] == "22:00"

    def test_protocol_includes_optimization_tips(self):
        """Debe incluir tips de optimización."""
        result = create_timing_protocol(
            supplements=["vitamin_d3", "omega3"]
        )
        assert "optimization_tips" in result
        assert len(result["optimization_tips"]) > 0

    def test_protocol_invalid_empty_list(self):
        """Debe rechazar lista vacía."""
        result = create_timing_protocol(supplements=[])
        assert result["status"] == "error"


class TestCheckInteractions:
    """Tests para check_interactions."""

    def test_check_basic_interactions(self):
        """Debe verificar interacciones básicas."""
        result = check_interactions(
            supplements=["omega3", "vitamin_k2"]
        )
        assert result["status"] == "checked"

    def test_detects_synergies(self):
        """Debe detectar sinergias."""
        result = check_interactions(
            supplements=["vitamin_d3", "vitamin_k2"]
        )
        assert result["total_synergies"] > 0 or "synergies" in result

    def test_detects_medication_interactions(self):
        """Debe detectar interacciones con medicamentos."""
        result = check_interactions(
            supplements=["omega3"],
            medications=["anticoagulantes"],
        )
        assert result["total_interactions"] > 0

    def test_detects_condition_warnings(self):
        """Debe detectar warnings por condiciones."""
        result = check_interactions(
            supplements=["ashwagandha"],
            conditions=["hipertiroidismo"],
        )
        assert len(result["condition_warnings"]) > 0

    def test_calculates_safety_score(self):
        """Debe calcular score de seguridad."""
        result = check_interactions(
            supplements=["vitamin_d3", "magnesium"]
        )
        assert "overall_safety" in result
        assert "score" in result["overall_safety"]

    def test_groups_by_severity(self):
        """Debe agrupar por severidad."""
        result = check_interactions(
            supplements=["omega3", "zinc"]
        )
        assert "interactions_by_severity" in result
        assert "severe" in result["interactions_by_severity"]
        assert "moderate" in result["interactions_by_severity"]
        assert "mild" in result["interactions_by_severity"]

    def test_generates_recommendations(self):
        """Debe generar recomendaciones de seguridad."""
        result = check_interactions(
            supplements=["ashwagandha", "magnesium"]
        )
        assert "recommendations" in result

    def test_includes_disclaimer(self):
        """Debe incluir disclaimer."""
        result = check_interactions(
            supplements=["creatine"]
        )
        assert "disclaimer" in result

    def test_invalid_empty_list(self):
        """Debe rechazar lista vacía."""
        result = check_interactions(supplements=[])
        assert result["status"] == "error"


class TestGradeEvidence:
    """Tests para grade_evidence."""

    def test_grade_known_supplement(self):
        """Debe evaluar suplemento conocido."""
        result = grade_evidence(supplement="creatine")
        assert result["status"] == "evaluated"
        assert result["overall_evidence_level"] == "A"

    def test_grade_includes_meaning(self):
        """Debe incluir significado del nivel."""
        result = grade_evidence(supplement="vitamin_d3")
        assert "evidence_meaning" in result

    def test_grade_includes_details(self):
        """Debe incluir detalles de evidencia."""
        result = grade_evidence(supplement="omega3")
        assert "evidence_details" in result

    def test_grade_with_claim(self):
        """Debe evaluar claim específico."""
        result = grade_evidence(
            supplement="creatine",
            claim="aumenta la fuerza",
        )
        assert "claim_evaluation" in result
        assert result["claim_evaluation"] is not None

    def test_grade_unknown_supplement(self):
        """Debe manejar suplemento desconocido."""
        result = grade_evidence(supplement="suplemento_inventado")
        assert result["status"] == "not_found"

    def test_grade_maps_spanish_names(self):
        """Debe mapear nombres en español."""
        result = grade_evidence(supplement="vitamina_d")
        assert result["status"] == "evaluated"

    def test_grade_includes_recommended_form(self):
        """Debe incluir forma recomendada."""
        result = grade_evidence(supplement="magnesium")
        assert "recommended_form" in result

    def test_grade_includes_typical_dose(self):
        """Debe incluir dosis típica."""
        result = grade_evidence(supplement="ashwagandha")
        assert "typical_dose" in result

    def test_grade_invalid_empty_supplement(self):
        """Debe rechazar suplemento vacío."""
        result = grade_evidence(supplement="")
        assert result["status"] == "error"


class TestSupplementsDatabaseIntegrity:
    """Tests para integridad de SUPPLEMENTS_DATABASE."""

    def test_all_supplements_have_required_fields(self):
        """Todos los suplementos deben tener campos requeridos."""
        required_fields = [
            "name_es", "category", "evidence_level",
            "typical_dose", "timing", "benefits",
        ]
        for supp_id, supp_data in SUPPLEMENTS_DATABASE.items():
            for field in required_fields:
                assert field in supp_data, f"Suplemento {supp_id} falta campo {field}"

    def test_evidence_levels_valid(self):
        """Niveles de evidencia deben ser válidos."""
        valid_levels = ["A", "B", "C", "D"]
        for supp_id, supp_data in SUPPLEMENTS_DATABASE.items():
            assert supp_data["evidence_level"] in valid_levels

    def test_categories_valid(self):
        """Categorías deben ser válidas."""
        valid_categories = [
            "foundational", "performance", "health",
            "sleep", "cognitive", "recovery",
        ]
        for supp_id, supp_data in SUPPLEMENTS_DATABASE.items():
            assert supp_data["category"] in valid_categories

    def test_benefits_not_empty(self):
        """Beneficios no deben estar vacíos."""
        for supp_id, supp_data in SUPPLEMENTS_DATABASE.items():
            assert len(supp_data["benefits"]) > 0


class TestInteractionsDatabaseIntegrity:
    """Tests para integridad de INTERACTIONS_DATABASE."""

    def test_all_interactions_have_required_fields(self):
        """Todas las interacciones deben tener campos requeridos."""
        required_fields = ["with", "type", "severity", "mechanism", "recommendation"]
        for supp_id, interactions in INTERACTIONS_DATABASE.items():
            for interaction in interactions:
                for field in required_fields:
                    assert field in interaction, f"Interacción de {supp_id} falta campo {field}"

    def test_severity_levels_valid(self):
        """Severidades deben ser válidas."""
        valid_severities = ["severe", "moderate", "mild", "synergy"]
        for supp_id, interactions in INTERACTIONS_DATABASE.items():
            for interaction in interactions:
                assert interaction["severity"] in valid_severities


class TestGoalToSupplementsIntegrity:
    """Tests para integridad de GOAL_TO_SUPPLEMENTS."""

    def test_all_goals_have_supplements(self):
        """Todos los objetivos deben tener suplementos."""
        for goal, supplements in GOAL_TO_SUPPLEMENTS.items():
            assert len(supplements) > 0, f"Objetivo {goal} sin suplementos"

    def test_all_supplements_exist_in_database(self):
        """Todos los suplementos referenciados deben existir."""
        for goal, supplements in GOAL_TO_SUPPLEMENTS.items():
            for supp in supplements:
                assert supp in SUPPLEMENTS_DATABASE, f"Suplemento {supp} no existe en DB"

    def test_expected_goals_exist(self):
        """Deben existir objetivos esperados."""
        expected = ["muscle_gain", "fat_loss", "sleep", "cognitive", "health"]
        for goal in expected:
            assert goal in GOAL_TO_SUPPLEMENTS


class TestTimingWindowsIntegrity:
    """Tests para integridad de TIMING_WINDOWS."""

    def test_all_windows_have_required_fields(self):
        """Todas las ventanas deben tener campos requeridos."""
        required_fields = ["name_es", "supplements", "reasoning"]
        for window_id, window_data in TIMING_WINDOWS.items():
            for field in required_fields:
                assert field in window_data, f"Ventana {window_id} falta campo {field}"

    def test_expected_windows_exist(self):
        """Deben existir ventanas esperadas."""
        expected = ["morning_fasted", "pre_workout", "evening"]
        for window in expected:
            assert window in TIMING_WINDOWS
