# ADR-003: Arquitectura Solo Supabase (PostgreSQL + Realtime)

Status: Accepted
Date: 2025-10-28

## Contexto
- Requerimos una fuente de verdad única para usuarios, métricas y conversaciones.
- Opciones previas: Supabase (PostgreSQL) + Firestore (realtime) con replicación.
- Riesgo identificado: dual-write y consistencia eventual entre bases.

## Decisión
Utilizar únicamente Supabase (PostgreSQL + Realtime + RLS) como capa de datos para el MVP. Firestore queda como posible caché realtime en fases posteriores si la experiencia lo exige.

## Justificación
- **Integridad ACID**: PostgreSQL asegura consistencia fuerte para conversaciones, métricas y auditoría.
- **RLS**: Supabase provee row-level security, imprescindible para separar accesos de agentes.
- **Realtime suficiente**: Supabase Realtime (logical replication) entrega notificaciones sub-segundo, suficiente para chat y dashboards.
- **Simplicidad operativa**: Evitamos pipelines de replicación y manejo de fallos inter-bases.
- **Offline**: Implementaremos caché local (SQLite) en el cliente móvil con sincronización delta hacia Supabase.

## Consecuencias
- El streaming token-a-token se envía desde Cloud Run vía SSE; al finalizar, persistimos en Supabase y dejamos que Realtime distribuya el evento final.
- Implementamos RPCs SECURITY DEFINER para agentes con machine users.
- Debemos diseñar índices apropiados y monitoreo de crecimiento (vacuum/retención).
- Firestore se reevalúa post-MVP sólo si la UX demanda presencia/typing ultra-baja latencia.

## Retención y Gobernanza
- Mensajes crudos: 90 días (configurable); resúmenes persistentes para memoria a largo plazo.
- Logs (`agent_events`): 7 años (preparado para cumplimiento futuro HIPAA).
- Backups automáticos diarios (Supabase Pro) + exportaciones programadas a Cloud Storage.

## Referencias
- Supabase RLS y Realtime docs.
- Recomendaciones Postgres para multi-tenant con RLS.
