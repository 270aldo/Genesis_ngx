# Genesis NGX

Sistema multi-agente de bienestar (wellness) construido con Google ADK (Agent Development Kit), Gemini 2.5 y Supabase. **Listo para producción en México** con compliance LFPDPPP.

> **Versión**: 1.0.0 | **Tests**: 1104+ | **Coverage**: 89% | **Status**: Production Ready

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                      │
│                  Expo Mobile / Next.js Web                          │
└─────────────────────────────┬───────────────────────────────────────┘
                              │ HTTPS + JWT
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    GATEWAY (FastAPI - Cloud Run)                    │
│  ┌─────────┐ ┌──────────┐ ┌────────┐ ┌────────┐ ┌───────────────┐  │
│  │Auth JWT │ │Rate Limit│ │ Budget │ │Logging │ │ Orchestration │  │
│  └─────────┘ └──────────┘ └────────┘ └────────┘ └───────────────┘  │
└─────────────────────────────┬───────────────────────────────────────┘
                              │ A2A Protocol
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              VERTEX AI AGENT ENGINE (13 Agents)                     │
├─────────────────────────────────────────────────────────────────────┤
│                    ┌─────────────────────────────────┐              │
│                    │          GENESIS_X              │              │
│                    │       (Orchestrator - Pro)      │              │
│                    └───────────────┬─────────────────┘              │
│                                    │                                │
│        ┌───────────────────────────┼───────────────────────────┐    │
│        │                           │                           │    │
│ ┌──────▼──────┐          ┌────────▼────────┐         ┌───────▼───┐ │
│ │   FITNESS   │          │   NUTRITION     │         │   OTHER   │ │
│ │             │          │                 │         │           │ │
│ │ BLAZE: 💪  │          │ SAGE: Strategy  │         │ SPARK: 🔥 │ │
│ │ ATLAS: 🧘  │          │ METABOL: TDEE   │         │ STELLA: 📊│ │
│ │ TEMPO: 🏃  │          │ MACRO: Macros   │         │ LUNA: 🌙  │ │
│ │ WAVE: 🌊   │          │ NOVA: Supps     │         │ LOGOS: 📚 │ │
│ └─────────────┘          └─────────────────┘         └───────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SUPABASE (PostgreSQL + RLS)                      │
│           Tiered Health Data | Consent System | RPC APIs            │
└─────────────────────────────────────────────────────────────────────┘
```

### Modelos por Rol

| Rol | Modelo | Agentes | Latency SLO |
|-----|--------|---------|-------------|
| **Orquestador** | gemini-2.5-pro | GENESIS_X | ≤6s |
| **Educación** | gemini-2.5-pro | LOGOS | ≤6s |
| **Especialistas** | gemini-2.5-flash | 11 agentes | ≤2s |

## Características

- **Orquestador GENESIS_X**: Clasificación de intents y coordinación de agentes especializados
- **Gateway FastAPI**: BFF (Backend for Frontend) con auth, rate limiting y budget tracking
- **Framework ADK**: Google Agent Development Kit para definición nativa de agentes
- **Gemini 2.5**: Pro para orquestación, Flash para agentes especializados
- **Supabase**: PostgreSQL + RLS como única fuente de verdad
- **Protocolo A2A v0.3**: JSON-RPC + SSE para comunicación inter-agentes
- **Compliance LFPDPPP**: Sistema de consentimiento por tiers para datos de salud
- **Testing**: Suite completa con pytest (1104+ tests, 89% coverage)

## Estructura del Proyecto

```
Genesis_ngx/
├── agents/                 # 13 Agentes ADK
│   ├── genesis_x/          # Orquestador principal (Pro)
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
│   └── shared/             # Código compartido
│
├── gateway/                # FastAPI BFF (Cloud Run)
│   ├── api/v1/             # Endpoints REST
│   ├── middleware/         # Auth, Rate Limit, Logging
│   ├── services/           # Orchestration, Persistence
│   └── tests/              # Tests del gateway
│
├── terraform/              # Infraestructura como código
│   └── modules/            # WIF, Service Accounts
│
├── schemas/                # JSON Schemas (Contract Testing)
├── tests/
│   ├── contract/           # Contract tests
│   └── golden/             # Golden path validations
│
├── monitoring/             # Alertas y dashboards
│   └── alerts/             # SLO alerts (Cloud Monitoring)
│
├── supabase/               # Migraciones SQL
│   └── migrations/         # 001_init, 002_health_tiers
│
├── docs/                   # Documentación
│   ├── compliance/         # Verificación LFPDPPP
│   ├── legal/              # Aviso de privacidad
│   └── runbooks/           # Incident response
│
├── ADR/                    # Architecture Decision Records
├── adk.yaml                # Configuración ADK
└── requirements.txt        # Dependencias Python
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

**Total: 13 agentes, 1104+ tests, 89% coverage**

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

## Gateway API

El Gateway FastAPI actúa como BFF (Backend for Frontend) para clientes móviles y web.

### Endpoints

| Endpoint | Method | Auth | Descripción |
|----------|--------|------|-------------|
| `/v1/chat` | POST | JWT | Chat request/response |
| `/v1/chat/stream` | POST | JWT | SSE streaming |
| `/v1/conversations` | GET | JWT | Listar conversaciones |
| `/v1/conversations/{id}` | GET | JWT | Obtener conversación |
| `/health` | GET | No | Health check |
| `/ready` | GET | No | Readiness probe |

### Ejecutar Gateway

```bash
cd gateway
uvicorn main:app --reload --port 8080
```

## Compliance (México)

Sistema de consentimiento por tiers para datos de salud según LFPDPPP 2025.

| Tier | Datos | Consentimiento |
|------|-------|----------------|
| **Tier 1** | Peso, altura, pasos, calorías, sueño | Privacy Policy |
| **Tier 2** | Grasa corporal, FC reposo, calidad sueño | Checkbox adicional |
| **Tier 3** | Glucosa, presión, ciclo menstrual | Excluido v1 |

Ver [docs/compliance/backend-verification.md](docs/compliance/backend-verification.md) para detalles.

## Documentación

- **[AGENTS.md](AGENTS.md)**: Guía de implementación de agentes
- **[CLAUDE.md](CLAUDE.md)**: Contexto para Claude Code
- **[GENESIS_PRD.md](GENESIS_PRD.md)**: Product Requirements Document
- **[ADRs](ADR/)**: Architecture Decision Records
- **[Runbooks](docs/runbooks/)**: Guías de respuesta a incidentes
- **[Compliance](docs/compliance/)**: Verificación LFPDPPP

## Seguridad

- ✅ RLS en Supabase para aislamiento de datos
- ✅ Validación de PHI/PII en prompts
- ✅ Budget enforcement por request
- ✅ Rate limiting por usuario (60/min) e IP (100/min)
- ✅ JWT validation con Supabase Auth
- ✅ Sistema de consentimiento tiered (LFPDPPP)

## Infraestructura

```bash
# Deploy Gateway a Cloud Run
gcloud run deploy genesis-gateway \
  --source=gateway/ \
  --region=us-central1 \
  --allow-unauthenticated

# Deploy Agentes a Agent Engine
adk deploy --env production
```

## License

[MIT License](LICENSE)
