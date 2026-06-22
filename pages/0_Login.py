import streamlit as st
from supabase_client import authenticate, is_authenticated

st.set_page_config(page_title="Login", page_icon="PHI", layout="centered")

# If already logged in, go straight to dashboard
if is_authenticated():
    st.switch_page("Fitness.py")

st.markdown(
    """
    <style>
        .stApp, [data-testid="stAppViewContainer"] {
            background-color: #000000 !important;
        }
        .login-box {
            max-width: 360px;
            margin: 0 auto;
            padding: 2.5rem 2rem;
            background: #080b08;
            border: 1px solid #1a2a1a;
        }
        .login-title {
            color: #33ff33;
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.5rem;
            font-weight: 800;
            margin-bottom: 0.25rem;
        }
        .login-sub {
            color: #5a7a5a;
            font-size: 0.8rem;
            font-family: 'JetBrains Mono', monospace;
            margin-bottom: 2rem;
            letter-spacing: 0.05em;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="login-title">PHI</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">Personal Health Intelligence</div>', unsafe_allow_html=True)

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        submitted = st.form_submit_button("Login", use_container_width=True)

    if submitted:
        if authenticate(email, password):
            st.rerun()
