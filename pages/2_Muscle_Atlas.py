import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import database
from components.design_system import apply_platform_theme, page_header, stat_card, insight_card
from components.sidebar import render_sidebar_shell
from components.body_heatmap import render_svg_body_heatmap
from core.muscle_mapping import CANONICAL_MUSCLE_GROUPS
from core.muscle_mapping import STIMULUS_TYPES
from core.muscle_mapping import load_muscle_map as engine_load_muscle_map
from core.muscle_mapping import normalize_group
from core.muscle_mapping import normalize_muscle_list
from core.muscle_mapping import normalize_stimulus_type
from core.muscle_mapping import save_muscle_map as engine_save_muscle_map
from core.muscle_mapping import unmapped_exercises as engine_unmapped_exercises
from core.readiness_engine import ReadinessInputs, calculate_readiness
from ui.theme import PHI_COLORS

st.set_page_config(page_title="Muscle Atlas Engine", layout="wide", page_icon="PHI")

# Apply PHI theme
apply_platform_theme()
render_sidebar_shell("pages/2_Muscle_Atlas.py")


# ── Helpers ──────────────────────────────────────────────────
def _atlas_path() -> str:
    return os.path.join(os.path.dirname(__file__), "..", "muscle_map.json")


def load_muscle_map() -> dict:
    return engine_load_muscle_map()


def save_muscle_map(data: dict) -> None:
    engine_save_muscle_map(data)


def parse_secondary_muscles(value) -> list[str]:
    return normalize_muscle_list(value)


# ============================================================
# PAGE HEADER
# ============================================================
page_header(
    "Biomechanical Muscle Atlas",
    "Map exercises to muscle groups. Powers your Recovery Radar and Stimulus Heatmaps.",
    eyebrow="Personal Health Intelligence",
)

m_map = load_muscle_map()

# ============================================================
# STATS ROW
# ============================================================
unique_muscles = sorted({normalize_group(v.get("primary_group", "Unknown")) for v in m_map.values()})
all_logged_exercises = database.get_unique_exercises()
unmapped_exercises = [
    e for e in engine_unmapped_exercises(all_logged_exercises, m_map)
    if e != "Session Duration"
]

c1, c2, c3 = st.columns(3)
with c1:
    stat_card("Mapped exercises", str(len(m_map)), "In the muscle atlas")
with c2:
    stat_card("Muscle groups", str(len(unique_muscles)), "Primary groups covered")
with c3:
    tone = "warn" if unmapped_exercises else "good"
    label = f"{len(unmapped_exercises)} need mapping" if unmapped_exercises else "All exercises mapped"
    insight_card("Atlas coverage", label, tone)

st.markdown("")

# ============================================================
# ENGINE STATUS — how atlas data feeds readiness
# ============================================================
from services.health_data import load_snapshot, kpi_summary
snapshot = load_snapshot(days=90)
summary = kpi_summary(snapshot)
readiness = summary["readiness_report"]

st.markdown(
    """
    <div class="phi-section">
        <div class="phi-section-title">Muscle Readiness Matrix</div>
        <div class="phi-section-caption">How atlas mapping feeds recovery, fatigue, and next-session recommendations.</div>
    </div>
    """,
    unsafe_allow_html=True,
)
ready = ", ".join(readiness["recovered_muscles"][:5]) or "No recovered groups yet"
fatigued = ", ".join(readiness["fatigued_muscles"][:5]) or "No high fatigue groups"
undertrained = ", ".join(readiness.get("undertrained_muscles", [])[:5]) or "No obvious undertrained gap"
imbalance = " ".join(readiness.get("imbalance_risks", [])[:2]) or "No major push/pull or leg balance warning."

c1, c2, c3, c4 = st.columns(4)
with c1:
    stat_card("Engine readiness", f"{readiness['score']}%", readiness["label"])
with c2:
    insight_card("Recovered groups", ready, "good")
with c3:
    insight_card("Fatigue watch", fatigued, "warn" if readiness["fatigued_muscles"] else "good")
with c4:
    insight_card("Training gap", undertrained, "warn" if readiness.get("undertrained_muscles") else "good")

insight_card("Atlas decision", f"{readiness.get('key_action', readiness['recommended_split'])} {imbalance}", "warn" if readiness.get("imbalance_risks") else "good")

svg_col, table_col = st.columns([1, 1.5])
with svg_col:
    st.markdown("##### Visual Readiness")
    render_svg_body_heatmap(readiness.get("muscle_status", []))

with table_col:
    st.markdown("##### Readiness Breakdown")
    status_df = pd.DataFrame(readiness["muscle_status"])
    if not status_df.empty:
        status_df = status_df.sort_values(["status", "readiness"], ascending=[True, True])
        st.dataframe(
            status_df.rename(
                columns={
                    "muscle": "Muscle",
                    "fatigue": "Fatigue",
                    "readiness": "Readiness",
                    "status": "Status",
                    "load_7d": "7d Load",
                    "last_trained": "Last Trained",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

st.markdown("")

# ============================================================
# UNMAPPED EXERCISES — Priority Quick-Map Panel
# ============================================================
if unmapped_exercises:
    with st.expander(f"{len(unmapped_exercises)} unmapped exercise(s) from your workout logs - click to map", expanded=True):
        st.caption("These exercises are in your workout logs but not yet in the muscle atlas. Map them to unlock the Recovery Radar and Stimulus Heatmaps.")

        MUSCLE_GROUPS = CANONICAL_MUSCLE_GROUPS

        updated_map = dict(m_map)
        any_mapped = False

        for ex in unmapped_exercises:
            col_name, col_muscle, col_secondary, col_btn = st.columns([2, 1.2, 1.5, 0.7])
            with col_name:
                st.markdown(f"**{ex}**")
            with col_muscle:
                primary = st.selectbox(
                    "Primary", MUSCLE_GROUPS,
                    key=f"unmap_primary_{ex}",
                    label_visibility="collapsed"
                )
            with col_secondary:
                secondary_raw = st.text_input(
                    "Secondary (comma-sep)", placeholder="e.g. Biceps, Core",
                    key=f"unmap_sec_{ex}",
                    label_visibility="collapsed"
                )
            with col_btn:
                if st.button("Map", key=f"unmap_btn_{ex}", type="primary"):
                    updated_map[ex] = {
                        "primary_group": normalize_group(primary),
                        "secondary_muscles": normalize_muscle_list(secondary_raw),
                        "tertiary_muscles": [],
                        "stimulus_type": "unknown",
                        "notes": "",
                    }
                    any_mapped = True

        if any_mapped:
            save_muscle_map(updated_map)
            st.toast("Atlas updated!")
            time.sleep(0.8)
            st.rerun()

    st.markdown("")

# ============================================================
# SEARCH + REGISTRY EDITOR
# ============================================================
st.markdown(
    """
    <div class="phi-section">
        <div class="phi-section-title">Global Exercise Registry</div>
        <div class="phi-section-caption">Search, edit, and sync the muscle map used by readiness and recovery analytics.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

col_s1, col_s2 = st.columns([2, 1])
search_query = col_s1.text_input("Search exercise", placeholder="e.g. Bench Press", label_visibility="collapsed").lower()

# Build display table
map_list = []
for ex, details in m_map.items():
    if search_query and search_query not in ex.lower():
        continue
    map_list.append({
        "Exercise": ex,
        "Primary Group": normalize_group(details.get("primary_group", "")),
        "Secondary Muscles": ", ".join(details.get("secondary_muscles", [])) if isinstance(details.get("secondary_muscles"), list) else details.get("secondary_muscles", ""),
        "Tertiary Muscles": ", ".join(details.get("tertiary_muscles", [])) if isinstance(details.get("tertiary_muscles"), list) else details.get("tertiary_muscles", ""),
        "Stimulus Type": normalize_stimulus_type(details.get("stimulus_type", "unknown")),
        "Form Cues": details.get("notes", ""),
    })

df = pd.DataFrame(map_list)

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Primary Group": st.column_config.SelectboxColumn(options=CANONICAL_MUSCLE_GROUPS),
        "Stimulus Type": st.column_config.SelectboxColumn(options=STIMULUS_TYPES),
    },
    key="atlas_editor",
)

# Save + Export row
c1, c2, c3 = st.columns([1, 1, 3])
if c1.button("Sync to Engine", type="primary", use_container_width=True):
    new_map = {}
    for _, row in edited_df.iterrows():
        name = str(row["Exercise"]).strip()
        if name and name.lower() != "nan":
            new_map[name] = {
                "primary_group": normalize_group(row["Primary Group"]),
                "secondary_muscles": parse_secondary_muscles(row["Secondary Muscles"]),
                "tertiary_muscles": parse_secondary_muscles(row["Tertiary Muscles"]),
                "stimulus_type": normalize_stimulus_type(row["Stimulus Type"]),
                "notes": str(row["Form Cues"]).strip(),
            }
    save_muscle_map(new_map)
    st.toast("Atlas updated. Biomechanical engines recalibrated.")
    time.sleep(0.8)
    st.rerun()

if c2.button("Export JSON", use_container_width=True):
    st.download_button(
        "Download Atlas File",
        data=json.dumps(m_map, indent=4),
        file_name="muscle_map.json",
    )

# ============================================================
# BIOMECHANICAL COVERAGE CHART
# ============================================================
st.markdown("")
st.markdown(
    """
    <div class="phi-section">
        <div class="phi-section-title">Biomechanical Coverage</div>
        <div class="phi-section-caption">Distribution of mapped exercises across primary muscle groups.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not df.empty:
    coverage = df["Primary Group"].value_counts().reset_index()
    coverage.columns = ["Muscle", "Exercises"]

    fig = go.Figure(
        go.Bar(
            x=coverage["Muscle"],
            y=coverage["Exercises"],
            marker=dict(
                color=coverage["Exercises"],
                colorscale=[[0, "rgba(47,159,104,0.20)"], [1, PHI_COLORS["green"]]],
                showscale=False,
                line=dict(width=0),
                cornerradius=4,
            ),
            hovertemplate="<b>%{x}</b><br>%{y} exercise(s)<extra></extra>",
            text=coverage["Exercises"],
            textposition="outside",
            textfont=dict(color=PHI_COLORS["muted"], size=11),
        )
    )
    fig.update_layout(
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, Inter, sans-serif", color=PHI_COLORS["muted"]),
        margin=dict(t=20, b=40, l=10, r=10),
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=11)),
        yaxis=dict(showgrid=True, gridcolor=PHI_COLORS["grid"], zeroline=False, title="Exercises mapped"),
        showlegend=False,
        hoverlabel=dict(bgcolor="#ffffff", font_color=PHI_COLORS["ink"], font_size=13),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
else:
    st.info("Add exercises to the atlas to see coverage breakdown.")
