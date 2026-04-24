def load_css():
    """
    Returns all custom CSS for the app.
    """
    return """
    <style>
        /* ==========================================
         * 1. GOOGLE FONTS IMPORT
         * ==========================================
         */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@300;400;500;600;700;800&display=swap');

        /* ==========================================
         * 2. GLOBAL APP THEME — Midnight Obsidian
         * ==========================================
         */
        .stApp {
            background: linear-gradient(135deg, #05070a 0%, #0a0e17 50%, #05070a 100%);
            background-attachment: fixed;
            color: #f8fafc;
            font-family: 'Outfit', 'Inter', sans-serif;
        }

        /* -----------------------------------------------------------
         * 3. ELITE ANIMATIONS
         * ----------------------------------------------------------- */
        @keyframes fadeIn {
            from { opacity: 0; filter: blur(10px); }
            to { opacity: 1; filter: blur(0); }
        }

        @keyframes slideUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Apply global entry animation */
        .stApp > div {
            animation: fadeIn 0.8s ease-out forwards;
        }

        /* ==========================================
         * 4. GLASSMORPHISM CARDS
         * ==========================================
         */
        div[data-testid="stMetric"], .glass-card, [data-testid="stExpander"] {
            background: rgba(255, 255, 255, 0.03) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border-radius: 20px !important;
            padding: 24px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4) !important;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        div[data-testid="stMetric"]:hover {
            transform: translateY(-5px) scale(1.01) !important;
            background: rgba(255, 255, 255, 0.05) !important;
            border-color: rgba(0, 210, 255, 0.3) !important;
            box-shadow: 0 20px 60px rgba(0, 210, 255, 0.1) !important;
        }

        /* Metric Detail Styling */
        [data-testid="stMetricValue"] {
            font-family: 'Outfit', sans-serif !important;
            font-size: 32px !important;
            font-weight: 700 !important;
            background: linear-gradient(90deg, #00d2ff, #b14fff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        [data-testid="stMetricLabel"] {
            font-weight: 500 !important;
            font-size: 12px !important;
            color: #94a3b8 !important;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        /* ==========================================
         * 5. TYPOGRAPHY & HEADERS
         * ==========================================
         */
        h1 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 800 !important;
            font-size: 2.5rem !important;
            letter-spacing: -1px !important;
            background: linear-gradient(to right, #ffffff, #00d2ff, #b14fff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 2rem !important;
        }

        h2, h3, h4, h5 {
            font-family: 'Outfit', sans-serif !important;
            color: #f1f5f9 !important;
            letter-spacing: -0.5px !important;
        }

        /* ==========================================
         * 6. PREMIUM TABS
         * ==========================================
         */
        .stTabs [data-baseweb="tab-list"] {
            background: rgba(255, 255, 255, 0.02) !important;
            border-radius: 12px !important;
            padding: 6px !important;
            gap: 10px;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 10px !important;
            background: transparent !important;
            color: #94a3b8 !important;
            font-weight: 500 !important;
            border: none !important;
            transition: all 0.3s ease !important;
        }

        .stTabs [aria-selected="true"] {
            background: rgba(0, 210, 255, 0.1) !important;
            color: #00d2ff !important;
            box-shadow: 0 4px 15px rgba(0, 210, 255, 0.1) !important;
        }

        /* ==========================================
         * 7. BUTTONS (SaaS Aesthetic)
         * ==========================================
         */
        .stButton > button {
            background: linear-gradient(135deg, #00d2ff 0%, #008ebf 100%) !important;
            color: #0f172a !important;
            border-radius: 12px !important;
            border: none !important;
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: 0.5px !important;
            padding: 14px 28px !important;
            box-shadow: 0 8px 24px rgba(0, 210, 255, 0.25) !important;
            transition: all 0.3s ease !important;
        }

        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 12px 32px rgba(0, 210, 255, 0.45) !important;
            filter: brightness(1.1) !important;
        }

        /* Secondary/Ghost Buttons */
        .stButton > button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.05) !important;
            color: #f8fafc !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }

        /* ==========================================
         * 8. INPUTS & SELECTORS
         * ==========================================
         */
        .stTextInput input, .stSelectbox [data-baseweb="select"] {
            background: rgba(15, 23, 42, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            color: #f8fafc !important;
        }

        /* Segmented Control (Radios) */
        div[role="radiogroup"] {
            background: rgba(15, 23, 42, 0.6) !important;
            border-radius: 12px !important;
            padding: 6px !important;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #0a0e17 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        }

        /* ==========================================
         * 9. STATUS CARDS
         * ==========================================
         */
        .advisor-badge, .insight-card, .warning-card {
            border-radius: 14px !important;
            padding: 16px 20px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(5px);
            margin-bottom: 12px;
        }

        .advisor-badge { 
            background: rgba(0, 210, 255, 0.08) !important; 
            border-left: 4px solid #00d2ff !important;
        }
        .insight-card { 
            background: rgba(177, 79, 255, 0.08) !important; 
            border-left: 4px solid #b14fff !important;
        }
        .warning-card { 
            background: rgba(255, 121, 198, 0.08) !important; 
            border-left: 4px solid #ff79c6 !important;
        }

    </style>
    """
