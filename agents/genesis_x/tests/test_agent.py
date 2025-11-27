"""Tests para el agente GENESIS_X.

Cubre:
- Configuración del agente
- Agent Card
- Función orchestrate
- Función get_status
"""

from __future__ import annotations


from agents.genesis_x.agent import (
    genesis_x,
    root_agent,
    get_status,
    AGENT_CARD,
    AGENT_CONFIG,
)


class TestAgentConfiguration:
    """Tests para la configuración del agente."""

    def test_agent_exists(self):
        """El agente debe existir."""
        assert genesis_x is not None

    def test_agent_name(self):
        """El agente debe tener el nombre correcto."""
        assert genesis_x.name == "genesis_x"

    def test_agent_model(self):
        """El agente debe usar el modelo correcto (Pro)."""
        assert "pro" in genesis_x.model.lower() or "2.5" in genesis_x.model

    def test_agent_has_tools(self):
        """El agente debe tener tools definidas."""
        assert genesis_x.tools is not None
        assert len(genesis_x.tools) > 0

    def test_agent_has_instruction(self):
        """El agente debe tener instruction (system prompt)."""
        assert genesis_x.instruction is not None
        assert len(genesis_x.instruction) > 100  # Prompt sustancial

    def test_root_agent_is_genesis_x(self):
        """root_agent debe ser genesis_x."""
        assert root_agent is genesis_x


class TestAgentCard:
    """Tests para el Agent Card (A2A)."""

    def test_agent_card_has_required_fields(self):
        """Agent Card debe tener campos requeridos."""
        required_fields = [
            "name",
            "description",
            "version",
            "protocol",
            "capabilities",
            "methods",
            "limits",
        ]

        for field in required_fields:
            assert field in AGENT_CARD, f"Campo {field} faltante en AGENT_CARD"

    def test_agent_card_protocol(self):
        """Agent Card debe usar protocolo A2A v0.3."""
        assert AGENT_CARD["protocol"] == "a2a/0.3"

    def test_agent_card_has_orchestrate_method(self):
        """Agent Card debe exponer método orchestrate."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "orchestrate" in method_names

    def test_agent_card_has_classify_intent_method(self):
        """Agent Card debe exponer método classify_intent."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "classify_intent" in method_names

    def test_agent_card_limits(self):
        """Agent Card debe tener límites definidos."""
        limits = AGENT_CARD["limits"]

        assert limits["max_input_tokens"] == 50000
        assert limits["max_output_tokens"] == 4000
        assert limits["max_latency_ms"] == 6000
        assert limits["max_cost_per_invoke"] == 0.05

    def test_agent_card_privacy(self):
        """Agent Card debe indicar que NO maneja PHI/PII."""
        privacy = AGENT_CARD["privacy"]

        assert privacy["pii"] is False
        assert privacy["phi"] is False


class TestAgentConfig:
    """Tests para AGENT_CONFIG."""

    def test_agent_config_role(self):
        """AGENT_CONFIG debe tener role=orchestrator."""
        assert AGENT_CONFIG["role"] == "orchestrator"

    def test_agent_config_capabilities(self):
        """AGENT_CONFIG debe tener capabilities requeridas."""
        required_capabilities = [
            "intent_classification",
            "multi_agent_routing",
            "consensus_building",
        ]

        for cap in required_capabilities:
            assert cap in AGENT_CONFIG["capabilities"]

    def test_agent_config_limits_match_card(self):
        """Límites en AGENT_CONFIG deben coincidir con AGENT_CARD."""
        config_limits = AGENT_CONFIG["limits"]
        card_limits = AGENT_CARD["limits"]

        assert config_limits["max_input_tokens"] == card_limits["max_input_tokens"]
        assert config_limits["max_output_tokens"] == card_limits["max_output_tokens"]


class TestGetStatus:
    """Tests para get_status."""

    def test_get_status_returns_healthy(self):
        """get_status debe retornar status=healthy."""
        status = get_status()

        assert status["status"] == "healthy"

    def test_get_status_includes_version(self):
        """get_status debe incluir versión."""
        status = get_status()

        assert "version" in status
        assert status["version"] == AGENT_CARD["version"]

    def test_get_status_includes_available_agents(self):
        """get_status debe listar agentes disponibles."""
        status = get_status()

        assert "available_agents" in status
        assert len(status["available_agents"]) > 0
        assert "genesis_x" in status["available_agents"]
        assert "blaze" in status["available_agents"]

    def test_get_status_includes_model(self):
        """get_status debe incluir modelo usado."""
        status = get_status()

        assert "model" in status
        assert "pro" in status["model"].lower() or "2.5" in status["model"]


class TestOrchestratePlaceholder:
    """Tests básicos para orchestrate (sin llamadas reales a Supabase)."""

    # Nota: Tests de integración completos requieren mock de Supabase
    # Estos tests verifican la estructura de la función

    def test_orchestrate_function_exists(self):
        """La función orchestrate debe existir."""
        from agents.genesis_x.agent import orchestrate

        assert orchestrate is not None
        assert callable(orchestrate)

    def test_orchestrate_is_async(self):
        """orchestrate debe ser una función async."""
        import asyncio
        from agents.genesis_x.agent import orchestrate

        assert asyncio.iscoroutinefunction(orchestrate)
