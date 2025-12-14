# Contributing / Contribuciones

## Workflow / Flujo de trabajo

1. **Create branch from `main`** (trunk-based development):
   - `feature/<description>` - New features
   - `fix/<description>` - Bug fixes
   - `chore/<description>` - Maintenance tasks
   - `docs/<description>` - Documentation updates

2. **Follow [Conventional Commits](https://www.conventionalcommits.org/):**
   - `feat(logos): add quiz generation tool`
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
# 1. Linting
ruff check agents/

# 2. Tests with coverage
pytest agents/ -v --cov=agents --cov-fail-under=80

# 3. Validate ADK configuration
python -c "import yaml; yaml.safe_load(open('adk.yaml'))"

# 4. Validate migrations (if applicable)
supabase db lint
supabase db push --dry-run
```

- Update documentation (ADR, README, CLAUDE.md) if architecture changes

## Etiquetas y Issues

- `bug`, `feature`, `chore`, `docs`, `infra` para clasificar.
- Prioridad: `P0` (bloqueante), `P1` (alta), `P2` (media), `P3` (baja).
- Asociar PR a issue (`Closes #ID`).

## Seguridad

- No subir secretos (.env, keys). GitHub Actions tiene acceso a secretos por entorno.
- Rotar credenciales y usar Service Accounts específicos por servicio.
