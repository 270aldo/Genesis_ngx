# ADK Visual Builder → Genesis A2A Translation Guide

## Propósito

Este directorio (`adk_designs/`) contiene diseños visuales de agentes creados con **ADK Visual Builder** (`adk web`).

**IMPORTANTE**: Los YAML exportados NO se deployean directamente. Se traducen manualmente a clases `A2AServer` para mantener compatibilidad con el protocolo A2A v0.3.

---

## Workflow Híbrido

```
┌─────────────────┐
│ 1. DISEÑAR      │  Usar adk web para crear arquitectura visualmente
│ (Visual Builder)│  → http://localhost:8000/dev-ui/
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. EXPORTAR     │  Exportar diseño a YAML
│ (YAML)          │  → adk_designs/<agent_name>/root_agent.yaml
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. TRADUCIR     │  Implementar en Python como A2AServer
│ (Python Code)   │  → agents/<agent_name>/main.py
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. DEPLOYAR     │  Cloud Run con A2A endpoints (/invoke, /invoke/stream)
│ (Production)    │  → NOT using ADK's /run endpoint
└─────────────────┘
```

---

## Mapeo ADK → A2A

| ADK YAML Field | Genesis A2AServer Equivalent | Notas |
|----------------|------------------------------|-------|
| `name` | `AGENT_CARD['id']` | Use kebab-case (e.g., `fitness-coordinator`) |
| `description` | `AGENT_CARD['capabilities']` | Extract key action verbs |
| `instruction` | System prompt en `handle_method()` | Embed in business logic |
| `model` | Gemini model selector | Map: `flash`, `pro`, `lite` |
| `tools` | Custom methods + `FunctionTool` wrappers | Define as class methods |
| `sub_agents` | `A2AClient` invocations | Call other agents via A2A |
| `parameters` | `AGENT_CARD['limits']` | Map tokens, latency, cost |

---

## Ejemplo de Traducción

### ADK YAML (Visual Builder Export)

```yaml
name: fitness_coordinator
description: Generates personalized workout plans based on user goals
model: gemini-2.5-flash
instruction: |
  You are a fitness specialist. Analyze user goals and fitness level
  to create customized workout routines.

  Always consider:
  - Current fitness level
  - Available equipment
  - Time constraints
  - Injury history

tools:
  - google_search

parameters:
  max_tokens: 1000
  temperature: 0.7
```

### A2A Translation (Python Code)

```python
# agents/fitness/main.py
from agents.shared.a2a_server import A2AServer
from typing import Dict, Any

AGENT_CARD = {
    "id": "fitness-coordinator",
    "version": "0.1.0",
    "capabilities": ["workout_planning", "exercise_analysis"],
    "limits": {
        "max_input_tokens": 20000,
        "max_output_tokens": 1000,
        "max_latency_ms": 2000,
        "max_cost_per_invoke": 0.01,
    },
    "privacy": {"pii": False, "phi": False, "data_retention_days": 90},
    "auth": {"method": "oidc", "audience": "fitness-coordinator"},
}

class FitnessAgent(A2AServer):
    def __init__(self):
        super().__init__(AGENT_CARD)

    async def handle_method(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if method == "create_workout":
            # ADK instruction embedded here
            user_goal = params.get("goal")
            fitness_level = params.get("fitness_level", "beginner")

            # Call Gemini with ADK's system instruction
            plan = await self._generate_with_gemini(
                instruction="""You are a fitness specialist. Analyze user goals
                and fitness level to create customized workout routines.""",
                user_input=f"Goal: {user_goal}, Level: {fitness_level}",
                model="gemini-2.5-flash",
                temperature=0.7
            )

            return {"workout_plan": plan}

        return {"error": "unknown_method"}

agent = FitnessAgent()
app = agent.app
```

---

## Por Qué No Usar ADK Directamente

### ADK Native Approach
- ✅ Rápido para prototipos
- ✅ Integración automática con Gemini
- ❌ **Usa endpoint `/run`** (incompatible con A2A v0.3)
- ❌ **No soporta presupuestos** (`X-Budget-USD`)
- ❌ **No soporta `/negotiate`** para capacidades
- ❌ **No integra cost tracking** en Supabase

### Genesis A2A Approach
- ✅ **Protocolo A2A v0.3 completo** (`/invoke`, `/invoke/stream`, `/card`, `/negotiate`)
- ✅ **Budget enforcement** con `X-Budget-USD`
- ✅ **Cost tracking** automático en `agent_events`
- ✅ **Supabase RLS integration** vía RPCs
- ✅ **Security validation** (PHI/PII detection)
- ⚠️ Requiere traducción manual desde YAML

### Verdict
**Hybrid Approach** = Mejor de ambos mundos
- Diseñar rápido (Visual Builder)
- Deployar robusto (A2A Protocol)

---

## Directorio `adk_designs/`

```
adk_designs/
├── genesis_canvas/          # Canvas raíz para diseño
│   ├── __init__.py
│   ├── agent.py             # root_agent placeholder
│   └── root_agent.yaml      # (auto-exportado si se diseña)
│
├── fitness_agent/           # (Future) Diseño de Fitness Agent
│   ├── root_agent.yaml
│   └── design_notes.md
│
├── nutrition_agent/         # (Future)
│   └── root_agent.yaml
│
└── TRANSLATION_GUIDE.md     # Este archivo
```

---

## Comandos Útiles

### Lanzar Visual Builder

```bash
source .venv/bin/activate
adk web adk_designs --host 127.0.0.1 --port 8000
# Abrir http://localhost:8000/dev-ui/
```

### Exportar Diseño

1. Diseñar agente en UI
2. Click "Export" → Guardar YAML
3. Copiar a `adk_designs/<agent_name>/root_agent.yaml`

### Validar YAML

```bash
python -c "import yaml; yaml.safe_load(open('adk_designs/fitness_agent/root_agent.yaml'))"
```

---

## Limitaciones Conocidas

1. **ADK Visual Builder NO soporta A2A v0.3**
   - Usa sus propios endpoints (`/run`)
   - No tiene concepto de presupuestos
   - No implementa `/negotiate`

2. **Traducción es semi-manual**
   - YAML → Python no es 100% automatizable
   - Lógica de negocio debe implementarse manualmente
   - Tools requieren wrapping con FunctionTool

3. **YAML puede quedar desactualizado**
   - Si se modifica código Python, YAML no se actualiza automático
   - Solución: Usar YAML como **documentación de diseño inicial**, no source of truth
   - Source of truth = Python code in `agents/<name>/main.py`

---

## Mejores Prácticas

### ✅ HACER

1. **Diseñar primero** en Visual Builder para arquitectura
2. **Exportar YAML** como documentación
3. **Traducir a Python** usando este guide
4. **Version control** ambos (YAML + Python)
5. **Actualizar YAML** si cambia diseño significativo

### ❌ NO HACER

1. **No intentar deployar ADK YAML directamente** a Cloud Run
2. **No mezclar endpoints** (`/run` y `/invoke`)
3. **No asumir auto-sync** entre YAML y código
4. **No commitear credenciales** en YAML files

---

## Recursos

- **ADK Documentation**: https://cloud.google.com/agent-development-kit/docs
- **A2A v0.3 Protocol**: Ver `ADR/002-a2a-v03-protocol.md`
- **Genesis A2AServer**: Ver `agents/shared/a2a_server.py`
- **Gemini Models**: Ver `agents/shared/cost_calculator.py`

---

## Contacto

Para preguntas sobre el workflow híbrido:
- Revisar `CLAUDE.md` (instrucciones para Claude Code)
- Revisar `ADR/` para decisiones arquitectónicas
- Crear issue en GitHub

---

**Última actualización**: 2025-11-17
**Versión**: 1.0.0
