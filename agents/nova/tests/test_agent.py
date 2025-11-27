"""Tests para el agente NOVA."""

from __future__ import annotations

from agents.nova.agent import (
    nova,
    root_agent,
    get_status,
    quick_recommendation,
    quick_safety_check,
    AGENT_CARD,
    AGENT_CONFIG,
)


class TestAgentConfiguration:
    """Tests para la configuración del agente."""

    def test_agent_exists(self):
        """El agente debe existir."""
        assert nova is not None

    def test_agent_name(self):
        """El agente debe tener el nombre correcto."""
        assert nova.name == "nova"

    def test_agent_model_is_flash(self):
        """El agente debe usar modelo Flash (no Pro)."""
        assert "flash" in nova.model.lower()

    def test_agent_has_tools(self):
        """El agente debe tener tools definidas."""
        assert nova.tools is not None
        assert len(nova.tools) > 0

    def test_agent_has_5_tools(self):
        """El agente debe tener exactamente 5 tools."""
        assert len(nova.tools) == 5

    def test_agent_has_instruction(self):
        """El agente debe tener instruction (system prompt)."""
        assert nova.instruction is not None
        assert len(nova.instruction) > 100

    def test_root_agent_is_nova(self):
        """root_agent debe ser nova."""
        assert root_agent is nova

    def test_agent_output_key(self):
        """El agente debe tener output_key definido."""
        assert nova.output_key == "nova_response"


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
        assert AGENT_CARD["specialty"] == "supplementation"

    def test_agent_card_has_recommend_supplements_method(self):
        """Agent Card debe exponer método recommend_supplements."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "recommend_supplements" in method_names

    def test_agent_card_has_design_stack_method(self):
        """Agent Card debe exponer método design_stack."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "design_stack" in method_names

    def test_agent_card_has_create_timing_protocol_method(self):
        """Agent Card debe exponer método create_timing_protocol."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "create_timing_protocol" in method_names

    def test_agent_card_has_check_interactions_method(self):
        """Agent Card debe exponer método check_interactions."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "check_interactions" in method_names

    def test_agent_card_has_grade_evidence_method(self):
        """Agent Card debe exponer método grade_evidence."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "grade_evidence" in method_names

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
        """AGENT_CONFIG debe tener domain=nutrition."""
        assert AGENT_CONFIG["domain"] == "nutrition"

    def test_agent_config_specialty(self):
        """AGENT_CONFIG debe tener specialty correcta."""
        assert AGENT_CONFIG["specialty"] == "supplementation"

    def test_agent_config_capabilities(self):
        """AGENT_CONFIG debe tener capabilities requeridas."""
        required_capabilities = [
            "supplement_recommendations",
            "stack_design",
            "timing_protocols",
            "interaction_checking",
            "evidence_grading",
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
        """get_status debe indicar agente nova."""
        status = get_status()
        assert status["agent"] == "nova"

    def test_get_status_includes_version(self):
        """get_status debe incluir versión."""
        status = get_status()
        assert "version" in status
        assert status["version"] == AGENT_CARD["version"]

    def test_get_status_includes_supplements_count(self):
        """get_status debe incluir conteo de suplementos."""
        status = get_status()
        assert "supplements_in_database" in status
        assert status["supplements_in_database"] > 0

    def test_get_status_includes_goals_supported(self):
        """get_status debe incluir objetivos soportados."""
        status = get_status()
        assert "goals_supported" in status
        assert len(status["goals_supported"]) > 0

    def test_get_status_includes_timing_windows(self):
        """get_status debe incluir ventanas de timing."""
        status = get_status()
        assert "timing_windows" in status
        assert len(status["timing_windows"]) > 0

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


class TestQuickRecommendation:
    """Tests para quick_recommendation helper."""

    def test_quick_recommendation_basic(self):
        """Debe crear recomendación con parámetros básicos."""
        result = quick_recommendation(goal="muscle_gain")
        assert result["status"] == "recommended"
        assert "recommendations" in result

    def test_quick_recommendation_with_budget(self):
        """Debe respetar presupuesto."""
        result = quick_recommendation(
            goal="sleep",
            budget=30,
        )
        assert result["status"] == "recommended"
        assert result["estimated_monthly_cost_usd"] <= 30

    def test_quick_recommendation_limits_to_3(self):
        """Debe limitar a 3 suplementos."""
        result = quick_recommendation(goal="performance")
        assert len(result["recommendations"]) <= 3


class TestQuickSafetyCheck:
    """Tests para quick_safety_check helper."""

    def test_quick_safety_check_basic(self):
        """Debe verificar seguridad."""
        result = quick_safety_check(
            supplements=["vitamin_d3", "magnesium"]
        )
        assert result["status"] == "checked"
        assert "overall_safety" in result

    def test_quick_safety_check_detects_interactions(self):
        """Debe detectar interacciones si existen."""
        result = quick_safety_check(
            supplements=["omega3", "vitamin_k2"]
        )
        assert "total_interactions" in result or "total_synergies" in result


class TestAgentIntegration:
    """Tests de integración para verificar coherencia del agente."""

    def test_agent_card_methods_match_tools(self):
        """Los métodos del Agent Card deben corresponder a las tools."""
        method_names = {m["name"] for m in AGENT_CARD["methods"]}
        expected_methods = {
            "recommend_supplements",
            "design_stack",
            "create_timing_protocol",
            "check_interactions",
            "grade_evidence",
        }
        assert method_names == expected_methods

    def test_agent_config_capabilities_count(self):
        """AGENT_CONFIG debe tener 5 capabilities."""
        assert len(AGENT_CONFIG["capabilities"]) == 5

    def test_agent_description_mentions_supplements(self):
        """La descripción del agente debe mencionar suplementos."""
        assert "suplementación" in nova.description.lower() or "supplement" in nova.description.lower()

    def test_agent_description_mentions_evidence(self):
        """La descripción del agente debe mencionar evidencia."""
        assert "evidencia" in nova.description.lower() or "evidence" in nova.description.lower()

    def test_get_status_consistency(self):
        """get_status debe ser consistente con AGENT_CARD."""
        status = get_status()
        assert status["version"] == AGENT_CARD["version"]
        assert set(status["capabilities"]) == set(AGENT_CONFIG["capabilities"])
