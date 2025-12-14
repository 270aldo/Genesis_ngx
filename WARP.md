# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Commands

- Environment setup (Python 3.12)
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  python -m pip install -U pip
  pip install -r requirements.txt
  # Dev tools used in CI/local: ruff, pytest
  pip install -U ruff pytest
  ```

- Run agents locally (ADK Playground)
  ```bash
  # Interactive playground with all agents
  adk web

  # Run specific agent
  adk run genesis_x
  adk run blaze
  adk run logos
  ```

- Lint (CI mirrors this)
  ```bash
  ruff check agents/
  ```

- Tests (pytest with coverage)
  ```bash
  # Run all agent tests
  pytest agents/ -v

  # Run with coverage (CI requires 80%)
  pytest agents/ -v --cov=agents --cov-fail-under=80

  # Single agent tests
  pytest agents/genesis_x/tests/ -v
  pytest agents/blaze/tests/ -v
  ```

- Validate A2A Agent Card schema (Draft-07)
  ```bash
  python - <<'PY'
  import json, jsonschema
  with open('docs/a2a-agent-card.schema.json') as f:
      schema = json.load(f)
  jsonschema.Draft7Validator.check_schema(schema)
  print('OK: a2a-agent-card.schema.json')
  PY
  ```

- Supabase migrations (CLI required)
  ```bash
  supabase db push --dry-run   # validate
  supabase db push             # apply
  ```

- Deploy to Vertex AI Agent Engine
  ```bash
  # Staging deployment
  adk deploy agent_engine --env staging --project ngx-genesis-prod

  # Production deployment
  adk deploy agent_engine --env production --project ngx-genesis-prod
  ```

- Terraform (infrastructure)
  ```bash
  (cd terraform && terraform fmt -check && terraform init && terraform plan -input=false)
  ```

## Architecture & Structure

- Big picture
  - Multi-agent wellness system on **Vertex AI Agent Engine**.
  - Orchestrator **GENESIS_X** (Gemini 2.5 Pro) routes to specialized agents via A2A protocol.
  - **13 agents**: 1 orchestrator + 1 education specialist (Pro) + 11 domain specialists (Flash).
  - Supabase (PostgreSQL + Realtime + RLS) is the single source of truth; agents write via RPCs.
  - Agent Engine manages sessions (Memory Bank) automatically - no manual session storage.

- Key modules (focus areas)
  - `agents/<agent_name>/`
    - `agent.py`: ADK Agent definition with `root_agent` export, AGENT_CARD, tools.
    - `prompts.py`: System prompts for the agent.
    - `tools.py`: FunctionTools and domain logic.
    - `tests/`: Unit and integration tests.
  - `agents/shared/`
    - `cost_calculator.py`: Gemini pricing helpers (Pro/Flash/Flash-Lite).
    - `security.py`: PII/PHI and prompt-injection validation.
    - `supabase_client.py`: Supabase connection wrapper.
  - `legacy/` (DEPRECATED)
    - `a2a_server.py`: Old FastAPI A2A server (replaced by Agent Engine).
    - `a2a_client.py`: Old httpx A2A client (replaced by Agent Engine).
  - `supabase/`: SQL migrations and seeds; use CLI for dry-run/apply.
  - `docs/` and `ADR/`: Architectural blueprint and accepted decisions.

- A2A protocol (ADR-002)
  - Agent Engine handles A2A natively via `adk deploy`.
  - Conventions: `X-Request-ID` for tracing, `X-Budget-USD` for cost control.
  - Standard JSON-RPC error codes for agent communication.

- CI/CD (GitHub Actions)
  - `lint-test.yml`: Installs deps, runs `ruff check`, pytest with coverage (80% minimum), validates A2A schema.
  - `terraform-plan.yml`: fmt/init/plan for `terraform/`.
  - Deployment: `adk deploy agent_engine` (staging on develop, production on main).

- Conventions & contribution highlights
  - Branch strategy: `develop` (CI/dev), `release/v*` (staging), `main` (prod). Conventional Commits; PRs must pass checks.
  - Python style: 4 spaces, <=88 cols; prefer type hints. Lint with `ruff`.
  - Tests under `agents/<agent>/tests/`. Target: 80% coverage minimum.
  - Agents follow ADK pattern with `root_agent` export and AGENT_CARD constant.

## Notes

- **Agent Engine is the production runtime** - no manual Cloud Run deployment.
- Before opening a PR, run: `ruff check agents/`, `pytest agents/ --cov=agents --cov-fail-under=80`, and `supabase db push --dry-run`.
- Update ADRs/README if architecture changes.
- See `docs/LEGACY.md` for deprecated components and migration timeline.
