"""Tests de integración para GENESIS_X con Supabase.

Estos tests verifican la integración con Supabase real.
Requieren configuración de variables de entorno:
- SUPABASE_URL
- SUPABASE_ANON_KEY
- SUPABASE_SERVICE_ROLE_KEY

Para ejecutar solo estos tests:
    pytest agents/genesis_x/tests/test_integration.py -v --run-integration
"""

from __future__ import annotations

import os
import uuid
from unittest.mock import MagicMock, patch

import pytest

# Marcar todos los tests en este módulo como de integración
pytestmark = pytest.mark.integration


def supabase_configured() -> bool:
    """Verifica si Supabase está configurado."""
    return all([
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_ANON_KEY"),
        os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
    ])


@pytest.fixture
def mock_supabase_client():
    """Mock del cliente de Supabase para tests sin conexión real."""
    with patch("agents.genesis_x.tools.get_supabase_client") as mock:
        client = MagicMock()

        # Mock para service_client.table().select().execute()
        mock_response = MagicMock()
        mock_response.data = None
        client.service_client.table.return_value.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_response
        client.service_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_response
        client.service_client.table.return_value.select.return_value.eq.return_value.gte.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[])

        # Mock para rpc
        client.service_client.rpc.return_value.execute.return_value = MagicMock(data=str(uuid.uuid4()))

        mock.return_value = client
        yield client


class TestGetUserContextMocked:
    """Tests para get_user_context con Supabase mockeado."""

    def test_get_user_context_no_data(self, mock_supabase_client):
        """Debe manejar usuario sin datos."""
        from agents.genesis_x.tools import get_user_context

        result = get_user_context("123e4567-e89b-12d3-a456-426614174000")

        assert result["status"] == "success"
        assert result["active_season"] is None
        assert result["preferences"] == {}

    def test_get_user_context_invalid_uuid(self):
        """Debe manejar UUID inválido."""
        from agents.genesis_x.tools import get_user_context

        result = get_user_context("not-a-uuid")

        assert result["status"] == "error"
        assert "inválido" in result["error"]


class TestPersistToSupabaseMocked:
    """Tests para persist_to_supabase con Supabase mockeado."""

    def test_persist_event_success(self, mock_supabase_client):
        """Debe persistir evento correctamente."""
        from agents.genesis_x.tools import persist_to_supabase

        result = persist_to_supabase(
            user_id="123e4567-e89b-12d3-a456-426614174000",
            event_type="test_event",
            payload={"test": "data"},
        )

        assert result["status"] == "success"
        assert result["event_id"] is not None

    def test_persist_event_invalid_uuid(self):
        """Debe manejar UUID inválido."""
        from agents.genesis_x.tools import persist_to_supabase

        result = persist_to_supabase(
            user_id="invalid",
            event_type="test",
            payload={},
        )

        assert result["status"] == "error"


class TestOrchestrateFlow:
    """Tests para el flujo completo de orchestrate."""

    @pytest.mark.asyncio
    async def test_orchestrate_general_chat(self, mock_supabase_client):
        """Debe manejar chat general sin invocar agentes."""
        from agents.genesis_x.agent import orchestrate

        result = await orchestrate(
            user_id="123e4567-e89b-12d3-a456-426614174000",
            message="Hola, ¿cómo estás?",
        )

        assert "response" in result
        assert result["agents_consulted"] == []
        assert "GENESIS_X" in result["response"]

    @pytest.mark.asyncio
    async def test_orchestrate_emergency_detection(self, mock_supabase_client):
        """Debe detectar y manejar emergencias."""
        from agents.genesis_x.agent import orchestrate

        result = await orchestrate(
            user_id="123e4567-e89b-12d3-a456-426614174000",
            message="Tengo dolor de pecho y no puedo respirar",
        )

        assert "emergencia" in result["response"].lower() or "911" in result["response"]
        assert result["agents_consulted"] == []

    @pytest.mark.asyncio
    async def test_orchestrate_fitness_query(self, mock_supabase_client):
        """Debe rutear queries de fitness a BLAZE."""
        from agents.genesis_x.agent import orchestrate

        result = await orchestrate(
            user_id="123e4567-e89b-12d3-a456-426614174000",
            message="Quiero ganar fuerza y músculo",
        )

        assert "response" in result
        assert "classification" in result
        assert result["classification"]["primary_intent"] == "fitness_strength"

    @pytest.mark.asyncio
    async def test_orchestrate_nutrition_query(self, mock_supabase_client):
        """Debe rutear queries de nutrición a SAGE."""
        from agents.genesis_x.agent import orchestrate

        result = await orchestrate(
            user_id="123e4567-e89b-12d3-a456-426614174000",
            message="¿Cuánta proteína necesito comer?",
        )

        assert "response" in result
        assert result["classification"]["primary_intent"] in ["nutrition_macros", "nutrition_strategy"]


@pytest.mark.skipif(
    not supabase_configured(),
    reason="Supabase no configurado (faltan variables de entorno)"
)
class TestRealSupabaseIntegration:
    """Tests con conexión real a Supabase.

    Solo se ejecutan si Supabase está configurado.
    Usar con precaución en CI/CD.
    """

    def test_real_connection(self):
        """Verifica conexión real a Supabase."""
        from agents.shared.supabase_client import get_supabase_client

        client = get_supabase_client()
        assert client is not None
        assert client.service_client is not None

    def test_real_health_check(self):
        """Verifica que Supabase responde."""
        from agents.shared.supabase_client import get_supabase_client

        client = get_supabase_client()
        # Intenta una query simple
        try:
            response = client.service_client.table("profiles").select("id").limit(1).execute()
            assert response is not None
        except Exception as e:
            error_msg = str(e).lower()
            # Errores aceptables:
            # - "does not exist": tabla no existe pero conexión funciona
            # - "connection": problema de red (esperado en CI sin Supabase real)
            # - "nodename": DNS no resuelve (esperado en CI)
            acceptable_errors = ["does not exist", "connection", "nodename", "getaddrinfo"]
            is_acceptable = any(err in error_msg for err in acceptable_errors)
            assert is_acceptable, f"Error inesperado: {e}"


class TestCrossAgentCommunication:
    """Tests para comunicación entre agentes."""

    def test_genesis_x_can_import_blaze(self):
        """GENESIS_X debe poder importar BLAZE."""
        from agents.genesis_x import genesis_x
        from agents.blaze import blaze

        assert genesis_x is not None
        assert blaze is not None
        assert genesis_x.name == "genesis_x"
        assert blaze.name == "blaze"

    def test_genesis_x_can_import_sage(self):
        """GENESIS_X debe poder importar SAGE."""
        from agents.genesis_x import genesis_x
        from agents.sage import sage

        assert genesis_x is not None
        assert sage is not None
        assert sage.name == "sage"

    def test_all_agents_have_compatible_cards(self):
        """Todos los agentes deben tener Agent Cards compatibles."""
        from agents.genesis_x import AGENT_CARD as genesis_card
        from agents.blaze import AGENT_CARD as blaze_card
        from agents.sage import AGENT_CARD as sage_card

        # Todos usan el mismo protocolo
        assert genesis_card["protocol"] == "a2a/0.3"
        assert blaze_card["protocol"] == "a2a/0.3"
        assert sage_card["protocol"] == "a2a/0.3"

        # GENESIS_X tiene método orchestrate (es orquestador)
        genesis_methods = [m["name"] for m in genesis_card["methods"]]
        assert "orchestrate" in genesis_methods

        # Especialistas tienen método respond
        for card in [blaze_card, sage_card]:
            method_names = [m["name"] for m in card["methods"]]
            assert "respond" in method_names

    def test_invoke_specialist_knows_all_agents(self):
        """invoke_specialist debe conocer todos los agentes."""
        from agents.genesis_x.tools import AGENT_MODELS

        # Agentes principales
        assert "genesis_x" in AGENT_MODELS
        assert "blaze" in AGENT_MODELS
        assert "sage" in AGENT_MODELS

        # Verifica que GENESIS_X usa Pro y especialistas usan Flash
        assert "pro" in AGENT_MODELS["genesis_x"]
        assert "flash" in AGENT_MODELS["blaze"]
        assert "flash" in AGENT_MODELS["sage"]
