# GEMINI.md - Gemini LLM Quick Reference

This file provides guidance for Gemini-based AI tools when working with this repository.

## Project Overview

Genesis NGX is a multi-agent wellness system using:

- **Google ADK** (Agent Development Kit) for agent definitions
- **Vertex AI Agent Engine** as the production runtime
- **Gemini 2.5** models for AI capabilities
- **Supabase** PostgreSQL as the data layer

## Model Configuration

### Model Tiers

| Tier | Model | Use Case | Agents | Latency | Cost/Invoke |
|------|-------|----------|--------|---------|-------------|
| **Pro** | gemini-2.5-pro | Complex reasoning, orchestration | GENESIS_X, LOGOS | ≤6s | ≤$0.05 |
| **Flash** | gemini-2.5-flash | Fast responses, specialists | 11 specialists | ≤2s | ≤$0.01 |

### Agent Breakdown

**Pro Agents (2):**
- `genesis_x`: Main orchestrator - intent classification, specialist routing
- `logos`: Education specialist - explanations, evidence, quizzes

**Flash Agents (11):**
- `blaze`: Strength training
- `atlas`: Mobility & flexibility
- `tempo`: Cardio & endurance
- `wave`: Recovery
- `sage`: Nutrition strategy
- `metabol`: Metabolism & TDEE
- `macro`: Macronutrients
- `nova`: Supplements
- `spark`: Habits & behavior
- `stella`: Analytics
- `luna`: Women's health

## Running the Project

### Local Development

```bash
# Setup environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run ADK playground
adk web
```

### Running Tests

```bash
# All tests
pytest agents/ -v

# With coverage (80% minimum)
pytest agents/ -v --cov=agents --cov-fail-under=80
```

### Linting

```bash
ruff check agents/
```

## Development Workflow

1. Create agent directory: `agents/<agent_name>/`
2. Define agent in `agent.py` using ADK pattern
3. Implement tools in `tools.py`
4. Write system prompt in `prompts.py`
5. Add tests in `tests/`
6. Register in `adk.yaml`
7. Update `GENESIS_X` routing if needed

## Key Configuration

Agent configuration is in `adk.yaml`:

```yaml
agents:
  genesis_x:
    model: "gemini-2.5-pro"
    max_latency_ms: 6000
    max_cost_usd: 0.05

  logos:
    model: "gemini-2.5-pro"
    max_latency_ms: 6000
    max_cost_usd: 0.05

  blaze:
    model: "gemini-2.5-flash"
    max_latency_ms: 2000
    max_cost_usd: 0.01
  # ... 10 more flash agents
```

## Conventions

- **Commits:** Conventional Commits (`feat:`, `fix:`, `docs:`)
- **Linting:** ruff (Python)
- **Testing:** pytest with 80% coverage requirement
- **Documentation:** See `docs/INDEX.md` for full documentation index

## References

- [CLAUDE.md](CLAUDE.md) - Comprehensive project context
- [docs/INDEX.md](docs/INDEX.md) - Documentation index
- [ADR-004](ADR/004-gemini-model-selection.md) - Model selection strategy
- [ADR-007](ADR/ADR-007-agent-engine-migration.md) - Agent Engine migration
