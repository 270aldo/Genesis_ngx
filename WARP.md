# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Quick Reference

### Development Commands

```bash
# Environment setup (Python 3.12)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install google-adk

# ADK Playground (local development)
adk web

# Run specific agent
adk run genesis_x
adk run logos
adk run blaze
```

### Testing

```bash
# All tests
pytest agents/ -v

# Specific agent tests
pytest agents/logos/tests/ -v
pytest agents/genesis_x/tests/ -v

# With coverage (CI requirement: 80%)
pytest agents/ -v --cov=agents --cov-fail-under=80
```

### Linting

```bash
# Check code style
ruff check agents/

# Auto-fix issues
ruff check --fix agents/

# Format code
ruff format agents/
```

### Deployment

```bash
# Deploy to staging
adk deploy --env staging --project ngx-genesis-staging --region us-central1

# Deploy to production (requires approval)
adk deploy --env production --project ngx-genesis-prod --region us-central1

# List deployed agents
adk list --project <PROJECT_ID> --region us-central1
```

### Database

```bash
# Supabase migrations
supabase db push --dry-run   # Validate
supabase db push             # Apply
supabase db lint             # Check SQL
```

## Project Structure

```
genesis_ngx/
├── agents/
│   ├── genesis_x/    # Orchestrator (Gemini 2.5 Pro)
│   ├── logos/        # Education specialist (Gemini 2.5 Pro)
│   ├── blaze/        # Strength training (Flash)
│   ├── atlas/        # Mobility (Flash)
│   ├── tempo/        # Cardio (Flash)
│   ├── wave/         # Recovery (Flash)
│   ├── sage/         # Nutrition strategy (Flash)
│   ├── metabol/      # Metabolism/TDEE (Flash)
│   ├── macro/        # Macronutrients (Flash)
│   ├── nova/         # Supplements (Flash)
│   ├── spark/        # Habits/behavior (Flash)
│   ├── stella/       # Analytics (Flash)
│   ├── luna/         # Women's health (Flash)
│   └── shared/       # Common utilities
├── supabase/         # Database migrations
├── docs/             # Documentation
├── ADR/              # Architecture decisions
├── adk.yaml          # Agent configuration
└── CLAUDE.md         # AI assistant context
```

## Key Files

| File | Purpose |
|------|---------|
| `adk.yaml` | Agent Engine configuration |
| `CLAUDE.md` | Comprehensive project context |
| `agents/<name>/agent.py` | ADK Agent definition |
| `agents/<name>/tools.py` | Agent tools (FunctionTool) |
| `agents/<name>/prompts.py` | System prompts |
| `agents/shared/agent_engine_registry.py` | Inter-agent communication |

## Architecture

- **Framework:** Google ADK (Agent Development Kit)
- **Runtime:** Vertex AI Agent Engine
- **Models:** Gemini 2.5 Pro (orchestration), Flash (specialists)
- **Database:** Supabase PostgreSQL with RLS
- **Protocol:** A2A v0.3 (JSON-RPC 2.0 + SSE)

## Agent Pattern

All agents follow the ADK pattern:

```python
from google.adk import Agent
from google.adk.tools import FunctionTool

agent = Agent(
    name="agent_name",
    model="gemini-2.5-flash",
    description="Agent description",
    instruction=SYSTEM_PROMPT,
    tools=[tool1, tool2],
    output_key="agent_response",
)

root_agent = agent  # Entry point for ADK
```

## CI/CD Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `lint-test.yml` | PR/push | Linting + tests (80% coverage) |
| `security-scan.yml` | PR/push/weekly | Dependency + code security |
| `deploy-staging.yml` | push to develop | Auto-deploy to staging |
| `deploy-production.yml` | push to main | Deploy with approval |

## Conventions

- **Commits:** Conventional Commits (`feat:`, `fix:`, `docs:`, etc.)
- **Branch:** Trunk-based (main), feature branches
- **Code:** Python 3.12+, type hints, ruff linting
- **Tests:** pytest, 80% coverage minimum

## Before Opening a PR

```bash
# 1. Lint
ruff check agents/

# 2. Test
pytest agents/ -v --cov=agents --cov-fail-under=80

# 3. Validate ADK config
python -c "import yaml; yaml.safe_load(open('adk.yaml'))"
```

## References

- [ADK Documentation](https://google.github.io/adk-docs/)
- [docs/INDEX.md](docs/INDEX.md) - Documentation index
- [CLAUDE.md](CLAUDE.md) - Detailed project context
