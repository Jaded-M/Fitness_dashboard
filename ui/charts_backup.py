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

# Interactivity options for Plotly charts
CHART_CONFIG = dict(scrollZoom=True, displayModeBar=True, displaylogo=False)

# Shared chart styling to keep visuals consistent
CHART_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#f8fafc", family="Outfit, sans-serif"),
    hovermode="x unified",
    margin=dict(t=50, b=30, l=10, r=10),
    legend=dict(
        bgcolor="rgba(0,0,0,0.2)",
        bordercolor="rgba(255,255,255,0.05)",
        font=dict(size=11)
    ),
    xaxis=dict(gridcolor="rgba(255,255,255,0.03)", zeroline=False),
    yaxis=dict(gridcolor="rgba(255,255,255,0.03)", zeroline=False),
)

# Premium Color Palette
ACCENT_CYAN = "#00d2ff"
ACCENT_PURPLE = "#b14fff"
ACCENT_PINK = "#ff79c6"
ACCENT_OBSIDIAN = "#191922"

def render_consistency_heatmap(workout_df):
    """
    // WHAT IT DOES: Custom plots a GitHub-style heatmap of workout activity.
    // HOW IT WORKS: Maps dates -> week strings and days of week -> integers.
    //               Then places them onto a Plotly Heatmap grid.
    """
    st.markdown("##### 🟩 Consistency Heatmap")
    
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
    # Adjust for crossing years to keep linear X axis
    df["Week_Rank"] = df.groupby("Week").ngroup()
    
    # Create the matrix for Plotly (7 rows x N cols)
    # Z-value: 0=None, 1=Light, 2=Heavy
    # Re-pivot
    matrix = df.pivot(index="Day", columns="Week_Rank", values="counts").fillna(0)
    text_matrix = df.pivot(index="Day", columns="Week_Rank", values="Date").astype(str).replace("NaT", "")
    
    fig = go.Figure(data=go.Heatmap(
        z=matrix.values,
        text=text_matrix.values,
        hovertemplate="Date: %{text}<br>Exercises: %{z}<extra></extra>",
        colorscale=[[0, ACCENT_OBSIDIAN], [0.3, ACCENT_CYAN], [1.0, ACCENT_PURPLE]], # Elite Gradient Scales
        showscale=False,
        xgap=4,
        ygap=4
    ))
    
    fig.update_layout(
        height=180,
        margin=dict(t=10, b=20, l=40, r=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(
            tickmode="array",
            tickvals=[0, 2, 4, 6],
            ticktext=["Mon", "Wed", "Fri", "Sun"],
            autorange="reversed",
            showgrid=False,
            zeroline=False
        ),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def render_recovery_radar(workout_df, muscle_map_data):
    """
    // WHAT IT DOES: Renders a Muscular Status Radar indicating which muscle groups are recovered.
    """
    st.markdown("##### 🧬 Muscle Recovery Radar")
    if workout_df is None or workout_df.empty:
        st.info("Log workouts to build your recovery profile.")
        return

    # Find the last time each primary group was trained
    last_trained = {}
    for _, row in workout_df.iterrows():
        # Get base exercise name to match JSON
        ex_base = str(row["Workout"]).split(" (")[0]
        group = muscle_map_data.get(ex_base, {}).get("primary_group")
        if group:
            date = pd.to_datetime(row["Date"])
            if group not in last_trained or date > pd.to_datetime(last_trained[group]):
                last_trained[group] = date

    if not last_trained:
        st.info("Log mapped exercises to track recovery.")
        return

    now = datetime.now()
    groups = sorted(list(set(d.get("primary_group") for d in muscle_map_data.values() if d.get("primary_group"))))
    
    # Calculate recovery scores (0 = fully fatigued, 100 = fully recovered 48h)
    scores = []
    colors = []
    labels = []
    
    for g in groups:
        if g in last_trained:
            hours_since = (now - pd.to_datetime(last_trained[g])).total_seconds() / 3600.0
            score = min(hours_since / 48.0 * 100, 100) # 48h = 100% recovered
            scores.append(score)
            
            # Label with hours
            if hours_since < 24:
                labels.append(f"{g} ({int(hours_since)}h)")
                colors.append(ACCENT_PINK) # Legay Red replaced with Pink
            elif hours_since < 48:
                labels.append(f"{g} ({int(hours_since)}h)")
                colors.append("#ffb86c") # Legacy Amber replaced with warmer Orange
            else:
                labels.append(f"{g} (Ready)")
                colors.append("#50fa7b") # Legacy Green replaced with mint Green
        else:
            scores.append(100)
            labels.append(f"{g} (Ready)")
            colors.append("#50fa7b")

    # Close the radar loop
    scores.append(scores[0])
    labels.append(labels[0])
    
    fig = go.Figure(data=go.Scatterpolar(
        r=scores,
        theta=labels,
        fill='toself',
        fillcolor="rgba(0, 210, 255, 0.15)",
        line=dict(color=ACCENT_CYAN),
        hoverinfo="text",
        text=[f"Score: {int(s)}/100" for s in scores]
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 100]),
            angularaxis=dict(tickfont=dict(color="#d1d5db", size=10))
        ),
        showlegend=False,
        height=280,
        margin=dict(t=20, b=20, l=40, r=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
def render_progression_tab(real_df, all_exercises):
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

    chosen = st.selectbox("Select Exercise to Analyse:", all_exercises, key="prog_ex")
    ex_df  = real_df[real_df["Workout"] == chosen].sort_values("Date").copy()

    if ex_df.empty:
        st.info(f"No logs for {chosen} yet.")
        return

    # ── Quick stats row ────────────────────────────────────────
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("🏆 Best Weight", f"{ex_df['Weight'].max():.1f} kg")
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
            line=dict(color="rgba(255,255,255,0.05)", width=0.5),
            opacity=0.4,
        ),
        yaxis="y2",
        hovertemplate="<b>%{x|%d %b}</b><br>Volume: %{y:,.0f} kg·reps<extra></extra>"
    ))

    # TRACE 2: Max Weight line (foreground, solid)
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["Weight"],
        mode="lines+markers", name="Max Weight (kg)",
        line=dict(color=ACCENT_CYAN, width=3),
        marker=dict(size=8, color=ACCENT_CYAN, line=dict(color="white", width=1.5)),
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
    )
    
    fig.update_layout(**layout)

    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)


def render_split_volume_tab(real_df):
    """Renders the Pie Chart and Weekly Volume Bar Chart (Tab 2)."""
    split_counts = real_df["Split"].value_counts().reset_index()
    split_counts.columns = ["Split", "Sessions"]

    fig_donut = go.Figure(go.Pie(
        labels=split_counts["Split"], values=split_counts["Sessions"],
        hole=0.5, textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>%{value} sessions (%{percent})<extra></extra>",
        marker=dict(
            colors=["#00d2ff", "#ff79c6", "#8B4FEC", "#50fa7b", "#f1fa8c"],
            line=dict(color="rgba(255,255,255,0.15)", width=1.5)
        )
    ))
    layout_donut = CHART_LAYOUT.copy()
    layout_donut.update(dict(
        title=dict(text="🥧 Training Split Distribution", font=dict(size=16, color="#f1fa8c")),
        annotations=[dict(
            text=f"<b>{split_counts['Sessions'].sum()}</b><br>total",
            x=0.5, y=0.5, font_size=16, showarrow=False, font=dict(color="white")
        )]
    ))
    fig_donut.update_layout(layout_donut)
    st.plotly_chart(fig_donut, use_container_width=True, config=CHART_CONFIG)

    real_copy = real_df.copy()
    real_copy["Week"] = real_copy["Date"].dt.to_period("W").astype(str)
    weekly_vol = real_copy.groupby("Week").apply(lambda x: (x["Reps"] * x["Weight"]).sum()).reset_index()
    weekly_vol.columns = ["Week", "Volume"]
    weekly_vol = weekly_vol.tail(8)

    fig_weekly = go.Figure(go.Bar(
        x=weekly_vol["Week"], y=weekly_vol["Volume"],
        marker=dict(
            color=weekly_vol["Volume"], colorscale="Viridis", showscale=False,
            line=dict(color="rgba(255,255,255,0.1)", width=0.5)
        ),
        hovertemplate="<b>%{x}</b><br>Volume: %{y:,.0f} kg·reps<extra></extra>"
    ))
    layout_weekly = CHART_LAYOUT.copy()
    layout_weekly.update(dict(
        title=dict(text="📅 Weekly Volume — Last 8 Weeks", font=dict(size=16, color="#8B4FEC")),
        yaxis_title="Volume (kg·reps)", xaxis_tickangle=-30
    ))
    fig_weekly.update_layout(layout_weekly)
    st.plotly_chart(fig_weekly, use_container_width=True, config=CHART_CONFIG)


def render_steps_tab(steps_df):
    """Renders Daily Steps + Distance + Intensity (Tab 3)."""
    if steps_df is not None and not steps_df.empty:
        steps_copy = steps_df.copy()
        steps_copy["date"] = pd.to_datetime(steps_copy["date"])
        
        # Calculate Intensity (Cadence)
        steps_copy["cadence"] = (steps_copy["steps"] / steps_copy["active_minutes"]).fillna(0)
        
        # KPI Row
        k1, k2, k3 = st.columns(3)
        total_steps = steps_copy["steps"].sum()
        total_dist = steps_copy["distance"].sum()
        avg_cadence = steps_copy["cadence"].mean()
        
        k1.metric("👣 Total Steps (Period)", f"{total_steps:,}")
        k2.metric("📍 Total Distance", f"{total_dist:,.1f} km")
        k3.metric("⚡ Avg Intensity", f"{int(avg_cadence)} steps/min")

        st.markdown("---")
        
        # 1. Step Count Chart
        steps_copy["Color"] = steps_copy["steps"].apply(
            lambda s: "#50fa7b" if s >= 10000 else ACCENT_CYAN if s >= 7000 else "#ff5555"
        )
        steps_copy["Label"] = steps_copy["steps"].apply(
            lambda s: "10k+ 🔥" if s >= 10000 else "7k+ ✅" if s >= 7000 else "< 7k 💤"
        )

        fig_steps = go.Figure(go.Bar(
            x=steps_copy["date"], y=steps_copy["steps"],
            marker=dict(color=steps_copy["Color"], line=dict(color="rgba(255,255,255,0.05)", width=0.5)),
            text=steps_copy["Label"], textposition="outside",
            hovertemplate="<b>%{x|%d %b}</b><br>Steps: %{y:,}<extra></extra>"
        ))
        fig_steps.add_hline(
            y=7000, line_dash="dot", line_color=ACCENT_CYAN,
            annotation_text="7,000 Step Target", annotation_font_color=ACCENT_CYAN
        )
        layout_steps = CHART_LAYOUT.copy()
        layout_steps.update(dict(
            yaxis_title="Steps", showlegend=False
        ))
        fig_steps.update_layout(layout_steps)
        st.plotly_chart(fig_steps, use_container_width=True, config=CHART_CONFIG)
        st.caption(f"Daily average: **{int(steps_df['steps'].mean()):,} steps**")

        # 2. Intensity (Cadence) Chart
        # Calculate Rolling Cadence
        steps_copy["rolling_cadence"] = steps_copy["cadence"].rolling(window=7, min_periods=1).mean()
        
        fig_intensity = go.Figure()
        # Raw Cadence (Dots)
        fig_intensity.add_trace(go.Scatter(
            x=steps_copy["date"], y=steps_copy["cadence"],
            mode="markers", name="Daily Cadence",
            marker=dict(color="rgba(177, 79, 255, 0.4)", size=7),
            hovertemplate="Cadence: %{y:.0f} step/min<extra></extra>"
        ))
        # Rolling Cadence (Line)
        fig_intensity.add_trace(go.Scatter(
            x=steps_copy["date"], y=steps_copy["rolling_cadence"],
            mode="lines", name="7-Day Avg Intensity",
            line=dict(color=ACCENT_PURPLE, width=3),
            hovertemplate="Avg Intensity: %{y:.0f} step/min<extra></extra>"
        ))
        # Robust Layout Handling (Avoids Multiple Value Errors)
        step_intensity_layout = CHART_LAYOUT.copy()
        step_intensity_layout.update(dict(
            title=dict(text="⚡ Activity Intensity (Steps per Minute)", font=dict(size=14, color=ACCENT_PURPLE)),
            yaxis_title="Steps / Min",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        ))
        fig_intensity.update_layout(step_intensity_layout)
        st.plotly_chart(fig_intensity, use_container_width=True, config=CHART_CONFIG)
    else:
        st.info("Head over to **'⚙️ Settings'** (Tab 6) to Sync Google Fit or manually log your steps!")


def render_rpg_tab(real_df, best_df):
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
    if total_volume   > 500_000:   badges.append("🦾 Titan")

    if badges: st.success("**Badges:** " + "  ".join(badges))
    else: st.info("Keep lifting to unlock badges!")

    st.markdown("---")
    st.markdown("##### 🏆 Personal Records")
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
        st.plotly_chart(fig_pr, use_container_width=True, config=CHART_CONFIG)


def render_stimulus_tab(real_df, muscle_map_data):
    """Renders the Systemic Fatigue / Muscle Stimulus logic (Tab 5)."""
    st.markdown("##### 🎯 7-Day Muscle Stimulus & Fatigue")
    last_7_days = datetime.now() - timedelta(days=7)
    recent_df = real_df[real_df["Date"] >= last_7_days]

    muscle_points = {}
    for _, row in recent_df.iterrows():
        ex   = row["Workout"]
        sets = row["Sets"]
        # .get() safely returns a default dict if the exercise isn't mapped yet
        mapping = muscle_map_data.get(ex, {})

        # Use 'primary_group' (e.g., Chest, Back) for the main chart label
        prim = mapping.get("primary_group", "Other")
        if prim:
            muscle_points[prim] = muscle_points.get(prim, 0) + sets

        # Secondary muscles are stored as a list in our JSON
        sec_list = mapping.get("secondary_muscles", [])
        if isinstance(sec_list, list):
            for s in sec_list:
                # We give secondary muscles 0.5 points per set (half stimulus)
                muscle_points[s] = muscle_points.get(s, 0) + (sets * 0.5)

    if muscle_points:
        stim_df = pd.DataFrame(list(muscle_points.items()), columns=["Muscle", "Stimulus Points"])
        stim_df = stim_df.sort_values("Stimulus Points", ascending=True)

        fig_stim = go.Figure(go.Bar(
            x=stim_df["Stimulus Points"], y=stim_df["Muscle"], orientation="h",
            marker=dict(
                color=stim_df["Stimulus Points"], colorscale="Inferno", showscale=False,
                line=dict(color="rgba(255,255,255,0.1)", width=0.5)
            ),
            hovertemplate="<b>%{y}</b><br>Stimulus: %{x} points<extra></extra>",
            text=stim_df["Stimulus Points"].apply(lambda v: f"{v:.1f} pts"),
            textposition="inside", textfont=dict(color="white")
        ))
        layout_stim = CHART_LAYOUT.copy()
        layout_stim.update(dict(
            title=dict(text="🔥 Systemic Fatigue by Muscle Group", font=dict(size=16, color="#ff5555")),
            xaxis_title="Stimulus Points (Sets)",
            yaxis=dict(categoryorder="total ascending")
        ))
        fig_stim.update_layout(layout_stim)
        st.plotly_chart(fig_stim, use_container_width=True, config=CHART_CONFIG)
        st.info("💡 **Tip:** High points = high fatigue. Make sure those muscles recover!")
    else:
        st.info("No exercises logged in the past 7 days.")

import numpy as np

def render_insights_tab(real_df, session_df, food_df, steps_df, weight_df):
    """Renders the Data Science and Correlation Scatter plots (Tab 4)."""
    
    # 1. Gym Intensity Panel
    st.markdown("#### ⚡ Gym Intensity (Volume Rate)")
    if session_df is not None and not session_df.empty:
        # Group session duration and volume by date
        daily_vol = real_df.copy()
        daily_vol["Volume"] = daily_vol["Weight"] * daily_vol["Reps"]
        daily_v = daily_vol.groupby(daily_vol["Date"].dt.date)["Volume"].sum().reset_index()
        
        daily_s = session_df.groupby(session_df["Date"].dt.date)["Sets"].sum().reset_index(name="DurationMins")
        
        merged_intensity = pd.merge(daily_v, daily_s, on="Date")
        if not merged_intensity.empty:
            merged_intensity["Vol_Per_Min"] = merged_intensity["Volume"] / merged_intensity["DurationMins"]
            avg_intensity = merged_intensity["Vol_Per_Min"].mean()
            
            st.metric("Avg Training Intensity", f"{avg_intensity:.1f} kg/min", help="Total kg moved divided by your session duration.")
            
            # Line chart for intensity over time
            fig_i = go.Figure(go.Scatter(
                x=merged_intensity["Date"], y=merged_intensity["Vol_Per_Min"], 
                mode="lines+markers", line=dict(color="#00d2ff", width=3),
                marker=dict(size=8, color="#b14fff")
            ))
            layout_i = CHART_LAYOUT.copy()
            layout_i.update(dict(
                title=dict(text="Intensity Over Time", font=dict(color="#d1d5db")),
                yaxis_title="kg per minute",
                height=250
            ))
            fig_i.update_layout(layout_i)
            st.plotly_chart(fig_i, use_container_width=True, config=CHART_CONFIG)
    else:
        st.info("Log a 'Session Duration' (in minutes) to unlock Gym Intensity metrics.")

    # 2. 4D Correlation Plot
    st.markdown("---")
    st.markdown("#### 🔭 4D Correlation Engine")
    st.caption("Does high activity and low calories actually equal weight loss? Let's check the data.")
    
    if weight_df.empty or food_df.empty:
        st.warning("Needs both Weight logs (from Nutrition table) and Calorie logs to build the 4D model.")
        return

    # Build joined dataset
    # Daily Training Vol
    d_train = real_df.copy()
    d_train["Date"] = d_train["Date"].dt.date
    d_train["Volume"] = d_train["Weight"] * d_train["Reps"]
    d_train = d_train.groupby("Date")["Volume"].sum().reset_index()
    
    # Daily Food
    d_food = food_df.copy()
    d_food["Date"] = pd.to_datetime(d_food["date"]).dt.date
    d_food = d_food.groupby("Date")["calories"].sum().reset_index()
    
    # Daily Weight
    d_weight = weight_df.copy()
    d_weight["Date"] = pd.to_datetime(d_weight["Date"]).dt.date
    d_weight = d_weight.groupby("Date")["Weight"].mean().reset_index()
    
    # Daily Steps
    if steps_df is not None and not steps_df.empty:
        d_steps = steps_df.copy()
        d_steps["Date"] = pd.to_datetime(d_steps["date"]).dt.date
        d_steps = d_steps.groupby("Date")["steps"].sum().reset_index()
    else:
        d_steps = pd.DataFrame(columns=["Date", "steps"])
    
    # Merge all
    df_merged = d_weight.merge(d_food, on="Date", how="inner")
    
    # Left join volume/steps (since we might not train/walk every day)
    df_merged = df_merged.merge(d_train, on="Date", how="left").fillna({"Volume": 0})
    
    if not d_steps.empty:
        df_merged = df_merged.merge(d_steps, on="Date", how="left").fillna({"steps": 0})
    else:
        df_merged["steps"] = 0
        
    if df_merged.empty or len(df_merged) < 3:
        st.info("Not enough overlapping days of Weight + Calories to build correlation. Log more data!")
        return
        
    # Calculated Rolling Averages
    df_merged["roll_cal"] = df_merged["calories"].rolling(window=7, min_periods=1).mean()
    df_merged["roll_weight"] = df_merged["Weight"].rolling(window=7, min_periods=1).mean()
    
    
    fig_4d = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 1. Calories (Raw Bars - Faded)
    fig_4d.add_trace(
        go.Bar(x=df_merged["Date"], y=df_merged["calories"], name="Daily Calories (Raw)", marker_color="rgba(0, 210, 255, 0.2)", hoverinfo="skip"),
        secondary_y=False,
    )
    # 2. Calories (7-Day Avg - Solid Line)
    fig_4d.add_trace(
        go.Scatter(x=df_merged["Date"], y=df_merged["roll_cal"], name="7-Day Avg kcal", mode="lines", line=dict(color="#00d2ff", width=4)),
        secondary_y=False,
    )
    
    # 3. Weight (Raw Points - Faded)
    fig_4d.add_trace(
        go.Scatter(x=df_merged["Date"], y=df_merged["Weight"], name="Daily Weight (Raw)", mode="markers", marker=dict(color="rgba(245, 158, 11, 0.3)", size=6), hoverinfo="skip"),
        secondary_y=True,
    )
    # 4. Weight (7-Day Avg - Solid Line)
    fig_4d.add_trace(
        go.Scatter(x=df_merged["Date"], y=df_merged["roll_weight"], name="7-Day Avg Weight", mode="lines", line=dict(color="#f59e0b", width=4)),
        secondary_y=True,
    )
    
    # Robust Layout Handling (Avoids Multiple Value Errors)
    insight_layout = CHART_LAYOUT.copy()
    insight_layout.update(dict(
        title="🧬 Diet vs Weight Signal (7-Day Rolling)",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    ))
    
    fig_4d.update_layout(insight_layout)
    fig_4d.update_yaxes(title_text="Calories (kcal)", secondary_y=False, showgrid=False)
    fig_4d.update_yaxes(title_text="Weight (kg)", secondary_y=True, showgrid=False)
    
    st.plotly_chart(fig_4d, use_container_width=True, config=CHART_CONFIG)
