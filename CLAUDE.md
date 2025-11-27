# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Genesis NGX is a multi-agent wellness system using Google's ADK (Agent Development Kit), Gemini 2.5 models, and Supabase as the single source of truth. The system features:

- **GENESIS_X**: Main orchestrator agent (Gemini 2.5 Pro) that routes requests to specialized agents
- **Specialized Agents**: BLAZE (strength), SAGE (nutrition), ATLAS (mobility), TEMPO (cardio), WAVE (recovery), and more
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

### Current Agents

| Agent | Domain | Model | Status |
|-------|--------|-------|--------|
| GENESIS_X | Orchestration | gemini-2.5-pro | Implemented |
| BLAZE | Strength/Hypertrophy | gemini-2.5-flash | Implemented |
| SAGE | Nutrition Strategy | gemini-2.5-flash | Implemented |
| ATLAS | Mobility/Flexibility | gemini-2.5-flash | Planned |
| TEMPO | Cardio/Endurance | gemini-2.5-flash | Planned |
| WAVE | Recovery | gemini-2.5-flash | Planned |

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

Target: ≥80% coverage for agent code.

Test locations: `agents/<agent_name>/tests/`

Key test types:
- **Unit tests**: Test individual tools and functions
- **Agent tests**: Test agent configuration and AGENT_CARD
- **Integration tests**: Test Supabase connectivity and cross-agent communication

Use `pytest` with asyncio support for testing async code.
