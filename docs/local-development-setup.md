# Guía de Setup para Desarrollo Local

Esta guía te llevará paso a paso por el proceso de configurar Genesis NGX en tu máquina local para desarrollo.

## Requisitos Previos

### Software Requerido

1. **Python 3.12+**
   ```bash
   python --version  # Debe ser 3.12 o superior
   ```

2. **Git**
   ```bash
   git --version
   ```

3. **Docker & Docker Compose** (para servicios locales)
   ```bash
   docker --version
   docker-compose --version
   ```

4. **Supabase CLI** (opcional, para base de datos local)
   ```bash
   # Instalar con brew (macOS)
   brew install supabase/tap/supabase

   # O con npm
   npm install -g supabase
   ```

5. **Google Cloud SDK** (para Vertex AI / Gemini)
   ```bash
   gcloud --version
   ```

### Cuentas Requeridas

1. **Google Cloud Platform**
   - Proyecto con Vertex AI API habilitada
   - Service Account con permisos para Vertex AI
   - Credenciales JSON descargadas

2. **Supabase** (puede ser local o cloud)
   - Proyecto creado en https://supabase.com
   - URL y keys copiadas

## 1. Clonar el Repositorio

```bash
# Clonar
git clone https://github.com/270aldo/Genesis_ngx.git
cd Genesis_ngx

# Crear branch de desarrollo
git checkout -b feature/mi-nombre-setup
```

## 2. Configurar Entorno Python

### Crear Virtual Environment

```bash
# Crear venv
python -m venv .venv

# Activar venv
# En macOS/Linux:
source .venv/bin/activate

# En Windows:
.venv\Scripts\activate
```

### Instalar Dependencias

```bash
# Instalar todas las dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Verificar instalación
pip list | grep fastapi
pip list | grep google-cloud-aiplatform
```

## 3. Configurar Variables de Entorno

### Crear archivo .env.local

```bash
# Copiar el template
cp .env.example .env.local
```

### Editar .env.local

Abre `.env.local` y configura las siguientes variables:

```bash
# ============================================================================
# Environment
# ============================================================================
ENVIRONMENT=development
DEBUG=true

# ============================================================================
# Google Cloud Platform
# ============================================================================
GOOGLE_CLOUD_PROJECT=tu-proyecto-gcp
GOOGLE_CLOUD_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# ============================================================================
# Vertex AI / Gemini
# ============================================================================
GEMINI_PROJECT_ID=tu-proyecto-gcp
GEMINI_LOCATION=us-central1
GEMINI_DEFAULT_MODEL=gemini-2.0-flash-exp

# ============================================================================
# Supabase
# ============================================================================
# Opción 1: Supabase Cloud
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu-anon-key
SUPABASE_SERVICE_ROLE_KEY=tu-service-role-key

# Opción 2: Supabase Local (si usas supabase CLI)
# SUPABASE_URL=http://localhost:54321
# SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
# SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# ============================================================================
# JWT Secret (generar uno nuevo)
# ============================================================================
# Generar con: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET_KEY=tu-secret-key-segura-de-32-caracteres-minimo

# ============================================================================
# Logging
# ============================================================================
LOG_LEVEL=DEBUG
LOG_FORMAT=console
LOG_TO_CLOUD=false
```

### Obtener Credenciales de Google Cloud

```bash
# 1. Autenticarse con gcloud
gcloud auth login

# 2. Configurar proyecto
gcloud config set project tu-proyecto-gcp

# 3. Habilitar APIs necesarias
gcloud services enable aiplatform.googleapis.com
gcloud services enable logging.googleapis.com

# 4. Crear Service Account
gcloud iam service-accounts create genesis-dev \
    --display-name="Genesis Development"

# 5. Asignar permisos
gcloud projects add-iam-policy-binding tu-proyecto-gcp \
    --member="serviceAccount:genesis-dev@tu-proyecto-gcp.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# 6. Descargar key
gcloud iam service-accounts keys create ~/genesis-dev-key.json \
    --iam-account=genesis-dev@tu-proyecto-gcp.iam.gserviceaccount.com

# 7. Configurar en .env.local
# GOOGLE_APPLICATION_CREDENTIALS=/Users/tu-usuario/genesis-dev-key.json
```

## 4. Configurar Supabase

### Opción A: Supabase Local (Recomendado para desarrollo)

```bash
# Iniciar Supabase local
supabase init
supabase start

# Esto mostrará:
# - API URL: http://localhost:54321
# - anon key: eyJ...
# - service_role key: eyJ...

# Aplicar migraciones
supabase db push

# Verificar que las tablas existen
supabase db diff
```

### Opción B: Supabase Cloud

```bash
# Link a proyecto existente
supabase link --project-ref tu-proyecto-ref

# Aplicar migraciones
supabase db push

# O manualmente desde el dashboard de Supabase:
# 1. Ve a SQL Editor
# 2. Copia el contenido de supabase/migrations/001_initial_schema.sql
# 3. Ejecuta
```

## 5. Iniciar Servicios con Docker Compose

```bash
# Iniciar Redis (necesario para caché)
docker-compose up redis -d

# Ver logs
docker-compose logs -f redis

# Verificar que funciona
redis-cli ping  # Debe responder: PONG
```

## 6. Ejecutar NEXUS Localmente

### Modo Desarrollo (con hot reload)

```bash
# Desde la raíz del proyecto
python -m uvicorn agents.nexus.main:app --host 0.0.0.0 --port 8080 --reload

# O directamente
python agents/nexus/main.py
```

### Verificar que funciona

```bash
# Healthcheck
curl http://localhost:8080/healthz
# Respuesta: {"status":"ok"}

# Agent Card
curl http://localhost:8080/card
# Respuesta: JSON con agent card

# Test invoke
curl -X POST http://localhost:8080/invoke \
  -H "Content-Type: application/json" \
  -H "X-Budget-USD: 0.05" \
  -d '{
    "jsonrpc": "2.0",
    "method": "classify_intent",
    "params": {"message": "Quiero hacer ejercicio"},
    "id": "test-1"
  }'
```

## 7. Ejecutar Tests

```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=agents --cov-report=html

# Solo tests unitarios (rápidos)
pytest -m unit

# Solo un archivo específico
pytest agents/shared/tests/test_cost_calculator.py

# Ver coverage en navegador
open htmlcov/index.html
```

## 8. Linting y Code Quality

```bash
# Ejecutar ruff (linting)
ruff check agents/

# Autofix
ruff check --fix agents/

# Formatear con black
black agents/

# Type checking con mypy (opcional)
mypy agents/
```

## 9. Usar Docker Compose (Stack Completo)

```bash
# Iniciar todos los servicios
docker-compose up

# En background
docker-compose up -d

# Ver logs
docker-compose logs -f nexus

# Detener
docker-compose down

# Reconstruir después de cambios
docker-compose up --build
```

## 10. Desarrollo de Nuevos Agentes

### Crear estructura

```bash
# Crear directorio del agente
mkdir -p agents/fitness
touch agents/fitness/__init__.py
touch agents/fitness/main.py
touch agents/fitness/Dockerfile
mkdir -p agents/fitness/tests
```

### Template base (agents/fitness/main.py)

```python
"""Agent Fitness."""

from agents.shared.a2a_server import A2AServer

AGENT_CARD = {
    "id": "fitness-agent",
    "version": "0.1.0",
    "capabilities": ["workout_planning", "progress_tracking"],
    # ...
}

class FitnessAgent(A2AServer):
    def __init__(self):
        super().__init__(AGENT_CARD)

    async def handle_method(self, method: str, params: dict):
        # Implementar lógica
        pass

agent = FitnessAgent()
app = agent.app
```

### Actualizar docker-compose.yml

```yaml
fitness:
  build:
    context: .
    dockerfile: agents/fitness/Dockerfile
  ports:
    - "8081:8081"
  env_file:
    - .env.local
```

## 11. Trabajar con Git

```bash
# Ver estado
git status

# Crear commits siguiendo Conventional Commits
git add .
git commit -m "feat(fitness): add workout planning agent"

# Push
git push -u origin feature/mi-nombre-setup

# Crear PR
gh pr create --title "feat: add local development setup" \
  --body "Implements complete local dev environment"
```

## 12. Debugging

### VS Code

Crear `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "NEXUS Debug",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "agents.nexus.main:app",
        "--host", "0.0.0.0",
        "--port", "8080",
        "--reload"
      ],
      "envFile": "${workspaceFolder}/.env.local",
      "console": "integratedTerminal"
    },
    {
      "name": "Pytest Debug",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-v"],
      "console": "integratedTerminal"
    }
  ]
}
```

### Logs

```bash
# Ver logs estructurados
tail -f logs/nexus.log

# Con jq para formatear JSON
tail -f logs/nexus.log | jq .

# Filtrar por level
tail -f logs/nexus.log | jq 'select(.level == "ERROR")'
```

## Troubleshooting

### Error: "ModuleNotFoundError"

```bash
# Asegurarse de que PYTHONPATH incluye el directorio raíz
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# O activar el venv correctamente
source .venv/bin/activate
```

### Error: "google.auth.exceptions.DefaultCredentialsError"

```bash
# Verificar que GOOGLE_APPLICATION_CREDENTIALS está configurado
echo $GOOGLE_APPLICATION_CREDENTIALS

# Verificar que el archivo existe
ls -la $GOOGLE_APPLICATION_CREDENTIALS

# Autenticarse con gcloud
gcloud auth application-default login
```

### Error: Supabase "Invalid API key"

```bash
# Verificar que las keys son correctas
supabase status

# Resetear Supabase local
supabase stop
supabase start
```

### Tests fallan con "fixture not found"

```bash
# Asegurarse de que conftest.py está en la raíz
ls conftest.py

# Ejecutar con -v para ver más detalles
pytest -v
```

## Próximos Pasos

1. ✅ Configurar entorno local
2. ✅ Ejecutar NEXUS
3. ✅ Ejecutar tests
4. 📝 Leer `CONTRIBUTING.md` para guías de código
5. 📝 Leer `docs/gitflow-strategy.md` para workflow de git
6. 🚀 Crear tu primer agente especializado
7. 🚀 Implementar tu primera feature

## Recursos

- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [Vertex AI Python SDK](https://cloud.google.com/vertex-ai/docs/python-sdk/use-vertex-ai-python-sdk)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)
- [A2A Protocol Spec](docs/ADK_A2A_GCP_context.md)
- [Conventional Commits](https://www.conventionalcommits.org/)

## Soporte

Si encuentras problemas:

1. Revisa los logs: `docker-compose logs -f nexus`
2. Verifica las variables de entorno: `env | grep -E "(GEMINI|SUPABASE|GOOGLE)"`
3. Consulta el canal de Slack: `#genesis-dev`
4. Abre un issue en GitHub con etiqueta `help-wanted`
