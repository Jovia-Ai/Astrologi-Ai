-- AI quota, usage logging, and RevenueCat webhook support.
-- Run in Supabase SQL Editor.

begin;

alter table public.profiles
  add column if not exists free_questions_used integer not null default 0;

create table if not exists public.ai_entitlements (
  user_id uuid primary key references auth.users(id) on delete cascade,
  credits_remaining integer not null default 0 check (credits_remaining >= 0),
  is_pro boolean not null default false,
  pro_until timestamptz,
  updated_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.ai_usage_events (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  model text not null,
  prompt_tokens integer not null default 0 check (prompt_tokens >= 0),
  completion_tokens integer not null default 0 check (completion_tokens >= 0),
  total_tokens integer not null default 0 check (total_tokens >= 0),
  estimated_cost_usd numeric(12, 6) not null default 0,
  source text not null,
  created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.revenuecat_webhook_events (
  event_id text primary key,
  event_type text,
  app_user_id text,
  product_id text,
  payload jsonb not null,
  created_at timestamptz not null default timezone('utc', now()),
  processed_at timestamptz
);

create index if not exists ai_usage_events_user_created_idx
  on public.ai_usage_events(user_id, created_at desc);

create index if not exists revenuecat_webhook_events_app_user_idx
  on public.revenuecat_webhook_events(app_user_id, created_at desc);

create or replace function public.touch_ai_entitlements_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = timezone('utc', now());
  return new;
end;
$$;

drop trigger if exists trg_touch_ai_entitlements_updated_at on public.ai_entitlements;

create trigger trg_touch_ai_entitlements_updated_at
before update on public.ai_entitlements
for each row execute function public.touch_ai_entitlements_updated_at();

create or replace function public.bootstrap_ai_entitlements_for_auth_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.ai_entitlements (user_id)
  values (new.id)
  on conflict (user_id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created_ai_entitlements on auth.users;

create trigger on_auth_user_created_ai_entitlements
after insert on auth.users
for each row execute function public.bootstrap_ai_entitlements_for_auth_user();

insert into public.ai_entitlements (user_id)
select id
from auth.users
on conflict (user_id) do nothing;

create or replace function public.consume_ai_quota(p_user_id uuid)
returns table (
  consumed boolean,
  consumption_type text,
  remaining_free integer,
  credits_remaining integer,
  is_pro boolean
)
language plpgsql
security definer
set search_path = public
as $$
declare
  v_free_used integer := 0;
  v_credits integer := 0;
  v_is_pro boolean := false;
  v_pro_until timestamptz;
begin
  insert into public.ai_entitlements (user_id)
  values (p_user_id)
  on conflict (user_id) do nothing;

  select coalesce(free_questions_used, 0)
  into v_free_used
  from public.profiles
  where id = p_user_id
  for update;

  if not found then
    raise exception 'profile_missing';
  end if;

  select coalesce(credits_remaining, 0), coalesce(is_pro, false), pro_until
  into v_credits, v_is_pro, v_pro_until
  from public.ai_entitlements
  where user_id = p_user_id
  for update;

  v_is_pro := coalesce(v_is_pro, false) and (v_pro_until is null or v_pro_until > timezone('utc', now()));

  if v_is_pro then
    return query
    select true, 'pro', greatest(0, 3 - v_free_used), v_credits, true;
    return;
  end if;

  if v_free_used < 3 then
    update public.profiles
    set free_questions_used = coalesce(free_questions_used, 0) + 1
    where id = p_user_id
    returning coalesce(free_questions_used, 0) into v_free_used;

    return query
    select true, 'free', greatest(0, 3 - v_free_used), v_credits, false;
    return;
  end if;

  if v_credits > 0 then
    update public.ai_entitlements
    set credits_remaining = greatest(credits_remaining - 1, 0)
    where user_id = p_user_id
    returning coalesce(credits_remaining, 0) into v_credits;

    return query
    select true, 'credit', 0, v_credits, false;
    return;
  end if;

  return query
  select false, 'none', 0, v_credits, false;
end;
$$;

alter table public.ai_entitlements enable row level security;
alter table public.ai_usage_events enable row level security;
alter table public.revenuecat_webhook_events enable row level security;

drop policy if exists "ai_entitlements_select_own" on public.ai_entitlements;
drop policy if exists "ai_usage_events_select_own" on public.ai_usage_events;

create policy "ai_entitlements_select_own"
on public.ai_entitlements for select
using (auth.uid() = user_id);

create policy "ai_usage_events_select_own"
on public.ai_usage_events for select
using (auth.uid() = user_id);

commit;
