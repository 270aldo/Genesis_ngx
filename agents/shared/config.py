"""Sistema de configuración centralizado para Genesis NGX.

Usa pydantic-settings para validación y carga desde:
1. Variables de entorno
2. Archivos .env (.env.local, .env.staging, .env.production)
3. Google Cloud Secret Manager (en producción)
"""

from __future__ import annotations

import os
from enum import Enum
from functools import lru_cache
from typing import Any, Literal, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Ambientes soportados."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Niveles de logging."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class GeminiConfig(BaseSettings):
    """Configuración de Google Gemini."""

    model_config = SettingsConfigDict(
        env_prefix="GEMINI_",
        env_file=".env.local",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    project_id: str = Field(..., description="Google Cloud Project ID")
    location: str = Field(default="us-central1", description="GCP Region")
    default_model: str = Field(
        default="gemini-2.0-flash-exp",
        description="Modelo por defecto",
    )

    # Configuración
    max_retries: int = Field(default=3, ge=0, le=10)
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    enable_caching: bool = Field(default=True)
    cache_ttl_hours: int = Field(default=1, ge=1, le=24)

    # Control de costos
    max_cost_per_request: float = Field(default=0.05, ge=0.0, le=1.0)
    daily_budget_usd: float = Field(default=10.0, ge=0.0)

    @field_validator("project_id")
    @classmethod
    def validate_project_id(cls, v: str) -> str:
        if not v or v == "your-gcp-project-id":
            raise ValueError("GEMINI_PROJECT_ID debe ser configurado")
        return v


class SupabaseConfig(BaseSettings):
    """Configuración de Supabase."""

    model_config = SettingsConfigDict(
        env_prefix="SUPABASE_",
        env_file=".env.local",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    url: str = Field(..., description="Supabase URL")
    anon_key: str = Field(..., description="Supabase Anon Key")
    service_role_key: str = Field(..., description="Supabase Service Role Key")

    # Configuración
    db_schema: str = Field(default="public")
    max_connections: int = Field(default=10, ge=1, le=100)
    connection_timeout: int = Field(default=10, ge=1, le=60)

    @field_validator("url", "anon_key", "service_role_key")
    @classmethod
    def validate_not_placeholder(cls, v: str, info) -> str:
        field_name = info.field_name
        placeholders = ["your-project.supabase.co", "your-anon-key", "your-service-role-key"]
        if any(placeholder in v for placeholder in placeholders):
            raise ValueError(f"{field_name} debe ser configurado con valores reales")
        return v


class AuthConfig(BaseSettings):
    """Configuración de autenticación."""

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=".env.local",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # JWT
    jwt_secret_key: str = Field(..., description="Secret key para JWT")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=60, ge=5, le=1440)

    # OIDC
    oidc_issuer: str = Field(default="https://accounts.google.com")
    oidc_audience: str = Field(default="nexus-orchestrator")
    oidc_jwks_url: str = Field(default="https://www.googleapis.com/oauth2/v3/certs")

    # API Keys
    api_key_header: str = Field(default="X-API-Key")
    api_key_value: Optional[str] = Field(default=None)

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if "change-this" in v.lower() or len(v) < 32:
            raise ValueError(
                "JWT_SECRET_KEY debe ser una clave segura de al menos 32 caracteres"
            )
        return v


class LoggingConfig(BaseSettings):
    """Configuración de logging."""

    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        env_file=".env.local",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    level: LogLevel = Field(default=LogLevel.INFO)
    format: Literal["json", "console"] = Field(default="json")
    to_cloud: bool = Field(default=False, description="Enviar logs a Cloud Logging")

    # Privacy
    request_body: bool = Field(default=False, description="Loggear request body")
    response_body: bool = Field(default=False, description="Loggear response body")
    headers: bool = Field(default=False, description="Loggear headers")


class A2AConfig(BaseSettings):
    """Configuración del protocolo A2A."""

    model_config = SettingsConfigDict(
        env_prefix="A2A_",
        env_file=".env.local",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    version: str = Field(default="0.3")
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_backoff_seconds: float = Field(default=2.0, ge=0.1, le=60.0)

    # Budget
    default_budget_usd: float = Field(default=0.01, ge=0.0, le=1.0)
    enable_budget_enforcement: bool = Field(default=True)


class ServiceConfig(BaseSettings):
    """Configuración del servicio."""

    model_config = SettingsConfigDict(
        env_prefix="NEXUS_",
        env_file=".env.local",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8080, ge=1024, le=65535)
    reload: bool = Field(default=False, description="Hot reload (solo development)")


class AgentURLsConfig(BaseSettings):
    """URLs de agentes especializados."""

    model_config = SettingsConfigDict(
        env_prefix="AGENT_",
        env_file=".env.local",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    fitness_url: str = Field(default="http://localhost:8081")
    nutrition_url: str = Field(default="http://localhost:8082")
    mental_health_url: str = Field(default="http://localhost:8083")


class Settings(BaseSettings):
    """Configuración principal de la aplicación."""

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=False)

    # Google Cloud
    google_cloud_project: str = Field(..., description="Google Cloud Project ID")
    google_cloud_region: str = Field(default="us-central1")
    google_application_credentials: Optional[str] = Field(
        default=None,
        description="Path to service account key (solo local)",
    )

    # Sub-configs
    gemini: GeminiConfig = Field(default_factory=GeminiConfig)
    supabase: SupabaseConfig = Field(default_factory=SupabaseConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    a2a: A2AConfig = Field(default_factory=A2AConfig)
    service: ServiceConfig = Field(default_factory=ServiceConfig)
    agent_urls: AgentURLsConfig = Field(default_factory=AgentURLsConfig)

    # CORS
    cors_allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:19006"]
    )
    cors_allow_credentials: bool = Field(default=True)

    # Feature Flags
    enable_rag: bool = Field(default=False)
    enable_realtime: bool = Field(default=True)
    enable_streaming: bool = Field(default=True)
    enable_caching: bool = Field(default=True)
    enable_metrics: bool = Field(default=True)

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_requests_per_minute: int = Field(default=60, ge=1, le=10000)
    rate_limit_burst: int = Field(default=10, ge=1, le=100)

    # Testing
    test_mode: bool = Field(default=False)
    mock_gemini: bool = Field(default=False)
    mock_supabase: bool = Field(default=False)

    @field_validator("google_cloud_project")
    @classmethod
    def validate_gcp_project(cls, v: str) -> str:
        if not v or v == "your-gcp-project-id":
            raise ValueError("GOOGLE_CLOUD_PROJECT debe ser configurado")
        return v

    @property
    def is_development(self) -> bool:
        """True si estamos en development."""
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_staging(self) -> bool:
        """True si estamos en staging."""
        return self.environment == Environment.STAGING

    @property
    def is_production(self) -> bool:
        """True si estamos en production."""
        return self.environment == Environment.PRODUCTION

    def model_post_init(self, __context: Any) -> None:
        """Post-init: validaciones y setup."""
        # En producción, forzar ciertas configuraciones
        if self.is_production:
            if self.debug:
                raise ValueError("DEBUG no puede estar habilitado en producción")
            if self.service.reload:
                raise ValueError("RELOAD no puede estar habilitado en producción")
            if not self.logging.to_cloud:
                # Solo advertencia, no error
                print("WARNING: LOG_TO_CLOUD debería estar habilitado en producción")

        # Configurar GOOGLE_APPLICATION_CREDENTIALS si está definido
        if self.google_application_credentials:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
                self.google_application_credentials
            )


@lru_cache
def get_settings() -> Settings:
    """Obtiene la configuración de la aplicación (singleton)."""
    return Settings()


# Alias para importación conveniente
settings = get_settings()
