# ADR-005: Seguridad y Cumplimiento (MVP Wellness)

Status: Accepted
Date: 2025-10-28

## Contexto
- Aplicación de bienestar con datos personales sensibles (peso, hábitos, estado emocional).
- MVP declarado como wellness (sin PHI ni diagnosticar); debemos prepararnos para un futuro con cumplimiento regulatorio.

## Decisión
- Autenticación usuarios vía Supabase Auth (JWT, Magic Link, OAuth).
- Agentes como "machine users" con `agent_role` en `app_metadata`; operaciones privilegiadas a través de RPCs SECURITY DEFINER.
- Red: Cloud Run en VPC privada, Cloud Armor delante del load balancer, HTTPS obligatorio.
- Secrets: Google Secret Manager con rotación trimestral (mínimo) y uso de Workload Identity Federation entre servicios.
- DLP básico: sanitización de entradas (detección de PII/PHI) y filtros de prompt injection.
- Auditoría: tabla `agent_events` + Cloud Logging + export a BigQuery/Storage.

## Controles MVP
- RLS: políticas por `user_id` (usuarios) y `agent_role` (agentes).
- JWT claims: `agent_role`, `acting_user_id`, `session_id` para trazabilidad.
- Rate limiting: Nginx/Cloud Armor para usuarios; circuit breakers internos para agentes.
- Observabilidad: Cloud Trace + métricas custom (latencia, costo, intents críticos).
- Retención: mensajes 90 días, resúmenes persistentes; logs 7 años.

## Camino a HIPAA
- Clasificar datos por sensibilidad; aislar potencial PHI en tablas dedicadas con cifrado por columna (pgcrypto/KMS).
- Firmar BAA con proveedores (GCP, Supabase) antes de almacenar PHI.
- Añadir monitoreo de acceso, reportes y borrados automáticos según SLA.

## Riesgos
- Uso indebido de claves "service_role" podría saltarse RLS (mitigado usando RPCs dedicadas y guardando la llave solo en backend).
- Prompt injection o filtración de instrucciones internas: se requieren sanitizadores y limitación de memoria compartida.
- Datos emocionales sensibles: definir disclaimers y flujo de escalamiento humano ante riesgo (p. ej. autolesión).

## Referencias
- Supabase Security & RLS.
- Google Cloud Security Foundations.
