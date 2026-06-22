"""
# --------------------------------------------------------------------------------
# MODULE: ui/charts.py
# --------------------------------------------------------------------------------
# // WHAT IT DOES: 
# This module contains ALL the complex Plotly charting and visual logic.
#
# // HOW IT WORKS:
# Notice how this file has `import plotly` and `import streamlit`, but it doesn't 
# load any databases. It waits for the main app to hand it the data,
# and then it just draws the pretty pictures.
#
# // WHY WE DO IT THIS WAY:
# Separation of Concerns. The main `Fitness.py` file should just be the skeleton 
# of the app. It shouldn't be clogged up with 50-line blocks defining colors and 
# hover-templates for charts. 
# --------------------------------------------------------------------------------
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

from core.muscle_mapping import canonical_exercise_name, exercise_muscle_profile, normalize_group
from ui import theme as chart_theme
from ui.theme import PHI_COLORS

# ==========================================
# ELITE v2 — DESIGN TOKENS
# ==========================================
ACCENT_BLUE = PHI_COLORS["blue"]
ACCENT_STEEL = PHI_COLORS["muted"]
ACCENT_SURFACE = "#11161d"
ACCENT_GREEN = PHI_COLORS["green"]
ACCENT_ROSE = PHI_COLORS["rose"]
ACCENT_PURPLE = PHI_COLORS["violet"]

# Clean, professional layout for Elite v2
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=40, b=40, l=40, r=40),
    font=dict(color="#94A3B8", family="Inter, sans-serif"),
    xaxis=dict(
        showgrid=True,
        gridcolor="rgba(31, 41, 55, 0.5)", 
        zeroline=False, 
        tickfont=dict(size=10),
        title_font=dict(size=11, color="#64748B")
    ),
    yaxis=dict(
        gridcolor="rgba(31, 41, 55, 0.5)", 
        zeroline=False, 
        tickfont=dict(size=10),
        title_font=dict(size=11, color="#64748B")
    ),
    hoverlabel=dict(
        bgcolor="#ffffff",
        font_size=13,
        font_family="Inter, sans-serif"
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0.2)",
        bordercolor="rgba(255,255,255,0.05)",
        font=dict(size=11)
    )
)

CHART_CONFIG = chart_theme.CHART_CONFIG
CHART_LAYOUT = chart_theme.CHART_LAYOUT



def render_consistency_heatmap(workout_df, key: str = "consistency_heatmap"):
    """
    // WHAT IT DOES: Custom plots a GitHub-style heatmap of workout activity.
    """
    st.markdown(
        """<div class="phi-section-title">Consistency</div>
           <div class="phi-caption" style="margin-bottom:1rem;">Training frequency over the last 90 days</div>
        """,
        unsafe_allow_html=True
    )
    
    if workout_df is None or workout_df.empty:
        st.info("Log workouts to build your heatmap.")
        return

    # Count sessions per date
    daily_counts = workout_df.groupby(workout_df["Date"].dt.date).size().reset_index(name="counts")
    daily_counts["Date"] = pd.to_datetime(daily_counts["Date"])
    
    # Generate the last 90 days grid
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    grid = pd.DataFrame({"Date": pd.date_range(start_date, end_date)})
    grid["Date"] = grid["Date"].dt.normalize()
    
    daily_counts["Date"] = daily_counts["Date"].dt.normalize()
    df = pd.merge(grid, daily_counts, on="Date", how="left").fillna(0)
    
    # Calculate grid coords
    df["Week"] = df["Date"].dt.isocalendar().week
    df["Day"] = df["Date"].dt.dayofweek # 0=Monday, 6=Sunday
    df["Week_Rank"] = df.groupby("Week").ngroup()
    
    matrix = df.pivot(index="Day", columns="Week_Rank", values="counts").fillna(0)
    text_matrix = df.pivot(index="Day", columns="Week_Rank", values="Date").astype(str).replace("NaT", "")
    
    # Custom colorscale: 0 is faint, then gradient up to bright cyan
    colors = [
        [0.0, "rgba(255, 255, 255, 0.03)"],
        [0.01, "rgba(86, 199, 216, 0.15)"],
        [0.5, "rgba(86, 199, 216, 0.6)"],
        [1.0, "rgba(86, 199, 216, 1.0)"]
    ]
    
    fig = go.Figure(data=go.Heatmap(
        z=matrix.values,
        text=text_matrix.values,
        hovertemplate="Date: %{text}<br>Exercises logged: %{z}<extra></extra>",
        colorscale=colors,
        showscale=False,
        xgap=4,
        ygap=4,
        hoverlabel=dict(bgcolor="rgba(17, 22, 29, 0.95)", bordercolor="rgba(86,199,216,0.3)", font=dict(color="#f5f1e8"))
    ))
    
    fig.update_layout(
        height=160,
        margin=dict(t=0, b=0, l=40, r=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(
            tickmode="array",
            tickvals=[0, 2, 4, 6],
            ticktext=["Mon", "Wed", "Fri", "Sun"],
            autorange="reversed",
            showgrid=False,
            zeroline=False,
            tickfont=dict(color="#a7b0ae", size=10)
        ),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=key)

def render_progression_tab(real_df, all_exercises, key: str = "prog_ex", chart_key: str = "progression_chart"):
    """
    // WHAT IT DOES:
    //   Renders the COMBINED Strength + Volume progression chart.
    //   This is a "Dual-Axis" chart — two Y-axes on one graph.
    //
    // HOW IT WORKS:
    //   Left Y-axis  = Max Weight (kg) — shown as a cyan LINE with markers.
    //   Right Y-axis = Session Volume (kg·reps) — shown as purple BARS behind.
    //   A third trace shows Estimated 1RM as a dashed gold line.
    //
    // WHY ONE CHART INSTEAD OF TWO:
    //   When they're separate, you can't see the relationship.
    //   Combined, you can instantly spot: "Am I getting stronger because
    //   I'm doing more volume, or is my intensity genuinely increasing?"
    //
    // PLOTLY CONCEPT — make_subplots() with secondary_y:
    //   Plotly lets you add a second Y-axis on the right side.
    //   Traces are assigned to yaxis="y" (left) or yaxis="y2" (right).
    //   We do this manually with go.Figure() + update_layout(yaxis2=...).
    """
    if not all_exercises:
        st.info("No exercise data yet.")
        return

    chosen = st.selectbox("Select Exercise to Analyse:", all_exercises, key=key)
    ex_df  = real_df[real_df["Workout"] == chosen].sort_values("Date").copy()

    if ex_df.empty:
        st.info(f"No logs for {chosen} yet.")
        return

    # ── Quick stats row ────────────────────────────────────────
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Best Weight", f"{ex_df['Weight'].max():.1f} kg")
    s2.metric("🔥 Max Reps", int(ex_df["Reps"].max()))
    s3.metric("📅 Sessions", len(ex_df.groupby(ex_df["Date"].dt.date)))

    # ── Estimated 1RM (Epley Formula) ──────────────────────────
    # 1RM = weight × (1 + reps/30)
    # This estimates the heaviest single rep you could do.
    ex_df["E1RM"] = ex_df["Weight"] * (1 + ex_df["Reps"] / 30)
    best_e1rm = ex_df["E1RM"].max()
    s4.metric("🎯 Est. 1RM", f"{best_e1rm:.1f} kg")

    # ── Prepare daily aggregates ───────────────────────────────
    # groupby(date) then take the max weight and sum of volume per day.
    ex_df["Volume"] = ex_df["Reps"] * ex_df["Weight"]

    daily = ex_df.groupby(ex_df["Date"].dt.date).agg(
        max_weight=("Weight", "max"),
        total_volume=("Volume", "sum"),
        best_e1rm=("E1RM", "max"),
    ).reset_index()
    daily.columns = ["Date", "Weight", "Volume", "E1RM"]
    daily["Date"] = pd.to_datetime(daily["Date"])

    # ── Build the combined chart ───────────────────────────────
    fig = go.Figure()

    # TRACE 1: Volume bars (background, semi-transparent)
    # yaxis="y2" tells Plotly to use the RIGHT Y-axis for this trace.
    fig.add_trace(go.Bar(
        x=daily["Date"], y=daily["Volume"],
        name="Volume (kg·reps)",
        marker=dict(
            color=daily["Volume"], colorscale="Plasma", showscale=False,
            line=dict(width=0),
            cornerradius=4,
            opacity=0.4,
        ),
        yaxis="y2",
        hovertemplate="<b>%{x|%d %b}</b><br>Volume: %{y:,.0f} kg·reps<extra></extra>"
    ))

    # TRACE 2: Max Weight line (foreground, solid)
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["Weight"],
        mode="lines+markers", name="Max Weight (kg)",
        line=dict(color=ACCENT_BLUE, width=3),
        marker=dict(size=8, color=ACCENT_BLUE, line=dict(color="white", width=1.5)),
        fill="tozeroy", fillcolor="rgba(0,210,255,0.06)",
        hovertemplate="<b>%{x|%d %b}</b><br>Max: %{y:.1f} kg<extra></extra>"
    ))

    # TRACE 3: Estimated 1RM trendline (dashed gold)
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["E1RM"],
        mode="lines", name="Est. 1RM",
        line=dict(color="#ffb86c", width=2, dash="dash"),
        hovertemplate="<b>%{x|%d %b}</b><br>E1RM: %{y:.1f} kg<extra></extra>"
    ))

    # ── Layout with dual Y-axes ────────────────────────────────
    # yaxis = left axis (Weight, 1RM)
    # yaxis2 = right axis (Volume), overlaid on top (overlaying="y")
    # Create a copy of the base layout so we don't modify it permanently
    layout = CHART_LAYOUT.copy()
    layout.update(
        title=dict(
            text=f"📈 {chosen} — Strength × Volume Evolution",
            font=dict(size=16, color="#f8fafc")
        ),
        yaxis=dict(title="Weight / E1RM (kg)", side="left", showgrid=False),
        yaxis2=dict(
            title="Volume (kg·reps)",
            side="right",
            overlaying="y",
            showgrid=False,
            zeroline=False,
            tickfont=dict(color=ACCENT_PURPLE),
            rangemode="tozero"
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(255,255,255,0.04)", bordercolor="rgba(255,255,255,0.08)"
        ),
        barmode="overlay",   # Bars render behind the lines
        hovermode="closest",
    )
    
    fig.update_layout(**layout)

    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG, key=chart_key)


def render_split_volume_tab(real_df, key_prefix: str = "split_volume"):
    """
    Split volume analytics panel.

    Shows two charts built entirely from logged data:
      1. Horizontal bar chart — sessions per split, ranked by frequency.
      2. Grouped weekly volume bar chart — last 8 weeks, one bar per split.

    No hardcoded split names or colours — everything is derived at runtime.
    """
    # ── Palette: enough distinct colours for up to 8 splits ──────────────────
    _PALETTE = [
        "#197f96", "#7469c9", "#2f9f68", "#c98a18",
        "#ef7f82", "#b7cc7a", "#f9a87b", "#a8d8ea",
    ]

    # ── 1. Session frequency per split ───────────────────────────────────────
    split_sessions = (
        real_df.drop_duplicates(subset=["Date", "Split"])
        .groupby("Split").size()
        .rename("Sessions")
        .sort_values(ascending=True)
        .reset_index()
    )

    if split_sessions.empty:
        st.info("Log workouts to see split frequency.")
        return

    colours = [_PALETTE[i % len(_PALETTE)] for i in range(len(split_sessions))]
    total_sessions = split_sessions["Sessions"].sum()

    fig_freq = go.Figure(go.Bar(
        x=split_sessions["Sessions"],
        y=split_sessions["Split"],
        orientation="h",
        marker=dict(
            color=colours,
            line=dict(width=0),
            cornerradius=4,
        ),
        text=split_sessions["Sessions"].apply(lambda v: f"{v} session{'s' if v != 1 else ''}"),
        textposition="outside",
        textfont=dict(color="#68766f", size=11),
        hovertemplate="<b>%{y}</b><br>%{x} sessions<extra></extra>",
    ))
    layout_freq = CHART_LAYOUT.copy()
    layout_freq.update(
        title=dict(
            text=f"Training Split Frequency — {total_sessions} total sessions",
            font=dict(size=15, color="#f5f1e8"),
        ),
        xaxis=dict(title="Sessions", showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        showlegend=False,
        height=max(180, len(split_sessions) * 54 + 80),
        margin=dict(l=10, r=80, t=55, b=30),
    )
    fig_freq.update_layout(layout_freq)
    st.plotly_chart(fig_freq, use_container_width=True, config=CHART_CONFIG, key=f"{key_prefix}_freq")

    # ── 2. Weekly volume grouped by split — last 8 weeks ─────────────────────
    df_vol = real_df.copy()
    df_vol["Volume"] = df_vol["Reps"] * df_vol["Weight"]
    df_vol["Week"] = df_vol["Date"].dt.to_period("W").dt.start_time.dt.strftime("%d %b")

    weekly = (
        df_vol.groupby(["Week", "Split"])["Volume"]
        .sum()
        .reset_index()
    )
    # Keep only the 8 most recent weeks
    recent_weeks = sorted(weekly["Week"].unique())[-8:]
    weekly = weekly[weekly["Week"].isin(recent_weeks)]

    splits_ordered = (
        weekly.groupby("Split")["Volume"].sum()
        .sort_values(ascending=False).index.tolist()
    )

    fig_weekly = go.Figure()
    for idx, split in enumerate(splits_ordered):
        data = weekly[weekly["Split"] == split]
        fig_weekly.add_trace(go.Bar(
            x=data["Week"],
            y=data["Volume"],
            name=split,
            marker=dict(
                color=_PALETTE[idx % len(_PALETTE)],
                line=dict(width=0),
                cornerradius=4,
            ),
            hovertemplate=f"<b>{split}</b><br>Week of %{{x}}<br>Volume: %{{y:,.0f}} kg·reps<extra></extra>",
        ))

    layout_weekly = CHART_LAYOUT.copy()
    layout_weekly.update(
        title=dict(
            text="Weekly Volume by Split — Last 8 Weeks",
            font=dict(size=15, color="#f5f1e8"),
        ),
        barmode="group",
        yaxis=dict(title="Volume (kg·reps)", gridcolor="rgba(148,163,184,0.12)", zeroline=False),
        xaxis=dict(tickangle=-20, showgrid=False, zeroline=False),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(255,255,255,0.03)", bordercolor="rgba(255,255,255,0.08)",
        ),
        height=380,
        margin=dict(l=10, r=10, t=72, b=50),
    )
    fig_weekly.update_layout(layout_weekly)
    st.plotly_chart(fig_weekly, use_container_width=True, config=CHART_CONFIG, key=f"{key_prefix}_weekly")


def render_rpg_tab(real_df, best_df, key_prefix: str = "pr"):
    """Renders gamification badges, levels, and PRs (Tab 4)."""
    total_volume = (real_df["Reps"] * real_df["Weight"]).sum()
    level        = int(total_volume / 5000) + 1
    xp_progress  = (total_volume % 5000) / 5000

    lvl_col, bar_col = st.columns([1, 4])
    with lvl_col:
        st.markdown(f"## 🛡️ Lvl {level}")
    with bar_col:
        st.caption(f"XP: **{int(total_volume):,}** / **{level * 5000:,}**")
        st.progress(xp_progress)

    badges = []
    if len(real_df) > 10:          badges.append("🥉 Novice")
    if len(real_df) > 50:          badges.append("🥈 Intermediate")
    if total_volume   > 100_000:   badges.append("🚜 Bulldozer")
    if total_volume   > 500_000:   badges.append("Titan")

    if badges: st.success("**Badges:** " + "  ".join(badges))
    else: st.info("Keep lifting to unlock badges!")

    st.markdown("---")
    st.markdown("##### Personal Records")
    if not best_df.empty:
        best_df.columns = ["Exercise", "Best Weight (kg)", "Best Reps", "Sessions"]
        st.dataframe(best_df, use_container_width=True, hide_index=True)

        top10 = best_df.head(10)
        fig_pr = go.Figure(go.Bar(
            x=top10["Best Weight (kg)"], y=top10["Exercise"], orientation="h",
            marker=dict(
                color=top10["Best Weight (kg)"], colorscale="Plasma", showscale=False,
                line=dict(color="rgba(255,255,255,0.1)", width=0.5)
            ),
            hovertemplate="<b>%{y}</b><br>Best: %{x:.1f} kg<extra></extra>",
            text=top10["Best Weight (kg)"].apply(lambda v: f"{v:.1f} kg"),
            textposition="inside", insidetextanchor="middle", textfont=dict(color="white", size=11)
        ))
        layout_pr = CHART_LAYOUT.copy()
        layout_pr.update(dict(
            title=dict(text="🏅 Top 10 — Personal Records by Max Weight", font=dict(size=16, color="#f1fa8c")),
            xaxis_title="Max Weight (kg)",
            yaxis=dict(categoryorder="total ascending")
        ))
        fig_pr.update_layout(layout_pr)
        st.plotly_chart(fig_pr, use_container_width=True, config=CHART_CONFIG, key=f"{key_prefix}_chart")


