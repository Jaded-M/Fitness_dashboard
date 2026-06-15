from __future__ import annotations

from html import escape

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from components.design_system import insight_card, stat_card
from components.widgets import render_readiness_ring
from services.health_data import (
    HealthSnapshot,
    daily_nutrition,
    daily_steps,
    habit_consistency,
    kpi_summary,
    readiness_summary,
    weekly_report,
    weight_trend,
    workout_highlights,
)
import database
from core.muscle_mapping import canonical_exercise_name, dedupe_exercise_names
from ui.theme import CHART_CONFIG, PHI_COLORS, chart_layout
from ui.charts import (
    render_consistency_heatmap,
    render_progression_tab,
    render_rpg_tab,
    render_split_volume_tab,
)


def _layout(height=380):
    return chart_layout(
        height=height,
        xaxis={"tickformat": "%d %b", "title": ""},
        yaxis={"rangemode": "tozero"},
    )


def render_kpis(snapshot: HealthSnapshot, calorie_goal: int, step_goal: int):
    summary = kpi_summary(snapshot, calorie_goal, step_goal)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("Today calories", f"{summary['today_calories']:,}", f"Goal {calorie_goal:,} kcal")
    with c2:
        stat_card("Today protein", f"{summary['today_protein']}g", "Fuel for training")
    with c3:
        stat_card("Today steps", f"{summary['today_steps']:,}", f"Goal {step_goal:,}")
    with c4:
        value = f"{summary['latest_weight']:.1f} kg" if summary["latest_weight"] else "No log"
        delta = summary["weight_delta"]
        caption = "Start logging weight" if delta is None else f"{delta:+.1f} kg across records"
        stat_card("Latest weight", value, caption)


def _section(title: str, caption: str = ""):
    st.markdown(
        f"""
        <div class="phi-section">
            <div class="phi-section-title">{escape(title)}</div>
            <div class="phi-section-caption">{escape(caption)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _pill_list(items: list[str], tone: str = "", empty: str = "None") -> str:
    if not items:
        return f'<span class="phi-pill">{escape(empty)}</span>'
    tone_class = f" {tone}" if tone else ""
    return "".join(f'<span class="phi-pill{tone_class}">{escape(item)}</span>' for item in items)


def render_primary_layer(snapshot: HealthSnapshot, calorie_goal: int, step_goal: int):
    """Readiness-led command center: answer what matters before showing analytics."""
    summary = kpi_summary(snapshot, calorie_goal, step_goal)
    readiness = summary["readiness_report"]
    recovered = readiness["recovered_muscles"][:5]
    fatigued = readiness["fatigued_muscles"][:5]
    warnings = readiness["warnings"][:2] + readiness.get("imbalance_risks", [])[:1]
    warning_text = " ".join(warnings) if warnings else "No critical readiness blocker detected."
    warning_tone = "risk" if readiness["score"] < 45 or readiness["fatigued_muscles"] else "good"

    st.markdown(
        f"""
        <div class="phi-command {warning_tone}">
            <div class="phi-command-grid">
                <div>
        """,
        unsafe_allow_html=True,
    )
    render_readiness_ring(readiness["score"], readiness["label"])
    st.markdown(
        f"""
                </div>
                <div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
                        <div>
                            <div class="phi-label">What matters now</div>
                            <div class="phi-command-action">{escape(readiness.get('key_action', readiness['recommended_split']))}</div>
                            <div class="phi-caption" style="margin-top:0.7rem">{escape(readiness['recommended_split'])}</div>
                            <div style="margin-top:0.75rem">
                                {_pill_list(recovered, "good", "No recovered group yet")}
                            </div>
                        </div>
                        <div>
                            <div class="phi-label">Load management</div>
                            <div style="margin-top:0.5rem">{_pill_list(fatigued, "risk", "No high fatigue group")}</div>
                            <div class="phi-caption" style="margin-top:0.75rem">{escape(warning_text)}</div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="phi-metric-rail">
                <div class="phi-rail-item"><div class="phi-label">Recovery</div><div class="phi-rail-value">{readiness['recovery_score']}%</div></div>
                <div class="phi-rail-item"><div class="phi-label">Training load</div><div class="phi-rail-value">{readiness['training_load_score']}%</div></div>
                <div class="phi-rail-item"><div class="phi-label">Fuel</div><div class="phi-rail-value">{readiness['nutrition_score']}%</div></div>
                <div class="phi-rail-item"><div class="phi-label">Activity</div><div class="phi-rail-value">{readiness['activity_score']}%</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if warnings:
        st.markdown("")
        insight_card("Priority signal", warning_text, warning_tone)


def render_secondary_layer(snapshot: HealthSnapshot, calorie_goal: int, step_goal: int):
    summary = kpi_summary(snapshot, calorie_goal, step_goal)
    habits = habit_consistency(snapshot, calorie_goal, step_goal)
    highlights = workout_highlights(snapshot)

    weight_value = summary["weight_trend_direction"]
    weight_caption = "Need more weigh-ins" if summary["weekly_weight_change"] is None else f"{summary['weekly_weight_change']:+.2f} kg/week"

    st.markdown(
        f"""
        <div class="phi-quiet-grid">
            <div class="phi-quiet-card"><div class="phi-label">Body trend</div><div class="phi-rail-value">{escape(weight_value)}</div><div class="phi-caption">{escape(weight_caption)}</div></div>
            <div class="phi-quiet-card"><div class="phi-label">Nutrition</div><div class="phi-rail-value">{summary['calorie_adherence']}%</div><div class="phi-caption">Calorie adherence</div></div>
            <div class="phi-quiet-card"><div class="phi-label">Activity</div><div class="phi-rail-value">{summary['activity_score']}%</div><div class="phi-caption">{summary['avg_steps']:,} avg steps</div></div>
            <div class="phi-quiet-card"><div class="phi-label">Performance</div><div class="phi-rail-value">{escape(str(highlights['best_lift']))}</div><div class="phi-caption">{escape(str(highlights['volume_note']))}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def render_recovery_matrix(snapshot: HealthSnapshot, calorie_goal: int, step_goal: int, key: str = "recovery_matrix"):
    """Muscle-level recovery/load matrix for the recovery tab."""
    readiness = readiness_summary(snapshot, calorie_goal, step_goal)
    status = pd.DataFrame(readiness.get("muscle_status", []))
    if status.empty:
        st.info("Log mapped workouts to unlock muscle recovery analytics.")
        return

    status = status.sort_values("readiness", ascending=True)
    color_map = {"Ready": PHI_COLORS["green"], "Manage load": PHI_COLORS["amber"], "Fatigued": PHI_COLORS["rose"]}
    colors = [color_map.get(value, PHI_COLORS["muted"]) for value in status["status"]]

    fig = make_subplots(
        rows=1,
        cols=2,
        column_widths=[0.55, 0.45],
        horizontal_spacing=0.12,
        subplot_titles=("Muscle readiness", "7-day training load"),
    )
    fig.add_trace(
        go.Bar(
            x=status["readiness"],
            y=status["muscle"],
            orientation="h",
            marker_color=colors,
            name="Readiness",
            hovertemplate="<b>%{y}</b><br>Readiness: %{x:.0f}%<extra></extra>",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=status["load_7d"],
            y=status["muscle"],
            orientation="h",
            marker_color=PHI_COLORS["blue"],
            name="Load",
            hovertemplate="<b>%{y}</b><br>7-day load: %{x:,.0f}<extra></extra>",
        ),
        row=1,
        col=2,
    )
    layout = _layout(height=max(360, len(status) * 32 + 110))
    layout.update(
        title="Recovery and load matrix",
        showlegend=False,
        xaxis={"range": [0, 100], "title": "Readiness %", "gridcolor": "rgba(148,163,184,0.12)", "zeroline": False},
        xaxis2={"title": "Load", "gridcolor": "rgba(148,163,184,0.12)", "zeroline": False},
        yaxis={"showgrid": False, "zeroline": False},
        yaxis2={"showgrid": False, "zeroline": False, "showticklabels": False},
    )
    for ann in layout.get("annotations", []):
        ann.update(font={"color": "#a7b0ae", "size": 11})
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG, key=key)


def render_weight_chart(snapshot: HealthSnapshot, key: str = "weight_trend_chart"):
    df = weight_trend(snapshot)
    if df.empty:
        st.info("Log weight to unlock the trend chart.")
        return

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Weight"],
            mode="markers",
            name="Daily weight",
            marker={"size": 8, "color": "rgba(37, 99, 235, 0.45)"},
            hovertemplate="%{x|%d %b}<br>%{y:.1f} kg<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Trend"],
            mode="lines",
            name="Smoothed trend",
            line={"color": "#f8fafc", "width": 3},
            hovertemplate="%{x|%d %b}<br>Trend %{y:.1f} kg<extra></extra>",
        )
    )
    fig.update_layout(**_layout(height=420), title="Weight trend")
    fig.update_yaxes(title_text="Weight (kg)")
    st.plotly_chart(fig, width="stretch", config=CHART_CONFIG, key=key)


def render_nutrition_chart(snapshot: HealthSnapshot, calorie_goal: int, key: str = "nutrition_adherence_chart"):
    """
    Stacked subplot: calories bar (top) + protein line (bottom).
    Eliminates dual-axis confusion and improves readability.
    """
    df = daily_nutrition(snapshot)
    if df.empty:
        st.info("Log meals to see calorie and protein trends.")
        return

    # Compute adherence for annotation
    on_target = df["Calories"].between(calorie_goal * 0.85, calorie_goal * 1.08)
    adherence_pct = int(on_target.mean() * 100) if len(df) else 0
    avg_cal = int(df["Calories"].mean()) if len(df) else 0

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.10,
        subplot_titles=("Calories vs Goal", "Protein intake"),
        row_heights=[0.60, 0.40],
    )

    # ── Row 1: Calorie bars ────────────────────────────────────
    bar_colors = [
        "#34d399" if on else "rgba(37,99,235,0.45)"
        for on in on_target
    ]
    fig.add_trace(
        go.Bar(
            x=df["Date"],
            y=df["Calories"],
            name="Calories",
            marker_color=bar_colors,
            hovertemplate="<b>%{x|%a %d %b}</b><br>Calories: %{y:,} kcal<extra></extra>",
        ),
        row=1, col=1,
    )
    # Goal line
    fig.add_hline(
        y=calorie_goal,
        line_dash="dot",
        line_color="#f59e0b",
        line_width=1.5,
        annotation_text=f"Goal {calorie_goal:,}",
        annotation_font_color="#f59e0b",
        annotation_font_size=11,
        row=1, col=1,
    )
    # Average line
    fig.add_hline(
        y=avg_cal,
        line_dash="dash",
        line_color="rgba(148,163,184,0.5)",
        line_width=1,
        annotation_text=f"Avg {avg_cal:,}",
        annotation_font_color="#68766f",
        annotation_font_size=10,
        row=1, col=1,
    )

    # ── Row 2: Protein line ────────────────────────────────────
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Protein"],
            name="Protein (g)",
            mode="lines+markers",
            line={"color": "#059669", "width": 2.5},
            marker={"size": 6, "color": "#059669"},
            fill="tozeroy",
            fillcolor="rgba(5,150,105,0.08)",
            hovertemplate="<b>%{x|%a %d %b}</b><br>Protein: %{y}g<extra></extra>",
        ),
        row=2, col=1,
    )

    # ── Layout ─────────────────────────────────────────────────
    layout = _layout(height=520)
    layout.update(
        title=f"Nutrition adherence — {adherence_pct}% on target",
        showlegend=True,
        legend={"orientation": "h", "y": 1.06, "x": 0, "font": {"size": 11}},
        margin={"l": 18, "r": 18, "t": 58, "b": 38},
        xaxis2={"tickformat": "%d %b", "showgrid": False, "zeroline": False},
        yaxis={"title": "kcal", "gridcolor": "rgba(148,163,184,0.12)", "zeroline": False},
        yaxis2={"title": "g", "gridcolor": "rgba(148,163,184,0.12)", "zeroline": False},
    )
    # Subplot titles styling
    for ann in layout.get("annotations", []):
        ann.update(font={"color": "#68766f", "size": 11})
    fig.update_layout(**layout)
    st.plotly_chart(fig, width="stretch", config=CHART_CONFIG, key=key)


def render_steps_chart(snapshot: HealthSnapshot, step_goal: int, key: str = "activity_trend_chart"):
    df = daily_steps(snapshot)
    if df.empty:
        st.info("Log steps to see activity trends.")
        return

    # Three-tier colour coding
    def _step_color(s):
        if s >= step_goal:
            return "#34d399"        # green — goal hit
        elif s >= step_goal * 0.7:
            return "#197f96"        # blue - close
        return "#94a3b8"            # slate — far off

    colors = [_step_color(s) for s in df["Steps"]]
    avg_steps = int(df["Steps"].mean()) if len(df) else 0
    max_steps = max(float(df["Steps"].max()), float(step_goal), 1)

    fig = go.Figure(
        go.Bar(
            x=df["Date"],
            y=df["Steps"],
            marker_color=colors,
            hovertemplate="<b>%{x|%a %d %b}</b><br>Steps: %{y:,}<extra></extra>",
            name="Daily steps",
        )
    )
    # Goal reference
    fig.add_hline(
        y=step_goal,
        line_dash="dot",
        line_color="#2563eb",
        line_width=1.5,
        annotation_text=f"Goal {step_goal:,}",
        annotation_font_color="#2563eb",
        annotation_font_size=11,
    )
    # 7-day average
    fig.add_hline(
        y=avg_steps,
        line_dash="dash",
        line_color="rgba(148,163,184,0.55)",
        line_width=1,
        annotation_text=f"Avg {avg_steps:,}",
        annotation_font_color="#68766f",
        annotation_font_size=10,
    )
    layout = _layout(height=400)
    layout.update(
        title=f"Activity trend — avg {avg_steps:,} steps/day",
        yaxis={
            "title": "Steps",
            "gridcolor": "rgba(148, 163, 184, 0.14)",
            "zeroline": False,
            "range": [0, max_steps * 1.18],
        },
        showlegend=False,
    )
    fig.update_layout(**layout)
    st.plotly_chart(fig, width="stretch", config=CHART_CONFIG, key=key)


def render_training_table(snapshot: HealthSnapshot, key: str = "training_history_table"):
    """
    Recent training log. Rows with per-set JSON show a detail expander;
    older summary-only rows display the flat summary columns.
    """
    import json

    if snapshot.workouts.empty:
        st.info("Log workouts to build your progression history.")
        return

    df = snapshot.workouts.copy().head(40)
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%d %b %Y")

    # Split rows: detailed (has set_data) vs summary (old format)
    has_detail = df["set_data"].notna() & (df["set_data"] != "") if "set_data" in df.columns else pd.Series(False, index=df.index)
    detail_rows  = df[has_detail]
    summary_rows = df[~has_detail][["Date", "Split", "Workout", "Sets", "Reps", "Weight"]]

    if not detail_rows.empty:
        st.markdown("**Recent sessions — per-set detail**")
        # Group by date + split for display
        grouped = detail_rows.groupby(["Date", "Split"], sort=False)
        for (log_date, split), group in grouped:
            label = f"{log_date}  ·  {split}  ·  {len(group)} exercise(s)"
            with st.expander(label, expanded=False):
                for _, row in group.iterrows():
                    exercise_name = row["Workout"]
                    try:
                        sets = json.loads(row["set_data"]) if row["set_data"] else []
                    except (json.JSONDecodeError, TypeError):
                        sets = []

                    if sets:
                        sets_df = pd.DataFrame(sets)
                        sets_df.index = range(1, len(sets_df) + 1)
                        sets_df.index.name = "Set"
                        # Rename columns for display
                        col_map = {"weight": "Weight (kg)", "reps": "Reps",
                                   "rpe": "RPE", "note": "Note"}
                        sets_df = sets_df.rename(columns={k: v for k, v in col_map.items() if k in sets_df.columns})
                        # Highlight max weight row
                        if "Weight (kg)" in sets_df.columns:
                            max_w = sets_df["Weight (kg)"].max()
                        else:
                            max_w = None

                        st.markdown(
                            f"<span style='font-size:0.82rem;font-weight:700;"
                            f"color:#68766f;letter-spacing:0.06em;text-transform:uppercase'>"
                            f"{exercise_name}</span>"
                            + (f"<span style='color:#34d399;font-size:0.8rem;margin-left:8px'>"
                               f"Top {max_w:.1f} kg</span>" if max_w else ""),
                            unsafe_allow_html=True,
                        )
                        st.dataframe(
                            sets_df,
                            use_container_width=True,
                            key=f"{key}_detail_{row.name}",
                        )
                    else:
                        st.markdown(
                            f"<span style='font-size:0.82rem;color:#68766f'>"
                            f"{exercise_name} — {row['Sets']} sets × {row['Reps']} reps @ {row['Weight']} kg</span>",
                            unsafe_allow_html=True,
                        )

    if not summary_rows.empty:
        st.markdown("**Earlier logs**")
        st.dataframe(summary_rows, use_container_width=True, hide_index=True, key=key)



def render_workout_progression(snapshot: HealthSnapshot, key_prefix: str = "training"):
    """
    Full workout analytics panel: consistency heatmap, progression chart,
    split volume / PR breakdown, and gamification.
    """
    workouts = snapshot.workouts
    if workouts.empty:
        st.info("Log workouts to unlock progression analytics.")
        return

    real_df = workouts[workouts["Workout"] != "Session Duration"].copy()
    if real_df.empty:
        st.info("Log exercises (not just session durations) to unlock progression charts.")
        return

    # Ensure Date is datetime
    real_df["Date"] = pd.to_datetime(real_df["Date"], errors="coerce")

    real_df["WorkoutCanonical"] = real_df["Workout"].apply(canonical_exercise_name)
    all_exercises = sorted(dedupe_exercise_names(real_df["Workout"].unique().tolist()))
    best_df = database.get_best_lifts()

    prog_tab, split_tab, pr_tab, heat_tab = st.tabs(
        ["📈 Progression", "🥧 Split Volume", "🏆 Personal Records", "🟩 Heatmap"]
    )

    with prog_tab:
        render_progression_tab(
            real_df.assign(Workout=real_df["WorkoutCanonical"]),
            all_exercises,
            key=f"{key_prefix}_prog_ex",
            chart_key=f"{key_prefix}_progression_chart",
        )

    with split_tab:
        if not real_df.empty:
            render_split_volume_tab(real_df, key_prefix=f"{key_prefix}_split")
        else:
            st.info("Log splits to see volume distribution.")

    with pr_tab:
        render_rpg_tab(real_df, best_df, key_prefix=f"{key_prefix}_pr")

    with heat_tab:
        render_consistency_heatmap(workouts, key=f"{key_prefix}_heatmap")


def render_checkins(snapshot: HealthSnapshot, key: str = "checkins_table"):
    if snapshot.checkins.empty:
        st.info("Use daily check-ins to connect mood, sleep, and performance.")
        return
    df = snapshot.checkins.head(12).copy()
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%d %b %Y")
    df = df.rename(columns={"date": "Date", "mood": "Mood", "energy": "Energy", "sleep_hours": "Sleep", "note": "Note"})
    st.dataframe(df[["Date", "Mood", "Energy", "Sleep", "Note"]], width="stretch", hide_index=True, key=key)


def render_activity_sync_panel(snapshot: HealthSnapshot, step_goal: int, sync_fn):
    st.subheader("Activity sync")
    left, right = st.columns([1.15, 0.85])

    with left:
        st.caption("Keep manual logging, but use Google Fit when you want a clean backfill.")
        range_choice = st.selectbox("Sync window", [7, 30, 90, 180], index=1, key="activity_sync_window")
        if st.button("Sync Google Fit", type="primary", width="stretch"):
            end_date = pd.Timestamp.now().date()
            start_date = end_date - pd.Timedelta(days=range_choice)
            ok, message = sync_fn(start_date, end_date)
            if ok:
                st.success(message)
                st.rerun()
            else:
                st.warning(message)

    with right:
        summary = kpi_summary(snapshot, step_goal=step_goal)
        stat_card("Average steps", f"{summary['avg_steps']:,}", "Last 7 logged days")
        stat_card("Goal hit rate", f"{summary['activity_score']}%", f"Goal {step_goal:,} steps")
