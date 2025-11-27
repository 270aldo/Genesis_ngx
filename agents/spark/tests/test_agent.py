"""Tests para el agente SPARK."""

from __future__ import annotations

from agents.spark.agent import (
    spark,
    root_agent,
    get_status,
    quick_habit_plan,
    quick_barrier_analysis,
    AGENT_CARD,
    AGENT_CONFIG,
)


class TestAgentConfiguration:
    """Tests para la configuración del agente."""

    def test_agent_exists(self):
        """El agente debe existir."""
        assert spark is not None

    def test_agent_name(self):
        """El agente debe tener el nombre correcto."""
        assert spark.name == "spark"

    def test_agent_model_is_flash(self):
        """El agente debe usar modelo Flash (no Pro)."""
        assert "flash" in spark.model.lower()

    def test_agent_has_tools(self):
        """El agente debe tener tools definidas."""
        assert spark.tools is not None
        assert len(spark.tools) > 0

    def test_agent_has_5_tools(self):
        """El agente debe tener exactamente 5 tools."""
        assert len(spark.tools) == 5

    def test_agent_has_instruction(self):
        """El agente debe tener instruction (system prompt)."""
        assert spark.instruction is not None
        assert len(spark.instruction) > 100

    def test_root_agent_is_spark(self):
        """root_agent debe ser spark."""
        assert root_agent is spark

    def test_agent_output_key(self):
        """El agente debe tener output_key definido."""
        assert spark.output_key == "spark_response"


class TestAgentCard:
    """Tests para el Agent Card (A2A)."""

    def test_agent_card_has_required_fields(self):
        """Agent Card debe tener campos requeridos."""
        required_fields = ["name", "description", "version", "protocol", "capabilities", "methods", "limits"]
        for field in required_fields:
            assert field in AGENT_CARD, f"Campo {field} faltante en AGENT_CARD"

    def test_agent_card_protocol(self):
        """Agent Card debe usar protocolo A2A v0.3."""
        assert AGENT_CARD["protocol"] == "a2a/0.3"

    def test_agent_card_has_domain(self):
        """Agent Card debe indicar dominio behavior."""
        assert AGENT_CARD["domain"] == "behavior"
        assert AGENT_CARD["specialty"] == "habits_motivation"

    def test_agent_card_has_create_habit_plan_method(self):
        """Agent Card debe exponer método create_habit_plan."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "create_habit_plan" in method_names

    def test_agent_card_has_identify_barriers_method(self):
        """Agent Card debe exponer método identify_barriers."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "identify_barriers" in method_names

    def test_agent_card_has_design_accountability_method(self):
        """Agent Card debe exponer método design_accountability."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "design_accountability" in method_names

    def test_agent_card_has_assess_motivation_method(self):
        """Agent Card debe exponer método assess_motivation."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "assess_motivation" in method_names

    def test_agent_card_has_suggest_behavior_change_method(self):
        """Agent Card debe exponer método suggest_behavior_change."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "suggest_behavior_change" in method_names

    def test_agent_card_has_5_methods(self):
        """Agent Card debe exponer exactamente 5 métodos."""
        assert len(AGENT_CARD["methods"]) == 5

    def test_agent_card_limits(self):
        """Agent Card debe tener límites apropiados para Flash."""
        limits = AGENT_CARD["limits"]
        assert limits["max_latency_ms"] == 2000
        assert limits["max_cost_per_invoke"] == 0.01

    def test_agent_card_privacy(self):
        """Agent Card debe indicar que NO maneja PHI/PII."""
        privacy = AGENT_CARD["privacy"]
        assert privacy["pii"] is False
        assert privacy["phi"] is False

    def test_agent_card_auth(self):
        """Agent Card debe tener auth configurado."""
        auth = AGENT_CARD["auth"]
        assert auth["method"] == "bearer"
        assert auth["audience"] == "genesis-ngx"


class TestAgentConfig:
    """Tests para AGENT_CONFIG."""

    def test_agent_config_domain(self):
        """AGENT_CONFIG debe tener domain=behavior."""
        assert AGENT_CONFIG["domain"] == "behavior"

    def test_agent_config_specialty(self):
        """AGENT_CONFIG debe tener specialty correcta."""
        assert AGENT_CONFIG["specialty"] == "habits_motivation"

    def test_agent_config_capabilities(self):
        """AGENT_CONFIG debe tener capabilities requeridas."""
        required_capabilities = [
            "habit_formation",
            "motivation_strategies",
            "barrier_identification",
            "accountability_systems",
            "behavior_change_techniques",
        ]
        for cap in required_capabilities:
            assert cap in AGENT_CONFIG["capabilities"]

    def test_agent_config_model_tier(self):
        """AGENT_CONFIG debe indicar model_tier=flash."""
        assert AGENT_CONFIG["model_tier"] == "flash"

    def test_agent_config_cost_tier(self):
        """AGENT_CONFIG debe indicar cost_tier=low."""
        assert AGENT_CONFIG["cost_tier"] == "low"

    def test_agent_config_latency_tier(self):
        """AGENT_CONFIG debe indicar latency_tier=fast."""
        assert AGENT_CONFIG["latency_tier"] == "fast"


class TestGetStatus:
    """Tests para get_status."""

    def test_get_status_returns_healthy(self):
        """get_status debe retornar status=healthy."""
        status = get_status()
        assert status["status"] == "healthy"

    def test_get_status_includes_agent(self):
        """get_status debe indicar agente spark."""
        status = get_status()
        assert status["agent"] == "spark"

    def test_get_status_includes_version(self):
        """get_status debe incluir versión."""
        status = get_status()
        assert "version" in status
        assert status["version"] == AGENT_CARD["version"]

    def test_get_status_includes_frameworks(self):
        """get_status debe incluir frameworks disponibles."""
        status = get_status()
        assert "frameworks_available" in status
        assert len(status["frameworks_available"]) > 0

    def test_get_status_includes_barrier_categories(self):
        """get_status debe incluir categorías de barreras."""
        status = get_status()
        assert "barrier_categories" in status
        assert len(status["barrier_categories"]) > 0

    def test_get_status_includes_motivation_types(self):
        """get_status debe incluir tipos de motivación."""
        status = get_status()
        assert "motivation_types" in status
        assert len(status["motivation_types"]) > 0

    def test_get_status_includes_accountability_methods(self):
        """get_status debe incluir métodos de accountability."""
        status = get_status()
        assert "accountability_methods" in status
        assert len(status["accountability_methods"]) > 0

    def test_get_status_includes_capabilities(self):
        """get_status debe incluir capacidades."""
        status = get_status()
        assert "capabilities" in status
        assert len(status["capabilities"]) > 0

    def test_get_status_includes_model(self):
        """get_status debe indicar modelo usado."""
        status = get_status()
        assert "model" in status
        assert "flash" in status["model"].lower()


class TestQuickHabitPlan:
    """Tests para quick_habit_plan helper."""

    def test_quick_habit_plan_basic(self):
        """Debe crear plan con parámetros básicos."""
        result = quick_habit_plan(habit="meditar")
        assert result["status"] == "created"
        assert "all_versions" in result

    def test_quick_habit_plan_with_anchor(self):
        """Debe crear plan con ancla especificada."""
        result = quick_habit_plan(
            habit="meditar",
            anchor="después del café matutino",
        )
        assert result["status"] == "created"
        assert "anchors" in result

    def test_quick_habit_plan_with_minutes(self):
        """Debe respetar minutos disponibles."""
        result = quick_habit_plan(
            habit="leer",
            minutes=20,
        )
        assert result["status"] == "created"
        # Verificar que el tiempo se usó en las versiones
        assert result["all_versions"]["small"]["duration_minutes"] <= 20

    def test_quick_habit_plan_creates_versions(self):
        """Debe crear versiones de diferente dificultad."""
        result = quick_habit_plan(habit="ejercicio")
        versions = result["all_versions"]
        assert "tiny" in versions
        assert "small" in versions
        assert "medium" in versions
        assert "large" in versions

    def test_quick_habit_plan_includes_tracking(self):
        """Debe incluir métricas de éxito."""
        result = quick_habit_plan(habit="beber agua")
        assert "success_metrics" in result


class TestQuickBarrierAnalysis:
    """Tests para quick_barrier_analysis helper."""

    def test_quick_barrier_analysis_basic(self):
        """Debe analizar barreras con solo el objetivo."""
        result = quick_barrier_analysis(goal="ejercitarme regularmente")
        assert result["status"] == "analyzed"
        assert "barriers_identified" in result

    def test_quick_barrier_analysis_with_obstacles(self):
        """Debe incluir obstáculos conocidos."""
        result = quick_barrier_analysis(
            goal="meditar diariamente",
            obstacles=["falta de tiempo", "mente muy activa"],
        )
        assert result["status"] == "analyzed"
        assert "top_barriers" in result

    def test_quick_barrier_analysis_returns_solutions(self):
        """Debe incluir soluciones para barreras."""
        result = quick_barrier_analysis(goal="comer saludable")
        assert "solutions" in result
        assert len(result["solutions"]) > 0

    def test_quick_barrier_analysis_includes_priority(self):
        """Debe priorizar las barreras."""
        result = quick_barrier_analysis(goal="dormir 8 horas")
        assert "priority_action" in result


class TestAgentIntegration:
    """Tests de integración para verificar coherencia del agente."""

    def test_agent_card_methods_match_tools(self):
        """Los métodos del Agent Card deben corresponder a las tools."""
        method_names = {m["name"] for m in AGENT_CARD["methods"]}
        expected_methods = {
            "create_habit_plan",
            "identify_barriers",
            "design_accountability",
            "assess_motivation",
            "suggest_behavior_change",
        }
        assert method_names == expected_methods

    def test_agent_config_capabilities_count(self):
        """AGENT_CONFIG debe tener 5 capabilities."""
        assert len(AGENT_CONFIG["capabilities"]) == 5

    def test_agent_description_mentions_habits(self):
        """La descripción del agente debe mencionar hábitos."""
        assert "hábito" in spark.description.lower() or "habit" in spark.description.lower()

    def test_agent_description_mentions_motivation(self):
        """La descripción del agente debe mencionar motivación."""
        assert "motivación" in spark.description.lower() or "motivation" in spark.description.lower()

    def test_get_status_consistency(self):
        """get_status debe ser consistente con AGENT_CARD."""
        status = get_status()
        assert status["version"] == AGENT_CARD["version"]
        assert set(status["capabilities"]) == set(AGENT_CONFIG["capabilities"])
