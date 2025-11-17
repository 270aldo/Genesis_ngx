# Genesis NGX

## Project Overview

This is a multi-agent wellness system named "Genesis NGX". It's built using Google's Agent Development Kit (ADK), Gemini 2.5, and Supabase. The system features a main orchestrator called NEXUS and specialized agents for fitness, nutrition, and mental health. These agents run on Cloud Run and communicate using the A2A (Agent-to-Agent) v0.3 protocol. Supabase serves as the single source of truth for all data.

## Building and Running

The project is written in Python and uses FastAPI. To run the main Nexus agent:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r agents/nexus/requirements.txt
uvicorn "agents.nexus.main:app" --host 0.0.0.0 --port 8080 --reload
```

To apply Supabase database migrations:

```bash
supabase db push
```

## Development Conventions

The project follows the "Conventional Commits" specification for commit messages. All code is linted with `ruff` or `flake8` and tested with `pytest`. Pull requests require at least one approval and must pass all CI checks. For more details, see `docs/git-strategy.md` and `CONTRIBUTING.md`.
