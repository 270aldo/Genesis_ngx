# ADR-007: Migración de Cloud Run a Vertex AI Agent Engine

**Estado**: Aceptado  
**Fecha**: 2025-11-27  
**Decisores**: Aldo (CEO/Arquitecto), Claude Opus 4.5 (Co-Arquitecto)

## Contexto

El sistema GENESIS_X actualmente ejecuta agentes en Cloud Run con implementación manual del protocolo A2A. Desde que se escribió ADR-001 (Octubre 2025), Vertex AI Agent Engine ha madurado significativamente, ofreciendo:

- Soporte nativo para A2A protocol
- Sessions y Memory Bank managed (gratis)
- Observability y tracing built-in
- Deploy simplificado (`adk deploy`)
- Evaluación integrada
- Secure code execution sandbox

## Decisión

**Migraremos el runtime de agentes de Cloud Run a Vertex AI Agent Engine.**

### Qué cambia:

| Aspecto | Antes (Cloud Run) | Después (Agent Engine) |
|---------|-------------------|------------------------|
| Runtime | Cloud Run containers | Agent Engine managed |
| Framework | FastAPI + A2AServer custom | Google ADK |
| Sessions | Custom en Supabase | Agent Engine Sessions |
| Memory | Custom en Supabase | Memory Bank + Supabase |
| Deploy | Docker + Cloud Build | `adk deploy` |
| Observability | Custom logging | Built-in tracing |
| A2A | Implementación manual | Nativo |

### Qué NO cambia:

- **Supabase** sigue siendo la base de datos para:
  - Datos de usuario (profiles, preferences)
  - Datos de negocio (seasons, workouts, nutrition)
  - Health metrics y historial
  - Embeddings (user_context_embeddings)
  
- **Protocolo A2A**: Seguimos usando JSON-RPC 2.0 + SSE
- **Modelos**: Gemini 3 Pro/Flash
- **Frontends**: Expo SDK 54, Next.js 15

## Justificación

### 1. Reducción de Código Custom

```python
# ANTES: ~200 líneas de boilerplate por agente
class NexusAgent(A2AServer):
    def __init__(self):
        super().__init__(AGENT_CARD)
        # Setup manual de CORS, logging, sessions...
        
# DESPUÉS: ~50 líneas enfocadas en lógica
genesis_x = Agent(
    name="genesis_x",
    model="gemini-3-pro",
    tools=[...],
    instruction=PROMPT,
)
```

### 2. Sessions y Memory Gratis

Agent Engine incluye:
- **Sessions**: Memoria de corto plazo dentro de conversación
- **Memory Bank**: Memoria de largo plazo entre conversaciones

Esto elimina la necesidad de implementar y mantener esta lógica en Supabase.

### 3. Observability Sin Esfuerzo

```
Cloud Run: Configurar Cloud Logging, crear dashboards, implementar tracing manual
Agent Engine: Built-in tracing, debugging visual, métricas automáticas
```

### 4. Futuro-Proof

Google está invirtiendo fuertemente en Agent Engine:
- "Cientos de miles de agentes desplegados" (Nov 2025)
- Integración con Agentspace (enterprise)
- Agent Garden con templates
- Mejoras continuas en evaluación y seguridad

### 5. Costo Comparable

| Servicio | Cloud Run | Agent Engine |
|----------|-----------|--------------|
| Compute | $0.0864/vCPU-hr | vCPU/GiB hours |
| Memory | $0.009/GiB-hr | Incluido |
| Sessions | Custom (dev time) | Gratis |
| Tracing | Cloud Trace ($) | Incluido |
| **Idle** | Scale to zero ✅ | Scale to zero ✅ |

## Consecuencias

### Positivas

1. **Menor mantenimiento**: No mantenemos A2AServer, sessions, logging custom
2. **Faster iteration**: Deploy en un comando
3. **Mejor debugging**: Tracing visual de flujos multi-agente
4. **Escalabilidad**: Managed por Google
5. **Evaluación**: Tools integrados para medir calidad

### Negativas

1. **Curva de aprendizaje**: Equipo debe aprender ADK
2. **Vendor lock-in**: Más dependencia de GCP (mitigado: ADK es open source)
3. **Migración**: Esfuerzo de reescribir agentes existentes

### Riesgos y Mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Agent Engine down | Baja | Alto | Mantener Cloud Run como fallback temporal |
| Pricing changes | Media | Medio | Monitorear costos, alertas de budget |
| Missing features | Baja | Medio | Feature flags para comportamiento custom |
| Migration bugs | Media | Medio | Testing exhaustivo, rollout gradual |

## Plan de Migración

### Fase 1: Setup (Días 1-3)
- [ ] Instalar ADK CLI
- [ ] Crear proyecto staging
- [ ] Configurar Service Accounts

### Fase 2: GENESIS_X (Días 4-10)
- [ ] Reescribir nexus → genesis_x en formato ADK
- [ ] Migrar tools
- [ ] Conectar con Supabase
- [ ] Tests

### Fase 3: Agentes Especializados (Días 11-20)
- [ ] fitness → blaze
- [ ] nutrition → sage
- [ ] Nuevos agentes

### Fase 4: Validación (Días 21-30)
- [ ] Testing end-to-end
- [ ] Performance benchmarks
- [ ] Security review

### Fase 5: Cutover (Día 31+)
- [ ] Deploy a producción
- [ ] Monitoreo intensivo
- [ ] Deprecar Cloud Run

## Rollback Plan

Si la migración falla:

1. Los servicios Cloud Run permanecen deployeados durante transición
2. Feature flag `AGENT_RUNTIME` permite switchear:
   ```python
   if settings.agent_runtime == "cloud_run":
       # Usar implementación legacy
   else:
       # Usar Agent Engine
   ```
3. DNS/Load Balancer puede redirigir tráfico en minutos

## Referencias

- [Vertex AI Agent Engine Overview](https://cloud.google.com/agent-builder/agent-engine/overview)
- [ADK Documentation](https://google.github.io/adk-docs/)
- [ADR-001: Cloud Run over Agent Engine](./001-cloud-run-over-agent-engine.md) (superseded by this ADR)
- [GENESIS_PRD.md](../GENESIS_PRD.md)

## Notas

Este ADR **supersede parcialmente** ADR-001. La decisión original de usar Cloud Run fue correcta en Octubre 2025 cuando Agent Engine era menos maduro. Con las mejoras de Noviembre 2025, Agent Engine es ahora la mejor opción.

ADR-001 permanece en el repo como referencia histórica.
