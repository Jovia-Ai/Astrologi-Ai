-- Optional DB-side bootstrap: create profile + astro_settings rows
-- automatically when a new auth.users row is created.
-- Run in Supabase SQL editor.

begin;

create or replace function public.handle_new_auth_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, email, full_name)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data->>'full_name', split_part(coalesce(new.email, ''), '@', 1))
  )
  on conflict (id) do update
  set email = excluded.email;

  insert into public.astro_settings (user_id, house_system, zodiac_type)
  values (new.id, 'placidus', 'tropical')
  on conflict (user_id) do nothing;

  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;

create trigger on_auth_user_created
after insert on auth.users
for each row execute function public.handle_new_auth_user();

commit;
