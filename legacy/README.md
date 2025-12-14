# Legacy Code

Este directorio contiene codigo deprecado que fue parte de la arquitectura inicial basada en Cloud Run.

## Archivos

| Archivo | Descripcion | Fecha Deprecacion |
|---------|-------------|-------------------|
| `a2a_server.py` | Servidor FastAPI para A2A manual | Dic 2025 |
| `a2a_client.py` | Cliente httpx para A2A manual | Dic 2025 |

## Razon de Deprecacion

Genesis NGX migro de Cloud Run + FastAPI manual a **Vertex AI Agent Engine** con Google ADK.

Agent Engine provee:
- Gestion automatica de sesiones (Memory Bank)
- A2A nativo sin implementacion manual
- Escalado automatico
- Monitoring integrado

## Eliminacion Programada

Estos archivos seran eliminados despues de Q1 2026, una vez que la migracion a Agent Engine este completamente validada en produccion.

## Referencias

- ADR-007: Migration to ADK/Agent Engine
- docs/LEGACY.md: Documentacion completa de deprecaciones
