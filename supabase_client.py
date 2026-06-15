import os

from supabase import create_client

try:
    import streamlit as st
except ModuleNotFoundError:
    st = None


def _load_supabase_settings() -> tuple[str | None, str | None, str | None]:
    """Prefer Streamlit secrets when available, otherwise fall back to env vars."""
    if st is not None:
        try:
            supabase = st.secrets["supabase"]
            return (
                supabase.get("url"),
                supabase.get("key") or supabase.get("anon_key"),
                supabase.get("owner_id") or supabase.get("user_id"),
            )
        except Exception:
            pass
    return (
        os.environ.get("SUPABASE_URL"),
        os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_ANON_KEY"),
        os.environ.get("PHI_OWNER_USER_ID"),
    )


def _create_supabase_client():
    url, key, _ = _load_supabase_settings()
    if not url or not key:
        message = "Supabase URL or key not found in Streamlit secrets or environment variables."
        if st is not None:
            st.error(message)
            st.stop()
        raise RuntimeError(message)
    return create_client(url, key)


if st is not None:
    @st.cache_resource
    def get_supabase_client():
        return _create_supabase_client()
else:
    def get_supabase_client():
        return _create_supabase_client()


supabase_client = get_supabase_client()
OWNER_USER_ID = _load_supabase_settings()[2]
