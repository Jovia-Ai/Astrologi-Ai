-- People/Friends storage for profile-like birth records owned by auth user.
create table if not exists public.people_profiles (
  id uuid primary key default gen_random_uuid(),
  owner_user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  birth_date date not null,
  birth_time time,
  city text not null,
  country text not null,
  timezone text not null default 'Europe/Istanbul',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_people_profiles_owner_created
on public.people_profiles(owner_user_id, created_at desc);

alter table public.people_profiles enable row level security;

drop policy if exists "people_profiles_select_own" on public.people_profiles;
drop policy if exists "people_profiles_insert_own" on public.people_profiles;
drop policy if exists "people_profiles_update_own" on public.people_profiles;
drop policy if exists "people_profiles_delete_own" on public.people_profiles;

create policy "people_profiles_select_own"
on public.people_profiles for select
using (owner_user_id = auth.uid());

create policy "people_profiles_insert_own"
on public.people_profiles for insert
with check (owner_user_id = auth.uid());

create policy "people_profiles_update_own"
on public.people_profiles for update
using (owner_user_id = auth.uid())
with check (owner_user_id = auth.uid());

create policy "people_profiles_delete_own"
on public.people_profiles for delete
using (owner_user_id = auth.uid());

create or replace function public.touch_people_profiles_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_touch_people_profiles_updated_at on public.people_profiles;
create trigger trg_touch_people_profiles_updated_at
before update on public.people_profiles
for each row execute function public.touch_people_profiles_updated_at();
