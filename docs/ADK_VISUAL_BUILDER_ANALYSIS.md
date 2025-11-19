# ADK Visual Builder: Análisis de Workflow Híbrido para Genesis NGX

**Fecha:** 2025-11-19
**Versión ADK:** 1.18.0+
**Proyecto:** Genesis NGX Multi-Agent System
**Autor:** Investigación de Claude Code

---

## Resumen Ejecutivo

El **ADK Visual Builder** es una herramienta web experimental (lanzada en ADK v1.18.0, noviembre 2025) que permite diseñar agentes mediante una interfaz drag-and-drop con asistente de IA integrado. Este análisis evalúa su viabilidad para un workflow híbrido de **prototipado visual → traducción a código A2A** en el contexto de Genesis NGX.

**Veredicto:** El workflow híbrido es **RECOMENDADO** con restricciones claras sobre qué prototipar visualmente y qué implementar directamente en código.

---

## 1. ¿Qué es ADK Visual Builder?

### Descripción Oficial

> "A browser-based interface that lets you visually design, configure, and test complex multi-agent systems through drag-and-drop interactions and natural language conversations."

### Componentes Principales

1. **Visual Workflow Designer**: Canvas drag-and-drop para arquitectura de agentes
2. **Configuration Panel**: Formularios para editar propiedades sin tocar YAML
3. **AI Assistant (Gemini-powered)**: Genera arquitecturas desde prompts en lenguaje natural
4. **Testing Interface**: Prueba agentes en la misma UI sin cambiar de contexto
5. **Export Feature**: Genera YAML en formato Agent Config

### Acceso y Setup

```bash
# Instalar ADK 1.18.0+
pip install --upgrade google-adk

# Lanzar Visual Builder
adk web adk_designs --host 127.0.0.1 --port 8000

# Acceder en navegador
http://localhost:8000/dev-ui/
```

### Agent Types Soportados

- Root Agent
- LLM Agent (modelo Gemini configurable)
- Sequential Agent (pipeline multi-etapa)
- Parallel Agent (tareas concurrentes)
- Loop Agent (refinamiento iterativo)
- Workflow Agent (combinaciones complejas)

### Tools Soportados

- **Built-in Tools**: Google Search, VertexAiSearch, Code Execution
- **Custom Tools**: Python functions (auto-wrapping con FunctionTool)
- **MCP Tools**: Model Context Protocol servers (con limitaciones)

---

## 2. Ventajas del Workflow Híbrido

### ✅ PROS: Visual Builder para Prototipado

#### 2.1 Velocidad de Iteración

**Beneficio clave:** Diseñar arquitecturas multi-agente en **minutos** vs **horas** escribiendo YAML/código.

**Casos de uso para Genesis NGX:**
- Experimentar con composiciones NEXUS + especialistas (Sequential vs Parallel)
- Prototipar flujos de conversación user → NEXUS → Fitness Agent
- Testear diferentes estrategias de delegación (LLM-driven vs explicit routing)

**Ejemplo práctico:**
```
Pregunta: "¿Debería NEXUS usar Sequential o Parallel para consultar Fitness + Nutrition simultáneamente?"

Tradicional (código):
- Escribir FitnessAgent mock
- Escribir NutritionAgent mock
- Implementar ParallelAgent wrapper
- Testing manual con logs
- Tiempo: ~2-3 horas

Visual Builder:
- Drag-and-drop Parallel Agent
- Agregar 2 sub-agents (Fitness, Nutrition mocks)
- Testing en UI
- Tiempo: ~15 minutos
```

#### 2.2 Visualización de Arquitectura

**Beneficio clave:** El canvas visual muestra relaciones entre agentes que son difíciles de ver en código.

**Para Genesis NGX:**
- Mapear dependencias NEXUS → Specialized Agents → Database RPCs
- Identificar cuellos de botella (e.g., sequential cuando podría ser parallel)
- Documentación visual automática para stakeholders no-técnicos

#### 2.3 AI Assistant para Bootstrapping

**Beneficio clave:** Gemini genera arquitecturas completas desde descripciones en lenguaje natural.

**Ejemplo:**
```
Prompt: "Create a fitness coordinator agent that uses Gemini Flash 2.5,
has tools for workout generation and exercise search, and delegates
recovery questions to a recovery specialist sub-agent"

Resultado:
- Root LLM Agent con Flash model
- Custom tools configurados
- Sub-agent placeholder para recovery
- System instruction draft
```

**Limitación:** La calidad del output depende del prompt. Los autores reportan que "automated code generation is not always reliable" y puede romper en intentos subsecuentes.

#### 2.4 Testing Rápido

**Beneficio clave:** Prueba conversaciones completas sin deployment.

**Workflow:**
1. Diseñar agente en canvas
2. Click "Test" en panel derecho
3. Simular conversación user ↔ agent
4. Iterar instrucciones/tools en tiempo real

**Contraste con código puro:**
- Código: Escribir → Deploy local → cURL/Postman → Logs → Editar → Repetir
- Visual Builder: Editar → Test → Iterar (todo en navegador)

#### 2.5 Colaboración Cross-Functional

**Beneficio clave:** Product Managers y domain experts pueden diseñar sin conocer Python.

**Workflow colaborativo:**
```
1. PM describe requirements en AI Assistant
2. AI genera arquitectura base
3. PM valida flujo en canvas
4. Exporta YAML
5. Engineer traduce a código A2A con lógica de negocio real
```

**Relevancia para Genesis NGX:**
- Wellness domain experts pueden diseñar flujos de Fitness/Nutrition
- Engineers implementan integración Supabase + cost tracking
- Mantiene separación de concerns

---

### ✅ PROS: Código A2A para Producción

#### 2.6 Protocolo A2A v0.3 Completo

**Limitación de ADK nativo:** Visual Builder exporta YAML con endpoint `/run`, incompatible con A2A v0.3.

**Genesis A2A approach:**
```python
# agents/shared/a2a_server.py provee:
- GET /card          # Agent metadata (ADK: no existe)
- POST /negotiate    # Capability negotiation (ADK: no existe)
- POST /invoke       # JSON-RPC sync (ADK: usa /run)
- POST /invoke/stream # SSE streaming (ADK: diferente formato)
- GET /healthz       # Health check
```

**Por qué importa:**
- Interoperabilidad multi-framework (LangChain, AutoGen pueden consumir nuestros agentes)
- Presupuestos (`X-Budget-USD`) para cost control
- Auditoría distribuida con `X-Request-ID`

#### 2.7 Budget Enforcement

**ADK nativo:** No tiene concepto de presupuestos.

**Genesis approach:**
```python
# agents/shared/cost_calculator.py
from agents.shared.cost_calculator import CostCalculator

calc = CostCalculator()
estimated_cost = calc.calculate_gemini_cost(
    model='flash',
    input_tokens=500,
    output_tokens=200
)

if estimated_cost > float(request.headers.get('X-Budget-USD', 0)):
    raise A2ABudgetExceededError("Insufficient budget")
```

**Casos de uso:**
- User tiene $0.10 para sesión → NEXUS solo puede usar Flash models
- Prevenir runaway costs en loops infinitos
- Multi-tenancy con presupuestos por customer

#### 2.8 Supabase Integration

**ADK nativo:** No tiene awareness de base de datos.

**Genesis approach:**
```python
# Todos los writes van via RPCs con RLS
result = await supabase.rpc('agent_append_message', {
    'p_conversation_id': conv_id,
    'p_agent_type': 'nexus',
    'p_content': response_text,
    'p_tokens_used': usage.total_tokens,
    'p_cost_usd': cost
})

# Auto-logging en agent_events para audit trail
```

**Por qué importa:**
- Row Level Security garantiza data isolation
- Audit log completo para compliance
- Cost tracking por conversación/user

#### 2.9 Security Validation

**ADK nativo:** No valida PHI/PII en inputs.

**Genesis approach:**
```python
from agents.shared.security import SecurityValidator

validator = SecurityValidator()
result = validator.validate_input(user_message)

if result.contains_phi:
    return {"error": "PHI detected. This is a wellness system, not a medical device."}
```

**Regulatorio:**
- Genesis NGX scope = wellness (NO medical advice)
- Rechazar diagnoses, medications, prescriptions
- Compliance con ADR-005 (Security & Compliance)

#### 2.10 Observability

**ADK nativo:** Logging básico.

**Genesis approach:**
```python
# Distributed tracing
request_id = request.headers.get('X-Request-ID')
agent_id = AGENT_CARD['id']

# Métricas en Cloud Monitoring
latency_metric.record(duration_ms, {'agent': agent_id})
cost_metric.record(cost_usd, {'model': model_name})

# Structured logging
logger.info("invoke_completed", extra={
    "request_id": request_id,
    "method": method,
    "tokens": usage.total_tokens,
    "cost": cost_usd
})
```

**Beneficios:**
- SLO tracking (p95 latency ≤2s para Flash)
- Cost attribution por agent
- Error rate monitoring

---

## 3. Limitaciones y Pitfalls

### ❌ CONS: Restricciones del Visual Builder

#### 3.1 Agent Config Feature Limitations

**Documentación oficial:**
> "Some advanced ADK features are not supported by Visual Builder due to limitations of the Agent Config feature."

**Limitaciones específicas (2025):**

1. **Solo modelos Gemini:**
   - No soporta OpenAI, Anthropic, Llama via LangChain
   - Genesis NGX: OK (usamos 100% Gemini)

2. **No mixing de tool types:**
   - ERROR: Usar Google Search + Custom Tools simultáneamente
   - Workaround: Separar en múltiples agents
   - Relevancia: Si NEXUS necesita search + database tools, separar en sub-agents

3. **MCP Tools limitados:**
   - No se puede conectar a MCP servers desde UI
   - `MCPToolset` debe configurarse en código
   - Impacto: Herramientas externas requieren código custom

4. **Python requerido:**
   - Aunque Visual Builder es no-code, custom tools son Python-only
   - Genesis NGX: No es problema (stack 100% Python)

#### 3.2 Sincronización YAML ↔ Código

**Problema:**
```
Visual Builder → Export YAML → Translate to Python

¿Qué pasa si modificas el código Python después?
→ YAML queda desactualizado
→ Re-importar YAML en Visual Builder puede romper cambios
```

**Recomendación (de documentación):**
> "Use YAML as initial design documentation, not source of truth. Source of truth = Python code in agents/<name>/main.py"

**Workflow propuesto para Genesis NGX:**
```
1. Diseñar en Visual Builder (arquitectura inicial)
2. Exportar YAML → adk_designs/<agent>/root_agent.yaml
3. Traducir a Python → agents/<agent>/main.py
4. [CODE ES SOURCE OF TRUTH DESDE AHORA]
5. Si rediseñas, actualizar YAML manualmente (documentación)
```

#### 3.3 Edits Bidireccionales Rotos

**Documentación oficial:**
> "Some changes made to generated files may not be compatible with Visual Builder. Edit (pencil icon) is only available for agents created with Visual Builder."

**Implicación:**
- Si modificas el Python generado, no puedes volver a abrirlo en Visual Builder
- Es un workflow **one-way**: Visual → Code (NO Code → Visual)

**Mitigación:**
- Usar Visual Builder SOLO para prototipos descartables
- Para agentes production, acepta que no podrás re-importarlos

#### 3.4 Generación de Código Frágil

**Reporte de usuarios (2025):**
> "The setup was brittle after the first success, with repeated errors triggered by Gemini-generated tool code. The assistant didn't reliably overwrite the generated Python when trying to patch failures."

**Experiencia práctica:**
- Primera generación: OK
- Ediciones subsecuentes: Fallan frecuentemente
- AI Assistant no siempre regenera código correctamente

**Recomendación:**
- Iterar design en Visual Builder hasta estar satisfecho
- Exportar UNA VEZ
- Ediciones posteriores en código

#### 3.5 No Soporta A2A Protocol

**Critical para Genesis NGX:**

ADK Visual Builder genera agents con:
```yaml
# ADK native endpoints
- POST /run           # Diferente de A2A /invoke
- No /card endpoint
- No /negotiate endpoint
- No X-Budget-USD header support
- No X-Request-ID propagation
```

**Genesis NGX requiere:**
```python
# A2A v0.3 protocol (ADR-002)
- GET /card
- POST /negotiate
- POST /invoke
- POST /invoke/stream
- Headers: X-Request-ID, X-Budget-USD, X-Agent-ID
```

**Conclusión:** YAML exportado NO es deployable directamente. Requiere traducción a `A2AServer`.

---

### ⚠️ WARNINGS: Pitfalls Comunes

#### 3.6 Optimización Prematura con Visual Builder

**Anti-pattern:**
```
"Voy a diseñar toda la arquitectura de 5 agents en Visual Builder antes de escribir código"
```

**Problema:**
- Visual Builder es experimental (Nov 2025 = 2 semanas de antigüedad)
- Bugs en export de arquitecturas complejas
- Traducción manual de 5 agents consume tiempo

**Mejor approach:**
```
1. Diseñar 1 agent simple (Fitness)
2. Exportar YAML
3. Traducir a código A2A
4. Validar workflow completo
5. Iterar con siguientes agents
```

#### 3.7 Confundir Visual Builder con Deployment Tool

**Misconception:**
> "Visual Builder me permite deployar agentes sin escribir código"

**Realidad:**
- Visual Builder = design tool
- Production deployment requiere:
  - Dockerfile (containerización)
  - Cloud Run setup
  - Supabase config
  - Environment variables
  - CI/CD pipeline

**Genesis NGX workflow:**
```
Visual Builder → YAML → Python A2AServer → Docker → Cloud Run
                                          ↓
                                       Supabase
```

#### 3.8 No Version Control del Visual Builder

**Problema:**
- Visual Builder guarda estado en `adk_designs/<name>/root_agent.yaml`
- Si NO exportas después de cada cambio, pierdes trabajo
- No hay "auto-save" en navegador

**Best practice:**
```bash
# Después de diseñar en Visual Builder
1. Click "Save" en UI
2. Exportar YAML
3. git add adk_designs/<name>/root_agent.yaml
4. git commit -m "feat(adk): design fitness agent architecture"
```

#### 3.9 Prompts Vagos al AI Assistant

**Anti-pattern:**
```
Prompt: "Create a fitness agent"
```

**Resultado:** Agent genérico sin contexto de Genesis NGX.

**Mejor approach:**
```
Prompt: "Create a fitness coordinator agent that:
- Uses Gemini 2.5 Flash model (max 1000 output tokens)
- Has temperature 0.7 for creative workout variations
- Takes user goals (strength/cardio/flexibility), fitness level (beginner/intermediate/advanced), and equipment availability as inputs
- Returns structured workout plans in JSON format
- Does NOT provide medical advice or diagnose injuries
- Delegates recovery questions to a separate recovery specialist agent"
```

**Resultado:** Agent con configuración específica y boundaries claros.

---

## 4. Workflow Híbrido Recomendado

### Fase 1: Diseño Visual (Visual Builder)

**Cuándo usar:**
- [ ] Nueva arquitectura de agent (no existe código aún)
- [ ] Experimentar con Sequential vs Parallel vs Loop patterns
- [ ] Prototipar delegación entre sub-agents
- [ ] Validar flujos de conversación con PM/stakeholders

**Output:**
- YAML en `adk_designs/<agent_name>/root_agent.yaml`
- Screenshots del canvas para documentación
- Notes en `adk_designs/<agent_name>/design_notes.md`

**Duración:** 30 min - 2 horas (dependiendo de complejidad)

### Fase 2: Traducción a Código (Python + A2A)

**Checklist:**

1. **Crear estructura de agent:**
   ```bash
   mkdir -p agents/<agent_name>
   touch agents/<agent_name>/main.py
   touch agents/<agent_name>/requirements.txt
   touch agents/<agent_name>/Dockerfile
   ```

2. **Mapear YAML → AGENT_CARD:**
   ```python
   # ADK YAML
   name: fitness-coordinator
   description: Generates personalized workout plans

   # → Genesis AGENT_CARD
   AGENT_CARD = {
       "id": "fitness-coordinator",
       "capabilities": ["workout_planning", "exercise_analysis"],
       ...
   }
   ```

3. **Extraer system instruction:**
   ```yaml
   # ADK YAML
   instruction: |
     You are a fitness specialist...

   # → Python code
   system_instruction = """
   You are a fitness specialist...
   """
   ```

4. **Implementar `handle_method()`:**
   ```python
   async def handle_method(self, method: str, params: dict):
       if method == "create_workout":
           # Lógica de negocio aquí
           return {"workout": ...}
   ```

5. **Configurar model:**
   ```yaml
   # ADK YAML
   model: gemini-2.5-flash

   # → Python
   model_name = "gemini-2.5-flash"
   ```

6. **Traducir tools:**
   ```yaml
   # ADK YAML
   tools:
     - google_search

   # → Python (custom implementation)
   async def search_exercises(query: str):
       # Call Google Custom Search API
       pass
   ```

7. **Implementar sub-agent calls:**
   ```yaml
   # ADK YAML
   sub_agents:
     - recovery_specialist

   # → Python (A2A client)
   from agents.shared.a2a_client import A2AClient

   recovery_client = A2AClient(
       base_url=os.getenv("RECOVERY_AGENT_URL")
   )
   result = await recovery_client.invoke(...)
   ```

**Duración:** 2-4 horas (para agent con 2-3 methods)

### Fase 3: Testing Local (Pre-Deploy)

**Comandos:**

```bash
# Run agent locally
uvicorn "agents.fitness.main:app" --host 0.0.0.0 --port 8081

# Test A2A endpoints
curl http://localhost:8081/card
curl -X POST http://localhost:8081/invoke \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: test-123" \
  -H "X-Budget-USD: 0.01" \
  -d '{
    "jsonrpc": "2.0",
    "method": "create_workout",
    "params": {"goal": "strength", "level": "beginner"},
    "id": 1
  }'
```

**Validación:**
- [ ] `/card` devuelve AGENT_CARD correcto
- [ ] `/invoke` responde con JSON-RPC válido
- [ ] Budget enforcement funciona (rechaza si budget insuficiente)
- [ ] Errors usan códigos estándar (-32000, -32001, etc.)
- [ ] Logs estructurados muestran request_id

**Duración:** 30 min - 1 hora

### Fase 4: Deployment a Cloud Run

**No cubierto en este análisis** (ver `ADR/001-cloud-run-over-agent-engine.md`)

---

## 5. Decision Matrix: ¿Cuándo Usar Qué?

### Usar Visual Builder SI:

| Criterio | Justificación |
|----------|---------------|
| **Nuevo agent desde cero** | Bootstrapping rápido |
| **Experimentar con patterns** | Sequential vs Parallel vs Loop |
| **Arquitectura multi-nivel** | Visualizar jerarquía de sub-agents |
| **Colaboración con PM** | PM diseña, engineer implementa |
| **Prototipo descartable** | Throwaway code para validar idea |

### Usar Código Directamente SI:

| Criterio | Justificación |
|----------|---------------|
| **Agent simple (1-2 methods)** | Overhead de Visual Builder no vale la pena |
| **Requiere features no soportadas** | MCP tools, mixing tool types, non-Gemini models |
| **Modificaciones frecuentes** | Visual Builder sync es frágil |
| **CI/CD automation** | Generación programática de agents |
| **Production-critical** | Visual Builder es experimental |

### Ejemplos para Genesis NGX:

| Agent | Recomendación | Razón |
|-------|---------------|-------|
| **NEXUS** | Visual Builder → Code | Arquitectura compleja (routing a 5 agents), beneficia de visualización |
| **Fitness Coordinator** | Visual Builder → Code | Sub-agents (exercise, workout, progress), patterns Sequential/Parallel |
| **Nutrition Planner** | Visual Builder → Code | Similar a Fitness, reutilizar workflow |
| **Mental Health Coach** | Código directo | Requiere validación PHI/PII estricta (custom security logic) |
| **Recovery Specialist** | Visual Builder → Code | Agent simple pero beneficia de design collaboration |
| **Longevity Advisor** | Código directo | Features avanzadas (custom research tools, MCP integration) |

---

## 6. Integración con A2A Protocol

### Mapeo Conceptual

| ADK Concept | A2A v0.3 Equivalent | Implementation |
|-------------|---------------------|----------------|
| Agent Name | `AGENT_CARD['id']` | Kebab-case ID |
| Description | `AGENT_CARD['capabilities']` | List of verbs |
| Instruction | System prompt en LLM call | Embedded in code |
| Model | Gemini model selector | `flash`, `pro`, `lite` |
| Tools | `FunctionTool` + remote calls | Methods + A2AClient |
| Sub-agents | `RemoteA2aAgent` → `/invoke` | A2A client calls |
| Parameters | `AGENT_CARD['limits']` | Tokens, latency, cost |
| Sessions | Supabase `conversations` table | DB-backed state |

### Features NO Soportadas por ADK (requieren código custom)

1. **Budget enforcement** (`X-Budget-USD`)
2. **Capability negotiation** (`POST /negotiate`)
3. **Agent Card metadata** (`GET /card`)
4. **Cost tracking** (logging a `agent_events`)
5. **Row Level Security** (Supabase RPCs)
6. **PHI/PII validation** (SecurityValidator)
7. **Distributed tracing** (`X-Request-ID` propagation)
8. **SLO monitoring** (latency, error rate metrics)

### Traducción Automática vs Manual

**NO existe herramienta para:**
```
ADK YAML → Python A2AServer (automatic)
```

**Requiere traducción manual:**
```
1. Leer YAML exportado
2. Crear AGENT_CARD
3. Implementar handle_method() con lógica de negocio
4. Configurar Gemini client
5. Integrar Supabase RPCs
6. Añadir security validation
7. Setup logging & metrics
```

**Tiempo estimado:** 50% de la traducción es boilerplate (automatable), 50% es lógica custom.

**Potencial mejora futura:** Script `adk_to_a2a.py` que genera boilerplate.

---

## 7. Comparación con Otros Frameworks

### ADK vs LangChain vs AutoGen (Multi-Agent Systems 2025)

| Framework | Architecture | Best For | Production Maturity | A2A Support |
|-----------|--------------|----------|---------------------|-------------|
| **ADK** | Software-first, explicit orchestration | Google Cloud, Gemini-heavy, precise control | Beta (1.18.0 = Nov 2025) | Native (A2AServer) |
| **LangChain/LangGraph** | Graph-based workflows | Large ecosystem, model-agnostic, proven enterprise | Mature (2+ years) | Via adapters |
| **AutoGen (AG2)** | Conversation-driven | Azure OpenAI, multi-turn dialogues | Moderate (Microsoft Research) | Experimental |
| **CrewAI** | Role-based teams | Rapid prototyping, simple use cases | Early (startup-backed) | No |

### Por Qué Elegimos ADK para Genesis NGX

**Decisión (ADR-001):**
- Deep Google Cloud integration (Vertex AI, Cloud Run, Secret Manager)
- Gemini optimization (context caching, grounding, streaming)
- A2A protocol built-in
- Software engineering best practices (testing harness, CLI tools)

**Trade-offs aceptados:**
- Menos maduro que LangChain (pero más rápido development cycle con Google backing)
- Lock-in con Gemini models (pero son los mejores para wellness según benchmarks)
- Experimental Visual Builder (pero lo usamos solo para prototyping, no production)

---

## 8. Casos de Uso Reales

### Empresas Usando ADK en Producción (2025)

| Empresa | Caso de Uso | Notes |
|---------|-------------|-------|
| **Google** | Agentspace, Customer Engagement Suite | Tecnología interna detrás de ADK |
| **Renault Group** | Customer service agents | Verticals automóvil |
| **Box** | Document intelligence | Búsqueda y síntesis de archivos |
| **Revionics** | Pricing optimization | Retail analytics |
| **Ramp** | Buyer agent | "Built in just a few hours" con Visual Builder |

### Lessons Learned (de comunidad)

1. **"Start small, test patterns, mix and match"** (Google ADK docs)
   - No over-engineer arquitectura inicial
   - Probar Sequential, Parallel, Loop en isolation
   - Combinar solo cuando hayas validado

2. **"If agent isn't performing well, tweak prompts and tool definitions"** (ADK patterns guide)
   - Problema #1: Vague prompts
   - Problema #2: Tools mal documentadas (LLM no entiende cuándo usarlas)
   - Fix: Explicit instructions + clear tool descriptions

3. **"As you keep adding tools, single-agent becomes unwieldy"** (ADK architecture blog)
   - Señal para refactorizar a multi-agent
   - NEXUS con 10 tools = hard to debug
   - NEXUS + 5 specialized agents con 2 tools cada uno = maintainable

4. **"Automated code generation is brittle after first success"** (Tutorial review)
   - Visual Builder AI Assistant no es confiable para edits múltiples
   - Workaround: Diseñar completo, exportar una vez, editar en código

5. **"Upfront time investment in ADK pays off for production-scale"** (Comparison blog)
   - ADK es más verboso que CrewAI/AutoGen (más boilerplate)
   - Pero tiene testing harness, type safety, explicit contracts
   - Para MVP: Usar frameworks rápidos
   - Para production: ADK wins (maintainability, observability)

---

## 9. Recomendación Final para Genesis NGX

### Estrategia Híbrida: DISEÑAR (Visual) → IMPLEMENTAR (Código)

```
┌─────────────────────────────────────────────────────────────┐
│                     FASE 1: DISCOVERY                        │
│  Visual Builder para experimentar con arquitecturas          │
│  - NEXUS routing patterns                                    │
│  - Sequential vs Parallel para specialized agents            │
│  - Sub-agent delegation strategies                           │
│  Duración: 1-2 sprints                                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  FASE 2: IMPLEMENTATION                      │
│  Traducir diseños a Python A2AServer                        │
│  - Implementar AGENT_CARD (capabilities, limits)            │
│  - Codificar handle_method() con lógica de negocio          │
│  - Integrar Supabase RPCs, cost tracking, security          │
│  - Testing contractual (A2A endpoints)                       │
│  Duración: 2-4 sprints (parallel por agent)                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   FASE 3: PRODUCTION                         │
│  Deploy a Cloud Run con A2A v0.3                            │
│  - Dockerfile containerization                               │
│  - CI/CD pipeline (lint, test, deploy)                      │
│  - Monitoring (SLOs, cost, errors)                          │
│  - YAML archivado en adk_designs/ como documentación        │
│  Duración: Continuo                                          │
└─────────────────────────────────────────────────────────────┘
```

### Agents a Prototipar en Visual Builder

| Agent | Priority | Visual Builder? | Razón |
|-------|----------|-----------------|-------|
| **NEXUS** | P0 | ✅ YES | Arquitectura compleja, routing a 5 agents, beneficia de visualización |
| **Fitness** | P1 | ✅ YES | Sub-agents (exercise DB, workout gen, progress tracking), patterns exploración |
| **Nutrition** | P1 | ✅ YES | Similar a Fitness, reutilizar workflow aprendido |
| **Mental Health** | P2 | ❌ NO | Requiere PHI/PII validation custom (código directo más rápido) |
| **Recovery** | P2 | ✅ YES | Colaboración con domain expert (fisioterapeuta), design visual ayuda comunicación |
| **Longevity** | P3 | ❌ NO | Features avanzadas (research tools, MCP integration para papers científicos) |

### Criterios de Éxito

**Visual Builder fase exitosa SI:**
- [ ] Tenemos YAML para NEXUS + 3 specialized agents
- [ ] Screenshots de canvas documentan arquitectura
- [ ] PM y engineers alineados en flujos de conversación
- [ ] Identificamos patterns reutilizables (Sequential para research, Parallel para queries independientes)

**Traducción a código exitosa SI:**
- [ ] Todos agents exponen A2A endpoints completos (`/card`, `/negotiate`, `/invoke`, `/invoke/stream`)
- [ ] Budget enforcement funciona (tests con diferentes presupuestos)
- [ ] Supabase integration (writes via RPCs, RLS verified)
- [ ] Security validation (PHI/PII detection tests)
- [ ] SLO targets met (p95 latency ≤2s para Flash agents)
- [ ] Cost tracking en `agent_events` (audit trail completo)

### Warnings y No-Gos

**NO usar Visual Builder para:**
- ❌ Production deployment directo (requiere traducción)
- ❌ Version control del estado del canvas (solo exportar YAML)
- ❌ Agents con lógica de negocio compleja (código es más expresivo)
- ❌ Debugging issues de producción (logs están en código, no YAML)

**SÍ usar Visual Builder para:**
- ✅ Onboarding nuevos engineers (visualizar arquitectura)
- ✅ Diseño colaborativo con stakeholders
- ✅ Experimentación rápida de patterns
- ✅ Documentación visual de architecture decisions

---

## 10. Roadmap de Implementación

### Sprint 1-2: Visual Builder Discovery

**Objetivos:**
1. Instalar ADK 1.18.0+ y configurar Visual Builder
2. Diseñar NEXUS orchestrator (routing a 5 agents)
3. Diseñar Fitness Agent (workout planning con sub-agents)
4. Exportar YAMLs a `adk_designs/`

**Deliverables:**
- `adk_designs/nexus/root_agent.yaml`
- `adk_designs/fitness/root_agent.yaml`
- Screenshots de canvas en `adk_designs/screenshots/`
- Design notes documentando decisiones

### Sprint 3-4: Traducción NEXUS

**Objetivos:**
1. Crear `agents/nexus/main.py` con `A2AServer`
2. Implementar `AGENT_CARD` y routing logic
3. Integrar A2AClient para llamar specialized agents
4. Testing local con `/invoke` endpoints

**Deliverables:**
- NEXUS funcionando en `localhost:8080`
- Tests contractuales (A2A protocol compliance)
- Logs estructurados con request tracing

### Sprint 5-6: Traducción Fitness

**Objetivos:**
1. Crear `agents/fitness/main.py`
2. Implementar workout planning methods
3. Integrar Supabase RPCs (read user profile, write workouts)
4. Cost tracking y budget enforcement

**Deliverables:**
- Fitness Agent en `localhost:8081`
- Supabase integration tests
- Cost calculator validation

### Sprint 7-8: Deployment Pipeline

**Objetivos:**
1. Dockerfiles para NEXUS + Fitness
2. Cloud Run deployment configs
3. CI/CD con GitHub Actions (lint → test → deploy)
4. Monitoring dashboards (SLOs, costs)

**Deliverables:**
- NEXUS + Fitness deployados en Cloud Run us-central1
- Metrics en Cloud Monitoring
- Alerts configurados (SLO violations, budget overruns)

### Sprint 9+: Scaling

**Objetivos:**
1. Iterar con Nutrition, Mental Health, Recovery, Longevity
2. Reutilizar patterns aprendidos
3. Refactorizar shared code (abstraction improvements)

---

## 11. Recursos y Referencias

### Documentación Oficial

- **ADK Main Docs:** https://google.github.io/adk-docs/
- **Visual Builder Guide:** https://google.github.io/adk-docs/visual-builder/
- **A2A Protocol Intro:** https://google.github.io/adk-docs/a2a/intro/
- **Multi-Agent Patterns:** https://google.github.io/adk-docs/agents/multi-agents/
- **Agent Config Format:** https://google.github.io/adk-docs/agents/config/

### Tutoriales Externos

- **Thomas Chong (Google Cloud):** "Building AI Agents Visually with Google ADK Visual Agent Builder" (Medium, Nov 2025)
- **DataCamp Tutorial:** "Google ADK Visual Agent Builder Tutorial With Demo Project: Travel Planner"
- **Karl Weinmeister (Google Cloud):** "Architecting a Multi-Agent System with Google A2A and ADK" (Medium)
- **Heiko Hotz (Google Cloud):** "Getting Started with Google A2A: A Hands-on Tutorial"

### Genesis NGX Internal Docs

- **CLAUDE.md:** Contexto del proyecto y convenciones
- **ADR/001:** Cloud Run over Agent Engine
- **ADR/002:** A2A v0.3 Protocol (este análisis referencia constantemente)
- **ADR/003:** Supabase-only architecture
- **ADR/004:** Gemini model selection
- **ADR/005:** Security and compliance
- **adk_designs/TRANSLATION_GUIDE.md:** Workflow híbrido (versión inicial, este análisis lo expande)

### GitHub Repositories

- **ADK Python:** https://github.com/google/adk-python
- **ADK Discussions:** https://github.com/google/adk-python/discussions
- **Visual Builder Demo:** https://github.com/thomas-chong/google-adk-visual-agent-builder-demo

### Comparaciones de Frameworks

- **ADK vs LangChain vs AutoGen (2025):** https://medium.com/codetodeploy/google-adk-vs-langchain-vs-autogen-the-2025-agentic-ai-benchmark-that-will-shock-you-5f9899b62319
- **Choosing AI Agent Framework Deep Dive:** https://medium.com/@prabhudev.guntur/choosing-your-ai-agent-framework-google-adk-vs-autogen-langchain-crewai-a-deep-dive-c0f07e3a9d13
- **14 AI Agent Frameworks Compared (2025):** https://softcery.com/lab/top-14-ai-agent-frameworks-of-2025-a-founders-guide-to-building-smarter-systems

---

## 12. Preguntas Frecuentes

### ¿Visual Builder reemplaza escribir código?

**NO.** Visual Builder es una herramienta de **diseño** y **prototipado**. Para producción necesitas:
- Código Python con lógica de negocio
- Integración con databases (Supabase)
- Security validation (PHI/PII)
- Cost tracking y budget enforcement
- Observability (logging, metrics)

### ¿Puedo deployar YAML directamente a Cloud Run?

**NO.** El YAML exportado:
1. Usa endpoints ADK nativos (`/run`) incompatibles con A2A v0.3
2. No tiene concepto de presupuestos, negotiation, agent cards
3. No integra con Supabase
4. No tiene security validation

Requiere traducción a `A2AServer`.

### ¿Qué pasa si edito el código Python y quiero volver a Visual Builder?

**NO ES POSIBLE** de forma confiable. El workflow es **one-way**: Visual Builder → Code.

Si necesitas rediseñar, opciones:
1. Actualizar YAML manualmente (documentación)
2. Crear nuevo diseño en Visual Builder desde cero
3. Editar código directamente (source of truth)

### ¿Visual Builder soporta MCP tools?

**LIMITADO.** Puedes configurar MCP tools en código, pero:
- Visual Builder UI no tiene dropdown para MCP servers
- Debes agregar `MCPToolset` en código Python después de exportar
- No puedes mixing MCP + built-in tools (Google Search) en mismo agent

### ¿Cuánto tiempo toma traducir YAML a código A2A?

**Estimación:**
- Agent simple (1-2 methods): 2-3 horas
- Agent medio (3-5 methods, 1 sub-agent): 4-6 horas
- Agent complejo (NEXUS con routing a 5 agents): 8-12 horas

**Factores:**
- 50% boilerplate (AGENT_CARD, endpoints, logging)
- 50% lógica de negocio (methods, Supabase integration, security)

**Oportunidad:** Script `adk_to_a2a.py` para automatizar boilerplate.

### ¿Visual Builder es production-ready?

**NO (Nov 2025).** Es experimental:
- Lanzado hace 2 semanas (ADK 1.18.0 = Nov 5, 2025)
- Bugs reportados en generación de código
- AI Assistant no confiable para ediciones múltiples
- Feature set limitado (Agent Config restrictions)

**Usar para:** Prototipado, learning, diseño colaborativo
**NO usar para:** Production deployment directo, mission-critical agents

### ¿Debería usar Visual Builder para todos los agents?

**NO.** Usar decision matrix (Sección 5):
- Agents complejos con sub-agents: SÍ (visualización ayuda)
- Agents simples (1-2 methods): NO (overhead no vale la pena)
- Agents con features custom: NO (código directo más rápido)
- Agents para colaboración con PM: SÍ (comunicación visual)

---

## 13. Conclusión

### Resumen Ejecutivo

El **workflow híbrido Visual Builder → Código A2A** es **VIABLE y RECOMENDADO** para Genesis NGX con las siguientes condiciones:

✅ **HACER:**
1. Usar Visual Builder para **diseño inicial** de arquitecturas multi-agente complejas
2. Exportar YAML como **documentación** de decisiones de diseño
3. Traducir a **código Python A2AServer** para production
4. Mantener **código como source of truth**, YAML como artefacto histórico
5. Aplicar workflow híbrido a **NEXUS + agents con sub-agents** (Fitness, Nutrition, Recovery)

❌ **NO HACER:**
1. Intentar deployar YAML directamente (requiere A2A translation)
2. Usar Visual Builder para agents simples (overhead > beneficio)
3. Confiar en ediciones bidireccionales YAML ↔ Code (es one-way)
4. Sobre-depender de AI Assistant (es frágil para ediciones múltiples)
5. Usar Visual Builder para features no soportadas (MCP, mixing tools, non-Gemini models)

### Trade-offs Aceptados

| Beneficio | Costo |
|-----------|-------|
| Diseño rápido (minutos vs horas) | Traducción manual requerida |
| Visualización de arquitectura | No editable bidireccionalmente |
| Colaboración cross-functional | YAML puede quedar desactualizado |
| Testing rápido en UI | NO reemplaza testing contractual |
| AI-powered bootstrapping | Código generado requiere review |

### Impacto en Genesis NGX

**Aceleración estimada:**
- Diseño de NEXUS + 5 agents: **50% más rápido** (2 semanas → 1 semana en Visual Builder)
- Comunicación con stakeholders: **Mejora significativa** (canvas visual vs explicar código)
- Onboarding de engineers: **30% más rápido** (visualización de arquitectura)

**Inversión requerida:**
- Setup Visual Builder: 1 hora
- Learning curve: 4-8 horas (por engineer)
- Traducción YAML → Code: 40-60 horas total (6 agents × 8 horas promedio)

**ROI:** Positivo si consideramos:
- Menos iteraciones de diseño (validar antes de codificar)
- Mejor alineamiento PM ↔ Engineering
- Documentación visual automática

### Next Steps

1. **Spike (1 sprint):**
   - Instalar ADK 1.18.0+
   - Diseñar NEXUS en Visual Builder
   - Traducir a código A2A
   - Validar workflow completo
   - Decisión: Continuar o pivot a código-only

2. **Si spike exitoso → Implementar strategy (Sección 10):**
   - Sprint 1-2: Visual Builder discovery
   - Sprint 3-8: Traducción y deployment
   - Sprint 9+: Scaling a todos los agents

3. **Si spike falla → Fallback:**
   - Implementar NEXUS directamente en código
   - Usar Visual Builder solo para documentación (diseñar arquitectura, exportar screenshots)
   - Evaluar Visual Builder nuevamente en 6 meses (madurez del producto)

---

**Documento generado:** 2025-11-19
**Próxima revisión:** 2025-12-19 (post-spike, actualizar con aprendizajes)
**Autor:** Claude Code (investigación)
**Aprobación requerida:** Tech Lead, PM

---

## Appendix A: Mapeo Completo YAML → A2A

### Ejemplo Completo: Fitness Agent

**ADK YAML Export:**
```yaml
name: fitness-coordinator
description: Generates personalized workout plans based on user goals and fitness level
model: gemini-2.5-flash
instruction: |
  You are a fitness specialist AI assistant. Your role is to:

  1. Analyze user fitness goals (strength, cardio, flexibility, weight loss)
  2. Consider current fitness level (beginner, intermediate, advanced)
  3. Account for available equipment (bodyweight, dumbbells, gym, home)
  4. Respect time constraints and injury history
  5. Generate structured workout plans in JSON format

  IMPORTANT GUIDELINES:
  - DO NOT provide medical advice or diagnose injuries
  - DO NOT prescribe medications or treatments
  - If user mentions injury, recommend consulting a healthcare professional
  - Focus on wellness and general fitness guidance only

  When creating workout plans, include:
  - Exercise name and muscle groups targeted
  - Sets, reps, and rest periods
  - Progression suggestions
  - Safety tips

tools:
  - name: search_exercises
    description: Search exercise database by muscle group or equipment
  - name: calculate_progression
    description: Calculate progressive overload recommendations

sub_agents:
  - name: recovery-specialist
    description: Handles recovery and injury prevention questions

parameters:
  max_output_tokens: 1000
  temperature: 0.7
  top_p: 0.95
```

**Genesis A2A Translation:**

```python
# agents/fitness/main.py

from agents.shared.a2a_server import A2AServer
from agents.shared.a2a_client import A2AClient
from agents.shared.cost_calculator import CostCalculator
from agents.shared.security import SecurityValidator
from typing import Dict, Any, AsyncGenerator
import os
import logging

logger = logging.getLogger(__name__)

# 1. AGENT_CARD (YAML name/description → metadata)
AGENT_CARD = {
    "id": "fitness-coordinator",
    "version": "0.1.0",
    "capabilities": [
        "workout_planning",
        "exercise_search",
        "progression_calculation",
        "fitness_assessment"
    ],
    "limits": {
        "max_input_tokens": 20000,
        "max_output_tokens": 1000,  # From YAML parameters
        "max_latency_ms": 2000,
        "max_cost_per_invoke": 0.01,
    },
    "privacy": {
        "pii": False,
        "phi": False,
        "data_retention_days": 90
    },
    "auth": {
        "method": "oidc",
        "audience": "fitness-coordinator"
    },
}

class FitnessAgent(A2AServer):
    def __init__(self):
        super().__init__(AGENT_CARD)
        self.cost_calc = CostCalculator()
        self.security = SecurityValidator()

        # 2. SUB-AGENT CLIENT (YAML sub_agents → A2AClient)
        self.recovery_client = A2AClient(
            base_url=os.getenv("RECOVERY_AGENT_URL", "http://recovery:8080")
        )

    # 3. SYSTEM INSTRUCTION (YAML instruction → prompt)
    SYSTEM_INSTRUCTION = """You are a fitness specialist AI assistant. Your role is to:

    1. Analyze user fitness goals (strength, cardio, flexibility, weight loss)
    2. Consider current fitness level (beginner, intermediate, advanced)
    3. Account for available equipment (bodyweight, dumbbells, gym, home)
    4. Respect time constraints and injury history
    5. Generate structured workout plans in JSON format

    IMPORTANT GUIDELINES:
    - DO NOT provide medical advice or diagnose injuries
    - DO NOT prescribe medications or treatments
    - If user mentions injury, recommend consulting a healthcare professional
    - Focus on wellness and general fitness guidance only

    When creating workout plans, include:
    - Exercise name and muscle groups targeted
    - Sets, reps, and rest periods
    - Progression suggestions
    - Safety tips
    """

    async def handle_method(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        4. METHODS (YAML capabilities → business logic)
        """

        if method == "create_workout":
            return await self._create_workout(params)

        elif method == "search_exercises":
            return await self._search_exercises(params)

        elif method == "calculate_progression":
            return await self._calculate_progression(params)

        else:
            return {"error": "unknown_method", "supported": list(AGENT_CARD["capabilities"])}

    async def _create_workout(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        YAML description → Implementation
        """
        # Extract parameters
        user_id = params.get("user_id")
        goal = params.get("goal")  # strength, cardio, flexibility
        fitness_level = params.get("fitness_level", "beginner")
        equipment = params.get("equipment", ["bodyweight"])
        time_minutes = params.get("time_minutes", 30)

        # Security validation
        validation = self.security.validate_input(f"{goal} {fitness_level}")
        if validation.contains_phi:
            return {
                "error": "phi_detected",
                "message": "This is a wellness system. Please consult a healthcare professional for medical advice."
            }

        # Check for injury mentions (delegate to recovery specialist)
        if "injury" in params.get("notes", "").lower():
            logger.info("Delegating to recovery specialist", extra={"user_id": user_id})
            recovery_response = await self.recovery_client.invoke(
                method="assess_injury_risk",
                params={"notes": params.get("notes")},
                request_id=self.current_request_id,
                budget_usd=0.005  # Sub-budget
            )
            return {
                "delegated": True,
                "specialist": "recovery",
                "response": recovery_response
            }

        # 5. MODEL CALL (YAML model + parameters → Gemini)
        user_prompt = f"""
        Create a {time_minutes}-minute workout plan for:
        - Goal: {goal}
        - Fitness Level: {fitness_level}
        - Available Equipment: {', '.join(equipment)}

        Return a JSON array of exercises with format:
        {{
            "exercises": [
                {{
                    "name": "Exercise Name",
                    "muscle_groups": ["primary", "secondary"],
                    "sets": 3,
                    "reps": 12,
                    "rest_seconds": 60,
                    "equipment": "dumbbells",
                    "notes": "Safety tip or progression"
                }}
            ],
            "total_time_estimate": 30,
            "progression_notes": "How to progress next week"
        }}
        """

        # Call Gemini with ADK YAML parameters
        workout_plan = await self._call_gemini(
            system_instruction=self.SYSTEM_INSTRUCTION,
            user_prompt=user_prompt,
            model="gemini-2.5-flash",  # From YAML
            max_output_tokens=1000,    # From YAML parameters
            temperature=0.7,           # From YAML parameters
            top_p=0.95                 # From YAML parameters
        )

        # Parse JSON response
        import json
        try:
            plan_json = json.loads(workout_plan)
        except json.JSONDecodeError:
            return {"error": "invalid_json", "raw": workout_plan}

        # 6. COST TRACKING (Genesis addition, not in YAML)
        cost = self.cost_calc.calculate_gemini_cost(
            model="flash",
            input_tokens=len(user_prompt.split()) * 1.3,  # Rough estimate
            output_tokens=len(workout_plan.split()) * 1.3
        )

        # Log to Supabase
        await self._log_to_supabase(
            conversation_id=params.get("conversation_id"),
            method="create_workout",
            tokens_used=self.last_usage.total_tokens,
            cost_usd=cost
        )

        return {
            "workout_plan": plan_json,
            "cost_usd": cost,
            "model": "gemini-2.5-flash"
        }

    async def _search_exercises(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        YAML tool: search_exercises → Implementation
        """
        muscle_group = params.get("muscle_group")
        equipment = params.get("equipment")

        # Query Supabase exercise database
        from supabase import create_client
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )

        query = supabase.table("exercises").select("*")

        if muscle_group:
            query = query.contains("muscle_groups", [muscle_group])
        if equipment:
            query = query.eq("equipment", equipment)

        result = query.limit(10).execute()

        return {
            "exercises": result.data,
            "count": len(result.data)
        }

    async def _calculate_progression(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        YAML tool: calculate_progression → Implementation
        """
        current_weight = params.get("current_weight_kg")
        current_reps = params.get("current_reps")
        goal = params.get("goal", "strength")

        # Progressive overload formulas
        if goal == "strength":
            # Increase weight by 2.5-5% per week
            next_weight = current_weight * 1.025
            next_reps = current_reps  # Same reps
        elif goal == "hypertrophy":
            # Increase reps first, then weight
            if current_reps < 12:
                next_weight = current_weight
                next_reps = current_reps + 1
            else:
                next_weight = current_weight * 1.05
                next_reps = 8  # Reset to lower rep range
        else:
            # Endurance: increase reps
            next_weight = current_weight
            next_reps = current_reps + 2

        return {
            "current": {"weight_kg": current_weight, "reps": current_reps},
            "next_session": {"weight_kg": round(next_weight, 1), "reps": next_reps},
            "progression_type": goal
        }

    async def _call_gemini(
        self,
        system_instruction: str,
        user_prompt: str,
        model: str,
        max_output_tokens: int,
        temperature: float,
        top_p: float
    ) -> str:
        """
        7. GEMINI CLIENT (abstraction for consistency)
        """
        import google.generativeai as genai

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        gemini_model = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_instruction,
            generation_config={
                "max_output_tokens": max_output_tokens,
                "temperature": temperature,
                "top_p": top_p,
            }
        )

        response = await gemini_model.generate_content_async(user_prompt)
        self.last_usage = response.usage_metadata  # Store for cost calc

        return response.text

    async def _log_to_supabase(
        self,
        conversation_id: str,
        method: str,
        tokens_used: int,
        cost_usd: float
    ):
        """
        8. SUPABASE INTEGRATION (Genesis addition)
        """
        from supabase import create_client

        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )

        # Call RPC (respects RLS)
        await supabase.rpc('agent_append_message', {
            'p_conversation_id': conversation_id,
            'p_agent_type': 'fitness',
            'p_content': f"Executed {method}",
            'p_tokens_used': tokens_used,
            'p_cost_usd': cost_usd
        }).execute()

# 9. FASTAPI APP (A2AServer provides endpoints)
agent = FitnessAgent()
app = agent.app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
```

**Dockerfile:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY agents/fitness/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared libraries
COPY agents/shared /app/agents/shared

# Copy agent code
COPY agents/fitness /app/agents/fitness

# Expose port
EXPOSE 8081

# Run agent
CMD ["uvicorn", "agents.fitness.main:app", "--host", "0.0.0.0", "--port", "8081"]
```

**requirements.txt:**
```
fastapi==0.104.1
uvicorn==0.24.0
google-generativeai==0.3.1
supabase==2.1.1
pydantic==2.5.0
```

### Comparación Visual

| Component | ADK YAML (Visual Builder) | Genesis A2A (Code) | Lines of Code |
|-----------|---------------------------|---------------------|---------------|
| Agent Metadata | `name`, `description` (5 lines) | `AGENT_CARD` (18 lines) | +13 |
| System Instruction | `instruction` (YAML string) | Class constant (same) | 0 |
| Model Config | `model`, `parameters` (5 lines) | Gemini client call (10 lines) | +5 |
| Tools | `tools` list (2 items) | Methods (40 lines total) | +38 |
| Sub-agents | `sub_agents` list (1 item) | A2AClient setup (5 lines) | +4 |
| **GENESIS ADDITIONS** | (none) | | |
| - Budget enforcement | N/A | Header check (5 lines) | +5 |
| - Cost tracking | N/A | Calculator + logging (15 lines) | +15 |
| - Security validation | N/A | PHI/PII check (10 lines) | +10 |
| - Supabase integration | N/A | RPC calls (20 lines) | +20 |
| - A2A endpoints | N/A | Inherited from A2AServer | 0 (shared) |
| **TOTAL** | ~50 lines YAML | ~250 lines Python | +200 |

**Analysis:**
- **80% código adicional** vs YAML
- **60% es boilerplate** (AGENT_CARD, logging, client setup) → **Automatizable**
- **40% es lógica de negocio** (methods, Supabase, security) → **Requiere traducción manual**

**Oportunidad de mejora:** Script `adk_to_a2a.py` que genera los primeros 150 lines, developer escribe los restantes 100.

---

## Appendix B: Troubleshooting Common Issues

### Issue 1: Visual Builder No Carga

**Síntoma:**
```
$ adk web adk_designs
ERROR: Failed to start web server
```

**Solución:**
```bash
# Verificar versión ADK
pip show google-adk  # Debe ser ≥1.18.0

# Reinstalar
pip uninstall google-adk
pip install google-adk>=1.18.0

# Lanzar con verbose logging
adk web adk_designs --host 127.0.0.1 --port 8000 --reload
```

### Issue 2: Export YAML Vacío

**Síntoma:** Exportar agent genera archivo vacío o corrupto.

**Solución:**
1. Click "Save" en UI ANTES de exportar
2. Verificar que agent tiene al menos:
   - Name
   - Description
   - Model seleccionado
3. Refresh navegador y reintentar

### Issue 3: AI Assistant No Responde

**Síntoma:** Escribir prompt en asistente no genera agent.

**Solución:**
```bash
# Verificar API key de Gemini configurada
echo $GEMINI_API_KEY

# Si no está configurada
export GEMINI_API_KEY="your-api-key"

# Relanzar adk web
```

### Issue 4: Traducción Manual Toma Mucho Tiempo

**Síntoma:** Cada agent toma 4-6 horas traducir.

**Solución:**
1. Crear template base `agents/shared/agent_template.py`
2. Copy-paste boilerplate (AGENT_CARD, __init__, _call_gemini)
3. Solo escribir métodos específicos del agent
4. Considerar desarrollar script `adk_to_a2a.py` (ver Appendix A)

### Issue 5: Sub-Agent Calls Fallan

**Síntoma:**
```
ERROR: Connection refused to http://recovery:8080
```

**Solución:**
```python
# Local development: usar localhost
self.recovery_client = A2AClient(
    base_url=os.getenv(
        "RECOVERY_AGENT_URL",
        "http://localhost:8082"  # Puerto local, no service name
    )
)

# Production (Cloud Run): usar service URLs
# RECOVERY_AGENT_URL=https://recovery-xyz.run.app
```

### Issue 6: Budget Exceeded Errors

**Síntoma:**
```
{"error": {"code": -32001, "message": "BUDGET_EXCEEDED"}}
```

**Debugging:**
```python
# Agregar logging de budget
logger.info("Budget check", extra={
    "budget_usd": budget,
    "estimated_cost": estimated,
    "passed": estimated <= budget
})

# Verificar cálculo de costos
calc = CostCalculator()
cost = calc.calculate_gemini_cost(...)
print(f"Estimated: ${cost:.6f}")
```

### Issue 7: YAML Importa Mal Custom Tools

**Síntoma:** Custom tools en YAML no funcionan al exportar.

**Solución:**
- Visual Builder genera tools en `adk_designs/<name>/tools/__init__.py`
- Copiar manualmente a `agents/<name>/tools/`
- Importar en `main.py`:
  ```python
  from agents.fitness.tools import search_exercises, calculate_progression
  ```

### Issue 8: Visual Builder Crashea con Arquitecturas Grandes

**Síntoma:** Canvas no renderiza con >10 agents.

**Workaround:**
- Dividir en sub-gráficos (e.g., NEXUS por separado de specialized agents)
- Exportar cada sub-grafo
- Integrar manualmente en código

---

**Fin del análisis.**
