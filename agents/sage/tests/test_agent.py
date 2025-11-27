"""Tests para el agente SAGE."""

from __future__ import annotations

from agents.sage.agent import (
    sage,
    root_agent,
    get_status,
    calculate_nutrition_plan,
    AGENT_CARD,
    AGENT_CONFIG,
)


class TestAgentConfiguration:
    """Tests para la configuración del agente."""

    def test_agent_exists(self):
        """El agente debe existir."""
        assert sage is not None

    def test_agent_name(self):
        """El agente debe tener el nombre correcto."""
        assert sage.name == "sage"

    def test_agent_model_is_flash(self):
        """El agente debe usar modelo Flash."""
        assert "flash" in sage.model.lower()

    def test_agent_has_tools(self):
        """El agente debe tener tools definidas."""
        assert sage.tools is not None
        assert len(sage.tools) > 0

    def test_agent_has_instruction(self):
        """El agente debe tener instruction."""
        assert sage.instruction is not None
        assert len(sage.instruction) > 100

    def test_root_agent_is_sage(self):
        """root_agent debe ser sage."""
        assert root_agent is sage


class TestAgentCard:
    """Tests para el Agent Card (A2A)."""

    def test_agent_card_has_required_fields(self):
        """Agent Card debe tener campos requeridos."""
        required_fields = ["name", "description", "version", "protocol", "capabilities", "methods", "limits"]
        for field in required_fields:
            assert field in AGENT_CARD, f"Campo {field} faltante"

    def test_agent_card_protocol(self):
        """Agent Card debe usar protocolo A2A v0.3."""
        assert AGENT_CARD["protocol"] == "a2a/0.3"

    def test_agent_card_has_domain(self):
        """Agent Card debe indicar dominio nutrition."""
        assert AGENT_CARD["domain"] == "nutrition"
        assert AGENT_CARD["specialty"] == "strategy"

    def test_agent_card_has_calculate_method(self):
        """Agent Card debe exponer método calculate_nutrition_plan."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "calculate_nutrition_plan" in method_names

    def test_agent_card_limits(self):
        """Agent Card debe tener límites apropiados."""
        limits = AGENT_CARD["limits"]
        assert limits["max_latency_ms"] == 2000
        assert limits["max_cost_per_invoke"] == 0.01


class TestAgentConfig:
    """Tests para AGENT_CONFIG."""

    def test_agent_config_domain(self):
        """AGENT_CONFIG debe tener domain=nutrition."""
        assert AGENT_CONFIG["domain"] == "nutrition"

    def test_agent_config_capabilities(self):
        """AGENT_CONFIG debe tener capabilities requeridas."""
        required = ["nutrition_planning", "diet_periodization", "goal_alignment"]
        for cap in required:
            assert cap in AGENT_CONFIG["capabilities"]


class TestGetStatus:
    """Tests para get_status."""

    def test_get_status_returns_healthy(self):
        """get_status debe retornar status=healthy."""
        status = get_status()
        assert status["status"] == "healthy"

    def test_get_status_includes_foods(self):
        """get_status debe incluir número de alimentos."""
        status = get_status()
        assert "foods_in_database" in status
        assert status["foods_in_database"] > 0

    def test_get_status_includes_categories(self):
        """get_status debe incluir categorías de alimentos."""
        status = get_status()
        assert "food_categories" in status
        assert "protein" in status["food_categories"]


class TestCalculateNutritionPlan:
    """Tests para calculate_nutrition_plan."""

    def test_basic_plan_calculation(self):
        """Debe calcular un plan nutricional básico."""
        plan = calculate_nutrition_plan(
            user_id="test-user",
            weight_kg=80,
            height_cm=180,
            age=35,
            sex="male",
            activity_level="moderate",
            goal="muscle_gain",
        )
        assert plan["user_id"] == "test-user"
        assert "tdee" in plan
        assert "macros" in plan
        assert "meal_distribution" in plan

    def test_fat_loss_plan(self):
        """Plan de fat loss debe tener déficit calórico."""
        plan = calculate_nutrition_plan(
            user_id="test-user",
            weight_kg=80,
            height_cm=180,
            age=35,
            sex="male",
            activity_level="moderate",
            goal="fat_loss",
        )
        assert plan["target_calories"] < plan["tdee"]["tdee"]

    def test_muscle_gain_plan(self):
        """Plan de muscle gain debe tener superávit."""
        plan = calculate_nutrition_plan(
            user_id="test-user",
            weight_kg=80,
            height_cm=180,
            age=35,
            sex="male",
            activity_level="moderate",
            goal="muscle_gain",
        )
        assert plan["target_calories"] > plan["tdee"]["tdee"]

    def test_plan_includes_recommendations(self):
        """Plan debe incluir recomendaciones."""
        plan = calculate_nutrition_plan(
            user_id="test-user",
            weight_kg=80,
            height_cm=180,
            age=35,
            sex="male",
            activity_level="moderate",
            goal="maintenance",
        )
        assert "recommendations" in plan
        assert len(plan["recommendations"]) > 0
