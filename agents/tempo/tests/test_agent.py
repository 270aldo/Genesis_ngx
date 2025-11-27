"""Tests para el agente TEMPO."""

from __future__ import annotations

from agents.tempo.agent import (
    tempo,
    root_agent,
    get_status,
    generate_session,
    AGENT_CARD,
    AGENT_CONFIG,
)


class TestAgentConfiguration:
    """Tests para la configuracion del agente."""

    def test_agent_exists(self):
        """El agente debe existir."""
        assert tempo is not None

    def test_agent_name(self):
        """El agente debe tener el nombre correcto."""
        assert tempo.name == "tempo"

    def test_agent_model_is_flash(self):
        """El agente debe usar modelo Flash (no Pro)."""
        assert "flash" in tempo.model.lower()

    def test_agent_has_tools(self):
        """El agente debe tener tools definidas."""
        assert tempo.tools is not None
        assert len(tempo.tools) > 0

    def test_agent_has_instruction(self):
        """El agente debe tener instruction (system prompt)."""
        assert tempo.instruction is not None
        assert len(tempo.instruction) > 100

    def test_root_agent_is_tempo(self):
        """root_agent debe ser tempo."""
        assert root_agent is tempo


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
        assert AGENT_CARD["specialty"] == "cardio_endurance"

    def test_agent_card_has_calculate_hr_zones_method(self):
        """Agent Card debe exponer metodo calculate_hr_zones."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "calculate_hr_zones" in method_names

    def test_agent_card_has_generate_session_method(self):
        """Agent Card debe exponer metodo generate_session."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "generate_session" in method_names

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
        assert AGENT_CONFIG["specialty"] == "cardio_endurance"

    def test_agent_config_capabilities(self):
        """AGENT_CONFIG debe tener capabilities requeridas."""
        required_capabilities = [
            "heart_rate_zones",
            "hiit_programming",
            "liss_endurance",
        ]
        for cap in required_capabilities:
            assert cap in AGENT_CONFIG["capabilities"]


class TestGetStatus:
    """Tests para get_status."""

    def test_get_status_returns_healthy(self):
        """get_status debe retornar status=healthy."""
        status = get_status()
        assert status["status"] == "healthy"

    def test_get_status_includes_sessions(self):
        """get_status debe incluir sesiones disponibles."""
        status = get_status()
        assert "sessions_available" in status
        assert len(status["sessions_available"]) > 0

    def test_get_status_includes_hr_zones(self):
        """get_status debe incluir zonas HR disponibles."""
        status = get_status()
        assert "hr_zones_available" in status
        assert len(status["hr_zones_available"]) > 0


class TestGenerateSession:
    """Tests para generate_session."""

    def test_generate_hiit_session(self):
        """Debe generar una sesion HIIT."""
        session = generate_session(
            session_type="hiit_intermediate",
            age=35,
        )
        assert session["type"] == "hiit"
        assert "main_work" in session
        assert "warmup" in session
        assert "cooldown" in session

    def test_generate_liss_session(self):
        """Debe generar una sesion LISS."""
        session = generate_session(
            session_type="liss_fat_burn",
            age=40,
        )
        assert session["type"] == "liss"
        assert "main_work" in session

    def test_session_includes_hr_zones(self):
        """Sesion debe incluir zonas HR."""
        session = generate_session(
            session_type="hiit_intermediate",
            age=35,
        )
        assert "hr_zones" in session
        assert "zone_1" in session["hr_zones"]
        assert "zone_5" in session["hr_zones"]

    def test_session_includes_notes(self):
        """Sesion debe incluir notas."""
        session = generate_session(
            session_type="hiit_intermediate",
            age=35,
        )
        assert "notes" in session
        assert len(session["notes"]) > 0

    def test_session_respects_age(self):
        """Sesion debe calcular zonas HR segun edad."""
        session_young = generate_session(session_type="hiit_intermediate", age=25)
        session_old = generate_session(session_type="hiit_intermediate", age=55)
        # Persona joven tiene max HR mas alto
        young_max = max(z["max_hr"] for z in session_young["hr_zones"].values())
        old_max = max(z["max_hr"] for z in session_old["hr_zones"].values())
        assert young_max > old_max
