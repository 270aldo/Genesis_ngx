# ADR-002: Protocolo A2A v0.3 (JSON-RPC + SSE)

Status: Accepted
Date: 2025-10-28

## Contexto
- El sistema multi-agente requiere interoperabilidad multi-equipo y soporte para streaming.
- La especificación A2A v0.3 (julio 2025) define JSON-RPC 2.0 sobre HTTPS con soporte obligatorio para SSE; gRPC es opcional.

## Decisión
Implementar el protocolo A2A v0.3 usando JSON-RPC 2.0 sobre HTTPS y SSE para streaming. Dejar gRPC como opción futura intra-GCP.

## Justificación
- **Compatibilidad**: Alinear con la spec oficial garantiza interoperabilidad con agentes externos.
- **Simplicidad operativa**: JSON-RPC + SSE se implementa con FastAPI/HTTP estándar, facilitando debugging y seguridad.
- **Streaming**: SSE habilita respuesta token-a-token; los clientes web/móvil lo soportan nativamente.
- **Futuro**: La spec permite gRPC; podremos añadirlo para optimizar latencia en enlaces internos cuando sea necesario.

## Contrato de Endpoints
- `GET /card`: devuelve Agent Card (metadata, límites, privacidad, auth).
- `POST /negotiate`: negociación de capacidades y presupuesto (responde con acuerdos o degradaciones).
- `POST /invoke`: llamada JSON-RPC sin streaming.
- `POST /invoke/stream`: streaming SSE con eventos `data:`.
- `GET /healthz`: health check opcional para infraestructura.

## Reglas de Resiliencia
- Timeouts: conexión 5 s, request 30 s (configurable por agente).
- Reintentos exponenciales (3 intentos) para errores transitorios (5xx, timeout).
- Idempotency: encabezado `X-Request-ID` obligatorio para correlación y replay seguro.
- Presupuesto: encabezado `X-Budget-USD`; el servidor debe rechazar si el presupuesto disponible es **menor** que el coste mínimo esperado.
- Errores estándar (`code` JSON-RPC + `data.reason`):
  - `-32000` / `AGENT_UNAVAILABLE`
  - `-32001` / `BUDGET_EXCEEDED`
  - `-32002` / `TIMEOUT`
  - `-32003` / `RATE_LIMITED`
  - `-32602` / `VALIDATION_ERROR`

## Seguridad
- Autenticación entre servicios vía OIDC (Service Accounts) con validación de `aud` y `sub`.
- Firmar Agent Cards y exponer versiones (`semver`) para compatibilidad.
- Limitar tamaño de payloads (p. ej. ≤1 MB) y tokens (respeto a `max_input_tokens`).

## Consecuencias
- Necesitamos librerías compartidas para cliente/servidor A2A.
- Debemos mantener schemas validados (JSON Schema) y tests contractuales.
- Observabilidad: incluir `X-Request-ID`, `X-Agent-ID`, métricas de latencia y tasa de errores por agente.

## Referencias
- A2A Protocol Specification v0.3 (2025-07-31).
- ADK A2A docs (`adk api_server --a2a`).
