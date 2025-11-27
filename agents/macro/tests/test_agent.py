"""Tests para el agente MACRO."""

from __future__ import annotations

from agents.macro.agent import (
    macro,
    root_agent,
    get_status,
    calculate_user_macros,
    create_meal_plan,
    AGENT_CARD,
    AGENT_CONFIG,
)


class TestAgentConfiguration:
    """Tests para la configuración del agente."""

    def test_agent_exists(self):
        """El agente debe existir."""
        assert macro is not None

    def test_agent_name(self):
        """El agente debe tener el nombre correcto."""
        assert macro.name == "macro"

    def test_agent_model_is_flash(self):
        """El agente debe usar modelo Flash (no Pro)."""
        assert "flash" in macro.model.lower()

    def test_agent_has_tools(self):
        """El agente debe tener tools definidas."""
        assert macro.tools is not None
        assert len(macro.tools) > 0

    def test_agent_has_instruction(self):
        """El agente debe tener instruction (system prompt)."""
        assert macro.instruction is not None
        assert len(macro.instruction) > 100

    def test_root_agent_is_macro(self):
        """root_agent debe ser macro."""
        assert root_agent is macro


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
        """Agent Card debe indicar dominio nutrition."""
        assert AGENT_CARD["domain"] == "nutrition"
        assert AGENT_CARD["specialty"] == "macronutrients"

    def test_agent_card_has_calculate_macros_method(self):
        """Agent Card debe exponer método calculate_macros."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "calculate_macros" in method_names

    def test_agent_card_has_distribute_protein_method(self):
        """Agent Card debe exponer método distribute_protein."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "distribute_protein" in method_names

    def test_agent_card_has_plan_carb_cycling_method(self):
        """Agent Card debe exponer método plan_carb_cycling."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "plan_carb_cycling" in method_names

    def test_agent_card_has_optimize_fat_intake_method(self):
        """Agent Card debe exponer método optimize_fat_intake."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "optimize_fat_intake" in method_names

    def test_agent_card_has_compose_meal_method(self):
        """Agent Card debe exponer método compose_meal."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "compose_meal" in method_names

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


class TestAgentConfig:
    """Tests para AGENT_CONFIG."""

    def test_agent_config_domain(self):
        """AGENT_CONFIG debe tener domain=nutrition."""
        assert AGENT_CONFIG["domain"] == "nutrition"

    def test_agent_config_specialty(self):
        """AGENT_CONFIG debe tener specialty correcta."""
        assert AGENT_CONFIG["specialty"] == "macronutrients"

    def test_agent_config_capabilities(self):
        """AGENT_CONFIG debe tener capabilities requeridas."""
        required_capabilities = [
            "macro_calculation",
            "protein_distribution",
            "carb_cycling",
            "fat_optimization",
            "meal_composition",
        ]
        for cap in required_capabilities:
            assert cap in AGENT_CONFIG["capabilities"]


class TestGetStatus:
    """Tests para get_status."""

    def test_get_status_returns_healthy(self):
        """get_status debe retornar status=healthy."""
        status = get_status()
        assert status["status"] == "healthy"

    def test_get_status_includes_goals(self):
        """get_status debe incluir objetivos soportados."""
        status = get_status()
        assert "goals_supported" in status
        assert len(status["goals_supported"]) > 0

    def test_get_status_includes_activity_types(self):
        """get_status debe incluir tipos de actividad."""
        status = get_status()
        assert "activity_types" in status
        assert len(status["activity_types"]) > 0

    def test_get_status_includes_patterns(self):
        """get_status debe incluir patrones de ciclado."""
        status = get_status()
        assert "carb_cycling_patterns" in status
        assert len(status["carb_cycling_patterns"]) > 0

    def test_get_status_includes_capabilities(self):
        """get_status debe incluir capacidades."""
        status = get_status()
        assert "capabilities" in status
        assert len(status["capabilities"]) > 0


class TestCalculateUserMacros:
    """Tests para calculate_user_macros."""

    def test_calculate_basic_macros(self):
        """Debe calcular macros básicos."""
        result = calculate_user_macros(daily_calories=2000)
        assert result["status"] == "calculated"
        assert "macros" in result

    def test_calculate_with_weight(self):
        """Debe calcular con peso."""
        result = calculate_user_macros(
            daily_calories=2000,
            weight_kg=75.0,
        )
        assert result["status"] == "calculated"
        assert result["summary"]["protein_per_kg"] is not None

    def test_calculate_for_fat_loss(self):
        """Debe calcular para fat loss."""
        result = calculate_user_macros(
            daily_calories=1800,
            goal="fat_loss",
        )
        assert result["status"] == "calculated"
        assert result["macros"]["protein"]["percent"] >= 35

    def test_calculate_for_muscle_gain(self):
        """Debe calcular para muscle gain."""
        result = calculate_user_macros(
            daily_calories=2500,
            goal="muscle_gain",
        )
        assert result["status"] == "calculated"

    def test_calculate_with_activity(self):
        """Debe ajustar por tipo de actividad."""
        result = calculate_user_macros(
            daily_calories=2000,
            weight_kg=75.0,
            activity_type="strength",
        )
        assert result["status"] == "calculated"
        # Strength debería tener proteína por kg >= 1.4
        assert result["summary"]["protein_per_kg"] >= 1.4


class TestCreateMealPlan:
    """Tests para create_meal_plan."""

    def test_create_basic_plan(self):
        """Debe crear plan básico."""
        result = create_meal_plan(daily_calories=2000)
        assert result["status"] == "created"
        assert "meal_plan" in result

    def test_create_4_meal_plan(self):
        """Debe crear plan de 4 comidas."""
        result = create_meal_plan(daily_calories=2000, meals_per_day=4)
        assert len(result["meal_plan"]) == 4

    def test_create_3_meal_plan(self):
        """Debe crear plan de 3 comidas."""
        result = create_meal_plan(daily_calories=2000, meals_per_day=3)
        assert len(result["meal_plan"]) == 3

    def test_plan_includes_totals(self):
        """Plan debe incluir totales diarios."""
        result = create_meal_plan(daily_calories=2000)
        assert "daily_totals" in result
        assert "protein" in result["daily_totals"]

    def test_plan_for_fat_loss(self):
        """Debe crear plan para fat loss."""
        result = create_meal_plan(
            daily_calories=1800,
            goal="fat_loss",
        )
        assert result["goal"] == "fat_loss"

    def test_meals_have_suggestions(self):
        """Comidas deben tener sugerencias."""
        result = create_meal_plan(daily_calories=2000)
        for meal in result["meal_plan"]:
            assert "suggestions" in meal
