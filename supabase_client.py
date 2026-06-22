import os
from supabase import create_client

try:
    import streamlit as st
except ModuleNotFoundError:
    st = None


def _load_supabase_settings():
    """Prefer Streamlit secrets when available, otherwise fall back to env vars."""
    if st is not None:
        try:
            supabase = st.secrets["supabase"]
            return (
                supabase.get("url"),
                supabase.get("key") or supabase.get("anon_key"),
            )
        except Exception:
            pass
    return (
        os.environ.get("SUPABASE_URL"),
        os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_ANON_KEY"),
    )


def get_supabase_client():
    """Create a Supabase client with the current user's auth session if available."""
    url, key = _load_supabase_settings()
    if not url or not key:
        if st is not None:
            st.error("Supabase URL or key not found in Streamlit secrets or environment variables.")
            st.stop()
        raise RuntimeError("Supabase URL or key not found.")
    client = create_client(url, key)
    if st is not None and "auth_session" in st.session_state:
        session = st.session_state["auth_session"]
        client.auth.set_session(session.access_token, session.refresh_token)
    return client


def get_current_user_id() -> str | None:
    """Return the authenticated user's UUID, or None if not logged in."""
    if st is not None and "auth_session" in st.session_state:
        session = st.session_state["auth_session"]
        if session.user:
            return session.user.id
    return None


def is_authenticated() -> bool:
    return st is not None and "auth_session" in st.session_state


def authenticate(email: str, password: str) -> bool:
    """Log in with email and password. Stores the session on success."""
    try:
        url, key = _load_supabase_settings()
        if not url or not key:
            st.error("Supabase not configured.")
            return False
        client = create_client(url, key)
        result = client.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state["auth_session"] = result.session
        return True
    except Exception as exc:
        st.error(f"Login failed: {exc}")
        return False


def logout():
    if "auth_session" in st.session_state:
        del st.session_state["auth_session"]
