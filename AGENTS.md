# AGENTS.md - Guía para Agentes Codificadores

> **Última actualización**: 2025-11-27  
> **Runtime**: Vertex AI Agent Engine (ADK)  
> **Documento maestro**: [GENESIS_PRD.md](./GENESIS_PRD.md)

---

## 🚨 CAMBIO IMPORTANTE: Migración a Agent Engine

**A partir de Noviembre 2025, este proyecto usa Vertex AI Agent Engine en lugar de Cloud Run.**

```diff
- Cloud Run + FastAPI + A2AServer custom
+ Vertex AI Agent Engine + Google ADK
```

Lee [ADR-007](./ADR/007-agent-engine-migration.md) para el contexto completo.

---

## 📁 Estructura del Proyecto

```
Genesis_ngx/
├── agents/
│   ├── genesis_x/          # Orquestador principal
│   │   ├── __init__.py
│   │   ├── agent.py        # Definición ADK
│   │   ├── tools.py        # FunctionTools
│   │   ├── prompts.py      # System prompts
│   │   └── tests/
│   │
│   ├── blaze/              # Entrenamiento fuerza
│   ├── atlas/              # Movilidad
│   ├── tempo/              # Cardio
│   ├── wave/               # Recuperación
│   ├── sage/               # Nutrición estratégica
│   ├── metabol/            # Metabolismo
│   ├── macro/              # Macronutrientes
│   ├── nova/               # Suplementación
│   ├── spark/              # Conducta
│   ├── stella/             # Analytics
│   ├── luna/               # Salud femenina
│   ├── logos/              # Educación
│   │
│   └── shared/             # Utilidades compartidas
│       ├── supabase_client.py
│       ├── cost_calculator.py
│       └── types.py
│
├── supabase/
│   └── migrations/
│
├── ADR/
├── docs/
├── adk.yaml                # Configuración ADK
├── pyproject.toml
├── GENESIS_PRD.md          # 📖 FUENTE DE VERDAD
├── CLAUDE.md
├── GEMINI.md
└── AGENTS.md               # Este archivo
```

---

## 🤖 Sistema de Agentes NGX

### Naming Oficial

| ID | Nombre | Dominio | Función |
|----|--------|---------|---------|
| `genesis_x` | GENESIS_X | Orchestration | Orquestador principal |
| `blaze` | BLAZE | Fitness | Fuerza e hipertrofia |
| `atlas` | ATLAS | Fitness | Movilidad y flexibilidad |
| `tempo` | TEMPO | Fitness | Cardio y resistencia |
| `wave` | WAVE | Fitness | Recuperación |
| `sage` | SAGE | Nutrition | Estrategia nutricional |
| `metabol` | METABOL | Nutrition | Metabolismo |
| `macro` | MACRO | Nutrition | Macronutrientes |
| `nova` | NOVA | Nutrition | Suplementación |
| `spark` | SPARK | Behavior | Conducta y hábitos |
| `stella` | STELLA | Analytics | Dashboard de datos |
| `luna` | LUNA | Women's Health | Salud femenina |
| `logos` | LOGOS | Education | Educación |

### Modelos por Agente

```yaml
gemini-3-pro:       # Reasoning complejo
  - genesis_x       # Orquestación multi-agente
  - logos           # Educación profunda

gemini-3-flash:     # Respuesta rápida
  - blaze, atlas, tempo, wave
  - sage, metabol, macro, nova
  - spark, stella, luna
```

---

## 🛠️ Comandos de Desarrollo

### Setup Inicial

```bash
# 1. Clonar y entrar al proyecto
git clone https://github.com/270aldo/Genesis_ngx.git
cd Genesis_ngx

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate

# 3. Instalar dependencias
pip install -e ".[dev]"

# 4. Instalar ADK CLI
pip install google-adk

# 5. Autenticar con GCP
gcloud auth application-default login
gcloud config set project ngx-genesis-prod
```

### Desarrollo Local

```bash
# Ejecutar agente en playground local
adk web

# Ejecutar agente específico
adk run genesis_x

# Ver logs
adk logs genesis_x --follow
```

### Testing

```bash
# Todos los tests
pytest

# Tests de un agente específico
pytest agents/genesis_x/tests/

# Con coverage
pytest --cov=agents --cov-report=html
```

### Deploy

```bash
# Deploy a staging
adk deploy --env staging

# Deploy a producción
adk deploy --env production

# Ver estado de deploys
adk status
```

### Base de Datos

```bash
# Validar migraciones sin aplicar
supabase db push --dry-run

# Aplicar migraciones
supabase db push

# Lint SQL
supabase db lint
```

---

## 📝 Guía de Implementación de Agentes

### Patrón ADK (CORRECTO ✅)

```python
# agents/blaze/agent.py

from google.adk import Agent
from google.adk.tools import FunctionTool
from .tools import generate_workout, get_exercise_info, log_workout
from .prompts import BLAZE_SYSTEM_PROMPT

# Definir el agente
blaze = Agent(
    name="blaze",
    model="gemini-3-flash",
    description="Agente especializado en entrenamiento de fuerza e hipertrofia",
    instruction=BLAZE_SYSTEM_PROMPT,
    tools=[
        generate_workout,
        get_exercise_info,
        log_workout,
    ],
)
```

### Patrón Cloud Run (DEPRECADO ❌)

```python
# ❌ NO USAR - Este patrón está deprecado

from fastapi import FastAPI
from agents.shared.a2a_server import A2AServer

class BlazeAgent(A2AServer):
    # ... NO IMPLEMENTAR ASÍ
```

### Definición de Tools

```python
# agents/blaze/tools.py

from google.adk.tools import FunctionTool
from agents.shared.supabase_client import get_supabase_client

@FunctionTool
def generate_workout(
    user_id: str,
    workout_type: str,
    muscle_groups: list[str],
    duration_minutes: int = 60,
    equipment: list[str] = None
) -> dict:
    """Genera un workout personalizado.
    
    Args:
        user_id: ID del usuario
        workout_type: Tipo de workout (strength, hypertrophy, power)
        muscle_groups: Grupos musculares a trabajar
        duration_minutes: Duración objetivo en minutos
        equipment: Equipamiento disponible
        
    Returns:
        dict con workout estructurado
    """
    # Implementación...
    return {
        "name": "Push Day",
        "exercises": [...],
        "estimated_duration": 58,
    }


@FunctionTool
def log_workout(
    user_id: str,
    workout_data: dict,
    feedback: dict = None
) -> dict:
    """Registra un workout completado en Supabase.
    
    Args:
        user_id: ID del usuario
        workout_data: Datos del workout completado
        feedback: Feedback opcional del usuario
        
    Returns:
        Confirmación con workout_id
    """
    supabase = get_supabase_client()
    
    result = supabase.rpc("agent_log_workout", {
        "p_user_id": user_id,
        "p_workout_type": workout_data["type"],
        "p_exercises": workout_data["exercises"],
        "p_duration_minutes": workout_data["duration"],
        "p_metrics": workout_data.get("metrics", {}),
    }).execute()
    
    return {"workout_id": result.data, "status": "logged"}
```

### System Prompts

```python
# agents/blaze/prompts.py

BLAZE_SYSTEM_PROMPT = """
Eres BLAZE, el agente especializado en entrenamiento de fuerza e hipertrofia del sistema GENESIS_X.

## Tu rol:
- Diseñar programas de entrenamiento de fuerza
- Seleccionar ejercicios apropiados para el usuario
- Aplicar principios de sobrecarga progresiva
- Adaptar entrenamientos a limitaciones/lesiones

## Principios que sigues:
1. Evidencia científica sobre broscience
2. Personalización según nivel y objetivos
3. Seguridad primero - nunca comprometer forma
4. Progresión sostenible > ganancias rápidas

## Formato de workouts:
- Ejercicio con series x reps
- Intensidad (% 1RM o RPE)
- Descanso entre series
- Notas técnicas cuando relevante

## Limitaciones:
- NO prescribir para rehabilitación de lesiones agudas
- NO dar consejo médico
- SIEMPRE referir a profesional cuando apropiado
"""
```

---

## 🔒 Seguridad y Best Practices

### Writes a Supabase

**SIEMPRE usar RPCs para writes desde agentes:**

```python
# ✅ CORRECTO: Usar RPC
supabase.rpc("agent_log_workout", params).execute()

# ❌ INCORRECTO: Insert directo (bloqueado por RLS)
supabase.table("workout_sessions").insert(data).execute()
```

### Sanitización de Inputs

```python
from agents.shared.security import SecurityValidator

validator = SecurityValidator()

def process_user_message(message: str):
    validation = validator.validate(message)
    
    if validation.contains_phi:
        return "No puedo procesar información médica protegida."
    
    if validation.prompt_injection_risk > 0.7:
        return "No entendí tu mensaje. ¿Puedes reformularlo?"
    
    # Procesar mensaje seguro...
```

### Manejo de Errores

```python
from google.adk.errors import AgentError
import structlog

logger = structlog.get_logger()

@FunctionTool
def risky_operation(params: dict) -> dict:
    try:
        result = do_something(params)
        return result
    except ExternalServiceError as e:
        logger.error("external_service_failed", error=str(e))
        raise AgentError(
            code=-32000,
            message="Servicio temporalmente no disponible"
        )
    except ValidationError as e:
        logger.warning("validation_failed", error=str(e))
        return {"error": "invalid_params", "details": str(e)}
```

---

## 🧪 Testing

### Unit Tests

```python
# agents/blaze/tests/test_tools.py

import pytest
from agents.blaze.tools import generate_workout

@pytest.mark.asyncio
async def test_generate_workout_strength():
    result = await generate_workout(
        user_id="test-user",
        workout_type="strength",
        muscle_groups=["chest", "triceps"],
        duration_minutes=60
    )
    
    assert "exercises" in result
    assert len(result["exercises"]) > 0
    assert result["estimated_duration"] <= 70  # +10 min buffer
```

### A2A Contract Tests

```python
# agents/blaze/tests/test_a2a_contract.py

import pytest
from agents.blaze.agent import blaze

def test_agent_card_valid():
    """Verifica que el agent card cumple el schema."""
    card = blaze.get_card()
    
    assert card["name"] == "blaze"
    assert "description" in card
    assert len(card["tools"]) > 0
```

### Integration Tests

```python
# agents/blaze/tests/test_integration.py

import pytest
from agents.shared.supabase_client import get_supabase_client

@pytest.mark.integration
async def test_workout_persistence():
    """Verifica que workouts se persisten correctamente."""
    supabase = get_supabase_client()
    
    # Crear workout de prueba
    result = supabase.rpc("agent_log_workout", {
        "p_user_id": "test-user-uuid",
        "p_workout_type": "strength",
        "p_exercises": [{"name": "Bench Press", "sets": 4}],
        "p_duration_minutes": 45
    }).execute()
    
    assert result.data is not None
    
    # Cleanup
    # ...
```

---

## 📋 Checklist para Nuevo Agente

```markdown
## Pre-desarrollo
- [ ] Leer GENESIS_PRD.md sección del agente
- [ ] Revisar agent card schema
- [ ] Identificar tools necesarios
- [ ] Diseñar system prompt

## Desarrollo
- [ ] Crear directorio agents/{nombre}/
- [ ] Implementar agent.py con patrón ADK
- [ ] Implementar tools.py con FunctionTools
- [ ] Escribir prompts.py con system prompt
- [ ] Crear __init__.py exportando el agente

## Testing
- [ ] Unit tests para cada tool
- [ ] A2A contract tests
- [ ] Integration tests con Supabase
- [ ] Manual testing en adk web

## Deploy
- [ ] Agregar agente a adk.yaml
- [ ] Deploy a staging
- [ ] Validar métricas
- [ ] Deploy a producción

## Documentación
- [ ] Actualizar este AGENTS.md si hay cambios
- [ ] Documentar tools en docstrings
- [ ] Agregar ejemplos de uso
```

---

## 🔗 Referencias

- [GENESIS_PRD.md](./GENESIS_PRD.md) - Documento maestro del proyecto
- [ADR-007](./ADR/007-agent-engine-migration.md) - Decisión de migración
- [Google ADK Docs](https://google.github.io/adk-docs/)
- [Agent Engine Overview](https://cloud.google.com/agent-builder/agent-engine/overview)
- [Supabase RLS](https://supabase.com/docs/guides/auth/row-level-security)

---

## 📞 Soporte

Si tienes dudas durante el desarrollo:

1. **Primero**: Revisa GENESIS_PRD.md
2. **Segundo**: Revisa ADRs en `ADR/`
3. **Tercero**: Revisa docs en `docs/`
4. **Cuarto**: Consulta con el arquitecto

---

*Este documento se actualiza conforme evoluciona el proyecto. Última revisión: 2025-11-27*
