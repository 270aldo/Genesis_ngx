# Contribuciones

## Flujo de trabajo

1. **Crear rama** desde `develop` (o `main` si se usa trunk):
   - `feature/<ticket>-descripcion`
   - `fix/<ticket>-bug`
   - `hotfix/<ticket>-critico`
2. Mantener commits con [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat: agrega agente de nutrición`
   - `fix: corrige RLS para mensajes`
3. Abrir Pull Request hacia la rama objetivo:
   - Al menos 1 aprobación.
   - Checks verdes (`lint-test`, `supabase-migrate --dry-run`).
4. Merge mediante “Squash & Merge” (historial limpio) o “Merge commit” según política definida.
5. Borrar la rama después del merge.

## Requisitos antes de crear PR

- `ruff check` o `flake8` para linting.
- `pytest` (si aplica) y `scripts/benchmark_gemini.py` en modo reducido si afecta prompts.
- Validar migraciones: `supabase db lint` y `supabase db push --dry-run`.
- Actualizar documentación (ADR, README) si la decisión cambia.

## Etiquetas y Issues

- `bug`, `feature`, `chore`, `docs`, `infra` para clasificar.
- Prioridad: `P0` (bloqueante), `P1` (alta), `P2` (media), `P3` (baja).
- Asociar PR a issue (`Closes #ID`).

## Seguridad

- No subir secretos (.env, keys). GitHub Actions tiene acceso a secretos por entorno.
- Rotar credenciales y usar Service Accounts específicos por servicio.
