-- Supabase RLS setup for profiles, birth_data, astro_settings, archetype_profiles.
-- Run in Supabase SQL Editor.

begin;

-- 1) profiles.user_id -> uuid (safe guard: fail early if non-uuid rows exist)
do $$
begin
  if exists (
    select 1
    from public.profiles
    where user_id is not null
      and user_id::text !~* '^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
  ) then
    raise exception 'profiles.user_id has non-uuid values. Clean data or truncate before type change.';
  end if;
end $$;

alter table public.profiles
  alter column user_id type uuid using user_id::uuid;

-- 2) Enable RLS
alter table public.profiles enable row level security;
alter table public.birth_data enable row level security;
alter table public.astro_settings enable row level security;
alter table if exists public.archetype_profiles enable row level security;

-- 3) Replace policies (idempotent)
drop policy if exists "profiles_select_own" on public.profiles;
drop policy if exists "profiles_upsert_own" on public.profiles;
drop policy if exists "profiles_update_own" on public.profiles;

create policy "profiles_select_own"
on public.profiles for select
using (auth.uid() = user_id);

create policy "profiles_upsert_own"
on public.profiles for insert
with check (auth.uid() = user_id);

create policy "profiles_update_own"
on public.profiles for update
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists "birth_data_select_own" on public.birth_data;
drop policy if exists "birth_data_upsert_own" on public.birth_data;
drop policy if exists "birth_data_update_own" on public.birth_data;

create policy "birth_data_select_own"
on public.birth_data for select
using (auth.uid()::text = user_id::text);

create policy "birth_data_upsert_own"
on public.birth_data for insert
with check (auth.uid()::text = user_id::text);

create policy "birth_data_update_own"
on public.birth_data for update
using (auth.uid()::text = user_id::text)
with check (auth.uid()::text = user_id::text);

drop policy if exists "astro_settings_select_own" on public.astro_settings;
drop policy if exists "astro_settings_upsert_own" on public.astro_settings;
drop policy if exists "astro_settings_update_own" on public.astro_settings;

create policy "astro_settings_select_own"
on public.astro_settings for select
using (auth.uid()::text = user_id::text);

create policy "astro_settings_upsert_own"
on public.astro_settings for insert
with check (auth.uid()::text = user_id::text);

create policy "astro_settings_update_own"
on public.astro_settings for update
using (auth.uid()::text = user_id::text)
with check (auth.uid()::text = user_id::text);

do $$
begin
  if exists (
    select 1
    from information_schema.tables
    where table_schema = 'public'
      and table_name = 'archetype_profiles'
  ) then
    drop policy if exists "archetype_profiles_select_own" on public.archetype_profiles;
    drop policy if exists "archetype_profiles_insert_own" on public.archetype_profiles;
    drop policy if exists "archetype_profiles_update_own" on public.archetype_profiles;

    create policy "archetype_profiles_select_own"
    on public.archetype_profiles for select
    using (auth.uid() = user_id);

    create policy "archetype_profiles_insert_own"
    on public.archetype_profiles for insert
    with check (auth.uid() = user_id);

    create policy "archetype_profiles_update_own"
    on public.archetype_profiles for update
    using (auth.uid() = user_id)
    with check (auth.uid() = user_id);
  end if;
end $$;

commit;
