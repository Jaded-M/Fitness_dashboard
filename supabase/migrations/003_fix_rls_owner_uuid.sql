-- ============================================================
-- Migration 003: Update RLS policies to use auth.uid()
-- so only the authenticated Supabase user can access their data.
-- Run this AFTER setting up Supabase Auth and creating your user.
-- ============================================================

begin;

-- Steps
drop policy if exists "steps_owner_all" on public.steps;
create policy "steps_owner_all" on public.steps
    for all
    using      (auth.uid() = user_id)
    with check (auth.uid() = user_id);

-- Workouts
drop policy if exists "workouts_owner_all" on public.workouts;
create policy "workouts_owner_all" on public.workouts
    for all
    using      (auth.uid() = user_id)
    with check (auth.uid() = user_id);

-- Food logs
drop policy if exists "food_logs_owner_all" on public.food_logs;
create policy "food_logs_owner_all" on public.food_logs
    for all
    using      (auth.uid() = user_id)
    with check (auth.uid() = user_id);

-- Water logs
drop policy if exists "water_logs_owner_all" on public.water_logs;
create policy "water_logs_owner_all" on public.water_logs
    for all
    using      (auth.uid() = user_id)
    with check (auth.uid() = user_id);

-- Measurements
drop policy if exists "measurements_owner_all" on public.measurements;
create policy "measurements_owner_all" on public.measurements
    for all
    using      (auth.uid() = user_id)
    with check (auth.uid() = user_id);

-- Checkins
drop policy if exists "checkins_owner_all" on public.checkins;
create policy "checkins_owner_all" on public.checkins
    for all
    using      (auth.uid() = user_id)
    with check (auth.uid() = user_id);

commit;
