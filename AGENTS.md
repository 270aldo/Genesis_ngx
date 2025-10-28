# Repository Guidelines

## Project Structure & Module Organization
- `agents/` contiene los servicios A2A. Usa `agents/nexus/` como referencia para nuevos agentes y coloca utilidades compartidas en `agents/shared/`.
- `supabase/` centraliza el esquema de datos. Todas las migraciones van en `supabase/migrations/`; evita tocar la base en caliente.
- `docs/` guarda especificaciones (por ejemplo `a2a-agent-card.schema.json` y `architecture-october-2025.md`). Usa estos documentos antes de diseñar cambios mayores.
- `ADR/` registra decisiones arquitectónicas. Abre una ADR antes de introducir tecnologías o patrones nuevos.
- `.github/` define la automatización (workflows, templates y CODEOWNERS). Respeta los checks antes de pedir merge.

## Build, Test, and Development Commands
- Crear entorno: ``python -m venv .venv && source .venv/bin/activate`` seguido de `pip install -r agents/nexus/requirements.txt`.
- Ejecutar el orquestador local: ``uvicorn "agents.nexus.main:app" --host 0.0.0.0 --port 8080``.
- Linting: `ruff check agents` (incluye `agents/shared` y cualquier agente nuevo).
- Validar migraciones: `supabase db push --dry-run` antes de subir cambios SQL.

## Coding Style & Naming Conventions
- Python 3.12, tipado opcional pero recomendado (`from __future__ import annotations`).
- Usa `black`/`ruff` estilo por defecto (4 espacios, líneas ≤ 88 caracteres). Clases PascalCase, funciones snake_case.
- Los módulos de agentes deben nombrarse `agents/<dominio>/` y exponer una clase que herede de `A2AServer`.

## Testing Guidelines
- Añade tests asyncio con `pytest` (se configurará en futuras fases). Ubícalos en `agents/<dominio>/tests/`.
- Incluye pruebas contractuales A2A (validación de JSON-RPC y streaming) y RLS (ejecuta funciones RPC con distintos roles).
- Objetivo de cobertura inicial ≥70% en librerías compartidas.

## Commit & Pull Request Guidelines
- Usa Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`.
- Cada PR debe enlazar un issue (`Closes #ID`), pasar `lint-test` y adjuntar resultados relevantes (logs, capturas de Postman si aplica).
- Mantén PRs pequeños (<500 líneas). Añade notas si requieren despliegue coordinado o semillas adicionales.

## Agent Implementation Checklist
- Define `AGENT_CARD` conforme a `docs/a2a-agent-card.schema.json`.
- Implementa `handle_method` y `handle_stream` y registra cada mensaje vía `rpc.agent_append_message`.
- Documenta habilidades y límites en `docs/` o una ADR si cambias responsabilidades de transferencia.
