-- Domain tables for Genesis NGX
-- Required by get_user_context() and agent operations
-- PR #2: Supabase Readiness

-- =============================================================================
-- SEASONS
-- Tracks user training/wellness seasons with goals
-- =============================================================================

create table if not exists public.seasons (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  start_date date not null,
  end_date date,
  goal text,
  status text not null default 'active' check (status in ('active', 'completed', 'paused')),
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index if not exists idx_seasons_user_id on public.seasons(user_id);
create index if not exists idx_seasons_status on public.seasons(status) where status = 'active';
create index if not exists idx_seasons_dates on public.seasons(user_id, start_date desc);

-- =============================================================================
-- DAILY_CHECKINS
-- Daily wellness check-ins from users
-- =============================================================================

create table if not exists public.daily_checkins (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  date date not null,
  energy_level integer check (energy_level between 1 and 10),
  sleep_quality integer check (sleep_quality between 1 and 10),
  stress_level integer check (stress_level between 1 and 10),
  mood text check (mood in ('great', 'good', 'neutral', 'bad', 'terrible')),
  soreness_level integer check (soreness_level between 1 and 10),
  motivation_level integer check (motivation_level between 1 and 10),
  notes text,
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  constraint unique_user_date unique (user_id, date)
);

create index if not exists idx_daily_checkins_user_date on public.daily_checkins(user_id, date desc);

-- =============================================================================
-- USER_PREFERENCES
-- Key-value store for user preferences
-- =============================================================================

create table if not exists public.user_preferences (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  preference_key text not null,
  preference_value jsonb not null,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  constraint unique_user_preference unique (user_id, preference_key)
);

create index if not exists idx_user_preferences_user_key on public.user_preferences(user_id, preference_key);

-- =============================================================================
-- ROW LEVEL SECURITY
-- =============================================================================

alter table public.seasons enable row level security;
alter table public.daily_checkins enable row level security;
alter table public.user_preferences enable row level security;

-- Seasons policies
drop policy if exists "Users select own seasons" on public.seasons;
create policy "Users select own seasons" on public.seasons
  for select using (auth.uid() = user_id);

drop policy if exists "Users insert own seasons" on public.seasons;
create policy "Users insert own seasons" on public.seasons
  for insert with check (auth.uid() = user_id);

drop policy if exists "Users update own seasons" on public.seasons;
create policy "Users update own seasons" on public.seasons
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "Users delete own seasons" on public.seasons;
create policy "Users delete own seasons" on public.seasons
  for delete using (auth.uid() = user_id);

-- Service role bypass for agents (using service_role key)
drop policy if exists "Service role full access seasons" on public.seasons;
create policy "Service role full access seasons" on public.seasons
  for all using (auth.jwt() ->> 'role' = 'service_role');

-- Daily checkins policies
drop policy if exists "Users select own checkins" on public.daily_checkins;
create policy "Users select own checkins" on public.daily_checkins
  for select using (auth.uid() = user_id);

drop policy if exists "Users insert own checkins" on public.daily_checkins;
create policy "Users insert own checkins" on public.daily_checkins
  for insert with check (auth.uid() = user_id);

drop policy if exists "Users update own checkins" on public.daily_checkins;
create policy "Users update own checkins" on public.daily_checkins
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "Service role full access checkins" on public.daily_checkins;
create policy "Service role full access checkins" on public.daily_checkins
  for all using (auth.jwt() ->> 'role' = 'service_role');

-- User preferences policies
drop policy if exists "Users select own preferences" on public.user_preferences;
create policy "Users select own preferences" on public.user_preferences
  for select using (auth.uid() = user_id);

drop policy if exists "Users insert own preferences" on public.user_preferences;
create policy "Users insert own preferences" on public.user_preferences
  for insert with check (auth.uid() = user_id);

drop policy if exists "Users update own preferences" on public.user_preferences;
create policy "Users update own preferences" on public.user_preferences
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "Users delete own preferences" on public.user_preferences;
create policy "Users delete own preferences" on public.user_preferences
  for delete using (auth.uid() = user_id);

drop policy if exists "Service role full access preferences" on public.user_preferences;
create policy "Service role full access preferences" on public.user_preferences
  for all using (auth.jwt() ->> 'role' = 'service_role');

-- =============================================================================
-- TRIGGERS FOR updated_at
-- =============================================================================

create or replace function public.update_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists seasons_updated_at on public.seasons;
create trigger seasons_updated_at
  before update on public.seasons
  for each row execute function public.update_updated_at();

drop trigger if exists user_preferences_updated_at on public.user_preferences;
create trigger user_preferences_updated_at
  before update on public.user_preferences
  for each row execute function public.update_updated_at();

-- =============================================================================
-- HELPER RPCs FOR AGENTS
-- =============================================================================

-- Get user context for agents (seasons, recent checkins, preferences)
create or replace function rpc.get_user_context(p_user_id uuid)
returns jsonb
language plpgsql
stable
security definer
set search_path = public, rpc, pg_temp
as $$
declare
  v_context jsonb;
  v_active_season jsonb;
  v_recent_checkins jsonb;
  v_preferences jsonb;
begin
  -- Get active season
  select jsonb_build_object(
    'id', s.id,
    'name', s.name,
    'goal', s.goal,
    'start_date', s.start_date,
    'status', s.status
  ) into v_active_season
  from public.seasons s
  where s.user_id = p_user_id and s.status = 'active'
  order by s.start_date desc
  limit 1;

  -- Get recent checkins (last 7 days)
  select coalesce(jsonb_agg(
    jsonb_build_object(
      'date', c.date,
      'energy_level', c.energy_level,
      'sleep_quality', c.sleep_quality,
      'stress_level', c.stress_level,
      'mood', c.mood,
      'soreness_level', c.soreness_level,
      'motivation_level', c.motivation_level
    ) order by c.date desc
  ), '[]'::jsonb) into v_recent_checkins
  from public.daily_checkins c
  where c.user_id = p_user_id
    and c.date >= current_date - interval '7 days';

  -- Get user preferences
  select coalesce(jsonb_object_agg(
    p.preference_key, p.preference_value
  ), '{}'::jsonb) into v_preferences
  from public.user_preferences p
  where p.user_id = p_user_id;

  -- Build context object
  v_context := jsonb_build_object(
    'user_id', p_user_id,
    'active_season', v_active_season,
    'recent_checkins', v_recent_checkins,
    'preferences', v_preferences,
    'retrieved_at', now()
  );

  return v_context;
end;
$$;

grant execute on function rpc.get_user_context(uuid) to authenticated;

-- Upsert daily checkin
create or replace function rpc.upsert_daily_checkin(
  p_user_id uuid,
  p_date date,
  p_energy_level integer default null,
  p_sleep_quality integer default null,
  p_stress_level integer default null,
  p_mood text default null,
  p_soreness_level integer default null,
  p_motivation_level integer default null,
  p_notes text default null
)
returns uuid
language plpgsql
security definer
set search_path = public, rpc, pg_temp
as $$
declare
  v_checkin_id uuid;
begin
  -- Verify user owns this checkin or is service role
  if auth.uid() != p_user_id and (auth.jwt() ->> 'role') != 'service_role' then
    raise exception 'Forbidden: cannot create checkin for another user';
  end if;

  insert into public.daily_checkins (
    user_id,
    date,
    energy_level,
    sleep_quality,
    stress_level,
    mood,
    soreness_level,
    motivation_level,
    notes
  ) values (
    p_user_id,
    p_date,
    p_energy_level,
    p_sleep_quality,
    p_stress_level,
    p_mood,
    p_soreness_level,
    p_motivation_level,
    p_notes
  )
  on conflict (user_id, date) do update set
    energy_level = coalesce(excluded.energy_level, daily_checkins.energy_level),
    sleep_quality = coalesce(excluded.sleep_quality, daily_checkins.sleep_quality),
    stress_level = coalesce(excluded.stress_level, daily_checkins.stress_level),
    mood = coalesce(excluded.mood, daily_checkins.mood),
    soreness_level = coalesce(excluded.soreness_level, daily_checkins.soreness_level),
    motivation_level = coalesce(excluded.motivation_level, daily_checkins.motivation_level),
    notes = coalesce(excluded.notes, daily_checkins.notes)
  returning id into v_checkin_id;

  return v_checkin_id;
end;
$$;

grant execute on function rpc.upsert_daily_checkin(uuid, date, integer, integer, integer, text, integer, integer, text) to authenticated;
