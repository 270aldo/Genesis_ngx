# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Genesis NGX is a multi-agent wellness system using Google's ADK (Agent Development Kit), Gemini 2.5 models, and Supabase as the single source of truth. The system features:

- **NEXUS**: Main orchestrator agent that routes requests to specialized agents
- **Specialized Agents**: Fitness, Nutrition, Mental Health, Recovery, Longevity (to be implemented)
- **Protocol**: A2A (Agent-to-Agent) v0.3 using JSON-RPC 2.0 over HTTPS with SSE streaming
- **Runtime**: Cloud Run (Python 3.12 + FastAPI) in us-central1
- **Data**: Supabase PostgreSQL with pgvector for embeddings and RLS for security

## Development Environment Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (currently only NEXUS has requirements.txt)
pip install -r agents/nexus/requirements.txt

# Run NEXUS orchestrator locally
uvicorn "agents.nexus.main:app" --host 0.0.0.0 --port 8080 --reload
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
ruff check agents

# Format Python code (when ruff is configured)
ruff format agents

# Alternative linting
flake8 agents
```

## Architecture Key Points

### A2A Protocol Implementation

All agents inherit from `A2AServer` (in `agents/shared/a2a_server.py`) and must:

1. Define an `AGENT_CARD` dictionary conforming to `docs/a2a-agent-card.schema.json` with:
   - `capabilities`: list of what the agent can do
   - `limits`: `max_input_tokens`, `max_output_tokens`, `max_latency_ms`, `max_cost_per_invoke`
   - `privacy`: `pii`, `phi`, `data_retention_days`
   - `auth`: authentication method and audience

2. Implement two core methods:
   - `async def handle_method(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]` for synchronous requests
   - `async def handle_stream(self, method: str, params: Dict[str, Any]) -> AsyncGenerator[str, None]` for streaming responses

3. Expose standard A2A endpoints automatically:
   - `GET /card` - Returns agent metadata
   - `POST /negotiate` - Capability negotiation
   - `POST /invoke` - Synchronous JSON-RPC call
   - `POST /invoke/stream` - SSE streaming call

### Database Security Pattern

The database uses **Row Level Security (RLS)** with a specific pattern:

- **Direct writes to tables are BLOCKED** via RLS policies (`WITH CHECK (false)`)
- **All agent writes** must go through RPCs in the `rpc` schema (e.g., `rpc.agent_append_message`)
- **RPCs are SECURITY DEFINER** functions that validate `agent_role` from JWT claims
- **Agents are "machine users"** in Supabase Auth with `app_metadata.agent_role` set to their role (e.g., `nexus`, `agent_fitness`)

Example flow:
```python
# Agents call RPCs to write data
result = await supabase.rpc('agent_append_message', {
    'p_conversation_id': conv_id,
    'p_agent_type': 'nexus',
    'p_content': 'response text',
    'p_tokens_used': 150,
    'p_cost_usd': 0.0045
})
```

The RPC internally:
1. Validates the caller has an `agent_role` claim
2. Verifies ownership/authorization
3. Writes to the table (bypassing RLS because it's SECURITY DEFINER)
4. Logs to `agent_events` for audit trail

### Cost Tracking

The `CostCalculator` class in `agents/shared/cost_calculator.py` provides real pricing formulas (October 2025):

- **Cloud Run**: $0.0864/vCPU-hour, $0.009/GiB-hour
- **Gemini 2.5 Pro**: $1.25/M input tokens, $10/M output (≤200K context)
- **Gemini 2.5 Flash**: $0.30/M input, $2.50/M output
- **Gemini 2.5 Flash-Lite**: $0.10/M input, $0.40/M output
- **Context caching discount**: 90% off cached tokens (use `input_cached` rates)

Agents should check budget before expensive operations:
```python
from agents.shared.cost_calculator import CostCalculator

calc = CostCalculator()
estimated_cost = calc.calculate_gemini_cost(
    model='flash',
    input_tokens=500,
    output_tokens=200,
    cached_tokens=0  # Adjust based on cache hit
)

if estimated_cost > budget:
    raise A2ABudgetExceededError("Insufficient budget")
```

### Agent Communication Pattern

When NEXUS needs to invoke another agent:

```python
from agents.shared.a2a_client import A2AClient

# Initialize client
client = A2AClient(base_url="http://fitness-agent:8080")

# Get agent capabilities
card = await client.get_card()

# Negotiate if needed
negotiation = await client.negotiate(
    capabilities=["workout_planning"],
    budget_usd=0.01
)

# Invoke method
result = await client.invoke(
    method="create_workout_plan",
    params={"user_id": "...", "goal": "strength"},
    request_id="unique-id",
    budget_usd=0.01
)

# Or stream responses
async for chunk in client.invoke_stream(method="stream_plan", params={...}):
    print(chunk)
```

## Creating New Agents

When implementing a new specialized agent (e.g., Fitness, Nutrition):

1. **Create directory structure**:
   ```
   agents/fitness/
   ├── __init__.py
   ├── main.py
   ├── Dockerfile
   ├── requirements.txt
   └── README.md
   ```

2. **Define AGENT_CARD** following `docs/a2a-agent-card.schema.json`

3. **Inherit from A2AServer**:
   ```python
   from agents.shared.a2a_server import A2AServer

   class FitnessAgent(A2AServer):
       def __init__(self):
           super().__init__(AGENT_CARD)

       async def handle_method(self, method: str, params: dict):
           if method == "create_workout":
               # Implementation
               return {"workout": {...}}
   ```

4. **Use shared libraries**:
   - `agents.shared.cost_calculator` for cost estimation
   - `agents.shared.security` for input sanitization
   - `agents.shared.a2a_client` to call other agents

5. **Document in ADR** if the agent introduces new patterns or responsibilities

## Git Workflow

- **Branch naming**: `feature/<ticket>-description`, `fix/<ticket>-bug`, `hotfix/<ticket>-critical`
- **Commits**: Use Conventional Commits format: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`
- **Pull requests**: Must link to issue (`Closes #ID`), pass `lint-test` checks, get 1 approval
- **Merge strategy**: Squash & Merge for clean history

## Important Constraints

### Security
- **Never bypass RLS**: Always use `rpc.agent_append_message` and similar RPCs to write data
- **Sanitize inputs**: Use `agents.shared.security.SecurityValidator` to check for PHI/PII and prompt injection
- **Scope is wellness**: This is NOT a medical device; reject any PHI (diagnoses, medications, prescriptions)

### Performance Targets (SLOs from ADR-001)
- **Latency p95**: ≤2.0s for Flash models, ≤6.0s for Pro
- **Availability**: ≥99.5%
- **Cost per invoke**: ≤$0.01 for Flash agents, ≤$0.05 for NEXUS (Pro)

### A2A Protocol Rules (from ADR-002)
- **Always propagate `X-Request-ID`** for distributed tracing
- **Respect budgets**: Check `X-Budget-USD` header and reject if insufficient
- **Implement retries**: 3 attempts with exponential backoff for transient errors
- **Use standard error codes**: `-32000` (AGENT_UNAVAILABLE), `-32001` (BUDGET_EXCEEDED), `-32002` (TIMEOUT), etc.

## Module Import Convention

When running agents, use the fully qualified module path to ensure `agents.shared` imports work:

```bash
# Correct - full module path
uvicorn "agents.nexus.main:app" --host 0.0.0.0 --port 8080

# Incorrect - relative path causes import errors
cd agents/nexus && uvicorn "main:app"
```

## Database Schema Reference

Key tables:
- `profiles`: User profiles (references `auth.users`)
- `conversations`: Chat sessions with `user_id` and `status`
- `messages`: Individual messages with `conversation_id`, `role` (user/agent/system), `agent_type`, `cost_usd`
- `agent_events`: Audit log with `user_id`, `agent_type`, `event_type`, `payload`
- `health_metrics`: User health data with `metric_type`, `value`, `unit`
- `user_context_embeddings`: Vector embeddings (768-dim) with HNSW index for similarity search

All tables have RLS enabled. Users read their own data via `auth.uid()`. Agents write via RPCs.

## ADR Reference

Before making architectural changes, consult existing ADRs in `ADR/`:
- **001**: Why Cloud Run over Agent Engine (cost, flexibility, maturity)
- **002**: A2A v0.3 protocol implementation (JSON-RPC + SSE)
- **003**: Supabase-only architecture (no Firestore to avoid dual-write complexity)
- **004**: Gemini model selection strategy (Pro/Flash/Flash-Lite criteria)
- **005**: Security and compliance (wellness scope, no PHI in MVP)

Open a new ADR when introducing new technologies, patterns, or significant architectural decisions.

## Testing Strategy

Target: ≥70% coverage for shared libraries.

Test locations: `agents/<domain>/tests/`

Key test types:
- **Contractual tests**: Validate A2A JSON-RPC requests/responses against schema
- **RLS tests**: Execute RPCs with different roles to verify security boundaries
- **Integration tests**: End-to-end flows from client → NEXUS → specialized agent → database

Use `pytest` with asyncio support for testing async code.
