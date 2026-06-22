-- ============================================================
-- Migration 003: Replace auth.uid() RLS policies with a direct
-- owner UUID check so the app can write using the anon key.
-- ============================================================

begin;

-- Steps
drop policy if exists "steps_owner_all" on public.steps;
create policy "steps_owner_all" on public.steps
    for all
    using      (user_id = 'f1448c24-871d-4a7d-a519-7113c9cbd718')
    with check (user_id = 'f1448c24-871d-4a7d-a519-7113c9cbd718');

-- Workouts
drop policy if exists "workouts_owner_all" on public.workouts;
create policy "workouts_owner_all" on public.workouts
    for all
    using      (user_id = 'f1448c24-871d-4a7d-a519-7113c9cbd718')
    with check (user_id = 'f1448c24-871d-4a7d-a519-7113c9cbd718');

-- Food logs
drop policy if exists "food_logs_owner_all" on public.food_logs;
create policy "food_logs_owner_all" on public.food_logs
    for all
    using      (user_id = 'f1448c24-871d-4a7d-a519-7113c9cbd718')
    with check (user_id = 'f1448c24-871d-4a7d-a519-7113c9cbd718');

-- Water logs
drop policy if exists "water_logs_owner_all" on public.water_logs;
create policy "water_logs_owner_all" on public.water_logs
    for all
    using      (user_id = 'f1448c24-871d-4a7d-a519-7113c9cbd718')
    with check (user_id = 'f1448c24-871d-4a7d-a519-7113c9cbd718');

-- Measurements
drop policy if exists "measurements_owner_all" on public.measurements;
create policy "measurements_owner_all" on public.measurements
    for all
    using      (user_id = 'f1448c24-871d-4a7d-a519-7113c9cbd718')
    with check (user_id = 'f1448c24-871d-4a7d-a519-7113c9cbd718');

-- Checkins
drop policy if exists "checkins_owner_all" on public.checkins;
create policy "checkins_owner_all" on public.checkins
    for all
    using      (user_id = 'f1448c24-871d-4a7d-a519-7113c9cbd718')
    with check (user_id = 'f1448c24-871d-4a7d-a519-7113c9cbd718');

commit;
