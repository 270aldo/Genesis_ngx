# ADK Visual Builder: Referencia Rápida

**Última actualización:** 2025-11-19

---

## TL;DR: Decisión para Genesis NGX

### ✅ USAR Visual Builder para:
- NEXUS (arquitectura compleja, routing a 5 agents)
- Fitness Agent (sub-agents, patterns Sequential/Parallel)
- Nutrition Agent (similar a Fitness)
- Recovery Agent (colaboración con domain expert)

### ❌ NO USAR Visual Builder para:
- Mental Health (requiere PHI/PII validation custom)
- Longevity (features avanzadas: MCP integration)
- Agents simples con 1-2 métodos

### Workflow: Diseño → Código → Deploy
```
Visual Builder (30m-2h)
    ↓ Export YAML
Python A2AServer (2-6h por agent)
    ↓ Dockerfile
Cloud Run (A2A v0.3 endpoints)
```

---

## Comandos Esenciales

### Setup
```bash
pip install google-adk>=1.18.0
adk web adk_designs --host 127.0.0.1 --port 8000
# Abrir http://localhost:8000/dev-ui/
```

### Exportar Diseño
1. Diseñar en canvas
2. Click "Save"
3. Click "Export" → Guardar YAML
4. Mover a `adk_designs/<agent_name>/root_agent.yaml`

### Traducir a Código
```bash
# Ver ejemplo completo en ADK_VISUAL_BUILDER_ANALYSIS.md Appendix A
# Template base:
cp agents/shared/agent_template.py agents/<nombre>/main.py
# Editar AGENT_CARD, handle_method(), system_instruction
```

### Testing Local
```bash
uvicorn "agents.fitness.main:app" --host 0.0.0.0 --port 8081
curl http://localhost:8081/card
curl -X POST http://localhost:8081/invoke \
  -H "X-Request-ID: test" \
  -H "X-Budget-USD: 0.01" \
  -d '{"jsonrpc":"2.0","method":"create_workout","params":{...},"id":1}'
```

---

## Pros vs Cons

### ✅ PROS: Visual Builder

| Beneficio | Tiempo Ahorrado |
|-----------|-----------------|
| Diseño arquitectura multi-agente | 50% (2 semanas → 1 semana) |
| Visualización de flujos | Comunicación PM ↔ Engineering clara |
| AI Assistant bootstrapping | Genera estructura en minutos |
| Testing rápido en UI | Sin deployment para iterar |
| Colaboración cross-functional | PM diseña, engineers codifican |

### ❌ CONS: Limitaciones

| Limitación | Impacto en Genesis NGX |
|------------|------------------------|
| Solo Gemini models | OK (usamos 100% Gemini) |
| No mixing tools (Search + Custom) | Separar en sub-agents |
| No A2A protocol nativo | Requiere traducción manual |
| Experimental (Nov 2025) | NO usar para production-critical |
| Edits bidireccionales rotos | Workflow one-way (Visual → Code) |

---

## Mapeo YAML → A2A

| ADK YAML | Genesis A2AServer |
|----------|-------------------|
| `name` | `AGENT_CARD['id']` |
| `description` | `AGENT_CARD['capabilities']` |
| `instruction` | System prompt en `_call_gemini()` |
| `model` | Gemini model selector |
| `tools` | Métodos en clase + FunctionTool |
| `sub_agents` | `A2AClient` calls |
| `parameters.max_output_tokens` | `AGENT_CARD['limits']['max_output_tokens']` |

### Adiciones Requeridas (NO en YAML)

```python
# Genesis-specific (no existen en ADK YAML)
- Budget enforcement (X-Budget-USD header)
- Cost tracking (CostCalculator + Supabase logging)
- Security validation (PHI/PII detection)
- Supabase RPCs (agent_append_message)
- A2A endpoints (/card, /negotiate, /invoke, /invoke/stream)
```

---

## Decision Matrix

### ¿Usar Visual Builder?

**SÍ si:**
- [ ] Agent tiene sub-agents
- [ ] Arquitectura multi-nivel (Sequential/Parallel/Loop)
- [ ] Necesitas colaboración visual con PM
- [ ] Primera vez diseñando este tipo de agent

**NO si:**
- [ ] Agent simple (1-2 métodos)
- [ ] Requiere MCP tools
- [ ] Necesitas mixing Google Search + Custom Tools
- [ ] Production-critical (usar código directo)

---

## Pitfalls Comunes

### ⚠️ WARNING 1: YAML NO es Deployable
```bash
# ❌ INCORRECTO
gcloud run deploy --image <yaml_export>

# ✅ CORRECTO
Visual Builder → YAML → Python A2AServer → Docker → Cloud Run
```

### ⚠️ WARNING 2: Edits Bidireccionales NO Funcionan
```
Visual Builder → Export YAML ✅
Edit Python code ✅
Re-import to Visual Builder ❌ (rompe)

# Source of truth: Python code
# YAML: Documentación histórica
```

### ⚠️ WARNING 3: AI Assistant es Frágil
```
Primera generación: OK
Ediciones múltiples: Fallan frecuentemente

# Mejor approach:
# 1. Diseñar completo en Visual Builder
# 2. Exportar UNA VEZ
# 3. Ediciones posteriores en código
```

### ⚠️ WARNING 4: No Sobre-diseñar
```
# ❌ Anti-pattern
Diseñar 5 agents complejos en Visual Builder antes de código

# ✅ Mejor approach
1 agent simple → YAML → Code → Validar workflow
Iterar con siguiente agent
```

---

## Checklist de Traducción

Cuando traduces YAML → Código A2A:

### Setup Básico
- [ ] Crear `agents/<nombre>/main.py`
- [ ] Crear `agents/<nombre>/requirements.txt`
- [ ] Crear `agents/<nombre>/Dockerfile`

### AGENT_CARD
- [ ] Mapear `name` → `AGENT_CARD['id']`
- [ ] Extraer capabilities de `description`
- [ ] Configurar `limits` (tokens, latency, cost)
- [ ] Definir `privacy` (pii, phi, retention)
- [ ] Setup `auth` (OIDC audience)

### Business Logic
- [ ] Copiar `instruction` → `SYSTEM_INSTRUCTION`
- [ ] Implementar `handle_method()` con métodos del agent
- [ ] Traducir `tools` → métodos de clase
- [ ] Configurar sub-agents → `A2AClient` calls

### Genesis-Specific
- [ ] Integrar `CostCalculator` para budget checks
- [ ] Agregar `SecurityValidator` para PHI/PII
- [ ] Implementar Supabase RPCs (`agent_append_message`)
- [ ] Setup logging estructurado con `request_id`

### Testing
- [ ] Validar `/card` endpoint
- [ ] Validar `/invoke` con JSON-RPC
- [ ] Test budget enforcement (rechaza si insuficiente)
- [ ] Test error codes (-32000, -32001, etc.)
- [ ] Verificar logs en Supabase `agent_events`

---

## Estimaciones de Tiempo

| Actividad | Duración |
|-----------|----------|
| **Setup Visual Builder** | 1 hora (one-time) |
| **Diseñar 1 agent en UI** | 30 min - 2 horas |
| **Exportar YAML** | 5 minutos |
| **Traducir YAML → A2A (simple)** | 2-3 horas |
| **Traducir YAML → A2A (medio)** | 4-6 horas |
| **Traducir YAML → A2A (complejo)** | 8-12 horas |
| **Testing local** | 30 min - 1 hora |

**Total para 1 agent medio:** ~6-8 horas (diseño + código + testing)

**Comparado con código directo:** ~10-12 horas (sin visualización)

**Ahorro:** 30-40% en diseño + mejor comunicación con stakeholders

---

## ROI Analysis

### Inversión
- Setup inicial: 1 hora
- Learning curve: 4-8 horas/engineer
- Traducción 6 agents: 40-60 horas total

### Retorno
- Diseño 50% más rápido (validar antes de codificar)
- Comunicación PM ↔ Engineering mejorada
- Onboarding engineers 30% más rápido (visualización)
- Documentación visual automática

### Decisión
**ROI positivo SI:**
- Proyecto multi-agent con >3 agents
- Team distribuido (PM, engineers, domain experts)
- Arquitecturas complejas (sub-agents, loops, parallel)

**ROI negativo SI:**
- Agent único simple
- Solo developers (no necesitan visual)
- Timeline extremadamente ajustado (no tiempo para learning curve)

---

## Recursos

### Documentación
- **Análisis completo:** `docs/ADK_VISUAL_BUILDER_ANALYSIS.md`
- **Translation guide:** `adk_designs/TRANSLATION_GUIDE.md`
- **ADR A2A protocol:** `ADR/002-a2a-v03-protocol.md`

### ADK Official Docs
- Main: https://google.github.io/adk-docs/
- Visual Builder: https://google.github.io/adk-docs/visual-builder/
- A2A Protocol: https://google.github.io/adk-docs/a2a/intro/
- Multi-Agents: https://google.github.io/adk-docs/agents/multi-agents/

### Code Examples
- Template base: `agents/shared/agent_template.py` (TODO: crear)
- NEXUS implementation: `agents/nexus/main.py`
- A2AServer base: `agents/shared/a2a_server.py`

---

## Next Steps

### Spike (1 sprint)
```bash
# Week 1: Validar workflow
1. Instalar ADK 1.18.0+
2. Diseñar NEXUS en Visual Builder
3. Exportar YAML
4. Traducir a código A2A
5. Testing local (endpoints A2A)
6. Decisión: Continuar o pivot a código-only
```

### Si Spike Exitoso
```
Sprint 1-2: Visual Builder discovery (NEXUS + Fitness + Nutrition)
Sprint 3-4: Traducción NEXUS
Sprint 5-6: Traducción Fitness
Sprint 7-8: Deployment pipeline
Sprint 9+: Scaling (Recovery, Mental Health, Longevity)
```

### Si Spike Falla
```
1. Implementar NEXUS directamente en código
2. Usar Visual Builder solo para documentación (screenshots)
3. Re-evaluar en 6 meses (madurez del producto)
```

---

## FAQ Rápidas

**¿Visual Builder reemplaza código?**
NO. Es diseño/prototipado. Production requiere Python A2AServer.

**¿Puedo deployar YAML directo?**
NO. YAML usa endpoints ADK (`/run`), no A2A v0.3 (`/invoke`).

**¿Ediciones bidireccionales Visual ↔ Code?**
NO. Workflow es one-way: Visual → Code.

**¿Visual Builder es production-ready?**
NO (Nov 2025 = experimental). Usar para diseño, no deployment directo.

**¿Cuánto tiempo traducir YAML → A2A?**
2-12 horas (dependiendo de complejidad). Ver tabla arriba.

**¿Puedo usar MCP tools?**
SÍ, pero configuración en código (Visual Builder UI no soporta).

**¿Mixing Google Search + Custom Tools?**
NO en mismo agent. Separar en sub-agents.

---

**Última actualización:** 2025-11-19
**Próxima revisión:** Post-spike (actualizar con aprendizajes)
