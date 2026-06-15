# Supabase mobile ownership migration

Apply the migration in this order:

1. Run `migrations/001_add_user_ownership.sql` in the Supabase SQL editor.
2. Create the owner account in Supabase Auth and copy its user UUID.
3. Set `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and `PHI_OWNER_USER_ID`.
4. Run `python scripts/backfill_supabase_user.py`.
5. Confirm every table has a non-null `user_id`.
6. Run `migrations/002_enable_rls.sql`.

Never expose the service-role key to the Flutter app or commit it to this repository.
