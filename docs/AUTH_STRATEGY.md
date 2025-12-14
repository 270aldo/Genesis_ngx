# Estrategia de Autenticacion para Agentes

## Decision (MVP)

Los agentes de Genesis NGX utilizan **service_role** para operaciones server-side.

## Justificacion

1. **Velocidad de implementacion** - Desbloquea desarrollo sin complejidad de JWT minting
2. **Simplicidad** - Una sola estrategia, documentada, sin ambiguedad
3. **Seguridad suficiente para MVP** - Con logging y rotacion de secrets

## Implementacion

### Agentes (Server-Side)

Los agentes utilizan el `service_client` del `SupabaseClient`:

```python
from agents.shared.supabase_client import get_supabase_client

client = get_supabase_client()

# Usar service_client para operaciones de agente (bypass RLS)
result = client.service_client.rpc(
    "agent_log_event",
    {
        "p_user_id": str(user_id),
        "p_agent_type": "genesis_x",
        "p_event_type": "intent_classified",
        "p_payload": {"intent": "fitness"}
    }
).execute()
```

**Caracteristicas:**
- Usa `SUPABASE_SERVICE_ROLE_KEY` configurada en env
- Bypass de RLS (Row Level Security)
- Todas las operaciones se loggean en `agent_events`
- Secret rotation cada 90 dias

### Usuarios (Client-Side)

Los usuarios usan tokens JWT estandar de Supabase Auth:

```python
# Configurar sesion de usuario
client.set_auth_session(access_token, refresh_token)

# Operaciones con RLS activo
conversations = await client.get_user_conversations(user_id, auth_token=token)
```

**Caracteristicas:**
- RLS activo con `auth.uid()`
- Tokens JWT estandar de Supabase Auth
- Acceso solo a datos propios

## Flujo de Datos

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Usuario   │───>│   Gateway    │───>│   Agente    │
│  (JWT Auth) │    │  (Valida)    │    │ (service_   │
│             │<───│              │<───│   role)     │
└─────────────┘    └──────────────┘    └─────────────┘
       │                                      │
       │ RLS activo                           │ Bypass RLS
       ▼                                      ▼
┌─────────────────────────────────────────────────────┐
│                    SUPABASE                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ profiles │  │ messages │  │ agent_events     │  │
│  │ (RLS)    │  │ (RLS+RPC)│  │ (audit log)      │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Controles de Seguridad

### 1. Logging Obligatorio

Toda operacion de agente genera un evento en `agent_events`:

```sql
-- Ejemplo de log automatico en agent_append_message RPC
insert into public.agent_events (
  user_id,
  agent_type,
  event_type,
  payload
) values (
  v_owner,
  p_agent_type,
  'message_appended',
  jsonb_build_object(
    'message_id', v_message_id,
    'tokens_used', p_tokens_used,
    'cost_usd', p_cost_usd
  )
);
```

### 2. Secret Rotation

- `SUPABASE_SERVICE_ROLE_KEY` se rota cada 90 dias
- Almacenado en GCP Secret Manager
- Versionado para rollback si es necesario

### 3. Least Privilege

Agentes solo acceden a tablas necesarias:
- `messages` (via RPC)
- `agent_events` (via RPC)
- `conversations` (read via service_client)
- `seasons`, `daily_checkins`, `user_preferences` (read via service_client)

### 4. Audit Trail

Cada operacion incluye:
- `user_id`: Usuario afectado
- `agent_type`: Agente que ejecuto
- `event_type`: Tipo de operacion
- `payload`: Detalles (sin PII)
- `created_at`: Timestamp

## Tablas y RLS

### Politicas de Usuario (RLS Activo)

```sql
-- Usuarios ven solo sus datos
create policy "Users select own data" on public.table_name
  for select using (auth.uid() = user_id);
```

### Politicas de Service Role

```sql
-- service_role tiene acceso completo (agentes)
create policy "Service role full access" on public.table_name
  for all using (auth.jwt() ->> 'role' = 'service_role');
```

## Hardening Futuro (Post-MVP)

Si el riesgo lo justifica:

1. **JWT de corta vida** "acting-on-behalf-of user"
   - Mint JWT con claims especificos por agente
   - TTL de 5 minutos
   - Refresh automatico

2. **Claims especificos por agente**
   ```json
   {
     "agent_role": "genesis_x",
     "acting_user_id": "uuid",
     "permissions": ["read:conversations", "write:messages"],
     "exp": 1702500000
   }
   ```

3. **Rate limiting por usuario**
   - Max requests por minuto por usuario
   - Alertas en anomalias

## Fecha de Decision

13 Diciembre 2025

## Revision Programada

Q1 2026 (evaluar si migrar a JWT minting)

## Referencias

- ADR-007: Migration to ADK/Agent Engine
- [Supabase RLS Docs](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [Supabase Service Role](https://supabase.com/docs/guides/api/api-keys#service-role-key)
