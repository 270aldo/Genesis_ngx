# ADR-006: No Usar ADK Visual Builder para Genesis NGX

**Status:** Aceptado
**Date:** 2025-11-19
**Deciders:** Equipo Genesis NGX
**Tags:** adk, architecture, development-workflow, a2a-protocol

---

## Context

ADK (Agent Development Kit) v1.18.0 incluye **Visual Builder**, una herramienta experimental de diseño visual drag-and-drop para prototipar arquitecturas multi-agente en navegador. El equipo evaluó si adoptar un workflow híbrido (Visual Builder → Código) o implementar agentes directamente en Python.

### Visual Builder Ofrece:
- Canvas drag-and-drop para diseño de arquitecturas
- AI Assistant para generación automática desde prompts
- Testing rápido en navegador sin deployment
- Export a YAML para documentación
- Visualización clara de relaciones entre agents

### Genesis NGX Requiere:
- **A2A v0.3 protocol completo**: `/card`, `/negotiate`, `/invoke`, `/invoke/stream`
- **Budget enforcement**: Header `X-Budget-USD` con validación
- **Cost tracking**: Registro en Supabase `agent_events`
- **Security validation**: Detección PHI/PII, sanitización
- **RLS integration**: RPCs de Supabase con SECURITY DEFINER
- **Production-grade**: Testing contractual, SLOs, monitoring

---

## Decision

**Genesis NGX NO usará ADK Visual Builder** para desarrollo de agentes. Todos los agents se implementarán directamente en código Python usando la clase base `A2AServer`.

**Razones:**

### 1. Incompatibilidad con A2A v0.3 Protocol

Visual Builder exporta YAML que usa endpoints ADK nativos (`/run`), no A2A v0.3 (`/invoke`, `/invoke/stream`). Traducir YAML → A2A requiere:
- Reescribir routing logic manualmente
- Implementar endpoints A2A desde cero
- Mapear Agent Config → AGENT_CARD
- No hay generación automática de código A2A

**Resultado:** 50% del tiempo se pierde en traducción manual.

### 2. Features Enterprise Críticas NO Soportadas

| Feature | Visual Builder | Código Python | Criticidad |
|---------|----------------|---------------|------------|
| Budget enforcement | ❌ | ✅ | HIGH |
| Cost tracking | ❌ | ✅ | HIGH |
| Security validation (PHI/PII) | ❌ | ✅ | CRITICAL |
| RLS integration (Supabase RPCs) | ❌ | ✅ | HIGH |
| `/negotiate` endpoint completo | ❌ | ✅ | MEDIUM |
| SSE Streaming personalizado | ⚠️ Limitado | ✅ | MEDIUM |
| Custom middleware | ❌ | ✅ | MEDIUM |
| OpenTelemetry tracing | ❌ | ✅ | LOW |

**Resultado:** 7 de 8 features críticas NO disponibles en Visual Builder.

### 3. Madurez Experimental

- **Lanzamiento:** Nov 5, 2025 (2 semanas de antigüedad)
- **AI Assistant:** Primera generación OK, ediciones subsecuentes fallan frecuentemente
- **Bugs reportados:** Workflow one-way (no bidireccional), sincronización rota
- **Comunidad:** Casos de uso limitados, documentación incompleta

**Resultado:** Riesgo alto de bloqueadores en producción.

### 4. ROI Negativo para Genesis NGX

**Inversión estimada:**
- Learning curve: 4-8 horas/engineer
- Diseño en Visual Builder: 2-4 horas/agent
- Traducción YAML → A2A: 4-8 horas/agent
- Re-implementación de features: 8-16 horas/agent
- **Total por agent:** 18-36 horas

**Implementación directa:**
- Setup base `A2AServer`: 2-4 horas (una vez)
- Implementar agent: 8-12 horas/agent
- **Total por agent:** 8-12 horas

**Ahorro:** 10-24 horas/agent × 6 agents = **60-144 horas** (1.5-3.6 semanas)

---

## Consequences

### Positivas ✅

1. **Control Total sobre A2A Protocol**
   - Implementación completa de v0.3 specification
   - Customización de endpoints sin limitaciones
   - Testing contractual riguroso desde día 1

2. **Features Enterprise Desde Inicio**
   - Budget enforcement integrado
   - Cost tracking automático en Supabase
   - Security validation (PHI/PII) en cada request
   - RLS integration con RPCs

3. **Código como Source of Truth**
   - No drift entre YAML y código
   - Git history completo de cambios
   - Refactoring con herramientas estándar (IDE, linters)

4. **Performance y Observability**
   - Control granular de latency
   - OpenTelemetry tracing custom
   - Profiling y optimización directa

5. **Testing Robusto**
   - Unit tests con pytest
   - Integration tests con mock Supabase
   - Contractual tests contra A2A schema
   - Coverage >70% desde inicio

### Negativas ❌

1. **No Visualización de Arquitectura**
   - **Mitigación:** Crear diagramas en Mermaid/PlantUML
   - **Costo:** 2-4 horas una vez, actualizaciones 30 min

2. **Learning Curve de A2A Protocol**
   - **Mitigación:** Documentación en `ADR/002-a2a-v03-protocol.md`
   - **Costo:** 2-4 horas/engineer (una vez)

3. **Sin Testing Rápido en Navegador**
   - **Mitigación:** Usar `uvicorn --reload` + curl/Postman
   - **Costo:** Setup 30 min, flujo similar

4. **No AI Assistant para Generación**
   - **Mitigación:** Templates en `agents/shared/`, CLI scaffolding
   - **Costo:** Crear templates 4 horas (una vez)

### Riesgos y Mitigaciones ⚠️

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Duplicación de código entre agents | MEDIUM | MEDIUM | Extraer a `agents/shared/`, code reviews |
| Violación de A2A spec | LOW | HIGH | Contractual tests, schema validation |
| Drift de AGENT_CARD vs implementación | LOW | MEDIUM | Tests que validan card vs endpoints |
| Onboarding lento de nuevos engineers | MEDIUM | LOW | Documentación exhaustiva + pair programming |

---

## Alternatives Considered

### Opción A: Workflow Híbrido (Visual Builder → Código)
**Pros:** Diseño rápido, visualización
**Cons:** Traducción manual, features faltantes, experimental
**Decisión:** Rechazada (ROI negativo)

### Opción B: Visual Builder + Custom Extensions
**Pros:** Mejor de ambos mundos
**Cons:** ADK no soporta extensiones de Visual Builder, requeriría fork
**Decisión:** No factible técnicamente

### Opción C: LangChain/LangGraph
**Pros:** Ecosistema maduro, multi-model
**Cons:** A2A support experimental, menos optimizado para Gemini
**Decisión:** Evaluado en ADR-004, rechazado (deep Vertex AI integration)

### Opción D: Implementación Directa en Código ✅
**Pros:** Control total, features completas, production-grade
**Cons:** No visualización gráfica
**Decisión:** **ACEPTADA**

---

## Implementation Notes

### Estructura de Agent Base

Todos los agents heredan de `A2AServer`:

```python
# agents/<name>/main.py
from agents.shared.a2a_server import A2AServer

AGENT_CARD = {
    "id": "agent-name",
    "version": "0.1.0",
    "capabilities": ["capability1", "capability2"],
    "limits": {
        "max_input_tokens": 20000,
        "max_output_tokens": 2000,
        "max_latency_ms": 2000,
        "max_cost_per_invoke": 0.01,
    },
    "privacy": {"pii": False, "phi": False, "data_retention_days": 90},
    "auth": {"method": "oidc", "audience": "agent-name"},
}

class MyAgent(A2AServer):
    def __init__(self):
        super().__init__(AGENT_CARD)
        self.gemini = get_gemini_client()
        self.supabase = get_supabase_client()

    async def handle_method(self, method: str, params: dict) -> dict:
        # Implementación con budget checking, cost tracking, security
        pass

agent = MyAgent()
app = agent.app
```

### Herramientas de Desarrollo

1. **CLI Scaffolding** (a crear):
   ```bash
   scripts/create_agent.py --name fitness --capabilities workout_planning
   ```

2. **Testing Harness**:
   ```bash
   pytest agents/fitness/tests/ --cov
   ```

3. **Local Development**:
   ```bash
   uvicorn "agents.fitness.main:app" --reload --port 8081
   ```

4. **A2A Client Testing**:
   ```python
   from agents.shared.a2a_client import A2AClient
   client = A2AClient("http://localhost:8081")
   await client.invoke(method="create_workout", params={...})
   ```

### Documentación de Arquitectura

En lugar de Visual Builder, usar:
- **Mermaid diagrams** en `docs/architecture/`
- **PlantUML** para secuencias complejas
- **ADRs** para decisiones clave
- **AGENT_CARD** como spec formal

---

## Related Documents

- `ADR/002-a2a-v03-protocol.md` - Especificación A2A v0.3
- `ADR/004-gemini-model-selection.md` - Strategy de modelos Gemini
- `docs/ADK_VISUAL_BUILDER_ANALYSIS.md` - Investigación exhaustiva (referencia histórica)
- `docs/ADK_WORKFLOW_QUICK_REFERENCE.md` - Quick reference (si se reconsiderara)
- `adk_designs/TRANSLATION_GUIDE.md` - Workflow híbrido (no usado, referencia)

---

## Review and Updates

- **Next Review Date:** 2026-05-19 (6 meses)
- **Review Trigger:** ADK Visual Builder sale de experimental, soporta A2A v0.3
- **Owner:** Tech Lead Genesis NGX

**Criterios para Reconsiderar:**
1. Visual Builder soporta A2A v0.3 protocol nativamente
2. Export genera código Python A2AServer directamente (no YAML)
3. Features enterprise (budget, security, RLS) soportadas
4. Madurez probada (>6 meses en producción, comunidad activa)
5. ROI positivo demostrado en proyectos similares

---

**Última actualización:** 2025-11-19
**Versión:** 1.0.0
**Status:** Aceptado e implementado
