"""Tests para el agente LUNA."""

from __future__ import annotations

from datetime import datetime, timedelta

from agents.luna.agent import (
    luna,
    root_agent,
    get_status,
    quick_phase_check,
    quick_recommendations,
    AGENT_CARD,
    AGENT_CONFIG,
)


class TestAgentConfiguration:
    """Tests para la configuración del agente."""

    def test_agent_exists(self):
        """El agente debe existir."""
        assert luna is not None

    def test_agent_name(self):
        """El agente debe tener el nombre correcto."""
        assert luna.name == "luna"

    def test_agent_model_is_flash(self):
        """El agente debe usar modelo Flash (no Pro)."""
        assert "flash" in luna.model.lower()

    def test_agent_has_tools(self):
        """El agente debe tener tools definidas."""
        assert luna.tools is not None
        assert len(luna.tools) > 0

    def test_agent_has_5_tools(self):
        """El agente debe tener exactamente 5 tools."""
        assert len(luna.tools) == 5

    def test_agent_has_instruction(self):
        """El agente debe tener instruction (system prompt)."""
        assert luna.instruction is not None
        assert len(luna.instruction) > 100

    def test_root_agent_is_luna(self):
        """root_agent debe ser luna."""
        assert root_agent is luna

    def test_agent_output_key(self):
        """El agente debe tener output_key definido."""
        assert luna.output_key == "luna_response"


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
        """Agent Card debe indicar dominio womens_health."""
        assert AGENT_CARD["domain"] == "womens_health"
        assert AGENT_CARD["specialty"] == "female_physiology"

    def test_agent_card_has_track_cycle_method(self):
        """Agent Card debe exponer método track_cycle."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "track_cycle" in method_names

    def test_agent_card_has_get_phase_recommendations_method(self):
        """Agent Card debe exponer método get_phase_recommendations."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "get_phase_recommendations" in method_names

    def test_agent_card_has_analyze_symptoms_method(self):
        """Agent Card debe exponer método analyze_symptoms."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "analyze_symptoms" in method_names

    def test_agent_card_has_create_cycle_plan_method(self):
        """Agent Card debe exponer método create_cycle_plan."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "create_cycle_plan" in method_names

    def test_agent_card_has_assess_hormonal_health_method(self):
        """Agent Card debe exponer método assess_hormonal_health."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "assess_hormonal_health" in method_names

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
        """AGENT_CONFIG debe tener domain=womens_health."""
        assert AGENT_CONFIG["domain"] == "womens_health"

    def test_agent_config_specialty(self):
        """AGENT_CONFIG debe tener specialty correcta."""
        assert AGENT_CONFIG["specialty"] == "female_physiology"

    def test_agent_config_capabilities(self):
        """AGENT_CONFIG debe tener capabilities requeridas."""
        required_capabilities = [
            "cycle_tracking",
            "hormonal_considerations",
            "perimenopause_support",
            "phase_optimization",
            "symptom_management",
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
        """get_status debe indicar agente luna."""
        status = get_status()
        assert status["agent"] == "luna"

    def test_get_status_includes_version(self):
        """get_status debe incluir versión."""
        status = get_status()
        assert "version" in status
        assert status["version"] == AGENT_CARD["version"]

    def test_get_status_includes_phases_supported(self):
        """get_status debe incluir fases soportadas."""
        status = get_status()
        assert "phases_supported" in status
        assert len(status["phases_supported"]) == 4

    def test_get_status_includes_symptoms_tracked(self):
        """get_status debe incluir síntomas trackeados."""
        status = get_status()
        assert "symptoms_tracked" in status
        assert len(status["symptoms_tracked"]) > 0

    def test_get_status_includes_training_phases(self):
        """get_status debe incluir fases de entrenamiento."""
        status = get_status()
        assert "training_phases" in status
        assert len(status["training_phases"]) == 4

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


class TestQuickPhaseCheck:
    """Tests para quick_phase_check helper."""

    def test_quick_phase_check_basic(self):
        """Debe verificar fase con parámetros básicos."""
        today = datetime.now()
        last_period = (today - timedelta(days=10)).strftime("%Y-%m-%d")

        result = quick_phase_check(last_period=last_period)
        assert result["status"] == "tracked"
        assert "current_phase" in result

    def test_quick_phase_check_with_cycle_length(self):
        """Debe respetar duración del ciclo."""
        today = datetime.now()
        last_period = (today - timedelta(days=10)).strftime("%Y-%m-%d")

        result = quick_phase_check(
            last_period=last_period,
            cycle_length=30,
        )
        assert result["status"] == "tracked"
        assert result["cycle_length"] == 30


class TestQuickRecommendations:
    """Tests para quick_recommendations helper."""

    def test_quick_recommendations_basic(self):
        """Debe dar recomendaciones básicas."""
        result = quick_recommendations(phase="menstrual")
        assert result["status"] == "recommended"
        assert "training_recommendations" in result

    def test_quick_recommendations_all_phases(self):
        """Debe dar recomendaciones para todas las fases."""
        for phase in ["menstrual", "follicular", "ovulatory", "luteal"]:
            result = quick_recommendations(phase=phase)
            assert result["status"] == "recommended"


class TestAgentIntegration:
    """Tests de integración para verificar coherencia del agente."""

    def test_agent_card_methods_match_tools(self):
        """Los métodos del Agent Card deben corresponder a las tools."""
        method_names = {m["name"] for m in AGENT_CARD["methods"]}
        expected_methods = {
            "track_cycle",
            "get_phase_recommendations",
            "analyze_symptoms",
            "create_cycle_plan",
            "assess_hormonal_health",
        }
        assert method_names == expected_methods

    def test_agent_config_capabilities_count(self):
        """AGENT_CONFIG debe tener 5 capabilities."""
        assert len(AGENT_CONFIG["capabilities"]) == 5

    def test_agent_description_mentions_cycle(self):
        """La descripción del agente debe mencionar ciclo."""
        assert "ciclo" in luna.description.lower() or "cycle" in luna.description.lower()

    def test_agent_description_mentions_hormonal(self):
        """La descripción del agente debe mencionar hormonal."""
        assert "hormonal" in luna.description.lower()

    def test_get_status_consistency(self):
        """get_status debe ser consistente con AGENT_CARD."""
        status = get_status()
        assert status["version"] == AGENT_CARD["version"]
        assert set(status["capabilities"]) == set(AGENT_CONFIG["capabilities"])
