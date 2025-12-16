"""Sistema de logging estructurado con structlog.

Características:
- JSON logging para Cloud Logging
- Console logging para desarrollo
- Context binding (request_id, user_id, agent_type)
- Integración con FastAPI
- Filtrado de PII/PHI
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from google.cloud import logging as cloud_logging

from agents.shared.config import LoggingConfig, get_settings


def configure_logging(config: LoggingConfig | None = None) -> None:
    """Configura el sistema de logging.

    Args:
        config: Configuración de logging (usa settings si es None)
    """
    if config is None:
        config = get_settings().logging

    # Procesadores comunes
    processors: list[Any] = [
        # Agregar nombre del logger
        structlog.stdlib.add_log_level,
        # Agregar timestamp
        structlog.processors.TimeStamper(fmt="iso"),
        # Agregar info de stack en caso de excepciones
        structlog.processors.StackInfoRenderer(),
        # Formatear excepciones
        structlog.processors.format_exc_info,
    ]

    # Procesadores específicos por formato
    if config.format == "json":
        processors.extend(
            [
                # Procesador para Cloud Logging
                _add_cloud_logging_fields,
                # Renderizar como JSON
                structlog.processors.JSONRenderer(),
            ]
        )
    else:
        processors.extend(
            [
                # Colorear output en consola
                structlog.dev.ConsoleRenderer(colors=True),
            ]
        )

    # Configurar structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configurar logging estándar
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, config.level.value),
    )

    # Integrar con Cloud Logging si está habilitado
    if config.to_cloud:
        try:
            client = cloud_logging.Client()
            client.setup_logging()
        except Exception as exc:
            # No fallar si Cloud Logging no está disponible (ej: desarrollo local)
            print(f"WARNING: No se pudo configurar Cloud Logging: {exc}")


def _add_cloud_logging_fields(
    logger: Any, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Agrega campos específicos de Cloud Logging.

    Cloud Logging espera ciertos campos en formato específico:
    - severity: nivel de log
    - message: mensaje principal
    - timestamp: timestamp ISO
    """
    # Mapear level a severity de Cloud Logging
    level = event_dict.get("level", "info").upper()
    event_dict["severity"] = level

    # Renombrar event a message (Cloud Logging lo espera así)
    if "event" in event_dict:
        event_dict["message"] = event_dict.pop("event")

    return event_dict


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Obtiene un logger con el nombre especificado.

    Args:
        name: Nombre del logger (usualmente __name__)

    Returns:
        Logger configurado
    """
    return structlog.get_logger(name)


class RequestLogger:
    """Logger con contexto de request.

    Permite hacer bind de información del request (request_id, user_id, etc.)
    que se incluirá en todos los logs.
    """

    def __init__(self, logger: structlog.stdlib.BoundLogger):
        self.logger = logger

    def bind(self, **kwargs: Any) -> "RequestLogger":
        """Agrega contexto al logger.

        Args:
            **kwargs: Pares key-value para agregar al contexto

        Returns:
            Nuevo RequestLogger con contexto agregado
        """
        return RequestLogger(self.logger.bind(**kwargs))

    def debug(self, event: str, **kwargs: Any) -> None:
        """Log debug."""
        self.logger.debug(event, **kwargs)

    def info(self, event: str, **kwargs: Any) -> None:
        """Log info."""
        self.logger.info(event, **kwargs)

    def warning(self, event: str, **kwargs: Any) -> None:
        """Log warning."""
        self.logger.warning(event, **kwargs)

    def error(self, event: str, **kwargs: Any) -> None:
        """Log error."""
        self.logger.error(event, **kwargs)

    def critical(self, event: str, **kwargs: Any) -> None:
        """Log critical."""
        self.logger.critical(event, **kwargs)

    def exception(self, event: str, **kwargs: Any) -> None:
        """Log excepción (incluye stack trace)."""
        self.logger.exception(event, **kwargs)


def get_request_logger(
    name: str,
    request_id: str | None = None,
    user_id: str | None = None,
    agent_type: str | None = None,
    **extra: Any,
) -> RequestLogger:
    """Obtiene un logger con contexto de request.

    Args:
        name: Nombre del logger
        request_id: ID del request (X-Request-ID)
        user_id: ID del usuario
        agent_type: Tipo de agente
        **extra: Contexto adicional

    Returns:
        RequestLogger con contexto
    """
    logger = get_logger(name)

    # Bind de contexto
    context = {}
    if request_id:
        context["request_id"] = request_id
    if user_id:
        context["user_id"] = user_id
    if agent_type:
        context["agent_type"] = agent_type
    if extra:
        context.update(extra)

    if context:
        logger = logger.bind(**context)

    return RequestLogger(logger)


def sanitize_for_logging(data: dict[str, Any], config: LoggingConfig) -> dict[str, Any]:
    """Sanitiza datos para logging (elimina PII/PHI si está configurado).

    Args:
        data: Datos a sanitizar
        config: Configuración de logging

    Returns:
        Datos sanitizados
    """
    # Si no estamos loggeando bodies/headers, no sanitizar (no se loggearán)
    if not config.request_body and not config.response_body and not config.headers:
        return data

    # Campos sensibles a redactar
    sensitive_fields = {
        "password",
        "token",
        "api_key",
        "secret",
        "authorization",
        "cookie",
        "ssn",
        "credit_card",
        "card_number",
    }

    sanitized = {}
    for key, value in data.items():
        # Redactar si es campo sensible
        if any(field in key.lower() for field in sensitive_fields):
            sanitized[key] = "[REDACTED]"
        # Recursivo si es dict
        elif isinstance(value, dict):
            sanitized[key] = sanitize_for_logging(value, config)
        # Recursivo si es lista
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_for_logging(item, config) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized


def log_request(
    logger: RequestLogger,
    method: str,
    path: str,
    query_params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> None:
    """Loggea un request HTTP.

    Args:
        logger: Logger con contexto
        method: Método HTTP
        path: Path del request
        query_params: Query parameters
        body: Body del request
        headers: Headers del request
    """
    config = get_settings().logging

    log_data: dict[str, Any] = {
        "http_method": method,
        "http_path": path,
    }

    if query_params:
        log_data["query_params"] = query_params

    if config.request_body and body:
        log_data["request_body"] = sanitize_for_logging(body, config)

    if config.headers and headers:
        log_data["headers"] = sanitize_for_logging(headers, config)

    logger.info("http_request", **log_data)


def log_response(
    logger: RequestLogger,
    status_code: int,
    latency_ms: float,
    body: dict[str, Any] | None = None,
) -> None:
    """Loggea una respuesta HTTP.

    Args:
        logger: Logger con contexto
        status_code: Código de status HTTP
        latency_ms: Latencia en milisegundos
        body: Body de la respuesta
    """
    config = get_settings().logging

    log_data: dict[str, Any] = {
        "http_status": status_code,
        "latency_ms": round(latency_ms, 2),
    }

    if config.response_body and body:
        log_data["response_body"] = sanitize_for_logging(body, config)

    logger.info("http_response", **log_data)


def log_agent_invocation(
    logger: RequestLogger,
    agent_type: str,
    method: str,
    params: dict[str, Any],
    budget_usd: float,
) -> None:
    """Loggea una invocación A2A.

    Args:
        logger: Logger con contexto
        agent_type: Tipo de agente
        method: Método A2A
        params: Parámetros de la invocación
        budget_usd: Presupuesto en USD
    """
    logger.info(
        "a2a_invocation",
        agent_type=agent_type,
        a2a_method=method,
        params=params,
        budget_usd=budget_usd,
    )


def log_gemini_generation(
    logger: RequestLogger,
    model: str,
    prompt_tokens: int,
    output_tokens: int,
    cached_tokens: int,
    cost_usd: float,
    latency_ms: float,
) -> None:
    """Loggea una generación con Gemini.

    Args:
        logger: Logger con contexto
        model: Modelo usado
        prompt_tokens: Tokens del prompt
        output_tokens: Tokens de salida
        cached_tokens: Tokens cacheados
        cost_usd: Costo en USD
        latency_ms: Latencia en ms
    """
    logger.info(
        "gemini_generation",
        model=model,
        prompt_tokens=prompt_tokens,
        output_tokens=output_tokens,
        cached_tokens=cached_tokens,
        total_tokens=prompt_tokens + output_tokens,
        cost_usd=round(cost_usd, 6),
        latency_ms=round(latency_ms, 2),
        cache_hit_rate=round(cached_tokens / max(prompt_tokens, 1), 2),
    )


# Configurar logging al importar (puede ser sobreescrito después)
try:
    configure_logging()
except Exception:
    # Fallar silenciosamente si hay problemas de configuración
    # (permite importar el módulo sin errores)
    pass
