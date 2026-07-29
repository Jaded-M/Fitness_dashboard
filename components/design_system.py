from __future__ import annotations

from html import escape

import streamlit as st


def apply_platform_theme():
    """Apply the PHI Premium OS Streamlit skin — v3 Professional Edition."""
    st.markdown(
        """
        <style>        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@500;700&display=swap');

        .stApp, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
            background-color: var(--bg) !important;
        }

        /* Standardize uppercase labels */
        label, .phi-label, .phi-eyebrow, .phi-sidebar-section, .phi-form-label {
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }

        /* ==========================================
         * KEYFRAMES — only run on specific elements
         * ==========================================
         */
        @keyframes phi-rise {
            from { opacity: 0; transform: translateY(12px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes phi-ring-draw {
            from { stroke-dashoffset: 326.73; }
        }
        @keyframes phi-bar-fill {
            from { transform: scaleX(0); }
            to   { transform: scaleX(1); }
        }
        @keyframes phi-pulse {
            0%, 100% { box-shadow: none !important; }
            50%       { box-shadow: none !important; }
        }
        @keyframes phi-fadein {
            from { opacity: 0; }
            to   { opacity: 1; }
        }
        @keyframes phi-blink {
            0%, 100% { opacity: 1; }
            50%      { opacity: 0; }
        }


        .phi-section-title::after {
            content: "█";
            color: var(--green);
            animation: phi-blink 1s step-end infinite;
            margin-left: 0.12em;
            font-size: 0.75em;
            opacity: 0.5;
        }

        /* ==========================================
         * 1. ROOT & BASE
         * ==========================================
         */
        :root {
            --bg:           #080b12;
            --panel:        rgba(14, 20, 34, 0.86);
            --panel-2:      rgba(20, 29, 48, 0.90);
            --panel-3:      rgba(24, 34, 56, 0.94);
            --ink:          #f6fbff;
            --soft:         #d7f7ff;
            --muted:        rgba(154, 167, 184, 0.82);
            --faint:        rgba(154, 167, 184, 0.48);
            --line:         rgba(50, 216, 255, 0.16);
            --line-strong:  rgba(181, 108, 255, 0.34);
            --blue:         #32d8ff;
            --blue-2:       #6ee7ff;
            --green:        #40f2a0;
            --amber:        #ffd166;
            --rose:         #ff5c8a;
            --violet:       #b56cff;
            --orange:       #ff8a3d;
            --shadow:       0 0 0 1px rgba(50,216,255,0.08), 0 18px 40px rgba(0,0,0,0.26);
            --shadow-soft:  0 0 0 1px rgba(50,216,255,0.06);
            --radius:       4px;
            --radius-lg:    6px;
            --radius-sm:    3px;
            --font-body:    'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
            --font-display: 'Space Grotesk', 'Inter', system-ui, sans-serif;
        }

        /* ==========================================
         * 2. APP BACKGROUND — rich depth, no scan line
         * ==========================================
         */
        .block-container {
            max-width: 1340px;
            padding: 1.2rem 2rem 5rem;
            animation: phi-rise 0.38s ease-out both;
        }

        /* ==========================================
         * 3. SIDEBAR
         * ==========================================
         */
        [data-testid="stSidebar"] {
            background: var(--bg);
            border-right: 1px solid var(--line);
        }
        [data-testid="stSidebarNav"] {
            padding-top: 0.3rem;
            margin-top: 0.6rem;
            border-top: 1px solid var(--line);
        }
        [data-testid="stSidebarNav"] a,
        [data-testid="stPageLink"] a {
            position: relative;
            margin: 0.08rem 0 0.35rem;
            padding: 0.55rem 0.78rem !important;
            border: 1px solid var(--line);
            border-radius: var(--radius);
            color: var(--soft) !important;
            background: var(--panel);
            transition: background 140ms ease, border-color 140ms ease;
        }
        [data-testid="stSidebarNav"] a::before,
        [data-testid="stPageLink"] a::before {
            content: ">";
            position: absolute;
            left: 0.45rem;
            top: 50%;
            color: var(--green);
            font-family: var(--font-display);
            font-size: 0.55rem;
            opacity: 0.5;
            transform: translateY(-50%);
        }
        [data-testid="stSidebarNav"] a:hover,
        [data-testid="stPageLink"] a:hover {
            color: var(--green) !important;
            border-color: var(--green);
            background: var(--panel-2);
        }
        [data-testid="stPageLink"] a[aria-current="page"],
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            color: var(--green) !important;
            border-color: var(--green);
            background: var(--panel-3);
            border-left: 3px solid var(--green);
        }
        [data-testid="stPageLink"] a[aria-current="page"]::before,
        [data-testid="stSidebarNav"] a[aria-current="page"]::before {
            opacity: 1;
            color: var(--green);
        }
        .phi-nav-hint {
            color: var(--muted);
            font-size: 0.62rem;
            font-weight: 700;
            line-height: 1.25;
            margin: 0.44rem 0.2rem 0.14rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .phi-nav-hint.active {
            color: var(--green);
        }

        .phi-sidebar-brand {
            display: flex;
            align-items: center;
            gap: 0.85rem;
            padding: 1rem;
            margin: 0.25rem 0 1rem;
            border: 1px solid var(--line);
            border-radius: var(--radius);
            background: var(--panel);
        }
        .phi-sidebar-logo {
            display: grid;
            place-items: center;
            width: 46px;
            height: 46px;
            border: 1px solid var(--green);
            background: var(--panel-2);
            color: var(--green);
            font-family: var(--font-display);
            font-weight: 900;
            font-size: 0.88rem;
        }
        .phi-sidebar-title {
            color: var(--green);
            font-weight: 800;
            font-size: 0.92rem;
            line-height: 1.3;
            letter-spacing: -0.02em;
        }
        .phi-sidebar-subtitle, .phi-sidebar-footer {
            color: var(--muted);
            font-size: 0.72rem;
            margin-top: 0.18rem;
        }
        .phi-sidebar-section, .phi-form-label {
            color: var(--green);
            font-size: 0.65rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin: 0.9rem 0 0.4rem;
        }
        .phi-sidebar-card {
            margin: 0.55rem 0;
            padding: 0.82rem;
            border: 1px solid var(--line);
            border-radius: var(--radius);
            background: var(--panel);
        }
        .phi-sidebar-card.compact { padding: 0.68rem; }
        .phi-sidebar-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.6rem;
            margin: 0.45rem 0;
        }
        .phi-sidebar-kpi {
            color: var(--green);
            font-family: var(--font-display);
            font-size: 1.38rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            line-height: 1.2;
        }
        .phi-sidebar-kpi small {
            color: var(--muted);
            font-family: var(--font-body);
            font-size: 0.65rem;
            font-weight: 700;
            margin-left: 0.22rem;
        }
        .phi-sidebar-status {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            padding: 0.2rem 0.44rem;
            border: 1px solid var(--line);
            border-radius: var(--radius);
            color: var(--soft);
            background: var(--panel-2);
            font-size: 0.65rem;
            font-weight: 800;
            letter-spacing: 0.04em;
        }
        .phi-sidebar-status::before {
            content: "";
            width: 0.38rem;
            height: 0.38rem;
            background: var(--green);
        }
        .phi-sidebar-status.good::before { background: var(--green); }
        .phi-sidebar-status.warn::before { background: var(--amber); }
        .phi-sidebar-status.risk::before { background: var(--rose); }
        .phi-sidebar-progress {
            height: 0.44rem;
            overflow: hidden;
            border-radius: var(--radius);
            background: var(--panel-2);
            margin-top: 0.4rem;
        }
        .phi-sidebar-progress span {
            display: block;
            height: 100%;
            background: var(--green);
            transition: width 0.4s ease;
        }
        .phi-sidebar-progress.warn span { background: var(--amber); }
        .phi-sidebar-mini-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0,1fr));
            gap: 0.45rem;
            margin-top: 0.6rem;
        }
        .phi-sidebar-mini {
            padding: 0.56rem;
            border: 1px solid var(--line);
            border-radius: var(--radius);
            background: var(--panel-2);
        }
        .phi-sidebar-footer {
            padding: 0.8rem 0.2rem 1.1rem;
            border-top: 1px solid var(--line);
        }/* ==========================================
         * 4. TYPOGRAPHY
         * ==========================================
         */
        h1, h2, h3 {
            font-family: var(--font-display);
            color: var(--ink);
            letter-spacing: -0.03em;
        }
        h1 {
            font-size: clamp(2.0rem, 4vw, 3.2rem);
            line-height: 1.2;
            margin: 0;
            max-width: 860px;
            background: none;
        }
        h2, h3 { font-size: 1.18rem; margin-top: 1.1rem; }
        [data-testid="stMarkdownContainer"] h3 {
            color: var(--soft);
            font-family: var(--font-display);
            font-size: 1.12rem;
            letter-spacing: -0.02em;
            margin-top: 1.2rem;
        }
        [data-testid="stMarkdownContainer"] h4,
        [data-testid="stMarkdownContainer"] h5 {
            color: var(--muted);
            font-size: 0.74rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }
        p, span, label, div { letter-spacing: 0; }

        /* ==========================================
         * 5. PAGE HEADER
         * ==========================================
         */
        .phi-page-head {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 1rem;
            align-items: start;
            padding: 1rem 0 0.75rem;
            margin-bottom: 0.4rem;
        }
        .phi-eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            color: var(--blue);
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            margin-bottom: 0.65rem;
        }
        .phi-eyebrow::before {
            content: "";
            width: 7px;
            height: 7px;
            border-radius: 0px;
            background: var(--green);
            box-shadow: none !important;
        }
        .phi-subtitle {
            color: var(--muted);
            font-size: 0.88rem;
            line-height: 1.55;
            max-width: 720px;
            margin-top: 0.7rem;
        }
        .phi-status-chip {
            border: 1px solid rgba(51,255,51,0.32);
            color: var(--green);
            border-radius: 0px;
            padding: 0.52rem 0.88rem;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            background: rgba(51,255,51,0.08);
            box-shadow: none !important;
            white-space: nowrap;
        }

        /* ==========================================
         * 6. CARDS — blur only on command hero
         * ==========================================
         */
        .phi-card {
            position: relative;
            overflow: hidden;
            min-height: 114px;
            padding: 1.05rem;
            border: 1px solid var(--line);
            border-radius: var(--radius);
            background:
                linear-gradient(170deg, rgba(51,255,51,0.02), rgba(51,255,51,0.005)),
                rgba(12, 16, 26, 0.45);
            -webkit-box-shadow: none !important;
            transition: transform 140ms ease, border-color 140ms ease, box-shadow 140ms ease;
        }
        .phi-card::before {
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            background: linear-gradient(135deg, rgba(51,255,51,0.06) 0%, transparent 32%);
            opacity: 0.6;
        }
        .phi-card:hover {
            transform: translateY(-2px);
            border-color: rgba(51,255,51,0.38);
            box-shadow: none !important;
            will-change: transform;
        }
        .phi-card.good { border-color: rgba(51,255,51,0.34); }
        .phi-card.warn { border-color: rgba(240,192,96,0.34); }
        .phi-card.risk { border-color: rgba(248,96,112,0.34); }

        .phi-quiet-card {
            min-height: 112px;
            padding: 1rem;
            border: 1px solid var(--line);
            border-radius: var(--radius);
            background: rgba(12, 18, 28, 0.5);
            -webkit-box-shadow: none !important;
            transition: transform 140ms ease, border-color 140ms ease, box-shadow 140ms ease;
        }
        .phi-quiet-card:hover {
            transform: translateY(-2px);
            border-color: rgba(51,255,51,0.34);
            box-shadow: none !important;
            will-change: transform;
        }
        .phi-quiet-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0,1fr));
            gap: 0.8rem;
            margin: 0.3rem 0 0.8rem;
        }

        /* ==========================================
         * 7. MINI WIDGET (streak, water top row)
         * ==========================================
         */
        .phi-mini-widget {
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            min-height: 112px;
            border: 1px solid var(--line);
            border-radius: var(--radius-lg);
            padding: 1rem;
            background:
                radial-gradient(ellipse at 88% 12%, rgba(51,255,51,0.12) 0%, transparent 50%),
                rgba(12, 18, 28, 0.5);
            -webkit-box-shadow: none !important;
            transition: transform 140ms ease, border-color 140ms ease, box-shadow 140ms ease;
        }
        .phi-mini-widget::before {
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            background: linear-gradient(135deg, rgba(51,255,51,0.05) 0%, transparent 30%);
        }
        .phi-mini-widget:hover {
            transform: translateY(-2px);
            border-color: rgba(51,255,51,0.38);
            box-shadow: none !important;
            will-change: transform;
        }
        .phi-mini-widget.good { border-color: rgba(51,255,51,0.32); }
        .phi-mini-widget.warn { border-color: rgba(240,192,96,0.32); }
        .phi-mini-widget.risk { border-color: rgba(248,96,112,0.32); }
        .phi-widget-value {
            color: var(--ink);
            font-family: var(--font-display);
            font-size: 2.2rem;
            font-weight: 800;
            line-height: 1;
            margin-top: 0.45rem;
        }
        .phi-widget-value span {
            color: var(--muted);
            font-size: 0.78rem;
            font-family: var(--font-body);
            margin-left: 0.3rem;
            font-weight: 700;
        }
        .phi-widget-orb {
            display: grid;
            place-items: center;
            width: 70px;
            height: 70px;
            border-radius: 0px;
            color: var(--blue);
            font-size: 0.68rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            text-align: center;
            background: rgba(51,255,51,0.07);
            border: 1px solid rgba(51,255,51,0.20);
            box-shadow: none !important;
        }
        .phi-hydration-bars {
            display: grid;
            grid-template-columns: repeat(2, 10px);
            grid-auto-rows: 7px;
            gap: 4px;
            padding: 0.58rem;
            border-radius: var(--radius);
            border: 1px solid rgba(51,255,51,0.16);
            background: rgba(51,255,51,0.05);
        }
        .phi-hydration-bars span {
            display: block;
            border-radius: 0px;
            background: rgba(51,255,51,0.16);
        }
        .phi-hydration-bars span.filled {
            background: var(--blue);
            box-shadow: none !important;
        }

        /* ==========================================
         * 8. COMMAND HERO CARD — blur here is worth it
         * ==========================================
         */
        .phi-command {
            position: relative;
            overflow: hidden;
            padding: 1.35rem;
            border: 1px solid rgba(51,255,51,0.32);
            border-radius: var(--radius-lg);
            background:
                radial-gradient(ellipse at 14% 18%, rgba(51,255,51,0.15) 0%, transparent 50%),
                rgba(12, 18, 28, 0.4);
            box-shadow: none !important;
            -webkit-animation: phi-pulse 7s ease-in-out infinite;
        }
        .phi-command::before {
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            background: linear-gradient(135deg, rgba(51,255,51,0.06) 0%, transparent 35%);
        }
        .phi-command-grid {
            display: grid;
            grid-template-columns: 0.88fr 1.35fr 1fr;
            gap: 1.1rem;
            align-items: center;
            position: relative;
            z-index: 1;
        }
        .phi-command-action {
            color: var(--ink);
            font-family: var(--font-display);
            font-size: clamp(1.3rem, 2.2vw, 2rem);
            line-height: 1.10;
            font-weight: 800;
            margin-top: 0.42rem;
            letter-spacing: -0.03em;
        }
        .phi-ring-wrap {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        .phi-ring circle:nth-of-type(2) {
            animation: phi-ring-draw 900ms cubic-bezier(0.4,0,0.2,1) both;
        }
        .phi-ring-label {
            color: var(--soft);
            font-size: 0.98rem;
            font-weight: 800;
            line-height: 1.35;
            max-width: 200px;
        }
        .phi-metric-rail {
            display: grid;
            grid-template-columns: repeat(4, minmax(0,1fr));
            gap: 0.68rem;
            margin-top: 1rem;
            position: relative;
            z-index: 1;
        }
        .phi-rail-item {
            padding: 0.74rem;
            border-radius: 0px;
            border: 1px solid rgba(51,255,51,0.14);
            background: rgba(4,8,14,0.44);
        }
        .phi-rail-value {
            color: var(--ink);
            font-family: var(--font-display);
            font-size: 1.22rem;
            font-weight: 800;
            margin-top: 0.22rem;
        }

        /* ==========================================
         * 9. INSIGHT / PILL / BARS
         * ==========================================
         */
        .phi-insight {
            min-height: 112px;
            padding: 1rem;
            border-radius: var(--radius-lg);
            border: 1px solid var(--line);
            border-left: 4px solid var(--blue);
            background: rgba(12, 18, 28, 0.45);
            -webkit-box-shadow: none !important;
            transition: border-left-color 220ms ease;
        }
        .phi-insight.good { border-left-color: var(--green); }
        .phi-insight.warn { border-left-color: var(--amber); }
        .phi-insight.risk { border-left-color: var(--rose); }

        .phi-pill {
            display: inline-flex;
            align-items: center;
            border-radius: 0px;
            border: 1px solid rgba(51,255,51,0.22);
            padding: 0.28rem 0.58rem;
            color: var(--muted);
            font-size: 0.74rem;
            font-weight: 800;
            margin: 0.16rem 0.18rem 0.16rem 0;
            background: rgba(51,255,51,0.06);
            transition: background 120ms ease, border-color 120ms ease;
        }
        .phi-pill.good { color: var(--green); border-color: rgba(51,255,51,0.32); background: rgba(51,255,51,0.07); }
        .phi-pill.warn { color: var(--amber); border-color: rgba(240,192,96,0.34); background: rgba(240,192,96,0.07); }
        .phi-pill.risk { color: var(--rose);  border-color: rgba(248,96,112,0.32); background: rgba(248,96,112,0.07); }

        .phi-bar {
            height: 0.52rem;
            border-radius: 0px;
            background: rgba(51,255,51,0.12);
            overflow: hidden;
            margin-top: 0.55rem;
        }
        .phi-bar > span {
            display: block;
            height: 100%;
            border-radius: 0px;
            transform-origin: left center;
            animation: phi-bar-fill 0.75s cubic-bezier(0.4,0,0.2,1) both;
            background: linear-gradient(90deg, var(--rose), var(--amber), var(--green), var(--blue));
        }

        /* ==========================================
         * 10. SECTION HEADERS
         * ==========================================
         */
        .phi-section {
            margin: 1.2rem 0 0.65rem;
            padding: 0.85rem 0 0.12rem;
            border-top: 1px solid rgba(51,255,51,0.10);
        }
        .phi-section-title {
            color: var(--soft);
            font-family: var(--font-display);
            font-size: 1.05rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            padding-left: 0.7rem;
            border-left: 3px solid var(--blue);
        }
        .phi-section-caption {
            color: var(--muted);
            font-size: 0.84rem;
            line-height: 1.48;
            margin-top: 0.22rem;
            padding-left: 0.7rem;
        }
        .phi-label {
            color: var(--muted);
            font-size: 0.66rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }
        .phi-value {
            color: var(--ink);
            font-family: var(--font-display);
            font-size: 1.98rem;
            font-weight: 800;
            line-height: 1.2;
            margin-top: 0.5rem;
        }
        .phi-caption {
            color: var(--muted);
            font-size: 0.80rem;
            line-height: 1.48;
            margin-top: 0.42rem;
        }

        /* ==========================================
         * 11. KPI STRIP
         * ==========================================
         */
        .phi-kpi-strip {
            display: grid;
            grid-template-columns: repeat(4, minmax(0,1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        .phi-kpi-tile {
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            gap: 1.1rem;
            padding: 1.2rem;
            border-radius: var(--radius-lg);
            border: 1px solid rgba(51,255,51,0.05);
            background: rgba(16, 22, 34, 0.4);
            -webkit-box-shadow: none !important;
            transition: transform 150ms ease, border-color 150ms ease, box-shadow 150ms ease;
        }
        .phi-kpi-tile::before {
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            background: linear-gradient(135deg, rgba(51,255,51,0.04) 0%, transparent 40%);
        }
        .phi-kpi-tile:hover {
            transform: translateY(-2px);
            border-color: rgba(51,255,51,0.40);
            box-shadow: none !important;
            will-change: transform;
        }
        .phi-kpi-icon {
            display: grid;
            place-items: center;
            width: 48px;
            height: 48px;
            border-radius: 0px;
            background: rgba(51,255,51,0.08);
            border: 1px solid rgba(51,255,51,0.22);
            color: var(--blue);
            font-size: 1.4rem;
        }
        .phi-kpi-tile.good .phi-kpi-icon { color: var(--green); background: rgba(51,255,51,0.08); border-color: rgba(51,255,51,0.25); }
        .phi-kpi-tile.warn .phi-kpi-icon { color: var(--amber); background: rgba(240,192,96,0.08); border-color: rgba(240,192,96,0.25); }
        .phi-kpi-tile.risk .phi-kpi-icon { color: var(--rose); background: rgba(248,96,112,0.08); border-color: rgba(248,96,112,0.25); }
        .phi-kpi-title {
            color: var(--muted);
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }
        .phi-kpi-value {
            color: var(--ink);
            font-family: var(--font-display);
            font-size: 1.85rem;
            font-weight: 800;
            line-height: 1.1;
            margin-top: 0.2rem;
        }
        .phi-kpi-value span {
            color: var(--muted);
            font-size: 0.8rem;
            font-family: var(--font-body);
            font-weight: 700;
            margin-left: 0.25rem;
        }

        /* ==========================================
         * 12. ACTION BAR
         * ==========================================
         */
        .phi-action-bar {
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
            padding: 1rem;
            border: 1px solid rgba(51,255,51,0.20);
            border-radius: var(--radius-lg);
            background:
                radial-gradient(ellipse at 5% 50%, rgba(51,255,51,0.08) 0%, transparent 50%),
                linear-gradient(160deg, rgba(12,18,28,0.80), rgba(6,10,16,0.84));
            box-shadow: none !important;
            margin-bottom: 0.5rem;
        }
        .phi-action-bar-label {
            color: var(--blue);
            font-size: 0.64rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }

        /* ==========================================
         * 13. BUTTONS
         * ==========================================
         */
        .stButton > button {
            min-height: 2.75rem;
            border-radius: 0px;
            border: 1px solid rgba(51,255,51,0.20);
            background: linear-gradient(170deg, rgba(28,38,56,0.92), rgba(14,22,38,0.92));
            color: var(--ink);
            font-weight: 800;
            font-size: 0.83rem;
            box-shadow: none !important;
            transition: transform 120ms ease, border-color 120ms ease, box-shadow 120ms ease, background 120ms ease;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            border-color: rgba(51,255,51,0.48);
            box-shadow: none !important;
            will-change: transform;
        }
        .stButton > button[kind="primary"] {
            color: #000000;
            border-color: transparent;
            background: linear-gradient(135deg, var(--blue), var(--green));
            box-shadow: none !important;
        }
        .stButton > button[kind="primary"]:hover {
            box-shadow: none !important;
        }

        /* ==========================================
         * 14. TABS
         * ==========================================
         */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.3rem;
            padding: 0.4rem;
            border: 1px solid rgba(51,255,51,0.16);
            border-radius: var(--radius-lg);
            background: rgba(6,10,16,0.74);
            box-shadow: none !important;
        }
        .stTabs [data-baseweb="tab"] {
            height: 2.6rem;
            padding: 0 1rem;
            border-radius: 0px;
            color: var(--muted);
            font-size: 0.80rem;
            font-weight: 800;
            letter-spacing: 0.02em;
            background: rgba(51,255,51,0.02);
            border: 1px solid rgba(51,255,51,0.02);
            transition: color 120ms ease, background 120ms ease;
        }
        .stTabs [data-baseweb="tab"]:hover { color: var(--ink); background: rgba(51,255,51,0.08); }
        .stTabs [aria-selected="true"] {
            color: #000000;
            background: linear-gradient(135deg, var(--blue), var(--green));
            box-shadow: none !important;
            border: none;
        }

        /* ==========================================
         * 15. METRICS
         * ==========================================
         */
        div[data-testid="stMetric"] {
            border: 1px solid var(--line);
            border-left: 3px solid var(--blue);
            border-radius: var(--radius);
            background: linear-gradient(170deg, rgba(16,24,36,0.88), rgba(8,12,18,0.92));
            box-shadow: none !important;
            padding: 1rem;
            transition: transform 140ms ease, border-color 140ms ease;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            border-color: rgba(51,255,51,0.30);
            will-change: transform;
        }
        [data-testid="stMetricLabel"] {
            color: var(--muted);
            font-size: 0.65rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }
        [data-testid="stMetricValue"] {
            color: var(--ink);
            font-family: var(--font-display);
            font-size: clamp(1.4rem, 2.5vw, 1.9rem);
            font-weight: 800;
        }
        [data-testid="stMetricDelta"] { font-weight: 800; }

        /* ==========================================
         * 16. EXPANDERS, DATA, CHARTS
         * ==========================================
         */
        div[data-testid="stExpander"] {
            border: 1px solid rgba(51,255,51,0.14);
            border-radius: var(--radius-lg);
            background: rgba(7,11,18,0.74);
            box-shadow: none !important;
            overflow: hidden;
        }
        div[data-testid="stExpander"] summary {
            font-weight: 800;
            font-size: 0.88rem;
            color: var(--soft);
        }
        [data-testid="stDataFrame"], .stDataFrame {
            border: 1px solid rgba(51,255,51,0.12);
            border-radius: var(--radius);
            overflow: hidden;
            box-shadow: none !important;
        }
        .js-plotly-plot { border-radius: var(--radius); overflow: hidden; }
        [data-testid="stPlotlyChart"] {
            position: relative;
            padding: 0.8rem 1rem;
            border: 1px solid rgba(51,255,51,0.12);
            border-radius: var(--radius-lg);
            background: linear-gradient(170deg, rgba(10,16,26,0.74), rgba(5,8,13,0.74));
            box-shadow: none !important;
            transition: border-color 200ms ease;
        }
        [data-testid="stPlotlyChart"]:hover {
            border-color: rgba(51,255,51,0.22);
        }
        [data-testid="stRadio"] {
            padding: 0.4rem;
            border: 1px solid rgba(51,255,51,0.14);
            border-radius: var(--radius);
            background: rgba(6,10,16,0.58);
        }
        [data-testid="stRadio"] label { border-radius: 0px; padding: 0.16rem 0.32rem; }
        [data-testid="stPopover"] button,
        [data-testid="stDownloadButton"] button {
            min-height: 2.75rem;
            border-radius: 0px;
            border: 1px solid rgba(51,255,51,0.20);
            background: linear-gradient(170deg, rgba(28,38,56,0.92), rgba(14,22,38,0.92));
            color: var(--ink);
            font-weight: 800;
        }
        [data-testid="stDataEditor"] { border-radius: var(--radius); overflow: hidden; }

        /* ==========================================
         * 17. FORM INPUTS
         * ==========================================
         */
        .stTextInput input,
        .stNumberInput input,
        .stDateInput input,
        .stSelectbox div[data-baseweb="select"],
        .stTextArea textarea {
            border-radius: 0px !important;
            border-color: rgba(51,255,51,0.20) !important;
            background: rgba(5,9,15,0.80) !important;
            color: var(--ink) !important;
            font-size: 0.88rem !important;
        }
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
            min-height: auto !important;
            margin-bottom: 0.24rem !important;
            line-height: 1.2 !important;
        }
        [data-testid="stSidebar"] .stSelectbox,
        [data-testid="stSidebar"] .stNumberInput,
        [data-testid="stSidebar"] .stTextInput,
        [data-testid="stSidebar"] .stTextArea { margin-bottom: 0.50rem; }
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
            min-height: 2.55rem !important;
            height: auto !important;
            align-items: center !important;
            padding: 0 0.16rem !important;
            overflow: hidden !important;
        }
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
            min-height: 2.35rem !important;
            display: flex !important;
            align-items: center !important;
            overflow: hidden !important;
        }
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] span,
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] div {
            line-height: 1.2 !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }
        [data-testid="stSidebar"] .stSelectbox svg {
            flex: 0 0 auto !important;
            margin-left: 0.22rem !important;
        }
        [data-testid="stSidebar"] div[data-testid="stExpander"] summary {
            min-height: 2.65rem !important;
            display: flex !important;
            align-items: center !important;
            line-height: 1.2 !important;
        }
        div[data-baseweb="popover"] { z-index: 999999 !important; }
        div[data-baseweb="popover"] ul, div[role="listbox"] {
            padding: 0.32rem !important;
            border: 1px solid rgba(50,216,255,0.22) !important;
            border-radius: var(--radius) !important;
            background: #0b0f1a !important;
            box-shadow: none !important;
        }
        div[data-baseweb="popover"] li, div[role="option"] {
            min-height: 2.25rem !important;
            display: flex !important;
            align-items: center !important;
            border-radius: 0px !important;
            color: var(--soft) !important;
            line-height: 1.2 !important;
            white-space: nowrap !important;
        }
        div[data-baseweb="popover"] li:hover, div[role="option"]:hover {
            background: rgba(51,255,51,0.12) !important;
            color: var(--ink) !important;
        }

        /* ==========================================
         * 18. ALERTS, DIVIDERS
         * ==========================================
         */
        .stAlert {
            border-radius: var(--radius);
            border: 1px solid rgba(51,255,51,0.16);
            background: rgba(10,15,24,0.90);
            color: var(--ink);
        }
        hr { border-color: rgba(51,255,51,0.12); }

        /* ==========================================
         * 19. NUTRITION PAGE — macro cards & progress
         * ==========================================
         */
        .custom-progress-track {
            width: 100%;
            height: 10px;
            overflow: hidden;
            border-radius: 0px;
            background: rgba(22,30,44,0.80);
            border: 1px solid var(--line);
        }
        .custom-progress-fill {
            height: 100%;
            border-radius: 0px;
            background: linear-gradient(90deg, var(--blue), var(--green));
            transition: width 0.28s ease;
        }
        .custom-progress-fill.over {
            background: linear-gradient(90deg, var(--amber), var(--rose));
        }
        .macro-container {
            display: grid;
            grid-template-columns: repeat(3, minmax(0,1fr));
            gap: 12px;
            margin: 10px 0 20px;
        }
        .macro-card {
            background: linear-gradient(160deg, rgba(16,24,38,0.90), rgba(8,12,18,0.92));
            border: 1px solid var(--line);
            border-radius: var(--radius-sm);
            padding: 1rem;
            transition: transform 130ms ease, border-color 130ms ease;
        }
        .macro-card:hover {
            transform: translateY(-1px);
            border-color: rgba(51,255,51,0.28);
            will-change: transform;
        }
        .macro-title {
            color: var(--muted);
            font-size: 0.70rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.10em;
            margin-bottom: 6px;
        }
        .macro-value {
            color: var(--ink);
            font-family: var(--font-display);
            font-size: 1.22rem;
            font-weight: 800;
            margin-bottom: 8px;
        }
        .macro-value span {
            color: var(--muted);
            font-size: 0.84rem;
            font-weight: 600;
            font-family: var(--font-body);
        }

        /* ==========================================
         * 20. RGB RETRO-FUTURE CLEANUP
         * ========================================== */
        .stApp, [data-testid="stAppViewContainer"] {
            background:
                linear-gradient(rgba(50,216,255,0.035) 1px, transparent 1px),
                linear-gradient(90deg, rgba(181,108,255,0.030) 1px, transparent 1px),
                radial-gradient(ellipse at top, rgba(50,216,255,0.14), transparent 42%),
                linear-gradient(180deg, #0b0f1a 0%, #070a10 100%) !important;
            background-size: 44px 44px, 44px 44px, 100% 100%, 100% 100%;
        }
        [data-testid="stSidebar"] {
            background:
                linear-gradient(rgba(50,216,255,0.035) 1px, transparent 1px),
                linear-gradient(180deg, rgba(7,10,17,0.98), rgba(9,13,22,0.98)) !important;
            background-size: 100% 28px, 100% 100% !important;
            border-right: 1px solid rgba(50,216,255,0.14) !important;
        }
        .phi-sidebar-nav-stack {
            display: flex;
            flex-direction: column;
            gap: 0.28rem;
        }
        [data-testid="stSidebar"] [data-testid="stPageLink"] {
            margin: 0 !important;
        }
        [data-testid="stSidebar"] [data-testid="stPageLink"] a {
            min-height: 2.7rem !important;
            display: flex !important;
            align-items: center !important;
            border-radius: var(--radius) !important;
            border: 1px solid rgba(50,216,255,0.16) !important;
            background: rgba(8, 13, 23, 0.86) !important;
            color: var(--soft) !important;
            font-family: var(--font-display) !important;
            font-weight: 700 !important;
            letter-spacing: 0.01em !important;
        }
        [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
            background: rgba(50,216,255,0.08) !important;
            border-color: rgba(50,216,255,0.36) !important;
            color: var(--ink) !important;
        }
        [data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {
            background: linear-gradient(90deg, rgba(50,216,255,0.16), rgba(181,108,255,0.08)) !important;
            border-left: 3px solid var(--blue) !important;
            color: var(--ink) !important;
        }
        [data-testid="stSidebar"] .phi-nav-hint {
            min-height: 1rem;
            margin: 0.34rem 0 0.08rem !important;
            color: rgba(154,167,184,0.62) !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.58rem !important;
            letter-spacing: 0.07em !important;
        }
        .phi-sidebar-brand {
            background:
                linear-gradient(135deg, rgba(50,216,255,0.10), rgba(181,108,255,0.04)),
                rgba(8,13,23,0.92) !important;
            border-color: rgba(50,216,255,0.22) !important;
        }
        .phi-sidebar-logo {
            border-radius: var(--radius-sm) !important;
            border: 1px solid rgba(50,216,255,0.34) !important;
            background: rgba(50,216,255,0.07) !important;
            color: var(--blue) !important;
        }
        .phi-sidebar-title {
            color: var(--ink) !important;
            font-family: 'JetBrains Mono', monospace !important;
            letter-spacing: 0.12em !important;
        }
        .phi-sidebar-subtitle {
            color: var(--muted) !important;
        }
        .block-container {
            padding-top: 1rem !important;
        }
        .phi-section-title::after,
        .phi-cursor {
            display: none !important;
        }
        .phi-page-head {
            padding: 0.85rem 0 0.55rem !important;
            margin-bottom: 0.2rem !important;
        }
        h1 {
            color: var(--ink) !important;
            letter-spacing: 0 !important;
        }
        h2, h3, .phi-section-title, .phi-sidebar-title {
            letter-spacing: 0 !important;
        }
        label, .phi-label, .phi-eyebrow, .phi-sidebar-section, .phi-form-label {
            letter-spacing: 0.075em !important;
        }
        .phi-card,
        .phi-quiet-card,
        .phi-mini-widget,
        .phi-command,
        .phi-action-bar,
        .phi-kpi-tile,
        .phi-sidebar-card,
        .phi-sidebar-brand,
        div[data-testid="stMetric"],
        div[data-testid="stExpander"],
        [data-testid="stPlotlyChart"],
        .macro-card {
            background:
                linear-gradient(145deg, rgba(18, 26, 43, 0.92), rgba(10, 15, 25, 0.88)) !important;
            border-color: rgba(50,216,255,0.14) !important;
            box-shadow: var(--shadow-soft) !important;
        }
        .phi-card::before,
        .phi-mini-widget::before,
        .phi-command::before,
        .phi-kpi-tile::before {
            opacity: 0.22 !important;
            background: linear-gradient(135deg, rgba(50,216,255,0.12), transparent 42%) !important;
        }
        .phi-card:hover,
        .phi-quiet-card:hover,
        .phi-mini-widget:hover,
        .phi-kpi-tile:hover,
        div[data-testid="stMetric"]:hover,
        [data-testid="stPlotlyChart"]:hover {
            transform: translateY(-1px) !important;
            border-color: rgba(181,108,255,0.34) !important;
        }
        .phi-value,
        .phi-kpi-value,
        .phi-sidebar-kpi,
        .phi-widget-value,
        .phi-rail-value,
        .phi-hero-value,
        .phi-intel-value,
        [data-testid="stMetricValue"] {
            color: var(--ink) !important;
        }
        .phi-eyebrow,
        .phi-section-title,
        .phi-action-bar-label,
        .phi-intel-header,
        .phi-intel-label {
            color: var(--blue) !important;
        }
        .phi-status-chip,
        .phi-pill,
        .phi-sidebar-status {
            border-radius: var(--radius-sm) !important;
        }
        .stButton > button,
        [data-testid="stPopover"] button,
        [data-testid="stDownloadButton"] button {
            border-radius: var(--radius) !important;
            background: rgba(8,13,23,0.92) !important;
            border-color: rgba(50,216,255,0.24) !important;
            color: var(--ink) !important;
        }
        .stButton > button:hover,
        [data-testid="stPopover"] button:hover,
        [data-testid="stDownloadButton"] button:hover {
            border-color: rgba(255,92,138,0.42) !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            background: rgba(9, 13, 22, 0.72) !important;
            border-color: rgba(50,216,255,0.14) !important;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: var(--radius-sm) !important;
            background: transparent !important;
        }
        .stTabs [aria-selected="true"],
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, var(--blue), var(--violet), var(--rose)) !important;
            color: #071019 !important;
        }
        [data-testid="stPlotlyChart"] {
            padding: 0.6rem 0.75rem !important;
        }
        .custom-progress-fill,
        .phi-bar > span,
        .phi-sidebar-progress span {
            background: linear-gradient(90deg, var(--blue), var(--violet), var(--rose), var(--green)) !important;
        }
        .custom-progress-track,
        .phi-bar,
        .phi-sidebar-progress {
            background: rgba(154,167,184,0.12) !important;
            border-color: rgba(50,216,255,0.12) !important;
        }
        .phi-quiet-grid,
        .phi-kpi-strip {
            gap: 0.75rem !important;
            margin-bottom: 1rem !important;
        }
        .phi-section {
            margin-top: 0.95rem !important;
            border-top-color: rgba(50,216,255,0.12) !important;
        }
        .js-plotly-plot .plotly .main-svg {
            border-radius: var(--radius) !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title, subtitle, eyebrow="Personal Health Intelligence"):
    import datetime
    now_str = datetime.datetime.now().strftime("%d %b %H:%M")
    st.markdown(
        f"""
        <div class="phi-page-head">
            <div>
                <div class="phi-eyebrow">{escape(eyebrow)}</div>
                <h1>{escape(title)}</h1>
                <div class="phi-subtitle">{escape(subtitle)}</div>
            </div>
            <div class="phi-status-chip">Live | {now_str}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat_card(label, value, caption="", tone=""):
    tone_class = f" {tone}" if tone else ""
    st.markdown(
        f"""
        <div class="phi-card compact{tone_class}">
            <div class="phi-label">{escape(str(label))}</div>
            <div class="phi-value">{escape(str(value))}</div>
            <div class="phi-caption">{escape(str(caption))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_card(title, body, tone=""):
    tone_class = f" {tone}" if tone else ""
    st.markdown(
        f"""
        <div class="phi-insight{tone_class}">
            <div class="phi-label">{escape(str(title))}</div>
            <div style="font-weight:760; margin-top:0.5rem; line-height:1.48;">{escape(str(body))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
