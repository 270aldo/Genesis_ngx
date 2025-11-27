"""Tests para el agente METABOL."""

from __future__ import annotations

from agents.metabol.agent import (
    metabol,
    root_agent,
    get_status,
    calculate_user_tdee,
    AGENT_CARD,
    AGENT_CONFIG,
)


class TestAgentConfiguration:
    """Tests para la configuracion del agente."""

    def test_agent_exists(self):
        """El agente debe existir."""
        assert metabol is not None

    def test_agent_name(self):
        """El agente debe tener el nombre correcto."""
        assert metabol.name == "metabol"

    def test_agent_model_is_flash(self):
        """El agente debe usar modelo Flash (no Pro)."""
        assert "flash" in metabol.model.lower()

    def test_agent_has_tools(self):
        """El agente debe tener tools definidas."""
        assert metabol.tools is not None
        assert len(metabol.tools) > 0

    def test_agent_has_instruction(self):
        """El agente debe tener instruction (system prompt)."""
        assert metabol.instruction is not None
        assert len(metabol.instruction) > 100

    def test_root_agent_is_metabol(self):
        """root_agent debe ser metabol."""
        assert root_agent is metabol


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
        assert AGENT_CARD["specialty"] == "metabolism"

    def test_agent_card_has_calculate_tdee_method(self):
        """Agent Card debe exponer metodo calculate_tdee."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "calculate_tdee" in method_names

    def test_agent_card_has_assess_metabolic_rate_method(self):
        """Agent Card debe exponer metodo assess_metabolic_rate."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "assess_metabolic_rate" in method_names

    def test_agent_card_has_plan_nutrient_timing_method(self):
        """Agent Card debe exponer metodo plan_nutrient_timing."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "plan_nutrient_timing" in method_names

    def test_agent_card_has_detect_adaptation_method(self):
        """Agent Card debe exponer metodo detect_metabolic_adaptation."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "detect_metabolic_adaptation" in method_names

    def test_agent_card_has_assess_insulin_method(self):
        """Agent Card debe exponer metodo assess_insulin_sensitivity."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "assess_insulin_sensitivity" in method_names

    def test_agent_card_limits(self):
        """Agent Card debe tener limites apropiados para Flash."""
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
        assert AGENT_CONFIG["specialty"] == "metabolism"

    def test_agent_config_capabilities(self):
        """AGENT_CONFIG debe tener capabilities requeridas."""
        required_capabilities = [
            "metabolic_assessment",
            "tdee_calculation",
            "insulin_sensitivity",
            "nutrient_timing",
            "metabolic_adaptation",
        ]
        for cap in required_capabilities:
            assert cap in AGENT_CONFIG["capabilities"]


class TestGetStatus:
    """Tests para get_status."""

    def test_get_status_returns_healthy(self):
        """get_status debe retornar status=healthy."""
        status = get_status()
        assert status["status"] == "healthy"

    def test_get_status_includes_activity_levels(self):
        """get_status debe incluir niveles de actividad."""
        status = get_status()
        assert "activity_levels" in status
        assert len(status["activity_levels"]) > 0

    def test_get_status_includes_formulas(self):
        """get_status debe incluir formulas disponibles."""
        status = get_status()
        assert "formulas_available" in status
        assert len(status["formulas_available"]) > 0

    def test_get_status_includes_goals(self):
        """get_status debe incluir objetivos soportados."""
        status = get_status()
        assert "goals_supported" in status
        assert len(status["goals_supported"]) > 0


class TestCalculateUserTdee:
    """Tests para calculate_user_tdee."""

    def test_calculate_basic_tdee(self):
        """Debe calcular TDEE basico."""
        result = calculate_user_tdee(
            weight_kg=75.0,
            height_cm=175,
            age=35,
            sex="male",
            activity_level="moderate",
        )
        assert result["status"] == "calculated"
        assert "result" in result
        assert result["result"]["daily_calories"] > 0

    def test_calculate_tdee_for_fat_loss(self):
        """Debe calcular TDEE para perdida de grasa."""
        result = calculate_user_tdee(
            weight_kg=80.0,
            height_cm=170,
            age=40,
            goal="fat_loss",
        )
        assert result["status"] == "calculated"
        assert result["calculations"]["adjustment_type"] == "deficit"

    def test_calculate_tdee_for_muscle_gain(self):
        """Debe calcular TDEE para ganancia muscular."""
        result = calculate_user_tdee(
            weight_kg=70.0,
            height_cm=180,
            age=30,
            goal="muscle_gain",
        )
        assert result["calculations"]["adjustment_type"] == "surplus"

    def test_tdee_includes_range(self):
        """TDEE debe incluir rango."""
        result = calculate_user_tdee(
            weight_kg=75.0,
            height_cm=175,
            age=35,
        )
        assert "range" in result["result"]
        assert "low" in result["result"]["range"]
        assert "high" in result["result"]["range"]
