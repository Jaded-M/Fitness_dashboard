-- Migration: 004_user_settings.sql
-- Stores per-user fitness goal preferences with RLS.

CREATE TABLE IF NOT EXISTS user_settings (
    user_id        UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    calorie_goal   INTEGER NOT NULL DEFAULT 2300,
    step_goal      INTEGER NOT NULL DEFAULT 8000,
    protein_target INTEGER NOT NULL DEFAULT 150,
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Keep updated_at current on every write
CREATE OR REPLACE FUNCTION update_user_settings_timestamp()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_user_settings_updated_at ON user_settings;
CREATE TRIGGER trg_user_settings_updated_at
    BEFORE UPDATE ON user_settings
    FOR EACH ROW EXECUTE FUNCTION update_user_settings_timestamp();

-- Row-level security: each user can only read/write their own row
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users manage own settings" ON user_settings;
CREATE POLICY "Users manage own settings" ON user_settings
    FOR ALL
    USING  (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);
