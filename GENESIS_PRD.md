# GENESIS_X - Product Requirements Document (PRD)

> **Versión**: 1.0.0  
> **Fecha**: 2025-11-27  
> **Estado**: ACTIVO - Fuente de verdad para desarrollo  
> **Autor**: Arquitectura NGX + Claude Opus 4.5

---

## 📋 TABLA DE CONTENIDOS

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Visión del Producto](#2-visión-del-producto)
3. [Arquitectura del Sistema](#3-arquitectura-del-sistema)
4. [Sistema de Agentes NGX](#4-sistema-de-agentes-ngx)
5. [Stack Tecnológico](#5-stack-tecnológico)
6. [Guía de Migración a Agent Engine](#6-guía-de-migración-a-agent-engine)
7. [Schema de Base de Datos](#7-schema-de-base-de-datos)
8. [NGX ENGINE - Motor de Personalización](#8-ngx-engine---motor-de-personalización)
9. [APIs y Contratos](#9-apis-y-contratos)
10. [Seguridad y Compliance](#10-seguridad-y-compliance)
11. [Guía para Agentes Codificadores](#11-guía-para-agentes-codificadores)
12. [Plan de Implementación](#12-plan-de-implementación)
13. [Criterios de Aceptación](#13-criterios-de-aceptación)

---

## 1. RESUMEN EJECUTIVO

### 1.1 ¿Qué es GENESIS_X?

**GENESIS_X** es una plataforma de Performance & Longevity que combina inteligencia artificial con coaching humano opcional para optimizar el rendimiento físico y la salud a largo plazo de profesionales de 30-60 años.

### 1.2 Propuesta de Valor Única

```
"Rinde hoy. Vive mejor mañana."
```

- **Performance**: Optimización del rendimiento físico, fuerza, composición corporal
- **Longevity**: Prevención, salud metabólica, envejecimiento saludable
- **HIE (Hybrid Intelligence Engine)**: IA + Coach humano trabajando en sinergia

### 1.3 Productos

| Producto | Descripción | Target |
|----------|-------------|--------|
| **GENESIS** | App móvil para usuarios finales | Usuarios 30-60 años |
| **NGX COACH** | Consola web para coaches | Coaches certificados |

### 1.4 Planes de Suscripción

| Plan | Precio | Características |
|------|--------|-----------------|
| **ASCEND** | $99/mes | IA completa, 12 agentes, sin coach humano |
| **HYBRID** | $499/mes | Todo ASCEND + coach humano dedicado |

---

## 2. VISIÓN DEL PRODUCTO

### 2.1 Target Demográfico

**Rango de edad**: 30-60 años  
**Perfil**: Profesionales con recursos económicos, conscientes de su salud, buscan optimización sin ser atletas de élite.

### 2.2 ICP Clusters (sin arquetipos)

```yaml
clusters:
  recomposition_35_50:
    descripcion: "Profesionales buscando recomposición corporal"
    pain_points: ["Falta de tiempo", "Metabolismo más lento", "Lesiones previas"]
    
  longevity_40_60_joint_issues:
    descripcion: "Adultos con problemas articulares buscando longevidad"
    pain_points: ["Dolor de rodillas/espalda", "Miedo a lesionarse", "Pérdida de movilidad"]
    
  metabolic_reset_30_60:
    descripcion: "Personas con resistencia a insulina o prediabetes"
    pain_points: ["Energía inconsistente", "Grasa visceral", "Marcadores alterados"]
    
  womens_health_35_60:
    descripcion: "Mujeres en perimenopausia/menopausia"
    pain_points: ["Cambios hormonales", "Pérdida ósea", "Composición corporal"]
```

### 2.3 Principios de Diseño

1. **Educación como feature central**: El usuario entiende el "por qué" detrás de cada recomendación
2. **Criterio sobre dependencia**: Formamos usuarios autónomos, no dependientes
3. **Personalización explícita**: Sin arquetipos ocultos, el usuario ve y controla su configuración
4. **Temporada primero**: La experiencia gira alrededor del ciclo actual del usuario

---

## 3. ARQUITECTURA DEL SISTEMA

### 3.1 Diagrama de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENTES                                       │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │   GENESIS    │    │  NGX COACH   │    │   Wearables  │              │
│  │  (Expo 54)   │    │ (Next.js 15) │    │   (OAuth)    │              │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘              │
└─────────┼───────────────────┼───────────────────┼───────────────────────┘
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    VERTEX AI AGENT ENGINE                                │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      GENESIS_X (Orchestrator)                    │   │
│  │  • Intent Classification    • Multi-agent Routing               │   │
│  │  • Consensus Building       • Session Management                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                  │                                      │
│         ┌────────────────────────┼────────────────────────┐            │
│         ▼                        ▼                        ▼            │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐      │
│  │   FÍSICO    │         │  NUTRICIÓN  │         │   OTROS     │      │
│  ├─────────────┤         ├─────────────┤         ├─────────────┤      │
│  │ BLAZE      │         │ SAGE        │         │ SPARK       │      │
│  │ ATLAS      │         │ METABOL     │         │ STELLA      │      │
│  │ TEMPO      │         │ MACRO       │         │ LUNA        │      │
│  │ WAVE       │         │ NOVA        │         │ LOGOS       │      │
│  └─────────────┘         └─────────────┘         └─────────────┘      │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  MANAGED SERVICES (Agent Engine)                                 │   │
│  │  • Sessions (short-term memory)   • Memory Bank (long-term)     │   │
│  │  • Tracing & Observability        • Evaluation Service          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           SUPABASE                                       │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │  PostgreSQL  │    │  Auth        │    │  Storage     │              │
│  │  + pgvector  │    │  (JWT/OIDC)  │    │  (Media)     │              │
│  └──────────────┘    └──────────────┘    └──────────────┘              │
│                                                                         │
│  Tablas: profiles, health_metrics, workout_history, seasons,           │
│          nutrition_logs, agent_events, user_preferences                 │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Decisiones Arquitectónicas Clave

| Decisión | Elección | Razón |
|----------|----------|-------|
| Runtime de Agentes | **Agent Engine** | Managed sessions, memory, tracing, A2A nativo |
| Base de Datos | **Supabase** | RLS, Auth integrado, pgvector, RPCs |
| Modelos IA | **Gemini 3 Pro / Flash** | Mejor reasoning, costo-efectivo |
| Frontend Mobile | **Expo SDK 54** | Cross-platform, OTA updates |
| Frontend Coach | **Next.js 15** | Server components, edge runtime |
| Protocolo A2A | **JSON-RPC 2.0 + SSE** | Estándar Google, interoperabilidad |

---

## 4. SISTEMA DE AGENTES NGX

### 4.1 GENESIS_X - Orquestador Principal

```yaml
agent_id: "genesis-x"
display_name: "GENESIS_X"
role: "orchestrator"
model: "gemini-3-pro"
thinking_level: "high"

capabilities:
  - intent_classification
  - multi_agent_routing
  - consensus_building
  - session_management
  - handoff_to_human
  - planning

personality:
  tone: "Profesional pero cercano"
  style: "Directo, basado en evidencia"
  language: "Español (México), adaptable"

limits:
  max_input_tokens: 50000
  max_output_tokens: 4000
  max_latency_ms: 6000
  max_cost_per_invoke: 0.05
```

### 4.2 Agentes de Dominio Físico

#### BLAZE - Entrenamiento de Fuerza
```yaml
agent_id: "blaze"
display_name: "BLAZE"
domain: "fitness"
specialty: "strength_hypertrophy"
model: "gemini-3-flash"
thinking_level: "low"

capabilities:
  - workout_generation
  - exercise_selection
  - progressive_overload
  - periodization
  - form_guidance

tools:
  - exercise_database
  - rep_calculator
  - volume_tracker

limits:
  max_latency_ms: 2000
  max_cost_per_invoke: 0.01
```

#### ATLAS - Movilidad y Flexibilidad
```yaml
agent_id: "atlas"
display_name: "ATLAS"
domain: "fitness"
specialty: "mobility_flexibility"
model: "gemini-3-flash"

capabilities:
  - mobility_assessment
  - stretch_routines
  - joint_health
  - posture_correction
  - warm_up_cool_down
```

#### TEMPO - Cardio y Resistencia
```yaml
agent_id: "tempo"
display_name: "TEMPO"
domain: "fitness"
specialty: "cardio_endurance"
model: "gemini-3-flash"

capabilities:
  - cardio_programming
  - zone_training
  - hiit_design
  - liss_planning
  - heart_rate_zones
```

#### WAVE - Recuperación
```yaml
agent_id: "wave"
display_name: "WAVE"
domain: "fitness"
specialty: "recovery"
model: "gemini-3-flash"

capabilities:
  - recovery_protocols
  - sleep_optimization
  - deload_planning
  - stress_management
  - hrv_interpretation
```

### 4.3 Agentes de Dominio Nutrición

#### SAGE - Estrategia Nutricional
```yaml
agent_id: "sage"
display_name: "SAGE"
domain: "nutrition"
specialty: "strategy"
model: "gemini-3-flash"

capabilities:
  - nutrition_planning
  - diet_periodization
  - goal_alignment
  - preference_integration
  - restriction_handling
```

#### METABOL - Metabolismo
```yaml
agent_id: "metabol"
display_name: "METABOL"
domain: "nutrition"
specialty: "metabolism"
model: "gemini-3-flash"

capabilities:
  - metabolic_assessment
  - tdee_calculation
  - insulin_sensitivity
  - nutrient_timing
  - metabolic_adaptation
```

#### MACRO - Macronutrientes
```yaml
agent_id: "macro"
display_name: "MACRO"
domain: "nutrition"
specialty: "macros"
model: "gemini-3-flash"

capabilities:
  - macro_calculation
  - meal_composition
  - protein_distribution
  - carb_cycling
  - fat_intake_optimization
```

#### NOVA - Suplementación
```yaml
agent_id: "nova"
display_name: "NOVA"
domain: "nutrition"
specialty: "supplementation"
model: "gemini-3-flash"

capabilities:
  - supplement_recommendations
  - stack_design
  - timing_protocols
  - interaction_checking
  - evidence_grading

constraints:
  - "NO prescribir medicamentos"
  - "Solo suplementos de venta libre"
  - "Siempre mencionar consultar médico"
```

### 4.4 Agentes Transversales

#### SPARK - Conducta y Hábitos
```yaml
agent_id: "spark"
display_name: "SPARK"
domain: "behavior"
specialty: "habits_motivation"
model: "gemini-3-flash"

capabilities:
  - habit_formation
  - motivation_strategies
  - barrier_identification
  - accountability_systems
  - behavior_change_techniques
```

#### STELLA - Dashboard de Datos
```yaml
agent_id: "stella"
display_name: "STELLA"
domain: "analytics"
specialty: "data_visualization"
model: "gemini-3-flash"

capabilities:
  - progress_tracking
  - trend_analysis
  - goal_monitoring
  - biomarker_interpretation
  - report_generation

data_sources:
  - health_metrics
  - workout_history
  - nutrition_logs
  - wearable_data
  - check_ins
```

#### LUNA - Salud Femenina
```yaml
agent_id: "luna"
display_name: "LUNA"
domain: "womens_health"
specialty: "female_physiology"
model: "gemini-3-flash"

capabilities:
  - cycle_tracking
  - hormonal_considerations
  - perimenopause_support
  - menopause_adaptation
  - training_cycle_sync

constraints:
  - "NO es consejo médico"
  - "Referir a ginecólogo cuando apropiado"
```

#### LOGOS - Educación
```yaml
agent_id: "logos"
display_name: "LOGOS"
domain: "education"
specialty: "learning"
model: "gemini-3-pro"
thinking_level: "high"

capabilities:
  - concept_explanation
  - evidence_presentation
  - myth_debunking
  - deep_dives
  - quiz_generation
  - content_curation

personality:
  style: "Socrático - hace preguntas para guiar"
  depth: "Ajusta según nivel del usuario"
```

### 4.5 Matriz de Comunicación A2A

```
                    GENESIS_X
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
    ┌───────┐       ┌───────┐       ┌───────┐
    │ BLAZE │◄─────►│ SAGE  │◄─────►│ SPARK │
    │ ATLAS │       │METABOL│       │STELLA │
    │ TEMPO │       │ MACRO │       │ LUNA  │
    │ WAVE  │       │ NOVA  │       │ LOGOS │
    └───────┘       └───────┘       └───────┘
        │               │               │
        └───────────────┴───────────────┘
              Comunicación Cross-Domain
              
Ejemplo: BLAZE pide a SAGE macros post-workout
         STELLA recibe datos de todos para dashboard
         LOGOS puede explicar conceptos de cualquier dominio
```

---

## 5. STACK TECNOLÓGICO

### 5.1 Backend / Agentes

```yaml
runtime:
  platform: "Vertex AI Agent Engine"
  region: "us-central1"
  framework: "ADK (Agent Development Kit)"
  
models:
  orchestrator: "gemini-3-pro"
  specialized: "gemini-3-flash"
  lightweight: "gemini-3-flash-lite"
  
infrastructure:
  deploy: "adk deploy"
  scaling: "Managed (Agent Engine)"
  observability: "Built-in tracing"
```

### 5.2 Base de Datos

```yaml
primary:
  provider: "Supabase"
  database: "PostgreSQL 16"
  extensions:
    - pgvector  # Embeddings 768-dim
    - pgcrypto  # UUID generation
    
security:
  rls: true  # Row Level Security obligatorio
  auth: "Supabase Auth (JWT)"
  
patterns:
  writes: "Via RPCs (SECURITY DEFINER)"
  reads: "Direct con RLS policies"
```

### 5.3 Frontend

```yaml
mobile_app:
  name: "GENESIS"
  framework: "Expo SDK 54"
  react_native: "0.81"
  state: "Zustand + React Query"
  design_system: "Liquid Glass"
  
coach_console:
  name: "NGX COACH"
  framework: "Next.js 15"
  runtime: "Edge"
  auth: "NextAuth + Supabase"
```

### 5.4 Design System - Liquid Glass

```yaml
colors:
  background:
    primary: "#0A0A0A"      # Negro ónix
    secondary: "#141414"    # Gris oscuro
    
  accent:
    primary: "#6D00FF"      # Violeta NGX
    secondary: "#00D9FF"    # Aqua/Cyan
    
  text:
    primary: "#FFFFFF"
    secondary: "#A0A0A0"
    
  semantic:
    success: "#00FF88"
    warning: "#FFB800"
    error: "#FF3366"
    
effects:
  glassmorphism:
    blur: "20px"
    opacity: 0.1
    border: "1px solid rgba(255,255,255,0.1)"
    
typography:
  primary: "SF Pro Display"
  secondary: "SF Pro Text"
  mono: "SF Mono"
```

---

## 6. GUÍA DE MIGRACIÓN A AGENT ENGINE

### 6.1 Estado Actual vs Objetivo

```
ANTES (Cloud Run + A2A Manual)          DESPUÉS (Agent Engine)
─────────────────────────────          ────────────────────────
agents/nexus/main.py         ──────►   agents/genesis_x/agent.py
agents/fitness/main.py       ──────►   agents/blaze/agent.py
agents/nutrition/main.py     ──────►   agents/sage/agent.py
agents/shared/a2a_server.py  ──────►   (No necesario - ADK built-in)
agents/shared/a2a_client.py  ──────►   (No necesario - ADK built-in)
Custom session management    ──────►   Agent Engine Sessions
Custom logging               ──────►   Built-in Tracing
docker-compose.yml           ──────►   adk deploy
```

### 6.2 Proceso de Migración Paso a Paso

#### PASO 1: Preparación del Entorno

```bash
# 1.1 Instalar ADK CLI
pip install google-adk

# 1.2 Instalar SDK con extras necesarios
pip install google-cloud-aiplatform[adk,agent_engines]>=1.112

# 1.3 Autenticar con GCP
gcloud auth application-default login

# 1.4 Configurar proyecto
gcloud config set project ngx-genesis-prod
export GOOGLE_CLOUD_PROJECT=ngx-genesis-prod
export GOOGLE_CLOUD_LOCATION=us-central1
```

#### PASO 2: Estructura de Proyecto ADK

```
Genesis_ngx/
├── agents/
│   ├── genesis_x/           # Orquestador (antes nexus)
│   │   ├── __init__.py
│   │   ├── agent.py         # Definición del agente ADK
│   │   ├── tools.py         # Tools del agente
│   │   ├── prompts.py       # System prompts
│   │   └── tests/
│   │
│   ├── blaze/               # Fuerza (antes fitness)
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── tools.py
│   │   └── tests/
│   │
│   ├── sage/                # Nutrición estratégica
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── tools.py
│   │   └── tests/
│   │
│   └── shared/              # Utilidades compartidas
│       ├── __init__.py
│       ├── supabase_client.py  # Mantener - conexión a datos
│       ├── cost_calculator.py  # Mantener - tracking costos
│       └── types.py            # Tipos compartidos
│
├── pyproject.toml           # Dependencias unificadas
└── adk.yaml                 # Configuración ADK
```

#### PASO 3: Convertir Agente (Ejemplo GENESIS_X)

**ANTES** (`agents/nexus/main.py`):
```python
# Código actual basado en FastAPI + A2A manual
from agents.shared.a2a_server import A2AServer

class NexusAgent(A2AServer):
    def __init__(self):
        super().__init__(AGENT_CARD)
        self.gemini = get_gemini_client()
        
    async def handle_method(self, method: str, params: dict):
        if method == "orchestrate":
            return await self._orchestrate(params)
```

**DESPUÉS** (`agents/genesis_x/agent.py`):
```python
"""GENESIS_X - Orquestador principal del sistema NGX."""

from google.adk import Agent, Tool
from google.adk.tools import FunctionTool
from typing import Any

from agents.shared.supabase_client import get_supabase_client
from .tools import (
    classify_intent,
    route_to_agent,
    build_consensus,
    get_user_context,
)
from .prompts import GENESIS_X_SYSTEM_PROMPT


# Definir tools como funciones
@FunctionTool
def classify_user_intent(message: str, context: dict) -> dict:
    """Clasifica el intent del usuario para routing.
    
    Args:
        message: Mensaje del usuario
        context: Contexto de la conversación
        
    Returns:
        dict con intent, confidence, y suggested_agents
    """
    # Implementación...
    pass


@FunctionTool  
def invoke_specialist(
    agent_id: str,
    method: str,
    params: dict,
    budget_usd: float = 0.01
) -> dict:
    """Invoca un agente especializado via A2A.
    
    Args:
        agent_id: ID del agente (blaze, sage, etc.)
        method: Método a invocar
        params: Parámetros del método
        budget_usd: Presupuesto máximo
        
    Returns:
        Respuesta del agente especializado
    """
    # Agent Engine maneja A2A nativamente
    pass


@FunctionTool
def persist_to_supabase(
    user_id: str,
    event_type: str,
    payload: dict
) -> dict:
    """Persiste eventos importantes a Supabase.
    
    Args:
        user_id: ID del usuario
        event_type: Tipo de evento
        payload: Datos del evento
        
    Returns:
        Confirmación de persistencia
    """
    supabase = get_supabase_client()
    return supabase.log_event(user_id, event_type, payload)


# Definir el agente
genesis_x = Agent(
    name="genesis_x",
    model="gemini-3-pro",
    description="Orquestador principal de GENESIS NGX. Coordina agentes especializados para optimización de performance y longevidad.",
    instruction=GENESIS_X_SYSTEM_PROMPT,
    tools=[
        classify_user_intent,
        invoke_specialist,
        persist_to_supabase,
    ],
)
```

#### PASO 4: Configurar ADK

**`adk.yaml`**:
```yaml
# Configuración global de ADK para GENESIS NGX
version: "1.0"

project:
  name: "genesis-ngx"
  description: "Sistema multi-agente de Performance & Longevity"
  
defaults:
  region: "us-central1"
  model: "gemini-3-flash"
  
agents:
  genesis_x:
    path: "agents/genesis_x"
    model: "gemini-3-pro"
    entry_point: "agent:genesis_x"
    
  blaze:
    path: "agents/blaze"
    model: "gemini-3-flash"
    entry_point: "agent:blaze"
    
  sage:
    path: "agents/sage"
    model: "gemini-3-flash"
    entry_point: "agent:sage"
    
  # ... más agentes

deployment:
  staging:
    project_id: "ngx-genesis-staging"
    
  production:
    project_id: "ngx-genesis-prod"
```

#### PASO 5: Deploy

```bash
# Deploy a staging
adk deploy --env staging

# Probar en playground
adk web  # Abre playground local

# Deploy a producción
adk deploy --env production

# Ver logs
adk logs genesis_x --follow
```

### 6.3 Checklist de Migración

```markdown
## Pre-Migración
- [ ] Backup completo del código actual
- [ ] Documentar estado actual de cada agente
- [ ] Verificar acceso a GCP y Vertex AI APIs
- [ ] Crear proyecto staging en GCP

## Fase 1: GENESIS_X (Orquestador)
- [ ] Crear estructura `agents/genesis_x/`
- [ ] Migrar lógica de `nexus/main.py` a formato ADK
- [ ] Convertir AGENT_CARD a configuración ADK
- [ ] Migrar tools (classify_intent, orchestrate)
- [ ] Configurar conexión Supabase (mantener cliente existente)
- [ ] Tests unitarios
- [ ] Deploy a staging
- [ ] Validar comunicación con Supabase
- [ ] Tests de integración

## Fase 2: Agentes Especializados
- [ ] BLAZE (fitness → blaze)
- [ ] SAGE (nutrition → sage)
- [ ] Validar A2A entre GENESIS_X y especializados
- [ ] Tests cross-agent

## Fase 3: Nuevos Agentes
- [ ] ATLAS (movilidad)
- [ ] TEMPO (cardio)
- [ ] WAVE (recuperación)
- [ ] METABOL (metabolismo)
- [ ] MACRO (macros)
- [ ] NOVA (suplementos)
- [ ] SPARK (conducta)
- [ ] STELLA (datos)
- [ ] LUNA (salud femenina)
- [ ] LOGOS (educación)

## Post-Migración
- [ ] Deprecar código Cloud Run
- [ ] Actualizar documentación
- [ ] Actualizar CI/CD
- [ ] Monitoring en producción
- [ ] Eliminar infraestructura legacy
```

### 6.4 Manejo de Estado y Memoria

**Agent Engine proporciona:**

```python
# Sessions (memoria corto plazo - dentro de conversación)
# Manejado automáticamente por Agent Engine

# Memory Bank (memoria largo plazo - entre conversaciones)
from google.adk.memory import MemoryBank

memory = MemoryBank(user_id=user_id)

# Guardar fact importante
memory.store(
    key="training_preference",
    value="Prefiere entrenar por las mañanas",
    metadata={"source": "onboarding", "confidence": 0.9}
)

# Recuperar facts
preferences = memory.retrieve(
    query="preferencias de entrenamiento",
    limit=5
)
```

**Supabase sigue siendo usado para:**
- Datos estructurados (profiles, health_metrics, workouts)
- Historial de entrenamientos
- Logs de nutrición
- Métricas y progreso
- Datos de temporadas/fases (NGX ENGINE)

### 6.5 Rollback Plan

```bash
# Si algo falla, mantener Cloud Run como fallback

# 1. Los servicios Cloud Run siguen existiendo
# 2. DNS/Load Balancer puede switchear tráfico
# 3. Feature flag para elegir runtime:

AGENT_RUNTIME=cloud_run   # Legacy
AGENT_RUNTIME=agent_engine # Nuevo (default)
```

---

## 7. SCHEMA DE BASE DE DATOS

### 7.1 Tablas Core (Existentes)

```sql
-- Ya implementadas en 001_initial_schema.sql
-- Mantener sin cambios durante migración

profiles
conversations  
messages
agent_events
health_metrics
user_context_embeddings
```

### 7.2 Tablas Nuevas Requeridas

```sql
-- =====================================================
-- MIGRACIÓN 002: NGX ENGINE + Extensiones
-- =====================================================

-- Preferencias y configuración del usuario
CREATE TABLE IF NOT EXISTS public.user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Campos del Technical Implementation Guide V2.0
    primary_goal TEXT NOT NULL DEFAULT 'general_fitness',
    -- Valores: 'strength', 'hypertrophy', 'fat_loss', 'longevity', 'athletic_performance'
    
    training_experience TEXT NOT NULL DEFAULT 'intermediate',
    -- Valores: 'beginner', 'intermediate', 'advanced', 'elite'
    
    longevity_risk_profile JSONB DEFAULT '{}'::jsonb,
    -- Estructura: {metabolic_risk: low|medium|high, joint_issues: [...], etc}
    
    -- Preferencias de entrenamiento
    preferred_training_days INTEGER[] DEFAULT ARRAY[1,3,5], -- Lunes, Miércoles, Viernes
    preferred_training_time TEXT DEFAULT 'morning',
    session_duration_minutes INTEGER DEFAULT 60,
    equipment_available TEXT[] DEFAULT ARRAY['gym_full'],
    
    -- Preferencias de nutrición
    dietary_restrictions TEXT[] DEFAULT ARRAY[]::TEXT[],
    meal_frequency INTEGER DEFAULT 4,
    
    -- Preferencias de comunicación
    notification_preferences JSONB DEFAULT '{"daily_checkin": true, "workout_reminder": true}'::jsonb,
    language TEXT DEFAULT 'es-MX',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id)
);

-- Temporadas (ciclos de entrenamiento)
CREATE TABLE IF NOT EXISTS public.seasons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    name TEXT NOT NULL,
    description TEXT,
    
    -- Tipo de temporada
    season_type TEXT NOT NULL,
    -- Valores: 'hypertrophy', 'strength', 'cut', 'maintenance', 'deload', 'transition'
    
    -- Fechas
    start_date DATE NOT NULL,
    end_date DATE,
    planned_duration_weeks INTEGER NOT NULL DEFAULT 12,
    
    -- Estado
    status TEXT NOT NULL DEFAULT 'planned',
    -- Valores: 'planned', 'active', 'completed', 'paused', 'cancelled'
    
    -- Configuración
    config JSONB DEFAULT '{}'::jsonb,
    -- Estructura específica por season_type
    
    -- Métricas objetivo
    goals JSONB DEFAULT '{}'::jsonb,
    -- Ejemplo: {target_weight: 85, target_body_fat: 15, target_strength: {...}}
    
    -- Métricas alcanzadas
    results JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_seasons_user_status ON public.seasons(user_id, status);
CREATE INDEX idx_seasons_active ON public.seasons(user_id) WHERE status = 'active';

-- Fases dentro de una temporada
CREATE TABLE IF NOT EXISTS public.phases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    season_id UUID NOT NULL REFERENCES public.seasons(id) ON DELETE CASCADE,
    
    name TEXT NOT NULL,
    phase_number INTEGER NOT NULL,
    
    -- Tipo de fase
    phase_type TEXT NOT NULL,
    -- Valores: 'accumulation', 'intensification', 'realization', 'deload', 'transition'
    
    -- Duración
    duration_weeks INTEGER NOT NULL DEFAULT 4,
    start_week INTEGER NOT NULL,
    
    -- Configuración de entrenamiento
    training_config JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Estructura: {volume: high|medium|low, intensity: %, frequency: days/week, etc}
    
    -- Configuración de nutrición
    nutrition_config JSONB DEFAULT '{}'::jsonb,
    -- Estructura: {calories: X, protein_g_per_kg: Y, carb_cycling: true/false, etc}
    
    status TEXT NOT NULL DEFAULT 'pending',
    -- Valores: 'pending', 'active', 'completed'
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_phases_season ON public.phases(season_id, phase_number);

-- Semanas programadas
CREATE TABLE IF NOT EXISTS public.weeks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phase_id UUID NOT NULL REFERENCES public.phases(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    week_number INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    
    -- Configuración específica de la semana
    config JSONB DEFAULT '{}'::jsonb,
    
    -- Métricas de la semana
    metrics JSONB DEFAULT '{}'::jsonb,
    -- Estructura: {completed_workouts: X, total_volume: Y, avg_rpe: Z, etc}
    
    -- Check-ins de la semana
    checkins JSONB DEFAULT '[]'::jsonb,
    
    status TEXT NOT NULL DEFAULT 'planned',
    -- Valores: 'planned', 'active', 'completed'
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_weeks_phase ON public.weeks(phase_id, week_number);
CREATE INDEX idx_weeks_user_date ON public.weeks(user_id, start_date);

-- Historial de entrenamientos
CREATE TABLE IF NOT EXISTS public.workout_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    week_id UUID REFERENCES public.weeks(id),
    
    -- Metadata
    scheduled_date DATE,
    completed_at TIMESTAMPTZ,
    
    -- Tipo de sesión
    workout_type TEXT NOT NULL,
    -- Valores: 'strength', 'hypertrophy', 'cardio', 'mobility', 'mixed'
    
    -- Duración
    planned_duration_minutes INTEGER,
    actual_duration_minutes INTEGER,
    
    -- Contenido del workout (generado por BLAZE/TEMPO/ATLAS)
    exercises JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Estructura: [{exercise_id, sets: [{reps, weight, rpe, rest}], notes}]
    
    -- Métricas post-workout
    metrics JSONB DEFAULT '{}'::jsonb,
    -- Estructura: {total_volume: X, avg_rpe: Y, muscle_groups: [...]}
    
    -- Feedback del usuario
    user_feedback JSONB DEFAULT '{}'::jsonb,
    -- Estructura: {energy_level: 1-10, soreness: 1-10, enjoyment: 1-10, notes: ""}
    
    -- Estado
    status TEXT NOT NULL DEFAULT 'planned',
    -- Valores: 'planned', 'in_progress', 'completed', 'skipped', 'partial'
    
    -- Agente que generó el workout
    generated_by TEXT DEFAULT 'blaze',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_workouts_user_date ON public.workout_sessions(user_id, scheduled_date DESC);
CREATE INDEX idx_workouts_week ON public.workout_sessions(week_id);

-- Logs de nutrición
CREATE TABLE IF NOT EXISTS public.nutrition_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    logged_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    meal_type TEXT NOT NULL,
    -- Valores: 'breakfast', 'lunch', 'dinner', 'snack', 'pre_workout', 'post_workout'
    
    -- Contenido
    description TEXT,
    foods JSONB DEFAULT '[]'::jsonb,
    -- Estructura: [{name, quantity, unit, macros: {protein, carbs, fat, calories}}]
    
    -- Totales calculados
    total_calories INTEGER,
    total_protein_g NUMERIC(6,1),
    total_carbs_g NUMERIC(6,1),
    total_fat_g NUMERIC(6,1),
    total_fiber_g NUMERIC(6,1),
    
    -- Metadata
    photo_url TEXT,
    notes TEXT,
    
    -- Agente que procesó (si aplica)
    processed_by TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_nutrition_user_date ON public.nutrition_logs(user_id, logged_at DESC);

-- Check-ins diarios
CREATE TABLE IF NOT EXISTS public.daily_checkins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    checkin_date DATE NOT NULL,
    checked_in_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Métricas subjetivas (1-10)
    sleep_quality INTEGER CHECK (sleep_quality BETWEEN 1 AND 10),
    sleep_hours NUMERIC(3,1),
    energy_level INTEGER CHECK (energy_level BETWEEN 1 AND 10),
    stress_level INTEGER CHECK (stress_level BETWEEN 1 AND 10),
    soreness_level INTEGER CHECK (soreness_level BETWEEN 1 AND 10),
    motivation_level INTEGER CHECK (motivation_level BETWEEN 1 AND 10),
    
    -- Métricas objetivas (opcionales)
    morning_weight_kg NUMERIC(5,2),
    resting_heart_rate INTEGER,
    hrv_score INTEGER,
    
    -- Dolor o molestias
    pain_areas JSONB DEFAULT '[]'::jsonb,
    -- Estructura: [{area: "knee_left", intensity: 1-10, type: "sharp|dull|ache"}]
    
    -- Notas libres
    notes TEXT,
    
    -- Procesado por agente
    agent_analysis JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id, checkin_date)
);

CREATE INDEX idx_checkins_user_date ON public.daily_checkins(user_id, checkin_date DESC);

-- =====================================================
-- RLS POLICIES para nuevas tablas
-- =====================================================

ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.seasons ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.phases ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.weeks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workout_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nutrition_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_checkins ENABLE ROW LEVEL SECURITY;

-- Policies: Users can read/write their own data
CREATE POLICY "Users manage own preferences" ON public.user_preferences
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users manage own seasons" ON public.seasons
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users read own phases" ON public.phases
    FOR SELECT USING (
        season_id IN (SELECT id FROM public.seasons WHERE user_id = auth.uid())
    );

CREATE POLICY "Users read own weeks" ON public.weeks
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users manage own workouts" ON public.workout_sessions
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users manage own nutrition" ON public.nutrition_logs
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users manage own checkins" ON public.daily_checkins
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- =====================================================
-- RPCs para Agentes
-- =====================================================

-- RPC para que agentes creen/actualicen temporadas
CREATE OR REPLACE FUNCTION rpc.agent_create_season(
    p_user_id UUID,
    p_name TEXT,
    p_season_type TEXT,
    p_start_date DATE,
    p_duration_weeks INTEGER,
    p_config JSONB DEFAULT '{}'::jsonb,
    p_goals JSONB DEFAULT '{}'::jsonb
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, rpc, pg_temp
AS $$
DECLARE
    v_agent_role TEXT;
    v_season_id UUID;
BEGIN
    v_agent_role := rpc.get_agent_role();
    IF v_agent_role IS NULL THEN
        RAISE EXCEPTION 'Unauthorized: missing agent_role';
    END IF;
    
    INSERT INTO public.seasons (
        user_id, name, season_type, start_date, 
        planned_duration_weeks, config, goals, status
    ) VALUES (
        p_user_id, p_name, p_season_type, p_start_date,
        p_duration_weeks, p_config, p_goals, 'active'
    ) RETURNING id INTO v_season_id;
    
    -- Log event
    INSERT INTO public.agent_events (user_id, agent_type, event_type, payload)
    VALUES (p_user_id, v_agent_role, 'season_created', 
            jsonb_build_object('season_id', v_season_id));
    
    RETURN v_season_id;
END;
$$;

GRANT EXECUTE ON FUNCTION rpc.agent_create_season TO authenticated;

-- RPC para registrar workout completado
CREATE OR REPLACE FUNCTION rpc.agent_log_workout(
    p_user_id UUID,
    p_workout_type TEXT,
    p_exercises JSONB,
    p_duration_minutes INTEGER,
    p_metrics JSONB DEFAULT '{}'::jsonb,
    p_week_id UUID DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, rpc, pg_temp
AS $$
DECLARE
    v_agent_role TEXT;
    v_workout_id UUID;
BEGIN
    v_agent_role := rpc.get_agent_role();
    IF v_agent_role IS NULL THEN
        RAISE EXCEPTION 'Unauthorized';
    END IF;
    
    INSERT INTO public.workout_sessions (
        user_id, week_id, workout_type, exercises,
        actual_duration_minutes, metrics, completed_at,
        status, generated_by
    ) VALUES (
        p_user_id, p_week_id, p_workout_type, p_exercises,
        p_duration_minutes, p_metrics, NOW(),
        'completed', v_agent_role
    ) RETURNING id INTO v_workout_id;
    
    RETURN v_workout_id;
END;
$$;

GRANT EXECUTE ON FUNCTION rpc.agent_log_workout TO authenticated;
```

---

## 8. NGX ENGINE - MOTOR DE PERSONALIZACIÓN

### 8.1 Concepto

El **NGX ENGINE** es el cerebro de personalización que organiza la experiencia del usuario en ciclos estructurados:

```
TEMPORADA (Season)     12-16 semanas
    │
    ├── FASE 1         4 semanas (Acumulación)
    │   ├── Semana 1
    │   ├── Semana 2
    │   ├── Semana 3
    │   └── Semana 4
    │
    ├── FASE 2         4 semanas (Intensificación)
    │   └── ...
    │
    ├── FASE 3         3 semanas (Realización)
    │   └── ...
    │
    └── FASE 4         1 semana (Deload)
        └── ...
```

### 8.2 Tipos de Temporada

```yaml
hypertrophy:
  objetivo: "Maximizar ganancia muscular"
  duracion_tipica: 12-16 semanas
  fases:
    - accumulation: {volume: high, intensity: moderate}
    - intensification: {volume: moderate, intensity: high}
    - realization: {volume: low, intensity: very_high}
    - deload: {volume: very_low, intensity: low}
  nutrition: "Superávit calórico 10-20%"

strength:
  objetivo: "Maximizar fuerza en movimientos principales"
  duracion_tipica: 8-12 semanas
  fases:
    - accumulation: {volume: moderate, intensity: moderate}
    - intensification: {volume: low, intensity: high}
    - peaking: {volume: very_low, intensity: max}
    - deload: {volume: very_low, intensity: low}
  nutrition: "Mantenimiento o ligero superávit"

cut:
  objetivo: "Reducir grasa preservando músculo"
  duracion_tipica: 8-16 semanas
  fases:
    - aggressive: {deficit: 20-25%, cardio: moderate}
    - moderate: {deficit: 15-20%, cardio: moderate}
    - diet_break: {deficit: 0%, duration: 1-2 weeks}
  nutrition: "Déficit calórico, proteína alta"

maintenance:
  objetivo: "Mantener composición actual"
  duracion_tipica: 4-8 semanas
  fases:
    - maintenance: {volume: moderate, intensity: moderate}
  nutrition: "Calorías de mantenimiento"

longevity:
  objetivo: "Optimizar salud y funcionalidad a largo plazo"
  duracion_tipica: Ongoing
  fases:
    - foundation: {mobility: high, strength: moderate, cardio: zone2}
  nutrition: "Anti-inflamatorio, mediterráneo"
```

### 8.3 Flujo de Creación de Temporada

```python
# Ejemplo de flujo en GENESIS_X

async def create_user_season(user_id: str, goal: str, context: dict):
    """
    GENESIS_X orquesta la creación de una temporada consultando
    múltiples agentes especializados.
    """
    
    # 1. STELLA analiza datos históricos del usuario
    user_analysis = await invoke_agent("stella", "analyze_user_history", {
        "user_id": user_id,
        "metrics": ["strength_progress", "body_composition", "adherence"]
    })
    
    # 2. BLAZE propone estructura de entrenamiento
    training_plan = await invoke_agent("blaze", "design_season", {
        "goal": goal,
        "training_experience": context["training_experience"],
        "equipment": context["equipment_available"],
        "days_per_week": context["training_days"],
        "historical_data": user_analysis
    })
    
    # 3. SAGE propone estrategia nutricional
    nutrition_plan = await invoke_agent("sage", "design_nutrition_season", {
        "goal": goal,
        "current_weight": context["current_weight"],
        "target_weight": context.get("target_weight"),
        "dietary_restrictions": context["dietary_restrictions"],
        "training_plan": training_plan
    })
    
    # 4. GENESIS_X construye consenso y crea temporada
    season = build_season(
        user_id=user_id,
        training=training_plan,
        nutrition=nutrition_plan,
        duration_weeks=training_plan["recommended_duration"]
    )
    
    # 5. Persistir en Supabase
    season_id = await supabase.rpc("agent_create_season", {
        "p_user_id": user_id,
        "p_name": f"Temporada {goal.title()}",
        "p_season_type": goal,
        "p_start_date": date.today(),
        "p_duration_weeks": season["duration"],
        "p_config": season["config"],
        "p_goals": season["goals"]
    })
    
    # 6. LOGOS prepara contenido educativo
    await invoke_agent("logos", "prepare_season_education", {
        "season_type": goal,
        "user_experience": context["training_experience"]
    })
    
    return season_id
```

---

## 9. APIs Y CONTRATOS

### 9.1 Endpoints Principales (Frontend → Backend)

```yaml
# API REST para clientes (Expo, Next.js)

auth:
  POST /auth/signup
  POST /auth/login
  POST /auth/refresh
  POST /auth/logout

users:
  GET  /users/me
  PUT  /users/me
  GET  /users/me/preferences
  PUT  /users/me/preferences

seasons:
  GET  /seasons                    # Lista temporadas del usuario
  POST /seasons                    # Crear nueva temporada
  GET  /seasons/:id                # Detalle de temporada
  GET  /seasons/active             # Temporada activa actual

workouts:
  GET  /workouts/today             # Workout programado para hoy
  GET  /workouts/:id               # Detalle de workout
  POST /workouts/:id/complete      # Marcar como completado
  POST /workouts/:id/feedback      # Feedback post-workout

nutrition:
  GET  /nutrition/today            # Plan nutricional de hoy
  POST /nutrition/log              # Registrar comida
  GET  /nutrition/summary/:date    # Resumen del día

checkins:
  GET  /checkins/today             # Check-in de hoy
  POST /checkins                   # Enviar check-in
  GET  /checkins/history           # Historial de check-ins

chat:
  POST /chat/message               # Enviar mensaje a GENESIS_X
  GET  /chat/history               # Historial de conversación
  
  # El endpoint de chat conecta con Agent Engine
  # y maneja sessions automáticamente
```

### 9.2 Contrato A2A entre Agentes

```json
// Ejemplo: GENESIS_X invoca a BLAZE

// Request
{
  "jsonrpc": "2.0",
  "id": "req-uuid-123",
  "method": "generate_workout",
  "params": {
    "user_id": "user-uuid",
    "workout_type": "strength",
    "muscle_groups": ["chest", "triceps", "shoulders"],
    "duration_minutes": 60,
    "equipment": ["barbell", "dumbbells", "cables"],
    "phase_config": {
      "volume": "high",
      "intensity_range": [70, 80],
      "rep_range": [8, 12]
    }
  }
}

// Response
{
  "jsonrpc": "2.0",
  "id": "req-uuid-123",
  "result": {
    "workout": {
      "name": "Push Day - Semana 3",
      "estimated_duration": 58,
      "exercises": [
        {
          "name": "Bench Press",
          "sets": 4,
          "reps": "8-10",
          "intensity": "75% 1RM",
          "rest_seconds": 120,
          "notes": "Control excéntrico 3 segundos"
        }
        // ... más ejercicios
      ],
      "warmup": { /* ... */ },
      "cooldown": { /* ... */ }
    },
    "metrics": {
      "total_sets": 20,
      "estimated_volume": 15000,
      "primary_muscles": ["chest", "anterior_deltoid", "triceps"]
    }
  }
}
```

---

## 10. SEGURIDAD Y COMPLIANCE

### 10.1 Principios de Seguridad

```yaml
data_classification:
  public: "Información de marketing, precios"
  internal: "Configuraciones de agentes, logs"
  confidential: "Datos de usuarios, métricas de salud"
  restricted: "Credenciales, tokens, keys"

encryption:
  at_rest: "AES-256 (Supabase default)"
  in_transit: "TLS 1.3"
  
authentication:
  users: "Supabase Auth (JWT)"
  agents: "Service Account + IAM"
  inter_agent: "OIDC tokens via Agent Engine"

authorization:
  pattern: "RLS + RPCs"
  principle: "Least privilege"
```

### 10.2 Scope de Wellness (NO Medical)

```yaml
# GENESIS_X NO es un dispositivo médico

allowed:
  - Consejos de fitness y nutrición general
  - Tracking de métricas de bienestar
  - Educación basada en evidencia
  - Recomendaciones de suplementos OTC
  - Interpretación general de métricas

prohibited:
  - Diagnósticos médicos
  - Prescripción de medicamentos
  - Tratamiento de condiciones médicas
  - Almacenamiento de PHI (diagnósticos, recetas)
  - Consejos para condiciones agudas

disclaimers:
  required: "Siempre consulta a un profesional de salud"
  frequency: "En onboarding y cuando relevante"
```

### 10.3 Sanitización de Inputs

```python
# Todos los agentes deben usar esto

from agents.shared.security import SecurityValidator

validator = SecurityValidator()

# Antes de procesar cualquier input
validation = validator.validate(user_input)

if validation.contains_phi:
    return "No puedo procesar información médica protegida."
    
if validation.prompt_injection_risk > 0.7:
    log.warning("Potential prompt injection detected")
    return "No entendí tu mensaje. ¿Puedes reformularlo?"
```

---

## 11. GUÍA PARA AGENTES CODIFICADORES

### 11.1 Contexto para Claude Code / Gemini CLI / GPT Codex

```markdown
## Eres un agente codificador trabajando en GENESIS_X

### Tu contexto:
- Proyecto: Sistema multi-agente de fitness y longevidad
- Runtime: Vertex AI Agent Engine (NO Cloud Run)
- Framework: Google ADK
- Base de datos: Supabase PostgreSQL
- Frontend: Expo SDK 54 (mobile), Next.js 15 (web)

### Reglas críticas:
1. NUNCA escribir código para Cloud Run/FastAPI - usamos Agent Engine
2. SIEMPRE usar ADK patterns para definir agentes
3. SIEMPRE usar Supabase RPCs para writes desde agentes
4. NUNCA almacenar PHI (diagnósticos, prescripciones)
5. SIEMPRE incluir manejo de errores y logging

### Naming conventions:
- Agentes: snake_case (genesis_x, blaze, sage)
- Tablas: snake_case plural (workout_sessions)
- Funciones Python: snake_case
- Clases: PascalCase
- Constantes: UPPER_SNAKE_CASE

### Estructura de un agente ADK:
agents/{agent_name}/
├── __init__.py
├── agent.py      # Definición principal
├── tools.py      # FunctionTools
├── prompts.py    # System prompts
└── tests/
```

### 11.2 Prompts de Sistema por Agente

```python
# agents/genesis_x/prompts.py

GENESIS_X_SYSTEM_PROMPT = """
Eres GENESIS_X, el orquestador principal del sistema NGX de Performance & Longevity.

## Tu rol:
- Clasificar intents de usuarios
- Coordinar agentes especializados
- Construir respuestas coherentes
- Manejar handoffs a coaches humanos (plan HYBRID)

## Agentes que coordinas:
- BLAZE: Entrenamiento de fuerza e hipertrofia
- ATLAS: Movilidad y flexibilidad
- TEMPO: Cardio y resistencia
- WAVE: Recuperación
- SAGE: Estrategia nutricional
- METABOL: Metabolismo
- MACRO: Macronutrientes
- NOVA: Suplementación
- SPARK: Conducta y hábitos
- STELLA: Análisis de datos
- LUNA: Salud femenina
- LOGOS: Educación

## Reglas:
1. Responde en español a menos que el usuario escriba en otro idioma
2. Sé directo y basado en evidencia
3. Cuando no sepas algo, admítelo y consulta al especialista
4. Nunca des consejo médico - refiere al profesional de salud
5. Personaliza basándote en el contexto del usuario

## Formato de respuesta:
- Conversacional pero profesional
- Usa bullet points solo cuando mejoren claridad
- Incluye "¿Por qué?" cuando sea educativo
- Sugiere siguiente acción cuando sea apropiado
"""
```

### 11.3 Ejemplos de Código Correcto

```python
# ✅ CORRECTO: Definición de agente ADK

from google.adk import Agent
from google.adk.tools import FunctionTool

@FunctionTool
def get_user_season(user_id: str) -> dict:
    """Obtiene la temporada activa del usuario."""
    from agents.shared.supabase_client import get_supabase_client
    
    supabase = get_supabase_client()
    result = supabase.client.table('seasons')\
        .select('*')\
        .eq('user_id', user_id)\
        .eq('status', 'active')\
        .single()\
        .execute()
    
    return result.data if result.data else {}

blaze = Agent(
    name="blaze",
    model="gemini-3-flash",
    description="Agente especializado en entrenamiento de fuerza",
    instruction=BLAZE_SYSTEM_PROMPT,
    tools=[get_user_season, generate_workout, log_workout],
)
```

```python
# ❌ INCORRECTO: Esto es el patrón viejo de Cloud Run

from fastapi import FastAPI
from agents.shared.a2a_server import A2AServer

class BlazeAgent(A2AServer):  # NO USAR
    pass
```

---

## 12. PLAN DE IMPLEMENTACIÓN

### 12.1 Roadmap de Fases

```
FASE 0: Preparación (Semana actual)
├── ✅ Análisis de repo existente
├── ✅ Crear PRD (este documento)
├── [ ] Actualizar CLAUDE.md, GEMINI.md con nuevas instrucciones
├── [ ] Crear ADR-007-agent-engine-migration.md
└── [ ] Setup proyecto GCP staging

FASE 1: Core Migration (Semanas 1-2)
├── [ ] Migrar NEXUS → GENESIS_X
├── [ ] Configurar Agent Engine
├── [ ] Validar conexión Supabase
├── [ ] Deploy a staging
└── [ ] Tests de integración básicos

FASE 2: Agentes Especializados (Semanas 3-4)
├── [ ] Migrar fitness → BLAZE
├── [ ] Migrar nutrition → SAGE
├── [ ] Crear STELLA (analytics)
├── [ ] Validar A2A cross-agent
└── [ ] Tests de flujos completos

FASE 3: Sistema Completo (Semanas 5-8)
├── [ ] ATLAS, TEMPO, WAVE (fitness)
├── [ ] METABOL, MACRO, NOVA (nutrition)
├── [ ] SPARK (conducta)
├── [ ] LUNA (salud femenina)
├── [ ] LOGOS (educación)
└── [ ] NGX ENGINE (temporadas/fases)

FASE 4: Frontend (Semanas 9-12)
├── [ ] API Gateway setup
├── [ ] GENESIS app (Expo)
├── [ ] NGX COACH console (Next.js)
└── [ ] Integración completa

FASE 5: Polish & Launch (Semanas 13-16)
├── [ ] Testing exhaustivo
├── [ ] Performance optimization
├── [ ] Security audit
├── [ ] Beta testing
└── [ ] Production launch
```

### 12.2 Prioridad de Desarrollo

```
P0 (Crítico - Hacer primero):
├── GENESIS_X (orquestador)
├── BLAZE (entrenamiento)
├── SAGE (nutrición)
└── Supabase schema updates

P1 (Alta - Semanas 3-4):
├── STELLA (datos)
├── SPARK (conducta)
└── NGX ENGINE básico

P2 (Media - Semanas 5-6):
├── ATLAS, TEMPO, WAVE
├── METABOL, MACRO, NOVA
└── LOGOS

P3 (Normal - Semanas 7-8):
├── LUNA
├── Features avanzados
└── Optimizaciones
```

---

## 13. CRITERIOS DE ACEPTACIÓN

### 13.1 Definition of Done - Agente

```markdown
Un agente está "Done" cuando:

□ Código
  - [ ] Implementado en formato ADK
  - [ ] Tools definidos como FunctionTool
  - [ ] System prompt documentado
  - [ ] Manejo de errores completo
  - [ ] Logging estructurado

□ Testing
  - [ ] Unit tests (≥70% coverage)
  - [ ] Integration tests con Supabase
  - [ ] A2A contract tests
  - [ ] Manual testing en playground

□ Deployment
  - [ ] Deploy exitoso a staging
  - [ ] Métricas de latencia dentro de SLO
  - [ ] Sin errores en logs por 24h

□ Documentation
  - [ ] README del agente actualizado
  - [ ] Agent card documentado
  - [ ] Ejemplos de uso
```

### 13.2 SLOs del Sistema

```yaml
availability:
  target: 99.5%
  measurement: "Uptime de Agent Engine"

latency:
  genesis_x:
    p95: 6000ms
    p99: 8000ms
  specialized_agents:
    p95: 2000ms
    p99: 3000ms

error_rate:
  target: <1%
  measurement: "Errores / Total requests"

cost:
  genesis_x_per_invoke: ≤$0.05
  specialized_per_invoke: ≤$0.01
```

### 13.3 Checklist de Release

```markdown
□ Pre-release
  - [ ] Todos los tests pasan
  - [ ] Code review aprobado
  - [ ] Security review completado
  - [ ] Performance benchmarks OK
  - [ ] Documentación actualizada

□ Release
  - [ ] Deploy a producción
  - [ ] Smoke tests en producción
  - [ ] Monitoring activo
  - [ ] Alertas configuradas

□ Post-release
  - [ ] Monitorear métricas 24h
  - [ ] Revisar logs de errores
  - [ ] Feedback de usuarios beta
  - [ ] Retrospectiva del release
```

---

## APÉNDICES

### A. Glosario

| Término | Definición |
|---------|------------|
| **A2A** | Agent-to-Agent protocol (JSON-RPC 2.0 + SSE) |
| **ADK** | Agent Development Kit de Google |
| **Agent Engine** | Runtime managed de Vertex AI para agentes |
| **HIE** | Hybrid Intelligence Engine (IA + Coach humano) |
| **NGX ENGINE** | Motor de personalización (temporadas/fases) |
| **RLS** | Row Level Security de PostgreSQL |
| **Season** | Ciclo de entrenamiento de 8-16 semanas |

### B. Referencias

- [Master Source of Truth V9.0](./docs/NGX_Master_V9.0.pdf)
- [Technical Implementation Guide V2.0](./docs/Technical_Implementation_V2.0.pdf)
- [Product Experience Design V2.0](./docs/Product_Experience_V2.0.pdf)
- [Go-To-Market Strategy V2.0](./docs/GTM_Strategy_V2.0.pdf)
- [Vertex AI Agent Engine Docs](https://cloud.google.com/agent-builder/agent-engine/overview)
- [Google ADK Documentation](https://google.github.io/adk-docs/)

### C. Changelog

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2025-11-27 | Versión inicial del PRD |

---

**FIN DEL DOCUMENTO**

*Este PRD es la fuente de verdad para el desarrollo de GENESIS_X. Cualquier cambio debe ser discutido y aprobado antes de modificar este documento.*
