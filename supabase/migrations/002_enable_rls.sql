begin;

alter table public.workouts enable row level security;
alter table public.food_logs enable row level security;
alter table public.water_logs enable row level security;
alter table public.measurements enable row level security;
alter table public.checkins enable row level security;
alter table public.steps enable row level security;

alter table public.workouts force row level security;
alter table public.food_logs force row level security;
alter table public.water_logs force row level security;
alter table public.measurements force row level security;
alter table public.checkins force row level security;
alter table public.steps force row level security;

drop policy if exists "workouts_owner_all" on public.workouts;
drop policy if exists "food_logs_owner_all" on public.food_logs;
drop policy if exists "water_logs_owner_all" on public.water_logs;
drop policy if exists "measurements_owner_all" on public.measurements;
drop policy if exists "checkins_owner_all" on public.checkins;
drop policy if exists "steps_owner_all" on public.steps;

create policy "workouts_owner_all" on public.workouts
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "food_logs_owner_all" on public.food_logs
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "water_logs_owner_all" on public.water_logs
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "measurements_owner_all" on public.measurements
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "checkins_owner_all" on public.checkins
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "steps_owner_all" on public.steps
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

commit;
