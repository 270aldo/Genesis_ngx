# Genesis NGX

Sistema multi-agente de bienestar (wellness) construido con Google ADK (Agent Development Kit), Gemini 2.5 y Supabase.

## Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                    GENESIS_X                        │
│              (Orchestrator - Pro)                   │
│  - Intent Classification                            │
│  - Agent Routing                                    │
│  - Consensus Building                               │
└──────────────┬────────────────┬─────────────────────┘
               │                │
       ┌───────▼───────┐ ┌──────▼───────┐
       │    BLAZE      │ │     SAGE     │
       │   (Flash)     │ │   (Flash)    │
       │  Strength/    │ │  Nutrition   │
       │  Hypertrophy  │ │  Strategy    │
       └───────────────┘ └──────────────┘
               │                │
       ┌───────▼───────┐ ┌──────▼───────┐
       │    ATLAS      │ │    TEMPO     │  (Planned)
       │  Mobility     │ │   Cardio     │
       └───────────────┘ └──────────────┘
```

## Características

- **Orquestador GENESIS_X**: Clasificación de intents y coordinación de agentes especializados
- **Framework ADK**: Google Agent Development Kit para definición nativa de agentes
- **Gemini 2.5**: Pro para orquestación, Flash para agentes especializados
- **Supabase**: PostgreSQL + RLS como única fuente de verdad
- **Protocolo A2A v0.3**: JSON-RPC + SSE para comunicación inter-agentes
- **Testing**: Suite completa con pytest (148+ tests)

## Estructura del Proyecto

```
Genesis_ngx/
├── agents/
│   ├── genesis_x/          # Orquestador principal (ADK)
│   │   ├── agent.py        # Definición del agente
│   │   ├── tools.py        # FunctionTools
│   │   ├── prompts.py      # System prompts
│   │   └── tests/          # Tests unitarios e integración
│   │
│   ├── blaze/              # Agente de fuerza/hipertrofia
│   ├── sage/               # Agente de nutrición
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

| Agent | Dominio | Modelo | Estado |
|-------|---------|--------|--------|
| GENESIS_X | Orquestación | gemini-2.5-pro | ✅ Implementado |
| BLAZE | Fuerza/Hipertrofia | gemini-2.5-flash | ✅ Implementado |
| SAGE | Nutrición | gemini-2.5-flash | ✅ Implementado |
| ATLAS | Movilidad | gemini-2.5-flash | 🔜 Planificado |
| TEMPO | Cardio | gemini-2.5-flash | 🔜 Planificado |
| WAVE | Recuperación | gemini-2.5-flash | 🔜 Planificado |

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
