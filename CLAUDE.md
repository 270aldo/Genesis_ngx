# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Genesis NGX is a multi-agent wellness system using Google's ADK (Agent Development Kit), Gemini 2.5 models, and Supabase as the single source of truth.

**Project Status: v1.0.0 - All 13 agents implemented (1104+ tests, 89% coverage)**

### System Architecture

```
                    ┌─────────────────────────────────┐
                    │          GENESIS_X              │
                    │       (Orchestrator - Pro)      │
                    └───────────────┬─────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
┌───────▼───────┐          ┌────────▼────────┐         ┌───────▼───────┐
│    FITNESS    │          │   NUTRITION     │         │    OTHER      │
│               │          │                 │         │               │
│ BLAZE: Fuerza │          │ SAGE: Strategy  │         │ SPARK: Habits │
│ ATLAS: Movil. │          │ METABOL: TDEE   │         │ STELLA: Data  │
│ TEMPO: Cardio │          │ MACRO: Macros   │         │ LUNA: Women   │
│ WAVE: Recov.  │          │ NOVA: Supps     │         │ LOGOS: Educ.  │
└───────────────┘          └─────────────────┘         └───────────────┘
```

### Key Components

- **GENESIS_X**: Main orchestrator (Gemini 2.5 Pro) - routes requests to specialists
- **LOGOS**: Education specialist (Gemini 2.5 Pro) - explains concepts, debunks myths
- **11 Flash Specialists**: Domain-specific agents using Gemini 2.5 Flash
- **Framework**: Google ADK (Agent Development Kit) with native agent definitions
- **Protocol**: A2A (Agent-to-Agent) v0.3 using JSON-RPC 2.0 over HTTPS with SSE streaming
- **Data**: Supabase PostgreSQL with pgvector for embeddings and RLS for security

## Development Environment Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install ADK CLI
pip install google-adk

# Authenticate with GCP
gcloud auth application-default login

# Run agents in ADK playground
adk web
```

## Running Tests

```bash
# Run all agent tests
pytest agents/ -v

# Run specific agent tests
pytest agents/genesis_x/tests/ -v
pytest agents/blaze/tests/ -v
pytest agents/sage/tests/ -v

# With coverage
pytest --cov=agents --cov-report=html
```

## Database Operations

```bash
# Validate migrations without applying
supabase db push --dry-run

# Apply migrations to Supabase
supabase db push

# Lint SQL files
supabase db lint
```

## Code Quality Commands

```bash
# Linting Python code
ruff check agents/

# Format Python code
ruff format agents/

# Fix linting issues
ruff check --fix agents/
```

## Architecture Key Points

### ADK Agent Pattern

All agents follow the Google ADK pattern:

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

# Entry point for ADK
root_agent = agent
```

### Agent Directory Structure

```
agents/{agent_name}/
├── __init__.py      # Exports: agent, AGENT_CARD, AGENT_CONFIG
├── agent.py         # ADK Agent definition + AGENT_CARD + helper functions
├── prompts.py       # System prompts
├── tools.py         # FunctionTools + domain data/logic
└── tests/
    ├── __init__.py
    ├── test_agent.py
    └── test_tools.py
```

### All Agents (v1.0.0)

| Agent | Domain | Model | Tests | Tools |
|-------|--------|-------|-------|-------|
| **GENESIS_X** | Orchestration | gemini-2.5-pro | 39 | classify_intent, invoke_specialist |
| **BLAZE** | Strength/Hypertrophy | gemini-2.5-flash | 58 | generate_workout, calculate_1rm, suggest_progression |
| **ATLAS** | Mobility/Flexibility | gemini-2.5-flash | 58 | assess_mobility, generate_routine, suggest_for_workout |
| **TEMPO** | Cardio/Endurance | gemini-2.5-flash | 72 | calculate_zones, generate_session, analyze_performance |
| **WAVE** | Recovery | gemini-2.5-flash | 65 | assess_recovery, generate_protocol, analyze_sleep |
| **SAGE** | Nutrition Strategy | gemini-2.5-flash | 54 | analyze_diet, generate_plan, suggest_adjustments |
| **METABOL** | Metabolism/TDEE | gemini-2.5-flash | 86 | calculate_tdee, analyze_adaptation, suggest_adjustments |
| **MACRO** | Macronutrients | gemini-2.5-flash | 131 | calculate_macros, optimize_protein, cycle_carbs |
| **NOVA** | Supplementation | gemini-2.5-flash | 115 | evaluate_supplement, create_stack, check_interactions |
| **SPARK** | Behavior/Habits | gemini-2.5-flash | 132 | assess_readiness, design_habit, analyze_barriers |
| **STELLA** | Analytics | gemini-2.5-flash | 95 | generate_report, analyze_trends, create_dashboard |
| **LUNA** | Women's Health | gemini-2.5-flash | 120 | track_cycle, adapt_training, analyze_patterns |
| **LOGOS** | Education | gemini-2.5-pro | 140 | explain_concept, present_evidence, debunk_myth, create_deep_dive, generate_quiz |

### Model Tiers

| Tier | Model | Agents | Latency | Cost/Invoke |
|------|-------|--------|---------|-------------|
| **Pro** | gemini-2.5-pro | GENESIS_X, LOGOS | ≤6000ms | ≤$0.05 |
| **Flash** | gemini-2.5-flash | 11 specialists | ≤2000ms | ≤$0.01 |

### LOGOS - Special Case (Pro Model)

LOGOS is the **only specialist using Pro model** due to:
- Complex reasoning for educational content
- Adaptive explanations (3 user levels)
- Evidence evaluation and myth debunking
- Deep-dive and quiz generation

```python
# LOGOS configuration
logos = Agent(
    name="logos",
    model="gemini-2.5-pro",  # Pro for complex reasoning
    tools=[explain_concept, present_evidence, debunk_myth, create_deep_dive, generate_quiz],
    output_key="logos_response",
)
```

Expanded databases: 33 concepts, 15 myths, 14 evidences across 7 domains (fitness, nutrition, behavior, recovery, womens_health, mobility, analytics)

### Database Security Pattern

The database uses **Row Level Security (RLS)** with a specific pattern:

- **Direct writes to tables are BLOCKED** via RLS policies (`WITH CHECK (false)`)
- **All agent writes** must go through RPCs in the `rpc` schema (e.g., `rpc.agent_append_message`)
- **RPCs are SECURITY DEFINER** functions that validate `agent_role` from JWT claims

Example:
```python
# Agents call RPCs to write data
result = supabase.rpc('agent_append_message', {
    'p_conversation_id': conv_id,
    'p_agent_type': 'genesis_x',
    'p_content': 'response text',
    'p_tokens_used': 150,
    'p_cost_usd': 0.0045
}).execute()
```

### Cost Tracking

The `CostCalculator` class in `agents/shared/cost_calculator.py` provides Gemini pricing:

- **Gemini 2.5 Pro**: $1.25/M input tokens, $10/M output (≤200K context)
- **Gemini 2.5 Flash**: $0.30/M input, $2.50/M output
- **Context caching discount**: 90% off cached tokens

### Creating New Agents

1. **Create directory structure**:
   ```
   agents/new_agent/
   ├── __init__.py
   ├── agent.py
   ├── prompts.py
   ├── tools.py
   └── tests/
   ```

2. **Define agent in agent.py**:
   ```python
   from google.adk import Agent
   from .prompts import SYSTEM_PROMPT
   from .tools import ALL_TOOLS

   new_agent = Agent(
       name="new_agent",
       model="gemini-2.5-flash",
       description="Agent description",
       instruction=SYSTEM_PROMPT,
       tools=ALL_TOOLS,
       output_key="new_agent_response",
   )

   root_agent = new_agent
   ```

3. **Add to adk.yaml**:
   ```yaml
   agents:
     new_agent:
       path: "agents/new_agent"
       entry_point: "agent:new_agent"
       model: "gemini-2.5-flash"
   ```

4. **Update GENESIS_X routing** in `agents/genesis_x/tools.py`

## Git Workflow

- **Branch naming**: `feat/<description>`, `fix/<description>`, `chore/<description>`
- **Commits**: Use Conventional Commits format: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`
- **Pull requests**: Must pass `lint-test` checks, get approval
- **Merge strategy**: Squash & Merge for clean history

## Important Constraints

### Security
- **Never bypass RLS**: Always use RPCs to write data
- **Sanitize inputs**: Use `agents.shared.security.SecurityValidator` for PHI/PII and prompt injection
- **Scope is wellness**: This is NOT a medical device; reject any PHI

### Performance Targets (SLOs)
- **Latency p95**: ≤2.0s for Flash models, ≤6.0s for Pro
- **Availability**: ≥99.5%
- **Cost per invoke**: ≤$0.01 for Flash agents, ≤$0.05 for GENESIS_X (Pro)

### A2A Protocol Rules
- **Always propagate `X-Request-ID`** for distributed tracing
- **Respect budgets**: Check `X-Budget-USD` header and reject if insufficient
- **Use standard error codes**: `-32000` (AGENT_UNAVAILABLE), `-32001` (BUDGET_EXCEEDED), etc.

## Database Schema Reference

Key tables:
- `profiles`: User profiles (references `auth.users`)
- `conversations`: Chat sessions with `user_id` and `status`
- `messages`: Individual messages with `conversation_id`, `role`, `agent_type`, `cost_usd`
- `agent_events`: Audit log with `user_id`, `agent_type`, `event_type`, `payload`
- `health_metrics`: User health data with `metric_type`, `value`, `unit`
- `user_context_embeddings`: Vector embeddings (768-dim) with HNSW index

All tables have RLS enabled. Users read their own data via `auth.uid()`. Agents write via RPCs.

## ADR Reference

Before making architectural changes, consult existing ADRs in `ADR/`:
- **001**: Cloud Run architecture (SUPERSEDED by ADR-007)
- **002**: A2A v0.3 protocol implementation (JSON-RPC + SSE)
- **003**: Supabase-only architecture (no Firestore)
- **004**: Gemini model selection strategy (Pro/Flash/Flash-Lite criteria)
- **005**: Security and compliance (wellness scope, no PHI in MVP)
- **006**: Decision not to use ADK Visual Builder
- **007**: Migration to ADK/Agent Engine (CURRENT)

## Testing Strategy

**Current Status: 1104+ tests, 89% coverage**

Target: ≥80% coverage for agent code.

Test locations: `agents/<agent_name>/tests/`

```bash
# Run all tests
pytest agents/ -v

# Run specific agent tests
pytest agents/logos/tests/ -v
pytest agents/genesis_x/tests/ -v

# With coverage report
pytest --cov=agents --cov-report=html
```

Key test types:
- **Unit tests**: Test individual tools and functions
- **Agent tests**: Test agent configuration, AGENT_CARD, and AGENT_CONFIG
- **Database tests**: Test data integrity and coverage across domains
- **Integration tests**: Test Supabase connectivity and cross-agent communication

Use `pytest` with asyncio support for testing async code.

## Quick Reference

### Running the System

```bash
# Local development with ADK playground
adk web

# Run specific agent
adk run logos
adk run genesis_x

# Deploy to staging/production
adk deploy --env staging
adk deploy --env production
```

### Adding New Content to LOGOS

To add concepts, myths, or evidence to LOGOS databases:

1. Edit `agents/logos/tools.py`
2. Add to appropriate database (CONCEPTS_DATABASE, MYTHS_DATABASE, EVIDENCE_DATABASE)
3. Run tests: `pytest agents/logos/tests/ -v`
4. Ensure cross-domain coverage is maintained
