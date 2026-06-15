import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import database
import json
from datetime import datetime, timedelta

def calculate_1rm(weight: float, reps: int) -> float:
    """Calculate Estimated 1RM using the Epley formula."""
    if reps <= 0 or weight <= 0:
        return 0.0
    if reps == 1:
        return weight
    return weight * (1 + (reps / 30))


def extract_top_set(row) -> tuple[float, int]:
    """Return the heaviest set, preferring structured set_data when present."""
    set_data = row.get("set_data")
    top_weight = float(row.get("weight", 0) or 0)
    top_reps = int(row.get("reps", 0) or 0)

    if isinstance(set_data, str) and set_data.strip():
        try:
            set_data = json.loads(set_data)
        except Exception:
            set_data = None

    if isinstance(set_data, list):
        best_pair = (top_weight, top_reps)
        for set_row in set_data:
            weight = float(set_row.get("weight", 0) or 0)
            reps = int(set_row.get("reps", 0) or 0)
            candidate = (weight, reps)
            if candidate > best_pair:
                best_pair = candidate
        top_weight, top_reps = best_pair

    return top_weight, top_reps

def render_pr_board():
    """Render the Top 10 all-time PRs across all exercises."""
    st.markdown(
        """
        <div class="phi-section">
            <div class="phi-section-title">All-Time PR Board</div>
            <div class="phi-section-caption">Your absolute heaviest lifts across all tracked exercises.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    df = database.get_best_lifts()
    if df.empty:
        st.info("No workouts logged yet. Your PRs will appear here.")
        return
    
    # Sort by best weight and take top 10
    top_prs = df.sort_values(by="best_weight", ascending=False).head(10)
    
    for _, row in top_prs.iterrows():
        ex = row["exercise"]
        weight = row["best_weight"]
        reps = row["best_reps"]
        sessions = row["sessions"]
        
        st.markdown(
            f"""
            <div class="phi-card compact" style="margin-bottom: 0.5rem; padding: 0.8rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-weight: 600; color: var(--ink);">{ex}</div>
                    <div style="display: flex; align-items: baseline; gap: 0.5rem;">
                        <span style="font-size: 1.2rem; font-weight: 800; color: var(--green);">{weight:.1f} kg</span>
                        <span style="font-size: 0.8rem; color: var(--muted);">× {int(reps)} reps</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

def render_1rm_chart(exercise: str):
    """Render the Estimated 1RM progression chart for a specific exercise."""
    history = database.get_exercise_history(exercise, limit=100)
    if history.empty:
        st.caption(f"No data available for {exercise}.")
        return

    # Calculate 1RM for each session
    history['date'] = pd.to_datetime(history['date'])
    
    # Extract top set per session for 1RM calculation
    daily_1rm = []
    for _, row in history.iterrows():
        top_weight, top_reps = extract_top_set(row)
        top_1rm = calculate_1rm(top_weight, top_reps)
        daily_1rm.append({"date": row["date"], "e1RM": top_1rm})
        
    df_1rm = pd.DataFrame(daily_1rm).groupby("date").max().reset_index().sort_values("date")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_1rm["date"], y=df_1rm["e1RM"],
        mode="lines+markers",
        line=dict(color="#4bb7cf", width=3),
        marker=dict(size=8, color="#6fd18f"),
        name="Est. 1RM"
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=0, r=0, t=20, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, color="#8b98aa"),
        yaxis=dict(showgrid=True, gridcolor="rgba(164, 177, 196, 0.1)", color="#8b98aa", title="e1RM (kg)"),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def render_overload_status():
    """Show progressive overload status for recently trained exercises."""
    st.markdown(
        """
        <div class="phi-section">
            <div class="phi-section-title">Progressive Overload</div>
            <div class="phi-section-caption">Comparing your latest session to the one before it.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    recent_workouts = database.get_all_workouts()
    if recent_workouts.empty:
        st.info("No recent workouts to analyze.")
        return
        
    recent_workouts["date"] = pd.to_datetime(recent_workouts["date"])
    cutoff = datetime.now() - timedelta(days=14)
    recent = recent_workouts[recent_workouts["date"] >= cutoff]
    unique_exercises = recent["exercise"].unique()
    
    status_cards = []
    
    for ex in unique_exercises:
        if ex == "Session Duration":
            continue
            
        history = database.get_exercise_history(ex, limit=2)
        if len(history) < 2:
            continue
            
        w1, r1 = extract_top_set(history.iloc[0])
        w2, r2 = extract_top_set(history.iloc[1])
        
        diff_w = w1 - w2
        
        if diff_w > 0:
            status = f"<span style='color: var(--green); font-weight: 800;'>↑ +{diff_w:.1f} kg</span>"
            border = "var(--green)"
        elif diff_w < 0:
            status = f"<span style='color: var(--rose); font-weight: 800;'>↓ {diff_w:.1f} kg</span>"
            border = "var(--rose)"
        else:
            # Check reps if weight is same
            diff_r = r1 - r2
            if diff_r > 0:
                status = f"<span style='color: var(--green); font-weight: 800;'>↑ +{diff_r} reps</span>"
                border = "var(--green)"
            elif diff_r < 0:
                status = f"<span style='color: var(--rose); font-weight: 800;'>↓ {diff_r} reps</span>"
                border = "var(--rose)"
            else:
                status = "<span style='color: var(--muted); font-weight: 800;'>→ Maintained</span>"
                border = "var(--line)"
                
        status_cards.append(f"""
            <div class="phi-card compact" style="border-left: 3px solid {border}; margin-bottom: 0.5rem; padding: 0.8rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-weight: 600; color: var(--ink);">{ex}</div>
                    <div>{status}</div>
                </div>
                <div style="font-size: 0.75rem; color: var(--muted); margin-top: 0.2rem;">
                    Latest: {w1}kg × {r1} vs Prev: {w2}kg × {r2}
                </div>
            </div>
        """)
        
    if not status_cards:
        st.info("No comparative data available in the last 14 days.")
    else:
        st.markdown("".join(status_cards), unsafe_allow_html=True)
