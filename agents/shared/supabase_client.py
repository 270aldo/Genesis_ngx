"""Cliente para Supabase con soporte para RPCs, RLS y Realtime.

Características:
- Autenticación con Service Role y User JWT
- RPCs para agentes (agent_append_message, agent_log_event)
- Queries con RLS automático
- Manejo de errores y reintentos
- Type hints para mejor DX
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from supabase import Client, create_client
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from agents.shared.config import SupabaseConfig, get_settings


class SupabaseError(RuntimeError):
    """Error base para operaciones con Supabase."""


class SupabaseAuthError(SupabaseError):
    """Error de autenticación."""


class SupabaseRLSError(SupabaseError):
    """Error de Row Level Security."""


@dataclass
class Message:
    """Modelo de mensaje."""

    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str  # 'user', 'agent', 'system'
    content: str
    agent_type: Optional[str] = None
    tokens_used: Optional[int] = None
    cost_usd: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Message":
        """Crea un Message desde un diccionario."""
        return cls(
            id=uuid.UUID(data["id"]),
            conversation_id=uuid.UUID(data["conversation_id"]),
            role=data["role"],
            content=data["content"],
            agent_type=data.get("agent_type"),
            tokens_used=data.get("tokens_used"),
            cost_usd=float(data["cost_usd"]) if data.get("cost_usd") else None,
            created_at=datetime.fromisoformat(
                data["created_at"].replace("Z", "+00:00")
            ),
        )


@dataclass
class Conversation:
    """Modelo de conversación."""

    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Conversation":
        """Crea una Conversation desde un diccionario."""
        return cls(
            id=uuid.UUID(data["id"]),
            user_id=uuid.UUID(data["user_id"]),
            status=data["status"],
            created_at=datetime.fromisoformat(
                data["created_at"].replace("Z", "+00:00")
            ),
        )


@dataclass
class AgentEvent:
    """Modelo de evento de agente."""

    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    agent_type: str
    event_type: str
    payload: dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentEvent":
        """Crea un AgentEvent desde un diccionario."""
        return cls(
            id=uuid.UUID(data["id"]),
            user_id=uuid.UUID(data["user_id"]) if data.get("user_id") else None,
            agent_type=data["agent_type"],
            event_type=data["event_type"],
            payload=data.get("payload", {}),
            created_at=datetime.fromisoformat(
                data["created_at"].replace("Z", "+00:00")
            ),
        )


@dataclass
class SupabaseClient:
    """Cliente asíncrono para Supabase."""

    config: SupabaseConfig = field(default_factory=lambda: get_settings().supabase)
    _client: Optional[Client] = field(default=None, init=False)
    _service_client: Optional[Client] = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Inicializa los clientes."""
        # Cliente con anon key (para operaciones de usuario)
        self._client = create_client(
            supabase_url=self.config.url,
            supabase_key=self.config.anon_key,
        )

        # Cliente con service role (para operaciones de backend)
        self._service_client = create_client(
            supabase_url=self.config.url,
            supabase_key=self.config.service_role_key,
        )

    @property
    def client(self) -> Client:
        """Cliente principal (con anon key)."""
        if not self._client:
            raise SupabaseError("Cliente no inicializado")
        return self._client

    @property
    def service_client(self) -> Client:
        """Cliente con service role (bypass RLS)."""
        if not self._service_client:
            raise SupabaseError("Service client no inicializado")
        return self._service_client

    def set_auth_token(self, token: str) -> None:
        """Configura el token de autenticación para el usuario.

        Args:
            token: JWT token de Supabase Auth
        """
        self.client.auth.set_session(token)

    # =========================================================================
    # RPCs para Agentes
    # =========================================================================

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(SupabaseError),
        wait=wait_exponential_jitter(initial=1, max=10),
    )
    async def agent_append_message(
        self,
        conversation_id: uuid.UUID,
        agent_type: str,
        content: str,
        tokens_used: Optional[int] = None,
        cost_usd: Optional[float] = None,
        auth_token: Optional[str] = None,
    ) -> uuid.UUID:
        """Agrega un mensaje de agente a una conversación.

        Usa el RPC agent_append_message que valida:
        - El JWT tiene claim agent_role
        - El JWT tiene claim acting_user_id
        - El acting_user_id es dueño de la conversación

        Args:
            conversation_id: ID de la conversación
            agent_type: Tipo de agente (fitness, nutrition, etc.)
            content: Contenido del mensaje
            tokens_used: Tokens utilizados (opcional)
            cost_usd: Costo en USD (opcional)
            auth_token: JWT del agente (debe tener claims apropiados)

        Returns:
            UUID del mensaje creado

        Raises:
            SupabaseAuthError: Si el token no es válido
            SupabaseRLSError: Si el agente no tiene permiso
            SupabaseError: Otros errores
        """
        # Configurar auth si se provee
        client = self.service_client
        if auth_token:
            client = self.client
            self.set_auth_token(auth_token)

        try:
            response = client.rpc(
                "agent_append_message",
                {
                    "p_conversation_id": str(conversation_id),
                    "p_agent_type": agent_type,
                    "p_content": content,
                    "p_tokens_used": tokens_used,
                    "p_cost_usd": cost_usd,
                },
            ).execute()

            if not response.data:
                raise SupabaseError("No se pudo crear el mensaje")

            return uuid.UUID(response.data)

        except Exception as exc:
            error_msg = str(exc).lower()
            if "unauthorized" in error_msg or "agent_role" in error_msg:
                raise SupabaseAuthError(f"Error de autenticación: {exc}") from exc
            if "forbidden" in error_msg or "mismatch" in error_msg:
                raise SupabaseRLSError(f"Violación de RLS: {exc}") from exc
            raise SupabaseError(f"Error agregando mensaje: {exc}") from exc

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(SupabaseError),
        wait=wait_exponential_jitter(initial=1, max=10),
    )
    async def user_append_message(
        self,
        conversation_id: uuid.UUID,
        content: str,
        auth_token: str,
    ) -> uuid.UUID:
        """Agrega un mensaje de usuario a una conversación.

        Args:
            conversation_id: ID de la conversación
            content: Contenido del mensaje
            auth_token: JWT del usuario

        Returns:
            UUID del mensaje creado
        """
        self.set_auth_token(auth_token)

        try:
            response = self.client.rpc(
                "user_append_message",
                {
                    "p_conversation_id": str(conversation_id),
                    "p_content": content,
                },
            ).execute()

            if not response.data:
                raise SupabaseError("No se pudo crear el mensaje")

            return uuid.UUID(response.data)

        except Exception as exc:
            error_msg = str(exc).lower()
            if "forbidden" in error_msg:
                raise SupabaseRLSError("Usuario no es dueño de la conversación") from exc
            raise SupabaseError(f"Error agregando mensaje: {exc}") from exc

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(SupabaseError),
        wait=wait_exponential_jitter(initial=1, max=10),
    )
    async def agent_log_event(
        self,
        user_id: uuid.UUID,
        agent_type: str,
        event_type: str,
        payload: Optional[dict[str, Any]] = None,
        auth_token: Optional[str] = None,
    ) -> uuid.UUID:
        """Loggea un evento de agente.

        Args:
            user_id: ID del usuario
            agent_type: Tipo de agente
            event_type: Tipo de evento
            payload: Datos adicionales (JSON)
            auth_token: JWT del agente

        Returns:
            UUID del evento creado
        """
        client = self.service_client
        if auth_token:
            client = self.client
            self.set_auth_token(auth_token)

        try:
            response = client.rpc(
                "agent_log_event",
                {
                    "p_user_id": str(user_id),
                    "p_agent_type": agent_type,
                    "p_event_type": event_type,
                    "p_payload": payload or {},
                },
            ).execute()

            if not response.data:
                raise SupabaseError("No se pudo crear el evento")

            return uuid.UUID(response.data)

        except Exception as exc:
            raise SupabaseError(f"Error loggeando evento: {exc}") from exc

    # =========================================================================
    # Queries Básicas
    # =========================================================================

    async def get_conversation(
        self,
        conversation_id: uuid.UUID,
        auth_token: Optional[str] = None,
    ) -> Optional[Conversation]:
        """Obtiene una conversación por ID.

        Args:
            conversation_id: ID de la conversación
            auth_token: JWT del usuario (para RLS)

        Returns:
            Conversation o None si no existe
        """
        if auth_token:
            self.set_auth_token(auth_token)

        try:
            response = (
                self.client.table("conversations")
                .select("*")
                .eq("id", str(conversation_id))
                .maybe_single()
                .execute()
            )

            if not response.data:
                return None

            return Conversation.from_dict(response.data)

        except Exception as exc:
            raise SupabaseError(f"Error obteniendo conversación: {exc}") from exc

    async def get_conversation_messages(
        self,
        conversation_id: uuid.UUID,
        limit: int = 50,
        auth_token: Optional[str] = None,
    ) -> list[Message]:
        """Obtiene los mensajes de una conversación.

        Args:
            conversation_id: ID de la conversación
            limit: Número máximo de mensajes
            auth_token: JWT del usuario (para RLS)

        Returns:
            Lista de mensajes ordenados por created_at desc
        """
        if auth_token:
            self.set_auth_token(auth_token)

        try:
            response = (
                self.client.table("messages")
                .select("*")
                .eq("conversation_id", str(conversation_id))
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return [Message.from_dict(msg) for msg in response.data]

        except Exception as exc:
            raise SupabaseError(f"Error obteniendo mensajes: {exc}") from exc

    async def create_conversation(
        self,
        user_id: uuid.UUID,
        auth_token: str,
    ) -> Conversation:
        """Crea una nueva conversación.

        Args:
            user_id: ID del usuario
            auth_token: JWT del usuario

        Returns:
            Conversación creada
        """
        self.set_auth_token(auth_token)

        try:
            response = (
                self.client.table("conversations")
                .insert(
                    {
                        "user_id": str(user_id),
                        "status": "active",
                    }
                )
                .execute()
            )

            if not response.data or len(response.data) == 0:
                raise SupabaseError("No se pudo crear la conversación")

            return Conversation.from_dict(response.data[0])

        except Exception as exc:
            raise SupabaseError(f"Error creando conversación: {exc}") from exc

    async def get_user_conversations(
        self,
        user_id: uuid.UUID,
        limit: int = 20,
        auth_token: str = "",
    ) -> list[Conversation]:
        """Obtiene las conversaciones de un usuario.

        Args:
            user_id: ID del usuario
            limit: Número máximo de conversaciones
            auth_token: JWT del usuario

        Returns:
            Lista de conversaciones ordenadas por created_at desc
        """
        self.set_auth_token(auth_token)

        try:
            response = (
                self.client.table("conversations")
                .select("*")
                .eq("user_id", str(user_id))
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return [Conversation.from_dict(conv) for conv in response.data]

        except Exception as exc:
            raise SupabaseError(f"Error obteniendo conversaciones: {exc}") from exc


# Instancia global (lazy initialization)
_client: Optional[SupabaseClient] = None


def get_supabase_client() -> SupabaseClient:
    """Obtiene la instancia global del cliente Supabase."""
    global _client
    if _client is None:
        _client = SupabaseClient()
    return _client
