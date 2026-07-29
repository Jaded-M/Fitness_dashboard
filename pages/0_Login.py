import streamlit as st
from components.design_system import apply_platform_theme
from supabase_client import authenticate, is_authenticated

st.set_page_config(page_title="Login", page_icon="PHI", layout="centered")
apply_platform_theme()

# If already logged in, go straight to dashboard
if is_authenticated():
    st.switch_page("Fitness.py")

st.markdown(
    """
    <style>
        [data-testid="stHeader"] {
            background: transparent !important;
        }
        .block-container {
            max-width: 520px;
            min-height: 100vh;
            display: grid;
            align-content: center;
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
        }
        .phi-login-panel {
            padding: 1.25rem;
            border: 1px solid rgba(50,216,255,0.20);
            border-radius: var(--radius-lg);
            background:
                linear-gradient(135deg, rgba(50,216,255,0.10), rgba(181,108,255,0.05)),
                rgba(8,13,23,0.94);
            box-shadow: var(--shadow);
        }
        .phi-login-kicker {
            color: var(--blue);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }
        .login-title {
            color: var(--ink);
            font-family: var(--font-display);
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 0.25rem;
            letter-spacing: 0;
        }
        .login-sub {
            color: var(--muted);
            font-size: 0.86rem;
            margin-bottom: 1.25rem;
            line-height: 1.5;
        }
        .phi-login-line {
            height: 1px;
            margin: 1rem 0 1.15rem;
            background: linear-gradient(90deg, var(--blue), var(--violet), transparent);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="phi-login-panel">', unsafe_allow_html=True)
st.markdown('<div class="phi-login-kicker">Secure Lab Access</div>', unsafe_allow_html=True)
st.markdown('<div class="login-title">PHI</div>', unsafe_allow_html=True)
st.markdown('<div class="login-sub">Personal Health Intelligence command center</div>', unsafe_allow_html=True)
st.markdown('<div class="phi-login-line"></div>', unsafe_allow_html=True)

with st.form("login_form"):
    email = st.text_input("Email", placeholder="your@email.com")
    password = st.text_input("Password", type="password", placeholder="Enter password")
    submitted = st.form_submit_button("Login", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

if submitted:
    if authenticate(email, password):
        st.rerun()
