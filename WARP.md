# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Commands

- Environment setup (Python 3.12)
  ```bash path=null start=null
  python -m venv .venv
  source .venv/bin/activate
  python -m pip install -U pip
  pip install -r agents/nexus/requirements.txt
  # Dev tools used in CI/local: ruff, pytest, jsonschema
  pip install -U ruff pytest jsonschema
  ```

- Run NEXUS locally (FastAPI + Uvicorn)
  ```bash path=null start=null
  uvicorn "agents.nexus.main:app" --host 0.0.0.0 --port 8080 --reload
  ```

- Lint (CI mirrors this)
  ```bash path=null start=null
  ruff check agents
  ```

- Tests (pytest). Run all / single test
  ```bash path=null start=null
  pytest -q
  pytest -k <pattern> -q
  ```

- Validate A2A Agent Card schema (Draft-07)
  ```bash path=null start=null
  python - <<'PY'
  import json, jsonschema
  with open('docs/a2a-agent-card.schema.json') as f:
      schema = json.load(f)
  jsonschema.Draft7Validator.check_schema(schema)
  print('OK: a2a-agent-card.schema.json')
  PY
  ```

- Supabase migrations (CLI required)
  ```bash path=null start=null
  supabase db push --dry-run   # validate
  supabase db push             # apply
  ```

- Quick A2A endpoint checks (local)
  ```bash path=null start=null
  curl http://127.0.0.1:8080/card
  curl -X POST http://127.0.0.1:8080/invoke \
    -H "Content-Type: application/json" -H "X-Budget-USD: 0.05" \
    -d '{"jsonrpc":"2.0","method":"classify_intent","params":{"message":"Necesito un plan"},"id":"1"}'
  curl -N -X POST http://127.0.0.1:8080/invoke/stream \
    -H "Content-Type: application/json" -H "Accept: text/event-stream" \
    -d '{"jsonrpc":"2.0","method":"plan","params":{"steps":["analyze","recommend"]},"id":"2"}'
  ```

- Docker (local dev)
  ```bash path=null start=null
  # Build using agents/nexus as context (matches CI)
  docker build -t nexus:dev agents/nexus
  docker run --rm -p 8080:8080 nexus:dev
  ```

- Cloud Run (replicates CI steps; requires gcloud auth/vars)
  ```bash path=null start=null
  gcloud builds submit --tag "$GAR_REGION/genesis-ngx/nexus:$(git rev-parse --short HEAD)" agents/nexus
  gcloud run deploy nexus \
    --image "$GAR_REGION/genesis-ngx/nexus:$(git rev-parse --short HEAD)" \
    --region="$GCP_REGION" --project="$GCP_PROJECT_ID" --platform=managed \
    --allow-unauthenticated=false
  ```

- Terraform (if infra present)
  ```bash path=null start=null
  (cd terraform && terraform fmt -check && terraform init && terraform plan -input=false)
  ```

- Benchmark Gemini (requires Vertex AI SDK/auth)
  ```bash path=null start=null
  pip install -U google-cloud-aiplatform
  python scripts/benchmark_gemini.py
  ```

## Architecture & Structure

- Big picture
  - Multi-agent wellness system on Google Cloud Run.
  - Orchestrator NEXUS (FastAPI) exposes A2A v0.3 (JSON-RPC 2.0 + SSE) and delegates to specialized agents.
  - Supabase (PostgreSQL + Realtime + RLS) is the single source of truth; agents write via RPCs with machine-user roles.
  - Gemini 2.5 models: Pro (orchestration), Flash (conversational), Flash-Lite (light classification), with explicit/implicit caching.

- Key modules (focus areas)
  - `agents/shared/`
    - `a2a_server.py`: Base FastAPI server implementing A2A routes: `/card`, `/negotiate`, `/invoke`, `/invoke/stream`, `/healthz`. Subclass and override `negotiate_capabilities`, `handle_method`, `handle_stream`.
    - `a2a_client.py`: Async client with retries, budget header (`X-Budget-USD`), JSON-RPC payloads, and SSE streaming iterator.
    - `cost_calculator.py`: Gemini and Cloud Run cost helpers (per 1M tokens, vCPU/GiB hour).
    - `security.py`: Basic PII/PHI and prompt-injection checks.
  - `agents/nexus/`
    - `main.py`: Defines `AGENT_CARD` (limits, auth, privacy) and a `NexusAgent` that classifies intents and streams plan steps.
    - `Dockerfile`: Container for Cloud Run (CI builds with Google Cloud Build).
  - `supabase/`: SQL migrations and seeds; use CLI for dry-run/apply.
  - `docs/` and `ADR/`: Architectural blueprint and accepted decisions (protocol, data, security, model selection, Cloud Run vs Agent Engine).

- A2A protocol (ADR-002 distilled)
  - Endpoints: `/card`, `/negotiate`, `/invoke`, `/invoke/stream`, `/healthz`.
  - Conventions: `X-Request-ID` for idempotency, `X-Budget-USD` for cost control; standard JSON-RPC error `data.reason` (e.g., `BUDGET_EXCEEDED`, `VALIDATION_ERROR`).

- CI/CD (GitHub Actions)
  - `lint-test.yml`: installs deps, runs `ruff check`, validates `docs/a2a-agent-card.schema.json`, placeholder for `supabase db push --dry-run`.
  - `deploy-cloud-run.yml`: Cloud Build submit from `agents/nexus` and deploys to Cloud Run using environment-specific variables/secrets.
  - `terraform-plan.yml`: fmt/init/plan for `terraform/`.

- Conventions & contribution highlights
  - Branch strategy: `develop` (CI/dev), `release/v*` (staging), `main` (prod). Conventional Commits; PRs must pass checks.
  - Python style: 4 spaces, ≤88 cols; prefer type hints. Lint with `ruff`. Pytests under `agents/<domain>/tests/`.
  - Agents live under `agents/<dominio>/` and must expose a class inheriting `A2AServer` with an `AGENT_CARD` aligned to `docs/a2a-agent-card.schema.json`.

## Notes

- Local Docker build context matches CI (directory `agents/nexus`). The Dockerfile copies `../shared`; if your Docker tooling forbids parent-path COPY with that context, build in CI or adjust build context/Dockerfile paths accordingly.
- Before opening a PR, run: `ruff check agents`, `pytest` (if tests exist), and `supabase db push --dry-run`; update ADRs/README if architecture changes.
