def load_css():
    """
    Returns the Elite v2 CSS for the app.
    Professional, clean, high-contrast Health-App aesthetic.
    """
    return """
    <style>
        /* ==========================================
         * 1. GOOGLE FONTS IMPORT
         * ==========================================
         */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@300;400;500;600;700;800&display=swap');

        /* ==========================================
         * 2. GLOBAL THEME — Deep Abyss / Frost Blue
         * ==========================================
         */
        .stApp {
            background-color: #0B0E14;
            color: #F8FAFC;
            font-family: 'Outfit', 'Inter', -apple-system, sans-serif;
        }

        /* -----------------------------------------------------------
         * 3. CLEAN ANIMATIONS
         * ----------------------------------------------------------- */
        @keyframes subtleFadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .stApp > div {
            animation: subtleFadeIn 0.6s ease-out forwards;
        }

        /* ==========================================
         * 4. PROFESSIONAL CARDS (Elite v2)
         * ==========================================
         */
        /* Metric Cards, Expanders, and Generic Containers */
        div[data-testid="stMetric"], .stExpander, div[data-testid="stForm"], .element-container div.stMarkdown div.st-ae {
            background: #111827 !important;
            border: 1px solid #1F2937 !important;
            border-radius: 12px !important;
            padding: 20px !important;
            transition: all 0.3s ease !important;
        }

        /* Metric Lift Effect */
        div[data-testid="stMetric"]:hover {
            border-color: #38BDF8 !important;
            background: #161E2E !important;
            box-shadow: 0 10px 30px -10px rgba(56, 189, 248, 0.2) !important;
        }

        /* Metric Values - High Contrast Frost Blue */
        [data-testid="stMetricValue"] {
            font-family: 'Outfit', sans-serif !important;
            font-size: 2.2rem !important;
            font-weight: 700 !important;
            color: #38BDF8 !important;
            letter-spacing: -0.02em;
        }

        [data-testid="stMetricLabel"] {
            font-weight: 600 !important;
            font-size: 0.75rem !important;
            color: #94A3B8 !important;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }

        /* ==========================================
         * 5. TYPOGRAPHY
         * ==========================================
         */
        h1 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 800 !important;
            font-size: 2.8rem !important;
            color: #FFFFFF !important;
            letter-spacing: -0.04em !important;
            margin-bottom: 1.5rem !important;
        }

        h2, h3, h4, h5 {
            font-family: 'Outfit', sans-serif !important;
            color: #F1F5F9 !important;
            font-weight: 700 !important;
        }

        /* ==========================================
         * 6. MINIMALIST TABS
         * ==========================================
         */
        .stTabs [data-baseweb="tab-list"] {
            background: transparent !important;
            padding-bottom: 1px;
            border-bottom: 1px solid #1F2937 !important;
            gap: 20px;
        }

        .stTabs [data-baseweb="tab"] {
            background: transparent !important;
            color: #64748B !important;
            font-weight: 600 !important;
            border: none !important;
            padding: 8px 0px !important;
            transition: color 0.2s ease !important;
        }

        .stTabs [aria-selected="true"] {
            color: #38BDF8 !important;
            border-bottom: 2px solid #38BDF8 !important;
        }

        /* ==========================================
         * 7. BUTTONS (Utility First)
         * ==========================================
         */
        .stButton > button {
            background-color: #38BDF8 !important;
            color: #0F172A !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
            padding: 10px 24px !important;
            transition: all 0.2s ease !important;
            border: none !important;
        }

        .stButton > button:hover {
            background-color: #7DD3FC !important;
            transform: scale(1.02);
        }

        /* Secondary Button Style */
        .stButton > button[kind="secondary"] {
            background-color: #1F2937 !important;
            color: #F8FAFC !important;
            border: 1px solid #374151 !important;
        }

        /* ==========================================
         * 8. INPUTS & SELECTS
         * ==========================================
         */
        .stTextInput input, .stSelectbox [data-baseweb="select"], .stNumberInput input {
            background-color: #1F2937 !important;
            border: 1px solid #374151 !important;
            border-radius: 8px !important;
            color: #F8FAFC !important;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #0B0E14 !important;
            border-right: 1px solid #1F2937 !important;
        }

        /* ==========================================
         * 9. STATUS & INSIGHTS (Minimalist)
         * ==========================================
         */
        .advisor-badge, .insight-card, .warning-card {
            border-radius: 10px !important;
            padding: 16px !important;
            margin-bottom: 12px;
            background: #111827 !important;
            border: 1px solid #1F2937 !important;
        }

        .advisor-badge { border-left: 4px solid #38BDF8 !important; }
        .insight-card { border-left: 4px solid #A855F7 !important; }
        .warning-card { border-left: 4px solid #EF4444 !important; }

    </style>
    """
