# Arquitectura Octubre 2025 — Genesis NGX

## Visión General
- **Objetivo**: Sistema multi-agente de bienestar con orquestador NEXUS y agentes especializados.
- **Runtime**: Cloud Run (Python 3.12 + FastAPI + ADK) en us-central1.
- **Comunicación**: A2A v0.3 (JSON-RPC 2.0 + SSE) con descubrimiento por Agent Cards.
- **Modelos**: Gemini 2.5 (Pro/Flash/Flash-Lite) con caching implícito/ explícito (90% descuento).
- **Datos**: Supabase (PostgreSQL + Realtime + RLS) como única fuente de verdad.
- **Security**: OIDC entre servicios, RLS, Secret Manager, Cloud Armor.

## Flujo End-to-End
1. **Cliente** (Expo/Next.js) inicia sesión con Supabase Auth → obtiene JWT.
2. Envía mensajes via API Gateway (Cloud Run) → NEXUS (`gemini-2.5-pro`).
3. NEXUS usa A2A para negociar e invocar agentes especializados (Fitness, Nutrición, Salud Mental con `gemini-2.5-flash`).
4. Cada agente consulta Supabase (lectura segura) y opcionalmente Vertex AI Search/pgvector para RAG.
5. Respuestas se transmiten al cliente mediante SSE token-a-token.
6. Al finalizar, se persiste la conversación en Supabase; Supabase Realtime notifica a los clientes.
7. Métricas y eventos se registran en `agent_events` y Cloud Logging.

## Capas
- **Experiencia (Edge)**: Expo SDK 54 (iOS/Android), Next.js en Vercel. SSE para streaming; fallback WebSocket/polling.
- **Orquestación**: NEXUS (Cloud Run) maneja intents, selección de modelo y presupuesto.
- **Agentes Especializados**: Servicios Cloud Run independientes con ADK, exponen endpoints A2A.
- **Procesamiento**: Servicios batch/reportes (Cloud Run Jobs), integraciones externas.
- **Datos**: Supabase (Postgres) con tablas: `profiles`, `conversations`, `messages`, `health_metrics`, `agent_events`, `user_context_embeddings` (pgvector). Realtime para eventos.
- **Observabilidad**: Cloud Trace, Cloud Logging, Cloud Monitoring dashboards, métricas custom (latencia, costos, negotiation failure rate).

## Seguridad y Cumplimiento
- JWT con claims `agent_role`, `acting_user_id`, `session_id` para machine users.
- RLS estricta; agentes insertan vía RPCs SECURITY DEFINER (`rpc.agent_append_message`, `rpc.agent_log_event`).
- Secretos en Secret Manager; acceso via Workload Identity Federation.
- Cloud Armor para rate limiting e IP allowlist; VPC + Serverless VPC Access.
- DLP básico (regex de PII/PHI), filtros de prompt injection; agente "concierge" humano para escalamiento.
- Logs y auditorías retenidos 7 años; mensajes crudos 90 días, resúmenes persistentes.

## Costos (100k usuarios activos/mes)
- Cloud Run (~30% utilización): ≈ $265/mes.
- Gemini 2.5 (caching 50%): ≈ $62/mes.
- Supabase Pro + Storage: $299/mes.
- Memorystore (Redis) para caché de sesiones: $100/mes.
- Total estimado MVP: ~$876/mes.

## Plan de Escalamiento
- Autoscaling Cloud Run (min 1, max 20 por agente); balancing de cargas con etiquetas.
- Caching multi-capa: Redis (sesiones), prompt templates cacheados, delta context.
- Swarm pattern para orquestación paralela (fase 3) con reconciliación determinista.
- Evaluaciones continuas de RAG (recall@k ≥60% documental, ≥70% memoria usuario).

## Próximos Hitos Técnicos
1. Implementar agentes Fitness/Nutrición con A2A y cost control.
2. Integrar Frontend (Expo/Next.js) con SSE + Supabase Realtime.
3. Terraform para infraestructura (Cloud Run, Networking, Secret Manager, Monitoring).
4. CI/CD (GitHub Actions) con despliegue multi-entorno.
5. Dashboards y alertas (latencia, costos, caché, RLS violaciones).
