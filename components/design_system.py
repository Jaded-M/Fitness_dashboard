from __future__ import annotations

from html import escape

import streamlit as st


def apply_platform_theme():
    """Apply the PHI Premium OS Streamlit skin — v3 Professional Edition."""
    st.markdown(
        """
        <style>        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');

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
            0%, 100% { box-shadow: 0 0 0 0 rgba(51,255,51,0.0); }
            50%       { box-shadow: 0 0 34px 0 rgba(51,255,51,0.20); }
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
            --bg:           #000000;
            --panel:        #080b08;
            --panel-2:      #0c100c;
            --panel-3:      #0f140f;
            --ink:          #33ff33;
            --soft:         #33ff33;
            --muted:        rgba(51, 255, 51, 0.70);
            --faint:        rgba(51, 255, 51, 0.40);
            --line:         rgba(51, 255, 51, 0.18);
            --line-strong:  rgba(51, 255, 51, 0.35);
            --blue:         #33ff33;
            --blue-2:       #33ff33;
            --green:        #33ff33;
            --amber:        #e0b45d;
            --rose:         #ef6b75;
            --violet:       #33ff33;
            --orange:       #e0b45d;
            --shadow:       none;
            --shadow-soft:  none;
            --radius:       0px;
            --radius-lg:    0px;
            --radius-sm:    0px;
            --font-body:    'JetBrains Mono', 'IBM Plex Mono', monospace;
            --font-display: 'JetBrains Mono', 'IBM Plex Mono', monospace;
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
            background:
                radial-gradient(ellipse at 30% 0%, rgba(77,200,220,0.14) 0%, transparent 40%),
                linear-gradient(180deg, rgba(8,12,20,0.98) 0%, rgba(5,8,14,0.99) 100%);
            border-right: 1px solid rgba(77,200,220,0.18);
            box-shadow: 20px 0 60px rgba(0,0,0,0.36);
        }
        [data-testid="stSidebarNav"] {
            padding-top: 0.3rem;
            margin-top: 0.6rem;
            border-top: 1px solid rgba(140,156,180,0.10);
        }
        [data-testid="stSidebarNav"] a,
        [data-testid="stPageLink"] a {
            position: relative;
            margin: 0.08rem 0 0.35rem;
            padding: 0.62rem 0.78rem !important;
            border: 1px solid rgba(140,156,180,0.12);
            border-radius: 12px;
            color: var(--soft) !important;
            background: linear-gradient(135deg, rgba(16,22,34,0.62), rgba(5,8,14,0.48));
            box-shadow: 0 8px 22px rgba(0,0,0,0.16);
            transition: background 140ms ease, border-color 140ms ease, color 140ms ease, transform 140ms ease, box-shadow 140ms ease;
        }
        [data-testid="stSidebarNav"] a::before,
        [data-testid="stPageLink"] a::before {
            content: "";
            position: absolute;
            left: 0.42rem;
            top: 50%;
            width: 0.34rem;
            height: 0.34rem;
            border-radius: 999px;
            background: rgba(77,200,220,0.55);
            box-shadow: 0 0 12px rgba(77,200,220,0.24);
            transform: translateY(-50%);
        }
        [data-testid="stSidebarNav"] a:hover,
        [data-testid="stPageLink"] a:hover {
            color: var(--ink) !important;
            border-color: rgba(77,200,220,0.38);
            background: linear-gradient(135deg, rgba(77,200,220,0.16), rgba(82,221,160,0.08));
            transform: translateX(2px);
            box-shadow: 0 14px 30px rgba(0,0,0,0.22), 0 0 24px rgba(77,200,220,0.08);
        }
        [data-testid="stPageLink"] a[aria-current="page"],
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            color: var(--ink) !important;
            border-color: rgba(82,221,160,0.48);
            background: linear-gradient(135deg, rgba(77,200,220,0.22), rgba(82,221,160,0.12));
            box-shadow: 0 12px 30px rgba(0,0,0,0.24), inset 3px 0 0 rgba(82,221,160,0.9);
        }
        .phi-nav-hint {
            color: var(--faint);
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
            border: 1px solid rgba(77,200,220,0.20);
            border-radius: var(--radius);
            background: linear-gradient(135deg, rgba(77,200,220,0.12) 0%, rgba(176,160,248,0.07) 100%);
            box-shadow: 0 14px 40px rgba(0,0,0,0.24);
        }
        .phi-sidebar-logo {
            display: grid;
            place-items: center;
            width: 46px;
            height: 46px;
            border-radius: 13px;
            color: #040c10;
            background: linear-gradient(135deg, var(--blue), var(--green));
            font-family: var(--font-display);
            font-weight: 900;
            font-size: 0.88rem;
            letter-spacing: -0.02em;
            box-shadow: 0 0 22px rgba(77,200,220,0.30);
        }
        .phi-sidebar-title {
            color: var(--ink);
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
            color: var(--blue);
            font-size: 0.65rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin: 0.9rem 0 0.4rem;
        }
        .phi-sidebar-card {
            position: relative;
            overflow: hidden;
            margin: 0.55rem 0;
            padding: 0.82rem;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: var(--radius);
            background: linear-gradient(160deg, rgba(20,28,42,0.6), rgba(8,12,20,0.8));
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            box-shadow: 0 10px 40px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05);
        }
        .phi-sidebar-card.compact { padding: 0.68rem; }
        .phi-command {
            position: relative;
            padding: 2rem;
            border-radius: 28px;
            background: linear-gradient(160deg, rgba(8,12,18,0.92), rgba(3,7,12,0.96));
            border: 1px solid rgba(77,200,220,0.14);
            border-top-width: 4px;
            box-shadow: var(--shadow);
            margin-bottom: 2rem;
            overflow: hidden;
        }
        .phi-command.good { border-top-color: var(--green); }
        .phi-command.warn { border-top-color: var(--amber); }
        .phi-command.risk { border-top-color: var(--rose); }

        .phi-command::before {
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            background:
                radial-gradient(ellipse at 80% 0%, rgba(77,200,220,0.06) 0%, transparent 50%),
                radial-gradient(ellipse at 10% 100%, rgba(176,160,248,0.05) 0%, transparent 40%);
        }
        .phi-command-grid {
            position: relative;
            z-index: 1;
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 2.5rem;
            align-items: center;
        }
        .phi-sidebar-row {
            position: relative;
            z-index: 1;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.6rem;
            margin: 0.45rem 0;
        }
        .phi-sidebar-kpi {
            color: var(--ink);
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
            border: 1px solid rgba(140,156,180,0.16);
            border-radius: 999px;
            color: var(--muted);
            background: rgba(3,7,12,0.38);
            font-size: 0.65rem;
            font-weight: 800;
            letter-spacing: 0.04em;
        }
        .phi-sidebar-status::before {
            content: "";
            width: 0.38rem;
            height: 0.38rem;
            border-radius: 999px;
            background: var(--blue);
            box-shadow: 0 0 10px rgba(77,200,220,0.7);
        }
        .phi-sidebar-status.good::before { background: var(--green); box-shadow: 0 0 10px rgba(82,221,160,0.7); }
        .phi-sidebar-status.warn::before { background: var(--amber); box-shadow: 0 0 10px rgba(240,192,96,0.7); }
        .phi-sidebar-status.risk::before { background: var(--rose);  box-shadow: 0 0 10px rgba(248,96,112,0.7); }
        .phi-sidebar-progress {
            position: relative;
            z-index: 1;
            height: 0.44rem;
            overflow: hidden;
            border-radius: 999px;
            background: rgba(140,156,180,0.10);
            margin-top: 0.4rem;
        }
        .phi-sidebar-progress span {
            display: block;
            height: 100%;
            border-radius: inherit;
            background: linear-gradient(90deg, var(--blue), var(--green));
            box-shadow: 0 0 14px rgba(77,200,220,0.20);
            transition: width 0.4s ease;
        }
        .phi-sidebar-progress.warn span { background: linear-gradient(90deg, var(--amber), var(--rose)); }
        .phi-sidebar-mini-grid {
            position: relative; z-index: 1;
            display: grid;
            grid-template-columns: repeat(2, minmax(0,1fr));
            gap: 0.45rem;
            margin-top: 0.6rem;
        }
        .phi-sidebar-mini {
            padding: 0.56rem;
            border: 1px solid rgba(140,156,180,0.12);
            border-radius: 11px;
            background: rgba(3,7,12,0.32);
        }
        .phi-sidebar-footer {
            padding: 0.8rem 0.2rem 1.1rem;
            border-top: 1px solid rgba(140,156,180,0.10);
        }

        /* ==========================================
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
            background: linear-gradient(140deg, #ffffff 10%, #a8dce8 50%, #8aaabb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
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
            border-radius: 999px;
            background: var(--green);
            box-shadow: 0 0 14px rgba(82,221,160,0.9);
        }
        .phi-subtitle {
            color: var(--muted);
            font-size: 0.88rem;
            line-height: 1.55;
            max-width: 720px;
            margin-top: 0.7rem;
        }
        .phi-status-chip {
            border: 1px solid rgba(82,221,160,0.32);
            color: var(--green);
            border-radius: 999px;
            padding: 0.52rem 0.88rem;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            background: rgba(82,221,160,0.08);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 0 24px rgba(82,221,160,0.12);
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
                linear-gradient(170deg, rgba(255,255,255,0.03), rgba(255,255,255,0.005)),
                rgba(12, 16, 26, 0.45);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            box-shadow: var(--shadow-soft), inset 0 1px 1px rgba(255,255,255,0.08);
            transition: transform 140ms ease, border-color 140ms ease, box-shadow 140ms ease;
        }
        .phi-card::before {
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            background: linear-gradient(135deg, rgba(255,255,255,0.10) 0%, transparent 32%);
            opacity: 0.6;
        }
        .phi-card:hover {
            transform: translateY(-2px);
            border-color: rgba(77,200,220,0.38);
            box-shadow: var(--shadow), 0 0 0 1px rgba(77,200,220,0.10);
            will-change: transform;
        }
        .phi-card.good { border-color: rgba(82,221,160,0.34); }
        .phi-card.warn { border-color: rgba(240,192,96,0.34); }
        .phi-card.risk { border-color: rgba(248,96,112,0.34); }

        .phi-quiet-card {
            min-height: 112px;
            padding: 1rem;
            border: 1px solid var(--line);
            border-radius: var(--radius);
            background: rgba(12, 18, 28, 0.5);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            box-shadow: var(--shadow-soft), inset 0 1px 0 rgba(255,255,255,0.04);
            transition: transform 140ms ease, border-color 140ms ease, box-shadow 140ms ease;
        }
        .phi-quiet-card:hover {
            transform: translateY(-2px);
            border-color: rgba(77,200,220,0.34);
            box-shadow: var(--shadow);
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
                radial-gradient(ellipse at 88% 12%, rgba(77,200,220,0.12) 0%, transparent 50%),
                rgba(12, 18, 28, 0.5);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            box-shadow: var(--shadow-soft), inset 0 1px 1px rgba(255,255,255,0.08);
            transition: transform 140ms ease, border-color 140ms ease, box-shadow 140ms ease;
        }
        .phi-mini-widget::before {
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            background: linear-gradient(135deg, rgba(255,255,255,0.07) 0%, transparent 30%);
        }
        .phi-mini-widget:hover {
            transform: translateY(-2px);
            border-color: rgba(77,200,220,0.38);
            box-shadow: var(--shadow);
            will-change: transform;
        }
        .phi-mini-widget.good { border-color: rgba(82,221,160,0.32); }
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
            border-radius: 20px;
            color: var(--blue);
            font-size: 0.68rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            text-align: center;
            background: rgba(77,200,220,0.07);
            border: 1px solid rgba(77,200,220,0.20);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 0 24px rgba(77,200,220,0.10);
        }
        .phi-hydration-bars {
            display: grid;
            grid-template-columns: repeat(2, 10px);
            grid-auto-rows: 7px;
            gap: 4px;
            padding: 0.58rem;
            border-radius: var(--radius);
            border: 1px solid rgba(77,200,220,0.16);
            background: rgba(77,200,220,0.05);
        }
        .phi-hydration-bars span {
            display: block;
            border-radius: 999px;
            background: rgba(140,156,180,0.16);
        }
        .phi-hydration-bars span.filled {
            background: var(--blue);
            box-shadow: 0 0 10px rgba(77,200,220,0.55);
        }

        /* ==========================================
         * 8. COMMAND HERO CARD — blur here is worth it
         * ==========================================
         */
        .phi-command {
            position: relative;
            overflow: hidden;
            padding: 1.35rem;
            border: 1px solid rgba(77,200,220,0.32);
            border-radius: var(--radius-lg);
            background:
                radial-gradient(ellipse at 14% 18%, rgba(77,200,220,0.15) 0%, transparent 50%),
                rgba(12, 18, 28, 0.4);
            box-shadow: var(--shadow), 0 0 0 1px rgba(255,255,255,0.05);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            animation: phi-pulse 7s ease-in-out infinite;
        }
        .phi-command::before {
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            background: linear-gradient(135deg, rgba(255,255,255,0.10) 0%, transparent 35%);
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
            border-radius: 13px;
            border: 1px solid rgba(140,156,180,0.14);
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
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            box-shadow: var(--shadow-soft), inset 0 1px 0 rgba(255,255,255,0.05);
            transition: border-left-color 220ms ease;
        }
        .phi-insight.good { border-left-color: var(--green); }
        .phi-insight.warn { border-left-color: var(--amber); }
        .phi-insight.risk { border-left-color: var(--rose); }

        .phi-pill {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            border: 1px solid rgba(140,163,184,0.22);
            padding: 0.28rem 0.58rem;
            color: var(--muted);
            font-size: 0.74rem;
            font-weight: 800;
            margin: 0.16rem 0.18rem 0.16rem 0;
            background: rgba(140,163,184,0.06);
            transition: background 120ms ease, border-color 120ms ease;
        }
        .phi-pill.good { color: var(--green); border-color: rgba(82,221,160,0.32); background: rgba(82,221,160,0.07); }
        .phi-pill.warn { color: var(--amber); border-color: rgba(240,192,96,0.34); background: rgba(240,192,96,0.07); }
        .phi-pill.risk { color: var(--rose);  border-color: rgba(248,96,112,0.32); background: rgba(248,96,112,0.07); }

        .phi-bar {
            height: 0.52rem;
            border-radius: 999px;
            background: rgba(140,156,180,0.12);
            overflow: hidden;
            margin-top: 0.55rem;
        }
        .phi-bar > span {
            display: block;
            height: 100%;
            border-radius: 999px;
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
            border-top: 1px solid rgba(140,156,180,0.10);
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
            text-shadow: 0 0 22px rgba(77,200,220,0.16);
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
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(16, 22, 34, 0.4);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            box-shadow: var(--shadow-soft), inset 0 1px 1px rgba(255,255,255,0.08);
            transition: transform 150ms ease, border-color 150ms ease, box-shadow 150ms ease;
        }
        .phi-kpi-tile::before {
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            background: linear-gradient(135deg, rgba(255,255,255,0.06) 0%, transparent 40%);
        }
        .phi-kpi-tile:hover {
            transform: translateY(-2px);
            border-color: rgba(77,200,220,0.40);
            box-shadow: var(--shadow);
            will-change: transform;
        }
        .phi-kpi-icon {
            display: grid;
            place-items: center;
            width: 48px;
            height: 48px;
            border-radius: 14px;
            background: rgba(77,200,220,0.08);
            border: 1px solid rgba(77,200,220,0.22);
            color: var(--blue);
            font-size: 1.4rem;
        }
        .phi-kpi-tile.good .phi-kpi-icon { color: var(--green); background: rgba(82,221,160,0.08); border-color: rgba(82,221,160,0.25); }
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
            border: 1px solid rgba(77,200,220,0.20);
            border-radius: var(--radius-lg);
            background:
                radial-gradient(ellipse at 5% 50%, rgba(77,200,220,0.08) 0%, transparent 50%),
                linear-gradient(160deg, rgba(12,18,28,0.80), rgba(6,10,16,0.84));
            box-shadow: var(--shadow-soft);
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
            border-radius: 11px;
            border: 1px solid rgba(140,156,180,0.20);
            background: linear-gradient(170deg, rgba(28,38,56,0.92), rgba(14,22,38,0.92));
            color: var(--ink);
            font-weight: 800;
            font-size: 0.83rem;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.07), 0 8px 20px rgba(0,0,0,0.20);
            transition: transform 120ms ease, border-color 120ms ease, box-shadow 120ms ease, background 120ms ease;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            border-color: rgba(77,200,220,0.48);
            box-shadow: 0 16px 36px rgba(0,0,0,0.26), 0 0 20px rgba(77,200,220,0.10);
            will-change: transform;
        }
        .stButton > button[kind="primary"] {
            color: #030e11;
            border-color: transparent;
            background: linear-gradient(135deg, var(--blue), var(--green));
            box-shadow: 0 14px 32px rgba(77,200,220,0.22);
        }
        .stButton > button[kind="primary"]:hover {
            box-shadow: 0 18px 40px rgba(77,200,220,0.30);
        }

        /* ==========================================
         * 14. TABS
         * ==========================================
         */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.3rem;
            padding: 0.4rem;
            border: 1px solid rgba(77,200,220,0.16);
            border-radius: var(--radius-lg);
            background: rgba(6,10,16,0.74);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
        }
        .stTabs [data-baseweb="tab"] {
            height: 2.6rem;
            padding: 0 1rem;
            border-radius: 11px;
            color: var(--muted);
            font-size: 0.80rem;
            font-weight: 800;
            letter-spacing: 0.02em;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.04);
            transition: color 120ms ease, background 120ms ease;
        }
        .stTabs [data-baseweb="tab"]:hover { color: var(--ink); background: rgba(77,200,220,0.08); }
        .stTabs [aria-selected="true"] {
            color: #040e12;
            background: linear-gradient(135deg, var(--blue), var(--green));
            box-shadow: 0 8px 24px rgba(77,200,220,0.22);
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
            box-shadow: var(--shadow-soft);
            padding: 1rem;
            transition: transform 140ms ease, border-color 140ms ease;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            border-color: rgba(77,200,220,0.30);
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
            border: 1px solid rgba(77,200,220,0.14);
            border-radius: var(--radius-lg);
            background: rgba(7,11,18,0.74);
            box-shadow: var(--shadow-soft);
            overflow: hidden;
        }
        div[data-testid="stExpander"] summary {
            font-weight: 800;
            font-size: 0.88rem;
            color: var(--soft);
        }
        [data-testid="stDataFrame"], .stDataFrame {
            border: 1px solid rgba(77,200,220,0.12);
            border-radius: var(--radius);
            overflow: hidden;
            box-shadow: var(--shadow-soft);
        }
        .js-plotly-plot { border-radius: var(--radius); overflow: hidden; }
        [data-testid="stPlotlyChart"] {
            position: relative;
            padding: 0.8rem 1rem;
            border: 1px solid rgba(77,200,220,0.12);
            border-radius: var(--radius-lg);
            background: linear-gradient(170deg, rgba(10,16,26,0.74), rgba(5,8,13,0.74));
            box-shadow: inset 20px 20px 40px rgba(77,200,220,0.015), var(--shadow-soft);
            transition: border-color 200ms ease;
        }
        [data-testid="stPlotlyChart"]:hover {
            border-color: rgba(77,200,220,0.22);
        }
        [data-testid="stRadio"] {
            padding: 0.4rem;
            border: 1px solid rgba(77,200,220,0.14);
            border-radius: var(--radius);
            background: rgba(6,10,16,0.58);
        }
        [data-testid="stRadio"] label { border-radius: 999px; padding: 0.16rem 0.32rem; }
        [data-testid="stPopover"] button,
        [data-testid="stDownloadButton"] button {
            min-height: 2.75rem;
            border-radius: 11px;
            border: 1px solid rgba(140,156,180,0.20);
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
            border-radius: 10px !important;
            border-color: rgba(140,156,180,0.20) !important;
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
            border: 1px solid rgba(77,200,220,0.22) !important;
            border-radius: 13px !important;
            background: #07101c !important;
            box-shadow: 0 16px 44px rgba(0,0,0,0.48) !important;
        }
        div[data-baseweb="popover"] li, div[role="option"] {
            min-height: 2.25rem !important;
            display: flex !important;
            align-items: center !important;
            border-radius: 9px !important;
            color: var(--soft) !important;
            line-height: 1.2 !important;
            white-space: nowrap !important;
        }
        div[data-baseweb="popover"] li:hover, div[role="option"]:hover {
            background: rgba(77,200,220,0.12) !important;
            color: var(--ink) !important;
        }

        /* ==========================================
         * 18. ALERTS, DIVIDERS
         * ==========================================
         */
        .stAlert {
            border-radius: var(--radius);
            border: 1px solid rgba(77,200,220,0.16);
            background: rgba(10,15,24,0.90);
            color: var(--ink);
        }
        hr { border-color: rgba(140,156,180,0.12); }

        /* ==========================================
         * 19. NUTRITION PAGE — macro cards & progress
         * ==========================================
         */
        .custom-progress-track {
            width: 100%;
            height: 10px;
            overflow: hidden;
            border-radius: 999px;
            background: rgba(22,30,44,0.80);
            border: 1px solid var(--line);
        }
        .custom-progress-fill {
            height: 100%;
            border-radius: 999px;
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
            border-color: rgba(77,200,220,0.28);
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
         * 20. VISUAL OVERHAUL LAYER
         * ==========================================
         */
        .stApp {
            background:
                linear-gradient(180deg, rgba(75,183,207,0.055) 0%, transparent 28%),
                linear-gradient(135deg, #080b10 0%, #0b1017 46%, #06080c 100%);
        }
        .stApp::before {
            background-image:
                linear-gradient(rgba(164,177,196,0.026) 1px, transparent 1px),
                linear-gradient(90deg, rgba(164,177,196,0.020) 1px, transparent 1px);
            background-size: 36px 36px;
            mask-image: linear-gradient(180deg, rgba(0,0,0,0.42), transparent 68%);
        }
        .block-container {
            max-width: 1440px;
            padding: 1rem 1.4rem 4rem;
        }
        header[data-testid="stHeader"] {
            background: rgba(7,10,15,0.72) !important;
            backdrop-filter: blur(14px);
        }
        .phi-page-head {
            padding: 1.05rem 1.15rem;
            margin: 0 0 1rem;
            border: 1px solid rgba(164,177,196,0.14);
            border-radius: var(--radius);
            background:
                linear-gradient(135deg, rgba(18,24,33,0.96), rgba(10,14,21,0.96)),
                linear-gradient(90deg, rgba(75,183,207,0.12), transparent 48%);
            box-shadow: var(--shadow-soft);
        }
        .phi-page-head h1 {
            font-size: clamp(1.8rem, 3.2vw, 2.65rem);
            line-height: 1.08;
            letter-spacing: -0.02em;
            background: none;
            -webkit-text-fill-color: var(--ink);
        }
        .phi-subtitle {
            max-width: 780px;
            color: var(--muted);
            font-size: 0.92rem;
        }
        .phi-status-chip {
            border-radius: var(--radius-sm);
            background: rgba(111,209,143,0.08);
            box-shadow: none;
        }
        .phi-sidebar-brand,
        .phi-card,
        .phi-insight,
        .phi-quiet-card,
        .phi-mini-widget,
        .phi-sidebar-card,
        .phi-action-bar,
        .macro-card,
        div[data-testid="stMetric"],
        div[data-testid="stExpander"],
        [data-testid="stPlotlyChart"],
        [data-testid="stDataFrame"],
        [data-testid="stDataEditor"] {
            border-radius: var(--radius) !important;
            border-color: rgba(164,177,196,0.15) !important;
            background: linear-gradient(180deg, rgba(18,24,33,0.92), rgba(10,14,21,0.92)) !important;
            box-shadow: var(--shadow-soft) !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
        }
        .phi-card,
        .phi-quiet-card,
        .phi-mini-widget,
        .phi-insight {
            min-height: 104px;
        }
        .phi-card::before,
        .phi-mini-widget::before,
        .phi-kpi-tile::before,
        .phi-command::before {
            opacity: 0.24;
        }
        .phi-card:hover,
        .phi-quiet-card:hover,
        .phi-mini-widget:hover,
        .phi-insight:hover,
        div[data-testid="stMetric"]:hover {
            transform: translateY(-1px);
            border-color: rgba(75,183,207,0.30) !important;
            box-shadow: 0 14px 32px rgba(0,0,0,0.30) !important;
        }
        .phi-command {
            padding: 1.35rem;
            border-radius: var(--radius) !important;
            border-top-width: 3px;
            background: linear-gradient(135deg, rgba(18,24,33,0.98), rgba(9,13,20,0.98)) !important;
            animation: none !important;
        }
        .phi-command-grid {
            gap: 1.35rem;
        }
        .phi-command-action {
            font-size: clamp(1.35rem, 2.1vw, 2rem);
            line-height: 1.16;
        }
        .phi-kpi-strip,
        .phi-quiet-grid,
        .phi-metric-rail {
            gap: 0.7rem;
        }
        .phi-kpi-tile {
            border-radius: var(--radius) !important;
            background: linear-gradient(180deg, rgba(18,24,33,0.92), rgba(10,14,21,0.92)) !important;
        }
        .phi-label,
        .phi-kpi-title,
        [data-testid="stMetricLabel"] {
            color: var(--muted);
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .phi-value,
        .phi-widget-value,
        .phi-kpi-value,
        .phi-rail-value,
        [data-testid="stMetricValue"] {
            color: var(--ink);
            font-family: var(--font-display);
            letter-spacing: -0.02em;
        }
        div[data-testid="stMetric"] {
            min-height: 110px;
            padding: 0.95rem 1rem;
            border-left: 3px solid var(--blue) !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.65rem;
            font-weight: 800;
        }
        [data-testid="stMetricDelta"] {
            font-size: 0.78rem;
            font-weight: 800;
        }
        .stButton > button,
        [data-testid="stFormSubmitButton"] button,
        [data-testid="stDownloadButton"] button,
        [data-testid="stPopover"] button {
            min-height: 2.55rem;
            border-radius: var(--radius-sm) !important;
            border: 1px solid rgba(164,177,196,0.18) !important;
            background: linear-gradient(180deg, rgba(30,39,52,0.98), rgba(16,21,30,0.98)) !important;
            color: var(--ink) !important;
            font-size: 0.83rem !important;
            font-weight: 800 !important;
            box-shadow: 0 8px 18px rgba(0,0,0,0.20);
            transition: transform 120ms ease, border-color 120ms ease, box-shadow 120ms ease;
        }
        .stButton > button:hover,
        [data-testid="stFormSubmitButton"] button:hover,
        [data-testid="stDownloadButton"] button:hover,
        [data-testid="stPopover"] button:hover {
            transform: translateY(-1px);
            border-color: rgba(75,183,207,0.36) !important;
            box-shadow: 0 10px 24px rgba(0,0,0,0.28);
        }
        .stButton > button[kind="primary"],
        [data-testid="stFormSubmitButton"] button[kind="primary"] {
            color: #051016 !important;
            border-color: rgba(111,209,143,0.38) !important;
            background: linear-gradient(135deg, var(--green), var(--blue)) !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.25rem;
            padding: 0.25rem;
            border: 1px solid rgba(164,177,196,0.14);
            border-radius: var(--radius);
            background: rgba(8,12,18,0.78);
            overflow-x: auto;
        }
        .stTabs [data-baseweb="tab"] {
            height: 2.35rem;
            padding: 0 0.85rem;
            border-radius: var(--radius-sm);
            color: var(--muted);
            font-size: 0.78rem;
            font-weight: 800;
            background: transparent;
            border: 0;
            white-space: nowrap;
        }
        .stTabs [aria-selected="true"] {
            color: var(--ink) !important;
            background: rgba(75,183,207,0.12) !important;
            box-shadow: inset 0 0 0 1px rgba(75,183,207,0.24);
        }
        .stTextInput input,
        .stNumberInput input,
        .stDateInput input,
        .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"],
        [data-baseweb="select"] {
            min-height: 2.55rem !important;
            border-radius: var(--radius-sm) !important;
            border: 1px solid rgba(164,177,196,0.18) !important;
            background: rgba(6,9,14,0.92) !important;
            color: var(--ink) !important;
            box-shadow: none !important;
        }
        .stTextInput input:focus,
        .stNumberInput input:focus,
        .stDateInput input:focus,
        .stTextArea textarea:focus {
            border-color: rgba(75,183,207,0.42) !important;
            box-shadow: 0 0 0 1px rgba(75,183,207,0.18) !important;
        }
        div[data-baseweb="popover"] ul,
        div[role="listbox"] {
            border-radius: var(--radius) !important;
            background: #0b111a !important;
        }
        [data-testid="stRadio"] {
            border-radius: var(--radius) !important;
            background: rgba(8,12,18,0.70);
        }
        [data-testid="stPlotlyChart"] {
            padding: 0.65rem 0.75rem;
        }
        .js-plotly-plot {
            border-radius: var(--radius-sm);
        }
        .stDataFrame,
        [data-testid="stDataEditor"] {
            overflow: hidden;
        }
        .stAlert {
            border-radius: var(--radius) !important;
            border-color: rgba(164,177,196,0.18) !important;
            background: rgba(14,18,25,0.96) !important;
        }
        .phi-section {
            margin: 1.15rem 0 0.65rem;
        }
        .phi-section-title {
            font-size: 1rem;
            letter-spacing: -0.01em;
        }
        .phi-section-caption,
        .phi-caption,
        p,
        li,
        label {
            color: var(--soft);
        }
        .custom-progress-track {
            height: 8px;
            border-radius: 999px;
            background: rgba(4,7,11,0.80);
        }

        .phi-home-hero h2 .phi-cursor {
            color: var(--green);
            animation: phi-blink 1s step-end infinite;
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
