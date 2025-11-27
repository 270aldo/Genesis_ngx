"""Tests para el agente WAVE."""

from __future__ import annotations

from agents.wave.agent import (
    wave,
    root_agent,
    get_status,
    generate_protocol,
    AGENT_CARD,
    AGENT_CONFIG,
)


class TestAgentConfiguration:
    """Tests para la configuracion del agente."""

    def test_agent_exists(self):
        """El agente debe existir."""
        assert wave is not None

    def test_agent_name(self):
        """El agente debe tener el nombre correcto."""
        assert wave.name == "wave"

    def test_agent_model_is_flash(self):
        """El agente debe usar modelo Flash (no Pro)."""
        assert "flash" in wave.model.lower()

    def test_agent_has_tools(self):
        """El agente debe tener tools definidas."""
        assert wave.tools is not None
        assert len(wave.tools) > 0

    def test_agent_has_instruction(self):
        """El agente debe tener instruction (system prompt)."""
        assert wave.instruction is not None
        assert len(wave.instruction) > 100

    def test_root_agent_is_wave(self):
        """root_agent debe ser wave."""
        assert root_agent is wave


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
        """Agent Card debe indicar dominio fitness."""
        assert AGENT_CARD["domain"] == "fitness"
        assert AGENT_CARD["specialty"] == "recovery_rest"

    def test_agent_card_has_assess_recovery_method(self):
        """Agent Card debe exponer metodo assess_recovery."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "assess_recovery" in method_names

    def test_agent_card_has_generate_protocol_method(self):
        """Agent Card debe exponer metodo generate_protocol."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "generate_protocol" in method_names

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
        """AGENT_CONFIG debe tener domain=fitness."""
        assert AGENT_CONFIG["domain"] == "fitness"

    def test_agent_config_specialty(self):
        """AGENT_CONFIG debe tener specialty correcta."""
        assert AGENT_CONFIG["specialty"] == "recovery_rest"

    def test_agent_config_capabilities(self):
        """AGENT_CONFIG debe tener capabilities requeridas."""
        required_capabilities = [
            "recovery_assessment",
            "sleep_optimization",
            "deload_programming",
        ]
        for cap in required_capabilities:
            assert cap in AGENT_CONFIG["capabilities"]


class TestGetStatus:
    """Tests para get_status."""

    def test_get_status_returns_healthy(self):
        """get_status debe retornar status=healthy."""
        status = get_status()
        assert status["status"] == "healthy"

    def test_get_status_includes_techniques(self):
        """get_status debe incluir tecnicas disponibles."""
        status = get_status()
        assert "techniques_available" in status
        assert len(status["techniques_available"]) > 0

    def test_get_status_includes_deload_protocols(self):
        """get_status debe incluir protocolos de deload."""
        status = get_status()
        assert "deload_protocols_available" in status
        assert len(status["deload_protocols_available"]) > 0


class TestGenerateProtocol:
    """Tests para generate_protocol."""

    def test_generate_basic_protocol(self):
        """Debe generar un protocolo basico."""
        protocol = generate_protocol(
            fatigue_level="moderate",
            training_type="strength",
        )
        assert protocol["fatigue_level"] == "moderate"
        assert "protocol_techniques" in protocol
        assert "sleep_recommendations" in protocol

    def test_generate_high_fatigue_protocol(self):
        """Debe generar protocolo para fatiga alta."""
        protocol = generate_protocol(
            fatigue_level="high",
            time_available_minutes=30,
        )
        assert protocol["fatigue_level"] == "high"
        # Debe incluir tecnicas de recuperacion
        assert len(protocol["protocol_techniques"]) > 0

    def test_protocol_respects_time_limit(self):
        """Protocolo debe respetar limite de tiempo."""
        protocol = generate_protocol(
            fatigue_level="moderate",
            time_available_minutes=15,
        )
        assert protocol["total_duration_minutes"] <= 15

    def test_protocol_includes_notes(self):
        """Protocolo debe incluir notas generales."""
        protocol = generate_protocol(fatigue_level="moderate")
        assert "general_notes" in protocol
        assert len(protocol["general_notes"]) > 0
