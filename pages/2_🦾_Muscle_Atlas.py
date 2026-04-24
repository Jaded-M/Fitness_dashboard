import streamlit as st
import pandas as pd
import json
import plotly.express as px
import os
import sys
import time

# Absolute path fixes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database
import styles

st.set_page_config(page_title="Muscle Atlas Engine", layout="wide", page_icon="🦾")
st.markdown(styles.load_css(), unsafe_allow_html=True)

def load_muscle_map():
    if not os.path.exists("muscle_map.json"):
        return {}
    with open("muscle_map.json", "r") as f:
        return json.load(f)

def save_muscle_map(data):
    with open("muscle_map.json", "w") as f:
        json.dump(data, f, indent=4)

def parse_secondary_muscles(value):
    """Convert editor input into the list format used by chart logic."""
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if value is None or pd.isna(value):
        return []
    return [item.strip() for item in str(value).split(",") if item.strip()]

# Header
st.title("🦾 BIOMECHANICAL MUSCLE ATLAS")
st.markdown("""
<div class="glass-card" style="margin-bottom: 20px;">
    The Atlas is the <strong>Intelligence Layer</strong> of your dashboard. 
    It tells the app which muscles are being stimulated by each exercise, powering your 
    <strong>Recovery Radar</strong> and <strong>Stimulus Heatmaps</strong>.
</div>
""", unsafe_allow_html=True)

m_map = load_muscle_map()

# Quick Search & Stats
col_s1, col_s2, col_s3 = st.columns(3)
search_query = col_s1.text_input("🔍 Search Exercise...", placeholder="e.g. Bench Press").lower()
unique_muscles = sorted(list(set(v.get("primary_group", "Unknown") for v in m_map.values())))
col_s2.metric("🧬 Mapped Exercises", len(m_map))
col_s3.metric("🎯 Target Groups", len(unique_muscles))

# Main Editor
st.markdown("### 🗂️ Global Exercise Registry")

# Flatten the map for a data editor
map_list = []
for ex, details in m_map.items():
    if search_query and search_query not in ex.lower():
        continue
    map_list.append({
        "Exercise": ex,
        "Primary Muscle": details.get("primary_group", ""),
        "Secondary Muscles": details.get("secondary_muscles", ""),
        "Elite Form Cues": details.get("notes", "")
    })

df = pd.DataFrame(map_list)

# Use a clean data editor
edited_df = st.data_editor(
    df, 
    num_rows="dynamic", 
    use_container_width=True,
    column_config={
        "Primary Muscle": st.column_config.SelectboxColumn(
            options=["Chest", "Quads", "Hamstrings", "Back", "Shoulders", "Biceps", "Triceps", "Abs", "Calves", "Glutes", "Forearms"]
        )
    }
)

# Save Logic
c1, c2, c3 = st.columns([1, 1, 3])
if c1.button("💾 Sync to Engine", type="primary", use_container_width=True):
    new_map = {}
    for _, row in edited_df.iterrows():
        name = str(row["Exercise"]).strip()
        if name and name.lower() != "nan":
            new_map[name] = {
                "primary_group": str(row["Primary Muscle"]).strip(),
                "secondary_muscles": parse_secondary_muscles(row["Secondary Muscles"]),
                "notes": str(row["Elite Form Cues"]).strip()
            }
    save_muscle_map(new_map)
    st.toast("Atlas updated! Biomechanical engines recalibrated. 🦾")
    time.sleep(1)
    st.rerun()

if c2.button("📥 Export JSON", use_container_width=True):
    st.download_button(
        "Download Atlas File",
        data=json.dumps(m_map, indent=4),
        file_name="muscle_map.json"
    )

st.markdown("---")
st.markdown("### 🚦 Biomechanical Coverage")
# Simple bar chart of coverage
if not df.empty:
    coverage = df["Primary Muscle"].value_counts().reset_index()
    coverage.columns = ["Muscle", "Exercises"]
    fig = px.bar(coverage, x="Muscle", y="Exercises", color="Exercises", template="plotly_dark", color_continuous_scale="Viridis")
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
