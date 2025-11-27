# Genesis NGX

Sistema multi-agente de bienestar (wellness) construido con Google ADK (Agent Development Kit), Gemini 2.5 y Supabase.

## Arquitectura

```
                    ┌─────────────────────────────────┐
                    │          GENESIS_X              │
                    │       (Orchestrator - Pro)      │
                    │  Intent Classification          │
                    │  Agent Routing & Consensus      │
                    └───────────────┬─────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
┌───────▼───────┐          ┌────────▼────────┐         ┌───────▼───────┐
│    FITNESS    │          │   NUTRITION     │         │    OTHER      │
│               │          │                 │         │               │
│ BLAZE: Fuerza │          │ SAGE: Strategy  │         │ SPARK: Habits │
│ ATLAS: Movil. │          │ METABOL: TDEE   │         │ STELLA: Data  │
│ TEMPO: Cardio │          │ MACRO: Macros   │         │ LUNA: Women   │
│ WAVE: Recov.  │          │ NOVA: Supps     │         │ LOGOS: Educ.  │
└───────────────┘          └─────────────────┘         └───────────────┘
```

### Modelos por Rol

| Rol | Modelo | Agentes |
|-----|--------|---------|
| **Orquestador** | gemini-2.5-pro | GENESIS_X |
| **Educación** | gemini-2.5-pro | LOGOS |
| **Especialistas** | gemini-2.5-flash | 11 agentes |

## Características

- **Orquestador GENESIS_X**: Clasificación de intents y coordinación de agentes especializados
- **Framework ADK**: Google Agent Development Kit para definición nativa de agentes
- **Gemini 2.5**: Pro para orquestación, Flash para agentes especializados
- **Supabase**: PostgreSQL + RLS como única fuente de verdad
- **Protocolo A2A v0.3**: JSON-RPC + SSE para comunicación inter-agentes
- **Testing**: Suite completa con pytest (1045+ tests, 89% coverage)

## Estructura del Proyecto

```
Genesis_ngx/
├── agents/
│   ├── genesis_x/          # Orquestador principal (Pro)
│   │   ├── agent.py        # Definición del agente
│   │   ├── tools.py        # FunctionTools
│   │   ├── prompts.py      # System prompts
│   │   └── tests/          # Tests unitarios e integración
│   │
│   ├── blaze/              # Fuerza e hipertrofia (Flash)
│   ├── atlas/              # Movilidad y flexibilidad (Flash)
│   ├── tempo/              # Cardio y resistencia (Flash)
│   ├── wave/               # Recuperación (Flash)
│   ├── sage/               # Estrategia nutricional (Flash)
│   ├── metabol/            # Metabolismo y TDEE (Flash)
│   ├── macro/              # Macronutrientes (Flash)
│   ├── nova/               # Suplementación (Flash)
│   ├── spark/              # Conducta y hábitos (Flash)
│   ├── stella/             # Analytics y reportes (Flash)
│   ├── luna/               # Salud femenina (Flash)
│   ├── logos/              # Educación (Pro) ⭐
│   │
│   └── shared/             # Código compartido
│       ├── supabase_client.py
│       ├── cost_calculator.py
│       ├── security.py
│       └── config.py
│
├── ADR/                    # Architecture Decision Records
├── docs/                   # Documentación técnica
├── supabase/               # Migraciones SQL
├── adk.yaml               # Configuración ADK
├── requirements.txt       # Dependencias Python
└── pytest.ini            # Configuración de tests
```

## Arranque Rápido

### Prerequisitos

- Python 3.12+
- Google Cloud SDK
- Supabase CLI (opcional)

### 1. Configuración Inicial

```bash
# Clonar repositorio
git clone https://github.com/270aldo/Genesis_ngx.git
cd Genesis_ngx

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env.local
# Editar .env.local con tus credenciales
```

### 2. Autenticar con GCP

```bash
gcloud auth application-default login
gcloud config set project ngx-genesis-prod
```

### 3. Ejecutar Agentes

```bash
# Ejecutar en playground local (ADK)
adk web

# Ejecutar agente específico
adk run genesis_x
```

### 4. Verificar Tests

```bash
# Ejecutar todos los tests
pytest agents/ -v

# Con coverage
pytest --cov=agents --cov-report=html
```

## Agentes Disponibles

| Agent | Dominio | Modelo | Tests | Estado |
|-------|---------|--------|-------|--------|
| GENESIS_X | Orquestación | gemini-2.5-pro | 39 | ✅ Implementado |
| BLAZE | Fuerza/Hipertrofia | gemini-2.5-flash | 58 | ✅ Implementado |
| ATLAS | Movilidad | gemini-2.5-flash | 58 | ✅ Implementado |
| TEMPO | Cardio | gemini-2.5-flash | 72 | ✅ Implementado |
| WAVE | Recuperación | gemini-2.5-flash | 65 | ✅ Implementado |
| SAGE | Estrategia Nutricional | gemini-2.5-flash | 54 | ✅ Implementado |
| METABOL | Metabolismo/TDEE | gemini-2.5-flash | 86 | ✅ Implementado |
| MACRO | Macronutrientes | gemini-2.5-flash | 131 | ✅ Implementado |
| NOVA | Suplementación | gemini-2.5-flash | 115 | ✅ Implementado |
| SPARK | Conducta/Hábitos | gemini-2.5-flash | 132 | ✅ Implementado |
| STELLA | Analytics | gemini-2.5-flash | 95 | ✅ Implementado |
| LUNA | Salud Femenina | gemini-2.5-flash | 120 | ✅ Implementado |
| **LOGOS** | **Educación** | **gemini-2.5-pro** | **140** | ✅ Implementado |

**Total: 13 agentes, 1045+ tests**

## Testing

```bash
# Todos los tests
pytest

# Tests de un agente específico
pytest agents/genesis_x/tests/ -v

# Con coverage
pytest --cov=agents --cov-report=html

# Ver coverage en navegador
open htmlcov/index.html
```

## Desarrollo

### Linting

```bash
# Linting con ruff
ruff check agents/

# Autofix
ruff check --fix agents/

# Formatear
ruff format agents/
```

### Crear un Nuevo Agente

Ver [AGENTS.md](AGENTS.md) para la guía completa de implementación de agentes con ADK.

## Deploy

```bash
# Deploy a staging
adk deploy --env staging

# Deploy a producción
adk deploy --env production

# Ver estado
adk status
```

## Documentación

- **[AGENTS.md](AGENTS.md)**: Guía de implementación de agentes
- **[CLAUDE.md](CLAUDE.md)**: Contexto para Claude Code
- **[GENESIS_PRD.md](GENESIS_PRD.md)**: Product Requirements Document
- **[ADRs](ADR/)**: Architecture Decision Records

## Seguridad

- ✅ RLS en Supabase para aislamiento de datos
- ✅ Validación de PHI/PII en prompts
- ✅ Budget enforcement por request
- ✅ Rate limiting por agente

## License

[MIT License](LICENSE)
