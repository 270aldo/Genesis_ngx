# Contributing / Contribuciones

> **Actualizado**: 2025-12-15 | **Version**: 1.0.0

## Workflow / Flujo de trabajo

1. **Create branch from `main`** (trunk-based development):
   - `feat/<description>` - New features
   - `fix/<description>` - Bug fixes
   - `chore/<description>` - Maintenance tasks
   - `docs/<description>` - Documentation updates

2. **Follow [Conventional Commits](https://www.conventionalcommits.org/):**
   - `feat(logos): add quiz generation tool`
   - `feat(gateway): add rate limiting middleware`
   - `fix(genesis_x): correct intent classification`
   - `docs: update architecture guide`
   - `chore: upgrade dependencies`

3. **Open Pull Request to `main`:**
   - At least 1 approval required
   - Green checks: `lint-test`, `security-scan`
   - Coverage must be ≥80%

4. **Merge via "Squash & Merge"** for clean history

5. **Delete branch** after merge

## Pre-PR Requirements / Requisitos antes de crear PR

```bash
# 1. Linting (agents + gateway)
ruff check agents/ gateway/

# 2. Tests - Agents
pytest agents/ -v --cov=agents --cov-fail-under=80

# 3. Tests - Gateway
pytest gateway/tests/ -v

# 4. Tests - Contract
pytest tests/contract/ -v

# 5. Validate ADK configuration
python -c "import yaml; yaml.safe_load(open('adk.yaml'))"

# 6. Validate migrations (if applicable)
supabase db lint
supabase db push --dry-run
```

- Update documentation (ADR, README, CLAUDE.md) if architecture changes
- Run golden path tests if modifying agent behavior

## Componentes del Proyecto

| Componente | Ubicación | Tests |
|------------|-----------|-------|
| Agentes ADK | `agents/` | `pytest agents/` |
| Gateway FastAPI | `gateway/` | `pytest gateway/tests/` |
| Contract Tests | `tests/contract/` | `pytest tests/contract/` |
| Golden Paths | `tests/golden/` | Incluidos en contract tests |
| Terraform | `terraform/` | `terraform validate` |

## Etiquetas y Issues

- `bug`, `feature`, `chore`, `docs`, `infra` para clasificar.
- Prioridad: `P0` (bloqueante), `P1` (alta), `P2` (media), `P3` (baja).
- Asociar PR a issue (`Closes #ID`).

## Seguridad

- No subir secretos (.env, keys). GitHub Actions tiene acceso a secretos por entorno.
- Rotar credenciales y usar Service Accounts específicos por servicio.
- Verificar que no hay PHI/PII en logs o respuestas.
- Rate limiting: 60 req/min por usuario, 100 req/min por IP.

## Compliance (LFPDPPP)

Cuando trabajes con datos de salud:
- **Tier 1** (peso, pasos, etc.): Solo requiere Privacy Policy
- **Tier 2** (grasa corporal, FC): Requiere consentimiento adicional
- **Tier 3** (glucosa, etc.): Excluido de v1

Ver `docs/compliance/backend-verification.md` para detalles.
