"""Tests para las tools de SPARK."""

from __future__ import annotations

from agents.spark.tools import (
    create_habit_plan,
    identify_barriers,
    design_accountability,
    assess_motivation,
    suggest_behavior_change,
    HABIT_FORMATION_STAGES,
    MOTIVATION_TYPES,
    COMMON_BARRIERS,
    BEHAVIOR_FRAMEWORKS,
    ACCOUNTABILITY_SYSTEMS,
)


class TestCreateHabitPlan:
    """Tests para create_habit_plan."""

    def test_create_basic_plan(self):
        """Debe crear plan básico de hábito."""
        result = create_habit_plan(
            desired_habit="meditar",
            available_time_minutes=10,
        )
        assert result["status"] == "created"
        assert "habit_loop" in result
        assert "recommended_version" in result

    def test_create_plan_with_anchor(self):
        """Debe incluir ancla personalizada."""
        result = create_habit_plan(
            desired_habit="ejercicio",
            current_routine="después de despertar",
            available_time_minutes=30,
        )
        assert result["status"] == "created"
        assert len(result["anchors"]) > 0

    def test_creates_multiple_versions(self):
        """Debe crear versiones de diferentes tamaños."""
        result = create_habit_plan(
            desired_habit="leer",
            available_time_minutes=30,
        )
        assert "all_versions" in result
        assert "tiny" in result["all_versions"]
        assert "small" in result["all_versions"]
        assert "medium" in result["all_versions"]

    def test_tiny_version_is_two_minutes(self):
        """Versión tiny debe ser 2 minutos."""
        result = create_habit_plan(
            desired_habit="escribir",
            available_time_minutes=60,
        )
        assert result["all_versions"]["tiny"]["duration_minutes"] == 2

    def test_includes_habit_loop(self):
        """Debe incluir loop del hábito completo."""
        result = create_habit_plan(desired_habit="caminar")
        assert "cue" in result["habit_loop"]
        assert "craving" in result["habit_loop"]
        assert "response" in result["habit_loop"]
        assert "reward" in result["habit_loop"]

    def test_includes_weekly_plan(self):
        """Debe incluir plan semanal."""
        result = create_habit_plan(desired_habit="yoga")
        assert "weekly_plan" in result
        assert "frequency" in result["weekly_plan"]

    def test_includes_success_metrics(self):
        """Debe incluir métricas de éxito."""
        result = create_habit_plan(desired_habit="estiramientos")
        assert "success_metrics" in result
        assert "short_term" in result["success_metrics"]
        assert "long_term" in result["success_metrics"]

    def test_analyzes_previous_attempts(self):
        """Debe analizar intentos previos."""
        result = create_habit_plan(
            desired_habit="ejercicio",
            previous_attempts=["No tenía tiempo", "Perdí motivación"],
        )
        assert result["lessons_from_past"] is not None
        assert len(result["lessons_from_past"]) > 0

    def test_invalid_empty_habit(self):
        """Debe rechazar hábito vacío."""
        result = create_habit_plan(desired_habit="")
        assert result["status"] == "error"

    def test_invalid_short_time(self):
        """Debe rechazar tiempo muy corto."""
        result = create_habit_plan(
            desired_habit="ejercicio",
            available_time_minutes=1,
        )
        assert result["status"] == "error"


class TestIdentifyBarriers:
    """Tests para identify_barriers."""

    def test_identify_basic_barriers(self):
        """Debe identificar barreras básicas."""
        result = identify_barriers(goal="hacer ejercicio")
        assert result["status"] == "analyzed"
        assert "top_barriers" in result

    def test_identify_from_obstacles(self):
        """Debe identificar barreras de obstáculos declarados."""
        result = identify_barriers(
            goal="comer saludable",
            current_obstacles=["No tengo tiempo", "Estoy muy cansado"],
        )
        assert result["barriers_identified"] >= 2

    def test_provides_solutions(self):
        """Debe proveer soluciones por barrera."""
        result = identify_barriers(
            goal="meditar",
            current_obstacles=["Falta de tiempo"],
        )
        assert "solutions" in result
        assert len(result["solutions"]) > 0

    def test_includes_priority_action(self):
        """Debe incluir acción prioritaria."""
        result = identify_barriers(goal="ejercicio")
        assert "priority_action" in result
        assert "first_step" in result["priority_action"]

    def test_infers_from_energy_level(self):
        """Debe inferir barreras de nivel de energía."""
        result = identify_barriers(
            goal="hacer ejercicio",
            energy_level="low",
        )
        # Energy bajo debe generar barrera de energía
        categories = [b["category"] for b in result["top_barriers"]]
        assert "energy" in categories or result["context_insights"]["energy_level"] == "low"

    def test_infers_from_support_system(self):
        """Debe inferir barreras de sistema de apoyo."""
        result = identify_barriers(
            goal="perder peso",
            support_system="none",
        )
        assert result["context_insights"]["support_system"] == "none"

    def test_includes_context_recommendation(self):
        """Debe incluir recomendación de contexto."""
        result = identify_barriers(goal="ejercicio")
        assert "context_insights" in result
        assert "recommendation" in result["context_insights"]

    def test_invalid_empty_goal(self):
        """Debe rechazar objetivo vacío."""
        result = identify_barriers(goal="")
        assert result["status"] == "error"


class TestDesignAccountability:
    """Tests para design_accountability."""

    def test_design_basic_accountability(self):
        """Debe diseñar accountability básico."""
        result = design_accountability(goal="ejercicio diario")
        assert result["status"] == "designed"
        assert "primary_system" in result

    def test_uses_preferred_method(self):
        """Debe usar método preferido."""
        result = design_accountability(
            goal="meditar",
            preferred_method="accountability_partner",
        )
        assert result["primary_system"]["method"] == "accountability_partner"

    def test_includes_complementary_systems(self):
        """Debe incluir sistemas complementarios."""
        result = design_accountability(goal="comer saludable")
        assert "complementary_systems" in result

    def test_includes_checkin_schedule(self):
        """Debe incluir horario de check-ins."""
        result = design_accountability(
            goal="ejercicio",
            check_in_frequency="daily",
        )
        assert "check_in_schedule" in result
        assert result["check_in_schedule"]["frequency"] == "diario"

    def test_includes_consequences(self):
        """Debe incluir consecuencias."""
        result = design_accountability(goal="ejercicio")
        assert "consequences" in result
        assert "positive" in result["consequences"]
        assert "negative" in result["consequences"]

    def test_consequences_match_tolerance(self):
        """Consecuencias deben coincidir con tolerancia."""
        low = design_accountability(goal="ejercicio diario", consequence_tolerance="low")
        high = design_accountability(goal="ejercicio diario", consequence_tolerance="high")
        # High tolerance debería tener consecuencias más fuertes
        assert low["consequences"]["negative"] != high["consequences"]["negative"]

    def test_includes_implementation_intentions(self):
        """Debe incluir intenciones de implementación."""
        result = design_accountability(goal="ejercicio")
        assert "implementation_intentions" in result
        assert len(result["implementation_intentions"]) > 0

    def test_adds_partner_system_when_available(self):
        """Debe agregar partner cuando está disponible."""
        result = design_accountability(
            goal="ejercicio",
            has_partner=True,
            preferred_method="habit_tracking",
        )
        complementary_methods = [s["method"] for s in result["complementary_systems"]]
        assert "accountability_partner" in complementary_methods

    def test_invalid_empty_goal(self):
        """Debe rechazar objetivo vacío."""
        result = design_accountability(goal="")
        assert result["status"] == "error"


class TestAssessMotivation:
    """Tests para assess_motivation."""

    def test_assess_basic_motivation(self):
        """Debe evaluar motivación básica."""
        result = assess_motivation(stated_goal="perder peso")
        assert result["status"] == "assessed"
        assert "motivation_analysis" in result

    def test_identifies_dominant_type(self):
        """Debe identificar tipo dominante."""
        result = assess_motivation(
            stated_goal="hacer ejercicio",
            reasons_for_goal=["Me gusta cómo me siento", "Disfruto el proceso"],
        )
        assert "dominant_type" in result["motivation_analysis"]
        # Razones intrínsecas deberían dar motivación intrínseca
        assert result["motivation_analysis"]["dominant_type"] in [
            "intrinsic", "identified", "introjected", "extrinsic"
        ]

    def test_intrinsic_from_enjoyment_reasons(self):
        """Razones de disfrute deben dar intrínseca."""
        result = assess_motivation(
            stated_goal="ejercicio",
            reasons_for_goal=["Disfruto hacerlo", "Me divierte", "Me gusta"],
        )
        # Debería tener score alto en intrínseca
        assert result["motivation_analysis"]["all_scores"]["intrinsic"] > 0.2

    def test_extrinsic_from_external_reasons(self):
        """Razones externas deben dar extrínseca."""
        result = assess_motivation(
            stated_goal="perder peso",
            reasons_for_goal=["Para ganar una apuesta", "Por dinero"],
            external_pressure="high",
        )
        assert result["motivation_analysis"]["all_scores"]["extrinsic"] > 0.2

    def test_includes_commitment_analysis(self):
        """Debe incluir análisis de compromiso."""
        result = assess_motivation(stated_goal="ejercicio")
        assert "commitment_analysis" in result
        assert "level" in result["commitment_analysis"]
        assert "score" in result["commitment_analysis"]

    def test_includes_success_prediction(self):
        """Debe incluir predicción de éxito."""
        result = assess_motivation(stated_goal="ejercicio")
        assert "success_prediction" in result
        assert "probability_percent" in result["success_prediction"]

    def test_success_probability_under_100(self):
        """Probabilidad de éxito debe ser menor a 100."""
        result = assess_motivation(
            stated_goal="ejercicio",
            reasons_for_goal=["Disfruto", "Me hace bien", "Es importante"],
            past_attempts=5,
        )
        assert result["success_prediction"]["probability_percent"] <= 95

    def test_includes_recommendations(self):
        """Debe incluir recomendaciones."""
        result = assess_motivation(stated_goal="ejercicio")
        assert "recommendations" in result

    def test_identifies_risk_factors(self):
        """Debe identificar factores de riesgo."""
        result = assess_motivation(stated_goal="ejercicio")
        assert "risk_factors" in result["success_prediction"]

    def test_invalid_empty_goal(self):
        """Debe rechazar objetivo vacío."""
        result = assess_motivation(stated_goal="")
        assert result["status"] == "error"


class TestSuggestBehaviorChange:
    """Tests para suggest_behavior_change."""

    def test_suggest_basic_change(self):
        """Debe sugerir cambio básico."""
        result = suggest_behavior_change(target_behavior="hacer ejercicio")
        assert result["status"] == "suggested"
        assert "strategy" in result

    def test_uses_preferred_framework(self):
        """Debe usar framework preferido."""
        result = suggest_behavior_change(
            target_behavior="meditar",
            preferred_framework="tiny_habits",
        )
        assert result["framework"]["name"] == "tiny_habits"

    def test_includes_strategy(self):
        """Debe incluir estrategia."""
        result = suggest_behavior_change(target_behavior="leer")
        assert "core_principle" in result["strategy"]
        assert "steps" in result["strategy"]

    def test_includes_implementation_plan(self):
        """Debe incluir plan de implementación."""
        result = suggest_behavior_change(target_behavior="ejercicio")
        assert "implementation_plan" in result
        assert "phase_1" in result["implementation_plan"]

    def test_includes_techniques(self):
        """Debe incluir técnicas."""
        result = suggest_behavior_change(target_behavior="ejercicio")
        assert "techniques" in result
        assert len(result["techniques"]) > 0

    def test_techniques_match_learning_style(self):
        """Técnicas deben coincidir con estilo."""
        practical = suggest_behavior_change(
            target_behavior="ejercicio diario",
            learning_style="practical",
        )
        social = suggest_behavior_change(
            target_behavior="ejercicio diario",
            learning_style="social",
        )
        # Deberían tener técnicas diferentes
        practical_names = [t["name"] for t in practical["techniques"]]
        social_names = [t["name"] for t in social["techniques"]]
        assert practical_names != social_names

    def test_anticipates_obstacles(self):
        """Debe anticipar obstáculos."""
        result = suggest_behavior_change(target_behavior="ejercicio")
        assert "anticipated_obstacles" in result
        assert len(result["anticipated_obstacles"]) > 0

    def test_includes_weekly_commitment(self):
        """Debe incluir compromiso semanal."""
        result = suggest_behavior_change(
            target_behavior="ejercicio",
            time_available_weekly=90,
        )
        assert "weekly_commitment" in result
        assert result["weekly_commitment"]["total_minutes"] == 90

    def test_includes_progress_markers(self):
        """Debe incluir marcadores de progreso."""
        result = suggest_behavior_change(target_behavior="ejercicio")
        assert "progress_markers" in result
        # Debe incluir 7, 21, 66 días
        days = [m["day"] for m in result["progress_markers"]]
        assert 7 in days
        assert 21 in days
        assert 66 in days

    def test_includes_replacement_strategy(self):
        """Debe incluir estrategia de reemplazo cuando hay comportamiento actual."""
        result = suggest_behavior_change(
            target_behavior="ejercicio",
            current_behavior="ver TV",
        )
        assert "replacement_strategy" in result["strategy"]

    def test_invalid_empty_target(self):
        """Debe rechazar target vacío."""
        result = suggest_behavior_change(target_behavior="")
        assert result["status"] == "error"


class TestHabitFormationStagesIntegrity:
    """Tests para integridad de HABIT_FORMATION_STAGES."""

    def test_all_stages_have_required_fields(self):
        """Todas las etapas deben tener campos requeridos."""
        required_fields = ["name_es", "description", "types", "tips"]
        for stage_id, stage_data in HABIT_FORMATION_STAGES.items():
            for field in required_fields:
                assert field in stage_data, f"Etapa {stage_id} falta campo {field}"

    def test_expected_stages_exist(self):
        """Deben existir etapas esperadas."""
        expected = ["cue", "craving", "response", "reward"]
        for stage in expected:
            assert stage in HABIT_FORMATION_STAGES


class TestMotivationTypesIntegrity:
    """Tests para integridad de MOTIVATION_TYPES."""

    def test_all_types_have_required_fields(self):
        """Todos los tipos deben tener campos requeridos."""
        required_fields = ["name_es", "description", "drivers", "sustainability"]
        for type_id, type_data in MOTIVATION_TYPES.items():
            for field in required_fields:
                assert field in type_data, f"Tipo {type_id} falta campo {field}"

    def test_sustainability_in_valid_range(self):
        """Sustainability debe estar entre 0 y 1."""
        for type_id, type_data in MOTIVATION_TYPES.items():
            assert 0 <= type_data["sustainability"] <= 1

    def test_expected_types_exist(self):
        """Deben existir tipos esperados."""
        expected = ["intrinsic", "extrinsic", "identified", "introjected"]
        for type_name in expected:
            assert type_name in MOTIVATION_TYPES


class TestCommonBarriersIntegrity:
    """Tests para integridad de COMMON_BARRIERS."""

    def test_all_barriers_have_required_fields(self):
        """Todas las barreras deben tener campos requeridos."""
        required_fields = ["name_es", "description", "solutions", "reframe"]
        for barrier_id, barrier_data in COMMON_BARRIERS.items():
            for field in required_fields:
                assert field in barrier_data, f"Barrera {barrier_id} falta campo {field}"

    def test_solutions_not_empty(self):
        """Soluciones no deben estar vacías."""
        for barrier_id, barrier_data in COMMON_BARRIERS.items():
            assert len(barrier_data["solutions"]) > 0

    def test_expected_barriers_exist(self):
        """Deben existir barreras esperadas."""
        expected = ["time", "energy", "motivation", "knowledge", "social"]
        for barrier in expected:
            assert barrier in COMMON_BARRIERS


class TestBehaviorFrameworksIntegrity:
    """Tests para integridad de BEHAVIOR_FRAMEWORKS."""

    def test_all_frameworks_have_required_fields(self):
        """Todos los frameworks deben tener campos requeridos."""
        required_fields = ["name_es", "author", "core_principle"]
        for fw_id, fw_data in BEHAVIOR_FRAMEWORKS.items():
            for field in required_fields:
                assert field in fw_data, f"Framework {fw_id} falta campo {field}"

    def test_expected_frameworks_exist(self):
        """Deben existir frameworks esperados."""
        expected = ["atomic_habits", "tiny_habits", "habit_loop"]
        for framework in expected:
            assert framework in BEHAVIOR_FRAMEWORKS


class TestAccountabilitySystemsIntegrity:
    """Tests para integridad de ACCOUNTABILITY_SYSTEMS."""

    def test_all_systems_have_required_fields(self):
        """Todos los sistemas deben tener campos requeridos."""
        required_fields = ["name_es", "description", "effectiveness"]
        for sys_id, sys_data in ACCOUNTABILITY_SYSTEMS.items():
            for field in required_fields:
                assert field in sys_data, f"Sistema {sys_id} falta campo {field}"

    def test_effectiveness_in_valid_range(self):
        """Effectiveness debe estar entre 0 y 100."""
        for sys_id, sys_data in ACCOUNTABILITY_SYSTEMS.items():
            assert 0 <= sys_data["effectiveness"] <= 100

    def test_expected_systems_exist(self):
        """Deben existir sistemas esperados."""
        expected = ["habit_tracking", "accountability_partner", "public_commitment"]
        for system in expected:
            assert system in ACCOUNTABILITY_SYSTEMS
