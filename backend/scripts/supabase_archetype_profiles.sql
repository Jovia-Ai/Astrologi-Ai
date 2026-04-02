-- Supabase setup for persisted archetype profiles.
-- Run in Supabase SQL Editor.

begin;

create extension if not exists pgcrypto;

create table if not exists public.archetype_profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  birth_data_hash text not null,
  answers_hash text null,
  raw_answers jsonb not null default '[]'::jsonb,
  test_scores jsonb not null default '{}'::jsonb,
  context_scores jsonb not null default '{}'::jsonb,
  chart_prior jsonb not null default '{}'::jsonb,
  final_profile jsonb not null default '{}'::jsonb,
  engine_version text not null,
  taxonomy_version text not null,
  fusion_version text not null,
  question_bank_version text null,
  input_mode text not null default 'chart_only',
  computed_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create index if not exists archetype_profiles_birth_hash_idx
  on public.archetype_profiles (birth_data_hash);

alter table public.archetype_profiles enable row level security;

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

commit;
