# Deprecaciones y Migracion

## Estado Actual

Genesis NGX utiliza **Vertex AI Agent Engine** como runtime de produccion.

## Componentes Deprecados

### Cloud Run (Manual)
- **Estado:** DEPRECADO
- **Razon:** Agent Engine provee mejor integracion con Gemini y gestion de agentes
- **Alternativa:** `adk deploy agent_engine`

### FastAPI A2A Server (`a2a_server.py`)
- **Estado:** DEPRECADO, movido a `legacy/`
- **Razon:** Agent Engine gestiona A2A nativamente
- **Alternativa:** ADK Agent definitions + A2A protocol nativo

### httpx A2A Client (`a2a_client.py`)
- **Estado:** DEPRECADO, movido a `legacy/`
- **Razon:** Agent Engine provee invocacion de agentes via SDK
- **Alternativa:** `AgentEngineRegistry` (PR #3a)

### NEXUS Orchestrator (`agents/nexus/`)
- **Estado:** ELIMINADO
- **Razon:** Reemplazado por GENESIS_X usando ADK nativo
- **Alternativa:** `agents/genesis_x/`

## Timeline

| Milestone | Fecha | Descripcion |
|-----------|-------|-------------|
| Deprecacion | Dic 2025 | Codigo movido a `legacy/` |
| Migracion completa | Q1 2026 | Todos los agentes en Agent Engine |
| Eliminacion | Q2 2026 | Borrar directorio `legacy/` |

## Como Ejecutar Agentes

### Desarrollo Local

```bash
# ADK playground
adk web

# Agente especifico
adk run logos
adk run genesis_x
```

### Staging/Production

```bash
adk deploy agent_engine --env staging --project ngx-genesis-prod
adk deploy agent_engine --env production --project ngx-genesis-prod
```

## Separacion de Responsabilidades

```
AGENT ENGINE (Runtime)           SUPABASE (Persistencia)
-------------------------------- ------------------------
Sessions conversacionales        Datos de negocio
Memory Bank (gratis)             Perfiles de usuario
Estado de conversacion           Metricas de salud
Context window                   Preferencias
                                 Auditoria/eventos
NO persistir manualmente         Trazabilidad
```

**REGLA:** No reimplementar session storage manual. Agent Engine ya gestiona sesiones y memory. Supabase es para datos de dominio y trazabilidad.

## Referencias

- [ADK Deploy Docs](https://google.github.io/adk-docs/deploy/agent_engine/)
- [Agent Engine A2A](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/a2a)
- [Agent Engine Sessions](https://google.github.io/adk-docs/sessions/)
- ADR-007: Migration to ADK/Agent Engine
