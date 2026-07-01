from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from supabase_client import is_authenticated, logout


ROOT_DIR = Path(__file__).resolve().parents[1]


PAGES = (
    ("Fitness.py", "Command Center", "Readiness, training, and activity"),
    ("pages/1_Nutrition.py", "Nutrition", "Calories, macros, and hydration"),
    ("pages/2_Muscle_Atlas.py", "Muscle Atlas", "Muscle mapping and recovery"),
    ("pages/4_PR_Tracker.py", "PR Tracker", "Records and overload"),
)


def _logo_html() -> str:
    logo_path = ROOT_DIR / "logo.png"
    try:
        logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()
        return (
            '<img src="data:image/png;base64,'
            f'{logo_b64}" class="phi-sidebar-logo" '
            'style="object-fit:cover; border:none; background:transparent; box-shadow:none;">'
        )
    except OSError:
        return '<div class="phi-sidebar-logo">PHI</div>'


def render_sidebar(active_page: str | None = None) -> None:
    """Unified sidebar for every page.
    Hides the native Streamlit nav, shows brand + custom nav + logout.
    """
    st.sidebar.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] {{ display: none !important; }}
        </style>
        <div class="phi-sidebar-brand">
            {_logo_html()}
            <div>
                <div class="phi-sidebar-title">Personal Health Intelligence</div>
                <div class="phi-sidebar-subtitle">Local training command center</div>
            </div>
        </div>
        <div class="phi-sidebar-section">Navigation</div>
        """,
        unsafe_allow_html=True,
    )
    for path, label, caption in PAGES:
        active_class = " active" if (active_page and (active_page == path or active_page == label)) else ""
        st.sidebar.markdown(
            f'<div class="phi-nav-hint{active_class}"><span>{caption}</span></div>',
            unsafe_allow_html=True,
        )
        st.sidebar.page_link(path, label=label)

    if is_authenticated():
        if st.sidebar.button("> Logout", key="sidebar_logout", use_container_width=True):
            logout()
            st.rerun()
