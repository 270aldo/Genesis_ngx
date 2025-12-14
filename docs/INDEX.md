# Genesis NGX - Documentation Index

> Multi-agent wellness system using Google ADK, Vertex AI Agent Engine, and Supabase.

## Quick Start

| Document | Description |
|----------|-------------|
| [README.md](../README.md) | Project overview and quick setup |
| [local-development-setup.md](local-development-setup.md) | Detailed development environment setup |

## Architecture

| Document | Description |
|----------|-------------|
| [CLAUDE.md](../CLAUDE.md) | Comprehensive project context (AI assistant guide) |
| [AGENTS.md](../AGENTS.md) | Agent implementation guide for all 13 agents |
| [ARCHITECTURE_GUIDE_ADK_A2A.md](ARCHITECTURE_GUIDE_ADK_A2A.md) | Reference architecture for ADK + A2A + GCP |

## Architecture Decision Records (ADR)

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-007](../ADR/ADR-007-agent-engine-migration.md) | Agent Engine Migration | **CURRENT** |
| [ADR-006](../ADR/006-no-visual-builder.md) | No Visual Builder | Accepted |
| [ADR-005](../ADR/005-security-compliance.md) | Security & Compliance | Accepted |
| [ADR-004](../ADR/004-gemini-model-selection.md) | Gemini Model Selection | Accepted |
| [ADR-003](../ADR/003-supabase-only-architecture.md) | Supabase Only Architecture | Accepted |
| [ADR-002](../ADR/002-a2a-v03-protocol.md) | A2A v0.3 Protocol | Accepted |

## Workflows & Contribution

| Document | Description |
|----------|-------------|
| [gitflow-strategy.md](gitflow-strategy.md) | Git branching and release process |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | Contribution guidelines |

## Requirements

| Document | Description |
|----------|-------------|
| [GENESIS_PRD.md](../GENESIS_PRD.md) | Product Requirements Document |

## Quick References

| Document | Description |
|----------|-------------|
| [WARP.md](../WARP.md) | Terminal commands quick reference |
| [GEMINI.md](../GEMINI.md) | Gemini LLM integration guide |

## Archive

| Location | Description |
|----------|-------------|
| [docs/archive/](archive/) | Historical and research materials |

---

## Project Statistics

- **Agents:** 13 (2 Pro, 11 Flash)
- **Tests:** 1104+
- **Coverage:** 89%
- **Framework:** Google ADK + Vertex AI Agent Engine

## Getting Help

```bash
# Local development
adk web

# Run tests
pytest agents/ -v

# Linting
ruff check agents/
```
