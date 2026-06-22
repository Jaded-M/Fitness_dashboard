from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from components.design_system import apply_platform_theme, page_header
from components.sidebar import render_sidebar_shell
from supabase_client import is_authenticated


SIM_DIR = ROOT_DIR / "assets" / "biomechanics_sim"
SIM_HEIGHT_PX = 1080


st.set_page_config(
    page_title="Biomechanics Simulator",
    page_icon="PHI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if not is_authenticated():
    st.switch_page("pages/0_Login.py")

apply_platform_theme()
render_sidebar_shell("pages/3_Biomechanics_Sim.py")


def load_simulator_html() -> str:
    """Inline the sim bundle so Streamlit can render it inside one component."""
    index_html = (SIM_DIR / "index.html").read_text(encoding="utf-8")
    css = (SIM_DIR / "style.css").read_text(encoding="utf-8")
    physics_js = (SIM_DIR / "physics.js").read_text(encoding="utf-8")
    simulation_js = (SIM_DIR / "simulation.js").read_text(encoding="utf-8")
    app_js = (SIM_DIR / "app.js").read_text(encoding="utf-8")

    # Streamlit components run inside an iframe. Relative <link> and <script>
    # paths would point at Streamlit's server, not this repo, so we inline the
    # web bundle here. The order matters: app.js depends on the two engine files.
    html = index_html.replace(
        '<link rel="stylesheet" href="style.css">',
        f"<style>{css}</style>",
    )
    html = html.replace(
        '<script src="physics.js"></script>',
        f"<script>{physics_js}</script>",
    )
    html = html.replace(
        '<script src="simulation.js"></script>',
        f"<script>{simulation_js}</script>",
    )
    html = html.replace(
        '<script src="app.js"></script>',
        f"<script>{app_js}</script>",
    )
    return html


st.markdown("""
    <style>
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    iframe {
        border: none;
        height: 100vh !important;
    }
    </style>
""", unsafe_allow_html=True)

# We use the full height of the viewport minus a tiny bit for safety
components.html(
    load_simulator_html(),
    height=1200,
    scrolling=False,
)
