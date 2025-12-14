"""Tests for SupabaseClient.

These tests use mocks to avoid requiring a real Supabase connection.
"""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch


from agents.shared.supabase_client import (
    AgentEvent,
    Conversation,
    Message,
    SupabaseClient,
    SupabaseError,
)


# =============================================================================
# Model Tests
# =============================================================================


class TestMessage:
    """Tests for Message dataclass."""

    def test_from_dict_basic(self):
        """Should create Message from dict with required fields."""
        data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "conversation_id": "550e8400-e29b-41d4-a716-446655440001",
            "role": "user",
            "content": "Hello world",
            "created_at": "2025-12-13T10:00:00Z",
        }
        msg = Message.from_dict(data)

        assert msg.id == uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        assert msg.conversation_id == uuid.UUID("550e8400-e29b-41d4-a716-446655440001")
        assert msg.role == "user"
        assert msg.content == "Hello world"
        assert msg.agent_type is None
        assert msg.tokens_used is None
        assert msg.cost_usd is None

    def test_from_dict_with_optional_fields(self):
        """Should create Message with optional fields."""
        data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "conversation_id": "550e8400-e29b-41d4-a716-446655440001",
            "role": "agent",
            "content": "Response",
            "agent_type": "genesis_x",
            "tokens_used": 150,
            "cost_usd": "0.0045",
            "created_at": "2025-12-13T10:00:00+00:00",
        }
        msg = Message.from_dict(data)

        assert msg.agent_type == "genesis_x"
        assert msg.tokens_used == 150
        assert msg.cost_usd == 0.0045


class TestConversation:
    """Tests for Conversation dataclass."""

    def test_from_dict(self):
        """Should create Conversation from dict."""
        data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "user_id": "550e8400-e29b-41d4-a716-446655440001",
            "status": "active",
            "created_at": "2025-12-13T10:00:00Z",
        }
        conv = Conversation.from_dict(data)

        assert conv.id == uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        assert conv.user_id == uuid.UUID("550e8400-e29b-41d4-a716-446655440001")
        assert conv.status == "active"


class TestAgentEvent:
    """Tests for AgentEvent dataclass."""

    def test_from_dict_with_user(self):
        """Should create AgentEvent from dict with user_id."""
        data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "user_id": "550e8400-e29b-41d4-a716-446655440001",
            "agent_type": "blaze",
            "event_type": "workout_generated",
            "payload": {"workout_id": "123"},
            "created_at": "2025-12-13T10:00:00Z",
        }
        event = AgentEvent.from_dict(data)

        assert event.agent_type == "blaze"
        assert event.event_type == "workout_generated"
        assert event.payload == {"workout_id": "123"}

    def test_from_dict_without_user(self):
        """Should create AgentEvent without user_id."""
        data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "user_id": None,
            "agent_type": "genesis_x",
            "event_type": "system_startup",
            "created_at": "2025-12-13T10:00:00Z",
        }
        event = AgentEvent.from_dict(data)

        assert event.user_id is None
        assert event.payload == {}


# =============================================================================
# SupabaseClient Tests
# =============================================================================


class TestSupabaseClientInit:
    """Tests for SupabaseClient initialization."""

    @patch("agents.shared.supabase_client.create_client")
    @patch("agents.shared.supabase_client.get_settings")
    def test_creates_both_clients(self, mock_settings, mock_create):
        """Should create both anon and service role clients."""
        # Setup
        mock_config = MagicMock()
        mock_config.url = "https://test.supabase.co"
        mock_config.anon_key = "anon-key"
        mock_config.service_role_key = "service-key"
        mock_settings.return_value.supabase = mock_config

        mock_client = MagicMock()
        mock_create.return_value = mock_client

        # Execute
        client = SupabaseClient(config=mock_config)

        # Verify
        assert client is not None
        assert mock_create.call_count == 2
        mock_create.assert_any_call(
            supabase_url="https://test.supabase.co",
            supabase_key="anon-key",
        )
        mock_create.assert_any_call(
            supabase_url="https://test.supabase.co",
            supabase_key="service-key",
        )


class TestSupabaseClientAuth:
    """Tests for SupabaseClient authentication methods."""

    @patch("agents.shared.supabase_client.create_client")
    @patch("agents.shared.supabase_client.get_settings")
    def test_set_auth_session(self, mock_settings, mock_create):
        """Should call set_session with access and refresh tokens."""
        # Setup
        mock_config = MagicMock()
        mock_config.url = "https://test.supabase.co"
        mock_config.anon_key = "anon-key"
        mock_config.service_role_key = "service-key"
        mock_settings.return_value.supabase = mock_config

        mock_client = MagicMock()
        mock_create.return_value = mock_client

        client = SupabaseClient(config=mock_config)

        # Execute
        client.set_auth_session("access-token", "refresh-token")

        # Verify
        mock_client.auth.set_session.assert_called_once_with(
            "access-token", "refresh-token"
        )

    @patch("agents.shared.supabase_client.create_client")
    @patch("agents.shared.supabase_client.get_settings")
    def test_set_auth_session_without_refresh(self, mock_settings, mock_create):
        """Should allow empty refresh token."""
        # Setup
        mock_config = MagicMock()
        mock_config.url = "https://test.supabase.co"
        mock_config.anon_key = "anon-key"
        mock_config.service_role_key = "service-key"
        mock_settings.return_value.supabase = mock_config

        mock_client = MagicMock()
        mock_create.return_value = mock_client

        client = SupabaseClient(config=mock_config)

        # Execute
        client.set_auth_session("access-token")

        # Verify
        mock_client.auth.set_session.assert_called_once_with("access-token", "")


class TestSupabaseClientProperties:
    """Tests for SupabaseClient property access."""

    @patch("agents.shared.supabase_client.create_client")
    @patch("agents.shared.supabase_client.get_settings")
    def test_client_property_returns_anon_client(self, mock_settings, mock_create):
        """Should return anon client from client property."""
        mock_config = MagicMock()
        mock_config.url = "https://test.supabase.co"
        mock_config.anon_key = "anon-key"
        mock_config.service_role_key = "service-key"
        mock_settings.return_value.supabase = mock_config

        mock_anon = MagicMock(name="anon_client")
        mock_service = MagicMock(name="service_client")
        mock_create.side_effect = [mock_anon, mock_service]

        client = SupabaseClient(config=mock_config)

        assert client.client == mock_anon

    @patch("agents.shared.supabase_client.create_client")
    @patch("agents.shared.supabase_client.get_settings")
    def test_service_client_property(self, mock_settings, mock_create):
        """Should return service role client from service_client property."""
        mock_config = MagicMock()
        mock_config.url = "https://test.supabase.co"
        mock_config.anon_key = "anon-key"
        mock_config.service_role_key = "service-key"
        mock_settings.return_value.supabase = mock_config

        mock_anon = MagicMock(name="anon_client")
        mock_service = MagicMock(name="service_client")
        mock_create.side_effect = [mock_anon, mock_service]

        client = SupabaseClient(config=mock_config)

        assert client.service_client == mock_service


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestSupabaseErrors:
    """Tests for Supabase error classes."""

    def test_supabase_error_is_runtime_error(self):
        """SupabaseError should be a RuntimeError."""
        err = SupabaseError("test error")
        assert isinstance(err, RuntimeError)
        assert str(err) == "test error"

    def test_error_hierarchy(self):
        """Error classes should have correct hierarchy."""
        from agents.shared.supabase_client import (
            SupabaseAuthError,
            SupabaseRLSError,
        )

        assert issubclass(SupabaseAuthError, SupabaseError)
        assert issubclass(SupabaseRLSError, SupabaseError)
