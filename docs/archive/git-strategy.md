# Estrategia Git / GitHub

## Ramas

- `main`: producción (solo merges desde release/hotfix con tags).
- `develop`: integración continua (deploy automático a entorno `dev`).
- `feature/<ticket>`: desarrollo de nuevas funcionalidades (merge → `develop`).
- `hotfix/<ticket>`: arreglos urgentes en producción (merge → `main` y `develop`).
- `release/vX.Y.Z`: estabilización previa al lanzamiento, QA sobre staging.

## Convenciones

- Commits: [Conventional Commits](https://www.conventionalcommits.org/).
- Tags: `vX.Y.Z` firmados; changelog actualizado por release.
- Pull requests: plantilla obligatoria (`.github/pull_request_template.md`), checklist de pruebas.

## Entornos

| Rama      | Entorno | Despliegue |
|-----------|---------|------------|
| `develop` | dev     | Automático en merge (GitHub Actions) |
| `release` | staging | Manual tras aprobación QA |
| `main`    | prod    | Automático tras tag / release |

## CI/CD

- `lint-test.yml`: lint, tests, validación de migraciones y JSON Schema. Corre en PR.
- `deploy-cloud-run.yml`: build container y despliegue a Cloud Run (dev/staging/prod según rama/tag).
- `terraform-plan.yml`: plan en PR infra; apply solo en merge a `main` (con aprobación).

## Protecciones

- Branch protection en `main` y `develop`: revisiones obligatorias, checks verdes, prohibir pushes directos.
- CODEOWNERS para áreas críticas (p. ej. `supabase/`, `agents/`).
- Dependabot semanal y escaneo de secretos (`gitleaks` o GitHub Advanced Security).

## Releases

1. Crear rama `release/vX.Y.Z` desde `develop`.
2. Ajustar versión y changelog.
3. QA en staging → aprobación.
4. Merge en `main` (tag `vX.Y.Z`) y `develop` (fast-forward o merge para mantener historial).
5. Deploy automático a producción.
