-- Supabase initial schema for Genesis NGX

create extension if not exists "pgcrypto";
create extension if not exists "vector";

create schema if not exists rpc;

-- Profiles --------------------------------------------------------------

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text,
  date_of_birth date,
  timezone text default 'UTC',
  app_metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists public.conversations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  status text not null default 'active',
  created_at timestamptz default now()
);

create index if not exists idx_conversations_user on public.conversations(user_id, created_at desc);

create table if not exists public.messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references public.conversations(id) on delete cascade,
  role text not null check (role in ('user', 'agent', 'system')),
  agent_type text,
  content text not null,
  tokens_used integer,
  cost_usd numeric(10,6),
  created_at timestamptz default now()
);

create index if not exists idx_messages_conversation on public.messages(conversation_id, created_at desc);

create table if not exists public.agent_events (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id),
  agent_type text not null,
  event_type text not null,
  payload jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);

create index if not exists idx_agent_events_user on public.agent_events(user_id, created_at desc);

create table if not exists public.health_metrics (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  metric_type text not null,
  value numeric not null,
  unit text not null,
  recorded_at timestamptz not null,
  created_at timestamptz default now()
);

create index if not exists idx_health_metrics_user on public.health_metrics(user_id, recorded_at desc);

create table if not exists public.user_context_embeddings (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  content text not null,
  embedding vector(768),
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);

create index if not exists idx_embeddings_user on public.user_context_embeddings(user_id);
create index if not exists idx_embeddings_vector on public.user_context_embeddings using hnsw (embedding vector_cosine_ops);

-- Row Level Security ---------------------------------------------------

alter table public.profiles enable row level security;
alter table public.conversations enable row level security;
alter table public.messages enable row level security;
alter table public.agent_events enable row level security;
alter table public.health_metrics enable row level security;
alter table public.user_context_embeddings enable row level security;

-- Profiles policies
create policy if not exists "Users select own profile" on public.profiles
  for select using (auth.uid() = id);

create policy if not exists "Users update own profile" on public.profiles
  for update using (auth.uid() = id) with check (auth.uid() = id);

-- Conversations policies
create policy if not exists "Users select conversations" on public.conversations
  for select using (auth.uid() = user_id);

create policy if not exists "Users insert conversations" on public.conversations
  for insert with check (auth.uid() = user_id);

-- Messages policies
create policy if not exists "Users read messages" on public.messages
  for select using (
    conversation_id in (
      select id from public.conversations where user_id = auth.uid()
    )
  );

-- Bloqueamos inserciones directas; se realizan vía RPCs
create policy if not exists "Users insert messages" on public.messages
  for insert with check (false);

create policy if not exists "Agents insert messages" on public.messages
  for insert with check (false);

-- Agent events (solo agentes)
create policy if not exists "Agents insert events" on public.agent_events
  for insert with check ((auth.jwt() ->> 'app_metadata')::jsonb ->> 'agent_role' is not null);

create policy if not exists "Users view own events" on public.agent_events
  for select using (user_id = auth.uid());

-- Health metrics
create policy if not exists "Users read health metrics" on public.health_metrics
  for select using (user_id = auth.uid());

create policy if not exists "Users insert health metrics" on public.health_metrics
  for insert with check (user_id = auth.uid());

-- Embeddings
create policy if not exists "Users read embeddings" on public.user_context_embeddings
  for select using (user_id = auth.uid());

create policy if not exists "Users insert embeddings" on public.user_context_embeddings
  for insert with check (user_id = auth.uid());

-- RPCs -----------------------------------------------------------------

set search_path = public, rpc, extensions;

create or replace function rpc.get_agent_role() returns text
  language sql stable as $$ select (auth.jwt() ->> 'app_metadata')::jsonb ->> 'agent_role'; $$;

create or replace function rpc.get_acting_user_id() returns uuid
  language sql stable as $$
    select nullif(auth.jwt() ->> 'acting_user_id', '')::uuid;
  $$;

create or replace function rpc.agent_append_message(
  p_conversation_id uuid,
  p_agent_type text,
  p_content text,
  p_tokens_used integer default null,
  p_cost_usd numeric(10,6) default null
)
returns uuid
language plpgsql
security definer
set search_path = public, rpc, pg_temp
as $$
declare
  v_agent_role text;
  v_acting_user uuid;
  v_owner uuid;
  v_message_id uuid;
begin
  v_agent_role := rpc.get_agent_role();
  if v_agent_role is null then
    raise exception 'Unauthorized: missing agent_role claim';
  end if;

  v_acting_user := rpc.get_acting_user_id();
  if v_acting_user is null then
    raise exception 'Unauthorized: missing acting_user_id claim';
  end if;

  select user_id into v_owner from public.conversations where id = p_conversation_id;
  if v_owner is null then
    raise exception 'Conversation not found';
  end if;

  if v_owner <> v_acting_user then
    raise exception 'Forbidden: acting_user mismatch';
  end if;

  insert into public.messages (
    conversation_id,
    role,
    agent_type,
    content,
    tokens_used,
    cost_usd
  ) values (
    p_conversation_id,
    'agent',
    p_agent_type,
    p_content,
    p_tokens_used,
    p_cost_usd
  ) returning id into v_message_id;

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

  return v_message_id;
end;
$$;

grant execute on function rpc.agent_append_message(uuid, text, text, integer, numeric) to authenticated;

create or replace function rpc.user_append_message(
  p_conversation_id uuid,
  p_content text
)
returns uuid
language plpgsql
security definer
set search_path = public, rpc, pg_temp
as $$
declare
  v_owner uuid;
  v_message_id uuid;
begin
  select user_id into v_owner from public.conversations where id = p_conversation_id;
  if v_owner is null then
    raise exception 'Conversation not found';
  end if;

  if v_owner <> auth.uid() then
    raise exception 'Forbidden';
  end if;

  insert into public.messages (
    conversation_id,
    role,
    content
  ) values (
    p_conversation_id,
    'user',
    p_content
  ) returning id into v_message_id;

  insert into public.agent_events (
    user_id,
    agent_type,
    event_type,
    payload
  ) values (
    v_owner,
    'user',
    'message_appended',
    jsonb_build_object('message_id', v_message_id)
  );

  return v_message_id;
end;
$$;

grant execute on function rpc.user_append_message(uuid, text) to authenticated;

create or replace function rpc.agent_log_event(
  p_user_id uuid,
  p_agent_type text,
  p_event_type text,
  p_payload jsonb default '{}'::jsonb
)
returns uuid
language plpgsql
security definer
set search_path = public, rpc, pg_temp
as $$
declare
  v_agent_role text;
  v_event_id uuid;
begin
  v_agent_role := rpc.get_agent_role();
  if v_agent_role is null then
    raise exception 'Unauthorized';
  end if;

  insert into public.agent_events (
    user_id,
    agent_type,
    event_type,
    payload
  ) values (
    p_user_id,
    p_agent_type,
    p_event_type,
    coalesce(p_payload, '{}'::jsonb)
  ) returning id into v_event_id;

  return v_event_id;
end;
$$;

grant execute on function rpc.agent_log_event(uuid, text, text, jsonb) to authenticated;
