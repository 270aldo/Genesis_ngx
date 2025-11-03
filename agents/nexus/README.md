# NEXUS Orchestrator

Orquestador principal del sistema multi-agente de bienestar, construido con **Google ADK** y exponiendo protocolo **A2A v0.3**.

## Arquitectura

NEXUS está construido usando el patrón **Coordinator/Specialist** del Google Agent Development Kit (ADK):

```
NEXUS (LlmAgent - Gemini 2.5 Pro)
├── agent.py          → Definición del agente ADK
├── prompt.py         → System instructions
├── a2a_wrapper.py    → Wrapper para exponer A2A v0.3
└── main.py           → Entry point FastAPI
```

### Componentes

1. **Agent ADK** (`agent.py`):
   - Agente principal usando `google.adk.Agent`
   - Modelo: `gemini-2.5-pro` (para síntesis y resolución - ADR-004)
   - Tools: `classify_intent`, `persist_message`
   - Output key: `nexus_response`

2. **A2A Wrapper** (`a2a_wrapper.py`):
   - Expone agente ADK como endpoints A2A v0.3
   - JSON-RPC 2.0 para invocaciones
   - SSE para streaming
   - Maneja Sessions, State y Events de ADK

3. **System Prompts** (`prompt.py`):
   - Instrucciones del sistema para NEXUS
   - Prompts para clasificación de intents
   - Directrices de coordinación

## Ejecutar Localmente

### Prerequisitos

```bash
# Instalar dependencias
pip install -r ../../requirements.txt

# Configurar variables de entorno
cp ../../.env.example ../../.env.local
# Editar .env.local con credenciales
```

### Iniciar NEXUS

```bash
# Opción 1: Desde raíz del proyecto
uvicorn agents.nexus.main:app --host 0.0.0.0 --port 8080 --reload

# Opción 2: Como módulo Python
python -m agents.nexus.main

# Opción 3: Con Docker Compose
docker-compose up nexus
```

### Verificar

```bash
# Health check
curl http://localhost:8080/healthz

# Agent Card
curl http://localhost:8080/card
```

## Endpoints A2A v0.3

### GET /card

Devuelve el Agent Card con metadata, capacidades y límites.

```bash
curl http://localhost:8080/card
```

### GET /healthz

Health check del servicio.

```bash
curl http://localhost:8080/healthz
```

### POST /negotiate

Negociación de capacidades y presupuesto.

```bash
curl -X POST http://localhost:8080/negotiate \
  -H "Content-Type: application/json" \
  -d '{
    "capabilities": ["orchestration", "planning"],
    "budget_usd": 0.05
  }'
```

### POST /invoke

Invocación JSON-RPC sin streaming.

```bash
curl -X POST http://localhost:8080/invoke \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: test-123" \
  -H "X-Budget-USD: 0.05" \
  -d '{
    "jsonrpc": "2.0",
    "method": "default",
    "params": {
      "message": "Necesito un plan de ejercicios",
      "user_id": "user-123"
    },
    "id": "1"
  }'
```

### POST /invoke/stream

Invocación con streaming SSE.

```bash
curl -N -X POST http://localhost:8080/invoke/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "X-Request-ID: test-stream-456" \
  -d '{
    "jsonrpc": "2.0",
    "method": "default",
    "params": {
      "message": "Dame consejos de nutrición",
      "user_id": "user-123"
    },
    "id": "2"
  }'
```

## Herramientas (Tools)

NEXUS tiene acceso a las siguientes herramientas:

### `classify_intent(message: str)`

Clasifica el intent del mensaje del usuario.

**Returns:**
```python
{
  "intent": "fitness",
  "confidence": 0.85,
  "suggested_agent": "fitness"
}
```

### `persist_message(conversation_id, content, agent_type, tokens_used, cost_usd)`

Persiste un mensaje de agente en Supabase.

**Returns:**
```python
{
  "status": "success",
  "message_id": "uuid"
}
```

## Variables de Entorno

Ver `.env.example` en la raíz del proyecto. Variables clave:

```bash
# Google ADK / Gemini
GOOGLE_CLOUD_PROJECT=your-project
GEMINI_PROJECT_ID=your-project
# NEXUS siempre usa gemini-2.5-pro (hardcoded en agent.py)

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key

# Service
NEXUS_HOST=0.0.0.0
NEXUS_PORT=8080
NEXUS_RELOAD=true

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## Desarrollo

### Agregar Sub-Agentes

Cuando implementes agentes especializados (Fitness, Nutrition, Mental Health):

```python
# En agent.py
from .sub_agents.fitness import fitness_agent
from .sub_agents.nutrition import nutrition_agent

nexus_agent = Agent(
    name="nexus",
    model="gemini-2.5-pro",  # NEXUS usa Pro (ADR-004)
    instruction=NEXUS_INSTRUCTION,
    sub_agents=[
        fitness_agent,        # usa gemini-2.5-flash
        nutrition_agent,      # usa gemini-2.5-flash
    ],
    # ...
)
```

### Usar AgentTool

Para invocar sub-agentes explícitamente como tools:

```python
from google.adk.tools import AgentTool

nexus_agent = Agent(
    name="nexus",
    model="gemini-2.5-pro",  # NEXUS usa Pro (ADR-004)
    instruction=NEXUS_INSTRUCTION,
    tools=[
        AgentTool(agent=fitness_agent),    # Flash para respuestas rápidas
        AgentTool(agent=nutrition_agent),  # Flash para conversación
    ],
)
```

### Testing

```bash
# Tests unitarios
pytest agents/nexus/tests/

# Con coverage
pytest --cov=agents.nexus
```

## Deploy a Cloud Run

```bash
# Build
docker build -t gcr.io/PROJECT_ID/nexus:latest -f Dockerfile .

# Push
docker push gcr.io/PROJECT_ID/nexus:latest

# Deploy
gcloud run deploy nexus \
  --image gcr.io/PROJECT_ID/nexus:latest \
  --platform managed \
  --region us-central1 \
  --set-env-vars ENVIRONMENT=production
```

## Referencias

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [A2A Protocol Spec v0.3](../../docs/ADK_A2A_GCP_context.md)
- [ADR-001: Cloud Run over Agent Engine](../../ADR/001-cloud-run-over-agent-engine.md)
- [ADR-002: A2A v0.3 Protocol](../../ADR/002-a2a-v03-protocol.md)
- [Ejemplos Multi-Agentes ADK](../../docs/ejemplos_multiagents_adk.md)
