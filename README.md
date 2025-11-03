# Genesis NGX

Sistema multi-agente de bienestar (wellness) construido con el ADK de Google, Gemini 2.5 y Supabase como fuente única de verdad. El orquestador NEXUS y los agentes especializados se ejecutan en Cloud Run exponiendo el protocolo A2A v0.3.

## 🚀 Características

- **Orquestador NEXUS**: Clasificación de intents y coordinación de agentes especializados
- **Gemini 2.5**: Pro/Flash/Flash-Lite con caching automático y control de costos
- **Supabase**: PostgreSQL + Realtime + RLS como única fuente de verdad
- **Protocolo A2A v0.3**: JSON-RPC + SSE para comunicación inter-agentes
- **Logging Estructurado**: Integración con Cloud Logging
- **Type-Safe**: Python 3.12 con type hints y validación Pydantic
- **Testing**: Suite completa con pytest y coverage

## 📁 Estructura del Proyecto

```
Genesis_ngx/
├── ADR/                        # Architecture Decision Records
├── agents/
│   ├── shared/                 # Código compartido
│   │   ├── a2a_server.py      # Servidor base A2A
│   │   ├── a2a_client.py      # Cliente A2A con reintentos
│   │   ├── gemini_client.py   # Cliente Gemini con caching
│   │   ├── supabase_client.py # Cliente Supabase con RLS
│   │   ├── config.py          # Configuración centralizada
│   │   ├── logging_config.py  # Logging estructurado
│   │   ├── cost_calculator.py # Calculadora de costos
│   │   └── security.py        # Validación de seguridad
│   ├── nexus/                 # Orquestador NEXUS
│   │   ├── main.py           # FastAPI app principal
│   │   ├── Dockerfile        # Multi-stage Docker build
│   │   └── tests/            # Tests específicos
│   └── [fitness|nutrition]/   # Agentes especializados (futuro)
├── docs/                      # Documentación técnica
│   ├── architecture-october-2025.md
│   ├── gitflow-strategy.md
│   ├── local-development-setup.md
│   └── a2a-agent-card.schema.json
├── supabase/                  # Base de datos
│   ├── migrations/           # Migraciones SQL
│   └── seed.sql             # Datos iniciales
├── .github/                   # CI/CD workflows
├── docker-compose.yml        # Stack de desarrollo
├── requirements.txt          # Dependencias Python
├── pytest.ini               # Configuración de tests
└── .env.example             # Template de variables
```

## 🏃 Arranque Rápido

### Prerequisitos

- Python 3.12+
- Docker & Docker Compose
- Google Cloud SDK (para Gemini)
- Supabase CLI (opcional)

### 1. Configuración Inicial

```bash
# Clonar repositorio
git clone https://github.com/270aldo/Genesis_ngx.git
cd Genesis_ngx

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env.local
# Editar .env.local con tus credenciales
```

### 2. Configurar Supabase

```bash
# Opción A: Supabase Local
supabase init
supabase start
supabase db push

# Opción B: Supabase Cloud
# 1. Crear proyecto en https://supabase.com
# 2. Copiar URL y keys a .env.local
# 3. Aplicar migraciones desde el SQL Editor
```

### 3. Ejecutar NEXUS

```bash
# Modo desarrollo (con hot reload)
uvicorn agents.nexus.main:app --host 0.0.0.0 --port 8080 --reload

# O con Python
python agents/nexus/main.py

# O con Docker Compose
docker-compose up
```

### 4. Verificar Instalación

```bash
# Healthcheck
curl http://localhost:8080/healthz

# Agent Card
curl http://localhost:8080/card

# Test clasificación de intent
curl -X POST http://localhost:8080/invoke \
  -H "Content-Type: application/json" \
  -H "X-Budget-USD: 0.05" \
  -d '{
    "jsonrpc": "2.0",
    "method": "classify_intent",
    "params": {"message": "Quiero hacer ejercicio"},
    "id": "1"
  }'
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=agents --cov-report=html

# Solo tests unitarios
pytest -m unit

# Ver coverage en navegador
open htmlcov/index.html
```

## 🛠️ Desarrollo

### Linting y Code Quality

```bash
# Linting con ruff
ruff check agents/

# Autofix
ruff check --fix agents/

# Formatear con black
black agents/
```

### Crear un Nuevo Agente

```bash
# Usar NEXUS como template
cp -r agents/nexus agents/mi-agente

# Actualizar agent card y lógica en main.py
# Agregar a docker-compose.yml
# Crear tests en agents/mi-agente/tests/
```

## 📖 Documentación

- **[Setup Local Completo](docs/local-development-setup.md)**: Guía paso a paso
- **[GitFlow Strategy](docs/gitflow-strategy.md)**: Workflow de Git y branching
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Guía para contribuir
- **[AGENTS.md](AGENTS.md)**: Guía de implementación de agentes
- **[Arquitectura](docs/architecture-october-2025.md)**: Diseño del sistema
- **[ADRs](ADR/)**: Decisiones arquitectónicas

## 🌳 GitFlow

```bash
# Crear feature branch
git checkout develop
git checkout -b feature/GEN-123-mi-feature

# Commits con Conventional Commits
git commit -m "feat(nexus): add intent classification"
git commit -m "fix(shared): correct cost calculation"

# Push y crear PR
git push -u origin feature/GEN-123-mi-feature
gh pr create
```

Ver [docs/gitflow-strategy.md](docs/gitflow-strategy.md) para más detalles.

## 🚢 Despliegue

### Cloud Run (Producción)

```bash
# Build de imagen
docker build -t gcr.io/PROJECT_ID/nexus:latest -f agents/nexus/Dockerfile .

# Push a GCR
docker push gcr.io/PROJECT_ID/nexus:latest

# Deploy
gcloud run deploy nexus \
  --image gcr.io/PROJECT_ID/nexus:latest \
  --platform managed \
  --region us-central1 \
  --set-env-vars ENVIRONMENT=production
```

### Con Terraform (Recomendado)

```bash
cd terraform/
terraform init
terraform plan
terraform apply
```

## 🔒 Seguridad

- ✅ RLS en Supabase para aislamiento de datos
- ✅ OIDC para autenticación inter-servicios
- ✅ Validación de PII/PHI en prompts
- ✅ Rate limiting por agente
- ✅ Budget enforcement por request
- ✅ Secrets en Secret Manager (producción)

## 📊 Observabilidad

- **Logs**: Structured logging con Cloud Logging
- **Métricas**: Cost tracking, latencia, cache hit rate
- **Tracing**: Request ID en todos los logs
- **Dashboards**: Cloud Monitoring (ver `docs/monitoring.md`)

## 🤝 Contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para:
- Estilo de código
- Proceso de PR
- Testing guidelines
- Commit conventions

## 📝 License

[MIT License](LICENSE)

## 🙏 Agradecimientos

- [Google ADK](https://cloud.google.com/vertex-ai/docs/adk)
- [Supabase](https://supabase.com)
- [FastAPI](https://fastapi.tiangolo.com)
- [A2A Protocol Spec](https://www.microsoft.com/en-us/research/uploads/prod/2024/07/A2A_Protocol_Specification_v0_3.pdf)
