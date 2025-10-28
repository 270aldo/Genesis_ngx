# Genesis NGX

Sistema multi-agente de bienestar (wellness) construido con el ADK de Google, Gemini 2.5 y Supabase como fuente única de verdad. El orquestador NEXUS y los agentes especializados se ejecutan en Cloud Run exponiendo el protocolo A2A v0.3.

## Estructura

- `ADR/`: Architecture Decision Records.
- `agents/`: código de agentes (compartidos + servicios específicos).
- `docs/`: documentación técnica y esquemas.
- `supabase/`: migraciones SQL y datos seed.
- `scripts/`: utilidades de benchmarking.

## Arranque Rápido

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r agents/nexus/requirements.txt
uvicorn "agents.nexus.main:app" --host 0.0.0.0 --port 8080 --reload
```

## Migraciones Supabase

```bash
supabase db push
```

## Estrategia Git / GitHub

Consulta `docs/git-strategy.md` y `CONTRIBUTING.md` para el flujo de trabajo, naming de ramas y políticas de PR.
