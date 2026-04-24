import streamlit as st


def apply_platform_theme():
    """Apply the premium Personal Health Intelligence visual system."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            --bg: #070a12;
            --surface: #101622;
            --surface-2: #151d2c;
            --ink: #f8fafc;
            --muted: #9aa7b8;
            --line: rgba(148, 163, 184, 0.18);
            --blue: #38bdf8;
            --green: #34d399;
            --amber: #f59e0b;
            --rose: #fb7185;
            --violet: #a78bfa;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(56, 189, 248, 0.16), transparent 28rem),
                radial-gradient(circle at top right, rgba(167, 139, 250, 0.12), transparent 26rem),
                linear-gradient(180deg, #090d16 0%, var(--bg) 48%, #060812 100%);
            color: var(--ink);
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        .block-container {
            max-width: 1320px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        [data-testid="stSidebar"] {
            background: rgba(7, 10, 18, 0.96);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        [data-testid="stSidebar"] * {
            color: #e5e7eb;
        }

        h1, h2, h3 {
            letter-spacing: 0;
            color: var(--ink);
        }

        h1 {
            font-size: 2.35rem;
            line-height: 1.05;
            margin-bottom: 0.35rem;
        }

        .phi-eyebrow {
            color: var(--blue);
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 0.55rem;
        }

        .phi-subtitle {
            color: var(--muted);
            font-size: 1rem;
            max-width: 760px;
            margin-bottom: 1.2rem;
        }

        .phi-card {
            background: linear-gradient(180deg, rgba(21, 29, 44, 0.94), rgba(13, 18, 30, 0.94));
            border: 1px solid var(--line);
            border-radius: 14px;
            box-shadow: 0 18px 55px rgba(0, 0, 0, 0.28);
            padding: 1.05rem;
        }

        .phi-card.compact {
            padding: 0.9rem;
        }

        .phi-label {
            color: var(--muted);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .phi-value {
            color: var(--ink);
            font-size: 1.75rem;
            font-weight: 800;
            line-height: 1.15;
            margin-top: 0.4rem;
        }

        .phi-caption {
            color: var(--muted);
            font-size: 0.82rem;
            margin-top: 0.45rem;
        }

        .phi-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.85rem;
            margin: 1rem 0 1.2rem;
        }

        .phi-insight {
            border-left: 4px solid var(--blue);
            background: linear-gradient(180deg, rgba(21, 29, 44, 0.95), rgba(12, 17, 28, 0.95));
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 12px 34px rgba(0, 0, 0, 0.22);
            border-top: 1px solid var(--line);
            border-right: 1px solid var(--line);
            border-bottom: 1px solid var(--line);
        }

        .phi-insight.good { border-left-color: var(--green); }
        .phi-insight.warn { border-left-color: var(--amber); }
        .phi-insight.risk { border-left-color: var(--rose); }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.35rem;
            border-bottom: 1px solid var(--line);
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 999px 999px 0 0;
            padding: 0.75rem 1rem;
            color: var(--muted);
            font-weight: 700;
        }

        .stTabs [aria-selected="true"] {
            color: var(--blue);
            background: var(--surface);
            border: 1px solid var(--line);
            border-bottom-color: var(--surface);
        }

        .stButton > button {
            border-radius: 10px;
            border: 1px solid var(--line);
            font-weight: 750;
            min-height: 2.7rem;
            background: var(--surface-2);
            color: var(--ink);
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #38bdf8, #34d399);
            color: #06111c;
            border-color: rgba(56, 189, 248, 0.5);
        }

        div[data-testid="stMetric"] {
            background: linear-gradient(180deg, rgba(21, 29, 44, 0.94), rgba(12, 17, 28, 0.94));
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 1rem;
            box-shadow: 0 14px 38px rgba(0, 0, 0, 0.22);
        }

        [data-testid="stMetricValue"] {
            color: var(--ink);
            font-size: 1.55rem;
            font-weight: 800;
        }

        [data-testid="stMetricLabel"] {
            color: var(--muted);
            font-weight: 700;
        }

        .stDataFrame, [data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 12px;
            overflow: hidden;
        }

        .stAlert {
            background: rgba(21, 29, 44, 0.85);
            color: var(--ink);
        }

        @media (max-width: 980px) {
            .phi-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }

        @media (max-width: 640px) {
            .phi-grid {
                grid-template-columns: 1fr;
            }

            h1 {
                font-size: 1.85rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title, subtitle, eyebrow="Personal Health Intelligence"):
    st.markdown(
        f"""
        <div class="phi-eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <div class="phi-subtitle">{subtitle}</div>
        """,
        unsafe_allow_html=True,
    )


def stat_card(label, value, caption="", tone=""):
    tone_class = f" {tone}" if tone else ""
    st.markdown(
        f"""
        <div class="phi-card compact{tone_class}">
            <div class="phi-label">{label}</div>
            <div class="phi-value">{value}</div>
            <div class="phi-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_card(title, body, tone=""):
    tone_class = f" {tone}" if tone else ""
    st.markdown(
        f"""
        <div class="phi-insight{tone_class}">
            <div class="phi-label">{title}</div>
            <div style="font-weight:650; margin-top:0.45rem;">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
