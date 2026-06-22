from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[1]


PAGES = (
    ("Fitness.py", "Command Center", "Readiness, training, and activity"),
    ("pages/1_Nutrition.py", "Nutrition", "Calories, macros, and hydration"),
    ("pages/2_Muscle_Atlas.py", "Muscle Atlas", "Muscle mapping and recovery"),
    ("pages/3_Biomechanics_Sim.py", "Biomechanics Sim", "Posture and joint-load lab"),
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


def render_sidebar_shell(active_page: str | None = None) -> None:
    """Render the shared PHI sidebar shell used by every dashboard page."""
    st.sidebar.markdown(
        f"""
        <div class="phi-sidebar-brand">
            {_logo_html()}
            <div>
                <div class="phi-sidebar-title">Personal Health Intelligence</div>
                <div class="phi-sidebar-subtitle">Local training command center</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown('<div class="phi-sidebar-section">Navigation</div>', unsafe_allow_html=True)
    for path, label, caption in PAGES:
        selected_class = " active" if active_page == path or active_page == label else ""
        st.sidebar.markdown(
            f'<div class="phi-nav-hint{selected_class}"><span>{caption}</span></div>',
            unsafe_allow_html=True,
        )
        st.sidebar.page_link(path, label=label)

    st.sidebar.markdown(
        """
        <div class="phi-sidebar-footer">
            PHI / Streamlit OS<br>
            <span>Same navigation, every module.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
