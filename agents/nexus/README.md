# NEXUS Orchestrator (POC)

Servicio FastAPI desplegable en Cloud Run que expone endpoints A2A v0.3 para orquestación básica.

## Ejecutar localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r agents/nexus/requirements.txt
uvicorn "agents.nexus.main:app" --host 0.0.0.0 --port 8080 --reload
```

## Probar endpoints

```bash
curl http://127.0.0.1:8080/card

curl -X POST http://127.0.0.1:8080/invoke \
  -H "Content-Type: application/json" \
  -H "X-Budget-USD: 0.05" \
  -d '{"jsonrpc":"2.0","method":"classify_intent","params":{"message":"Necesito un plan"},"id":"1"}'

curl -N -X POST http://127.0.0.1:8080/invoke/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"plan","params":{"steps":["analyze","recommend"]},"id":"2"}'
```

## Variables relevantes (Cloud Run)

- `GOOGLE_CLOUD_PROJECT`: usada para logging/tracing.
- `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`: solo en servicios backend (no directo en NEXUS, que usa RPCs).
- `AGENT_CARD_PATH`: ruta opcional para cargar metadata externa.
