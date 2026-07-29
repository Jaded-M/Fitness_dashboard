from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from components.design_system import apply_platform_theme, page_header
from components.sidebar import render_sidebar
from supabase_client import is_authenticated


SIM_DIR = ROOT_DIR / "assets" / "biomechanics_sim"
SIM_HEIGHT_PX = 900


st.set_page_config(
    page_title="Biomechanics Simulator",
    page_icon="PHI",
    layout="wide",
    initial_sidebar_state="expanded",
)

if not is_authenticated():
    st.switch_page("pages/0_Login.py")

apply_platform_theme()
render_sidebar(active_page="pages/_3_Biomechanics_Sim.py")


def load_simulator_html() -> str:
    """Inline the sim bundle so Streamlit can render it inside one component."""
    index_html = (SIM_DIR / "index.html").read_text(encoding="utf-8")
    css = (SIM_DIR / "style.css").read_text(encoding="utf-8")
    physics_js = (SIM_DIR / "physics.js").read_text(encoding="utf-8")
    simulation_js = (SIM_DIR / "simulation.js").read_text(encoding="utf-8")
    app_js = (SIM_DIR / "app.js").read_text(encoding="utf-8")
    app_js = app_js.replace("showPage('page-overview');", "showPage('page-biomech');")
    phi_override = """
    :root {
      --bg-base:#070a10; --bg-panel:rgba(8,13,23,.94); --bg-card:rgba(12,18,31,.92);
      --bg-input:rgba(50,216,255,.06); --border:rgba(50,216,255,.18); --border-soft:rgba(50,216,255,.10);
      --primary:#32d8ff; --accent:#b56cff; --success:#40f2a0; --warning:#ffd166; --danger:#ff5c8a;
      --muted:#9aa7b8; --text-main:#f6fbff; --text-sub:#9aa7b8; --text-dim:rgba(154,167,184,.56);
      --radius:6px; --radius-sm:4px; --font:'Inter',system-ui,sans-serif; --font-display:'Space Grotesk',Inter,sans-serif;
    }
    html, body { background:#070a10; }
    body {
      background:
        linear-gradient(rgba(50,216,255,.035) 1px, transparent 1px),
        linear-gradient(180deg,#0b0f1a 0%,#070a10 100%);
      background-size:100% 28px,100% 100%;
    }
    .sidebar, .topbar { display:none !important; }
    .content { width:100vw; min-width:0; }
    .page { height:100vh; }
    .page.active { display:flex; }
    .bio-layout {
      height:100vh;
      grid-template-columns:minmax(220px,250px) minmax(420px,1fr) minmax(230px,270px);
      border:1px solid rgba(50,216,255,.16);
      background:rgba(7,10,16,.94);
    }
    .ctrl-panel, .tel-panel, .canvas-toolbar {
      background:rgba(8,13,23,.96);
      backdrop-filter:none;
      -webkit-backdrop-filter:none;
    }
    .canvas-panel { background:rgba(5,8,14,.72); }
    .ctrl-section, .tel-section {
      border:1px solid rgba(50,216,255,.10);
      background:rgba(12,18,31,.58);
      border-radius:6px;
      padding:10px;
    }
    .ctrl-section h3, .tel-section h3 {
      color:#32d8ff;
      font-family:'JetBrains Mono',monospace;
      letter-spacing:.08em;
    }
    .btn-preset, .btn-toggle, .btn-action, .speed-select, .tel-row, .score-box, .emg-canvas-wrap {
      border-radius:4px;
      border-color:rgba(50,216,255,.16);
      background:rgba(7,12,21,.82);
    }
    .btn-preset.active, .btn-toggle.active, .btn-action.primary-btn {
      color:#32d8ff;
      border-color:rgba(50,216,255,.44);
      background:rgba(50,216,255,.10);
    }
    .drag-hint, .status-badge { border-radius:4px; }
    #simCanvas { filter:drop-shadow(0 0 24px rgba(50,216,255,.08)); }
    .bar-fill.ok { background:linear-gradient(90deg,#32d8ff,#40f2a0); }
    .bar-fill.mid { background:linear-gradient(90deg,#ffd166,#ff8a3d); }
    .bar-fill.warn { background:linear-gradient(90deg,#ff5c8a,#b56cff); }
    @media (max-width: 980px) {
      .bio-layout { grid-template-columns:1fr; grid-template-rows:auto minmax(460px,1fr) auto; overflow:auto; }
      .ctrl-panel, .tel-panel { max-height:none; }
    }
    """

    # Streamlit components run inside an iframe. Relative <link> and <script>
    # paths would point at Streamlit's server, not this repo, so we inline the
    # web bundle here. The order matters: app.js depends on the two engine files.
    html = index_html.replace(
        '<link rel="stylesheet" href="style.css">',
        f"<style>{css}</style><style>{phi_override}</style>",
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
        padding-top: 1rem !important;
        max-width: 1340px !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    iframe {
        border: none;
        border-radius: var(--radius-lg);
        background: #070a10;
    }
    </style>
""", unsafe_allow_html=True)

page_header(
    "Biomechanics Lab",
    "Interactive posture, load, and strain simulator for movement analysis.",
    eyebrow="Simulation",
)

components.html(
    load_simulator_html(),
    height=SIM_HEIGHT_PX,
    scrolling=False,
)
