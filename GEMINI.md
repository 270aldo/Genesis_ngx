# Genesis NGX

## Project Overview

Genesis NGX is a multi-agent wellness system built using Google's Agent Development Kit (ADK), Vertex AI Agent Engine, Gemini 2.5 models, and Supabase. The system features a main orchestrator (GENESIS_X) and 12 specialized agents for fitness, nutrition, behavior, analytics, and women's health. Agents communicate using the A2A (Agent-to-Agent) v0.3 protocol managed natively by Agent Engine.

## Running Locally

```bash
# Setup environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run ADK playground (all agents)
adk web

# Run specific agent
adk run genesis_x
adk run logos
```

## Running Tests

```bash
# All tests
pytest agents/ -v

# With coverage (80% minimum required)
pytest agents/ -v --cov=agents --cov-fail-under=80

# Specific agent
pytest agents/logos/tests/ -v
```

## Database Migrations

```bash
supabase db push --dry-run   # Validate
supabase db push             # Apply
```

## Development Conventions

- **Commits:** Conventional Commits format (`feat:`, `fix:`, `chore:`, etc.)
- **Linting:** `ruff check agents/`
- **Testing:** `pytest` with 80% coverage minimum
- **Branches:** `develop` (integration), `main` (production)
- **PRs:** Require approval and passing CI checks

## Key Documentation

- `CLAUDE.md` - Project context and architecture details
- `docs/AGENTS.md` - Agent implementation guide
- `ADR/` - Architecture Decision Records
- `docs/LEGACY.md` - Deprecated components and migration info
