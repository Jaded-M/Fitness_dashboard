"""
# ════════════════════════════════════════════════════════════════
# MODULE: ui/nutrition_charts.py
# ════════════════════════════════════════════════════════════════
# // WHAT IT DOES:
#    Contains all the Plotly rendering logic for the Nutrition app.
#
# // HOW IT WORKS:
#    Instead of the main file calculating layout margins and appending
#    traces, it just passes the dataframe (e.g. food_df) to these functions.
#    These functions slice the data by timeframe and render the charts.
#
# // PYTHON CONCEPT: 
#    This heavily uses Pandas DataFrame filtering and grouping methods
#    (e.g., df.groupby() and dt.date masking).
# ════════════════════════════════════════════════════════════════
"""
import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go
from core.bca_engine import BCA_Engine
from ui.theme import CHART_CONFIG, chart_layout as cl_fn
from utils import get_day_stats

# Keep the cl() helper signature that this file already uses
def cl(**overrides):
    """Shorthand: merge BASE_LAYOUT with overrides."""
    return cl_fn(**overrides)


def render_weekly_trends(food_df, tf_days, cal_goal):
    if food_df.empty:
        st.info("Log meals to see weekly trends.")
        return
        
    today_ts = pd.Timestamp.now().normalize()
    last_7   = food_df[food_df["date"] >= (today_ts - datetime.timedelta(days=tf_days))]
    
    # ── Calorie Trend ──
    daily_cal  = last_7.groupby(last_7["date"].dt.date)["calories"].sum().reset_index()
    daily_cal.columns = ["Date", "Calories"]
    daily_cal["Date"] = pd.to_datetime(daily_cal["Date"])

    bar_colors = [
        "#00ff88" if c <= cal_goal else "#ff5555"
        for c in daily_cal["Calories"]
    ]

    fig_cal = go.Figure(go.Bar(
        x=daily_cal["Date"], y=daily_cal["Calories"],
        marker=dict(color=bar_colors, line=dict(color="rgba(255,255,255,0.1)", width=0.5)),
        hovertemplate="<b>%{x|%d %b}</b><br>Calories: %{y:,} kcal<extra></extra>"
    ))
    
    fig_cal.add_hline(
        y=cal_goal, line_dash="dot", line_color="orange",
        annotation_text="Daily Goal", annotation_font_color="orange"
    )
    
    if len(daily_cal) > 0:
        avg_cal = daily_cal["Calories"].mean()
        fig_cal.add_hline(
            y=avg_cal, line_dash="dash", line_color="cyan",
            annotation_text=f"Avg: {int(avg_cal)}", annotation_font_color="cyan"
        )
    
    chart_title = f"📅 Calorie Intake — Last {tf_days} Days" if tf_days < 9999 else "📅 Calorie Intake — All Time"
    fig_cal.update_layout(**cl(title=dict(text=chart_title, font=dict(size=16, color="#00d2ff")), yaxis_title="Calories (kcal)"))
    st.plotly_chart(fig_cal, use_container_width=True, config=CHART_CONFIG)

    # ── Protein Trend ──
    daily_p = last_7.groupby(last_7["date"].dt.date)["protein"].sum().reset_index()
    daily_p.columns = ["Date", "Protein"]
    daily_p["Date"] = pd.to_datetime(daily_p["Date"])

    fig_prot = go.Figure()
    fig_prot.add_trace(go.Scatter(
        x=daily_p["Date"], y=daily_p["Protein"],
        mode="lines+markers", name="Protein",
        line=dict(color="#ff79c6", width=3),
        marker=dict(size=8, color="#ff79c6", line=dict(color="white", width=1.5)),
        fill="tozeroy", fillcolor="rgba(255,121,198,0.08)",
        hovertemplate="<b>%{x|%d %b}</b><br>Protein: %{y}g<extra></extra>"
    ))
    chart_title_prot = f"🥩 Protein Intake — Last {tf_days} Days" if tf_days < 9999 else "🥩 Protein Intake — All Time"
    fig_prot.update_layout(**cl(title=dict(text=chart_title_prot, font=dict(size=16, color="#ff79c6")), yaxis_title="Protein (g)"))
    st.plotly_chart(fig_prot, use_container_width=True, config=CHART_CONFIG)


def render_day_breakdown(food_df, cal_goal, MACRO_SPLIT_PROTEIN, MACRO_SPLIT_CARBS, MACRO_SPLIT_FATS):
    if food_df.empty:
        st.info("Log meals to see the day breakdown.")
        return

    today_date = datetime.date.today()
    selected_day = st.date_input("📆 View metrics for:", today_date, key="day_picker")
    
    ts = pd.Timestamp(selected_day)
    day_df = food_df[food_df["date"].dt.normalize() == ts]
    s_cal, s_prot, s_carb, s_fat, s_fib = get_day_stats(food_df, selected_day)

    if day_df.empty:
        st.info(f"No food logged on {selected_day.strftime('%d %b %Y')}.")
        return

    tgt_cal  = cal_goal
    tgt_prot = int((tgt_cal * MACRO_SPLIT_PROTEIN) / 4)
    tgt_carb = int((tgt_cal * MACRO_SPLIT_CARBS) / 4)
    tgt_fat  = int((tgt_cal * MACRO_SPLIT_FATS) / 9)

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("🔥 Calories",  s_cal, f"{tgt_cal - s_cal:+} kcal remaining", delta_color="inverse")
    d2.metric("🥩 Protein",   s_prot, f"{tgt_prot - s_prot:+} g remaining", delta_color="inverse")
    d3.metric("🍞 Carbs",     s_carb, f"{tgt_carb - s_carb:+} g remaining", delta_color="inverse")
    d4.metric("🥑 Fats",      s_fat, f"{tgt_fat - s_fat:+} g remaining", delta_color="inverse")

    st.markdown("##### 📊 Macro Progress")
    
    def get_prog(current, tgt):
        return min(current / tgt, 1.0) * 100 if tgt > 0 else 0
        
    p_pct = get_prog(s_prot, tgt_prot)
    c_pct = get_prog(s_carb, tgt_carb)
    f_pct = get_prog(s_fat, tgt_fat)
    
    st.markdown(f"""
    <div class="macro-container">
        <div class="macro-card">
            <div class="macro-title">Protein</div>
            <div class="macro-value">{s_prot}g <span>/ {tgt_prot}g</span></div>
            <div class="custom-progress-track">
                <div class="custom-progress-fill {'over' if s_prot>tgt_prot else ''}" style="width: {p_pct}%;"></div>
            </div>
        </div>
        <div class="macro-card">
            <div class="macro-title">Carbs</div>
            <div class="macro-value">{s_carb}g <span>/ {tgt_carb}g</span></div>
            <div class="custom-progress-track">
                <div class="custom-progress-fill {'over' if s_carb>tgt_carb else ''}" style="width: {c_pct}%;"></div>
            </div>
        </div>
        <div class="macro-card">
            <div class="macro-title">Fats</div>
            <div class="macro-value">{s_fat}g <span>/ {tgt_fat}g</span></div>
            <div class="custom-progress-track">
                <div class="custom-progress-fill {'over' if s_fat>tgt_fat else ''}" style="width: {f_pct}%;"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=s_cal,
        delta={"reference": cal_goal, "decreasing": {"color": "#00ff88"}, "increasing": {"color": "#ff5555"}},
        title={"text": f"Calories — {selected_day.strftime('%d %b %Y')}", "font": {"color": "white"}},
        gauge={
            "axis": {"range": [0, cal_goal * 1.5], "tickcolor": "white"},
            "bar":  {"color": "#00d2ff"},
            "steps": [
                {"range": [0, cal_goal * 0.75], "color": "rgba(0,255,136,0.15)"},
                {"range": [cal_goal * 0.75, cal_goal], "color": "rgba(0,210,255,0.15)"},
                {"range": [cal_goal, cal_goal * 1.5], "color": "rgba(255,85,85,0.15)"},
            ],
            "threshold": {"line": {"color": "orange", "width": 3}, "value": cal_goal}
        },
        number={"suffix": " kcal", "font": {"color": "white"}}
    ))
    fig_gauge.update_layout(**cl(height=400, margin=dict(t=30, b=15, l=40, r=35), hovermode=False))
    st.plotly_chart(fig_gauge, use_container_width=True, config=CHART_CONFIG)

    gc1, gc2 = st.columns(2)
    with gc1:
        fig_donut = go.Figure(go.Pie(
            labels=["Protein", "Carbs", "Fats"],
            values=[s_prot, s_carb, s_fat],
            hole=0.5,
            marker=dict(colors=["#ff79c6", "#8B4FEC", "#f1fa8c"], line=dict(color="rgba(255,255,255,0.15)", width=2)),
            hovertemplate="<b>%{label}</b>: %{value}g (%{percent})<extra></extra>", textinfo="label+percent"
        ))
        fig_donut.update_layout(**cl(height=280, margin=dict(t=40, b=10, l=10, r=10), hovermode=False,
            title=dict(text="Consumed Macro Split", font=dict(size=14, color="#f1fa8c")),
            annotations=[dict(text=f"<b>{s_cal}</b><br>kcal", x=0.5, y=0.5, font_size=13, showarrow=False, font=dict(color="white"))]
        ))
        st.plotly_chart(fig_donut, use_container_width=True, config=CHART_CONFIG)
        
    with gc2:
        meal_split = day_df.groupby("meal_type")["calories"].sum().reset_index()
        meal_split.columns = ["Meal", "Calories"]
        fig_meal = go.Figure(go.Bar(
            x=meal_split["Calories"], y=meal_split["Meal"], orientation="h",
            marker=dict(color=meal_split["Calories"], colorscale="Plasma", showscale=False, line=dict(color="rgba(255,255,255,0.1)", width=0.5)),
            text=meal_split["Calories"].apply(lambda v: f"{v} kcal"), textposition="inside", textfont=dict(color="white")
        ))
        fig_meal.update_layout(**cl(height=280, margin=dict(t=40, b=10, l=10, r=10), hovermode="y unified", title=dict(text="By Meal", font=dict(size=14, color="#8B4FEC")), xaxis_title="kcal"))
        st.plotly_chart(fig_meal, use_container_width=True, config=CHART_CONFIG)

    st.markdown("##### 📋 Food Log")
    show_cols = ["food_item", "calories", "protein", "carbs", "fats", "fiber", "meal_type"]
    day_table = day_df[show_cols].copy()
    day_table.columns = ["Food", "Calories", "Protein", "Carbs", "Fats", "Fiber", "Meal"]
    st.dataframe(day_table, use_container_width=True, hide_index=True)


def render_body_progress(physical_df, tf_days):
    if physical_df.empty or len(physical_df) < 1:
        st.info("Log body measurements using the form on the left.")
        return
        
    today_ts = pd.Timestamp.now().normalize()
    phys = physical_df[physical_df["Date"] >= (today_ts - datetime.timedelta(days=tf_days))].copy() if tf_days < 9999 else physical_df.copy()
    phys = phys.sort_values("Date").copy()

    fig_w = go.Figure()
    fig_w.add_trace(go.Scatter(
        x=phys["Date"], y=phys["Weight"],
        mode="lines+markers", name="Weight (kg)",
        line=dict(color="#00d2ff", width=3),
        marker=dict(size=9, color="#00d2ff", line=dict(color="white", width=1.5)),
        fill="tozeroy", fillcolor="rgba(0,210,255,0.07)",
        hovertemplate="<b>%{x|%d %b %Y}</b><br>%{y:.1f} kg<extra></extra>"
    ))
    
    if len(phys) > 1:
        delta = phys["Weight"].iloc[-1] - phys["Weight"].iloc[0]
        fig_w.add_annotation(
            x=phys["Date"].iloc[-1], y=phys["Weight"].iloc[-1],
            text=(f"{'▼' if delta <= 0 else '▲'} {abs(delta):.1f} kg {'lost' if delta <= 0 else 'gained'}"),
            showarrow=True, arrowhead=2,
            font=dict(color="#00ff88" if delta <= 0 else "#ff5555", size=12),
            bgcolor="rgba(0,0,0,0.5)", borderpad=4
        )
        
    fig_w.update_layout(**cl(title=dict(text="⚖️ Weight Trend", font=dict(size=16, color="#00d2ff")), yaxis_title="Weight (kg)"))
    st.plotly_chart(fig_w, use_container_width=True, config=CHART_CONFIG)

    def render_measurement_chart(measurement, color, emoji):
        if measurement not in phys.columns: return
        m_data = phys[phys[measurement].notna() & (phys[measurement] > 0)]
        if not m_data.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=m_data["Date"], y=m_data[measurement],
                mode="lines+markers", name=f"{measurement} (in)",
                line=dict(color=color, width=3),
                marker=dict(size=9, color=color, line=dict(color="white", width=1.5)),
                fill="tozeroy", fillcolor=color.replace(")", ",0.07)").replace("rgb", "rgba"),
                hovertemplate="<b>%{x|%d %b %Y}</b><br>%{y:.1f} in<extra></extra>"
            ))
            fig.update_layout(**cl(title=dict(text=f"{emoji} {measurement} Trend", font=dict(size=16, color=color)), yaxis_title=f"{measurement} (inches)"))
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    render_measurement_chart("Waist", "#ff79c6", "📏")
    render_measurement_chart("Hips", "#8B4FEC", "🍑")
    render_measurement_chart("Thigh", "#f1fa8c", "🦵")
    render_measurement_chart("Chest", "#50fa7b", "🫁")
    render_measurement_chart("Arms", "#ffb86c", "💪")

    st.markdown("##### 📋 All Measurements")
    disp = phys.copy()
    disp["Date"] = disp["Date"].dt.strftime("%d %b %Y")
    st.dataframe(disp, use_container_width=True, hide_index=True)


def render_macro_history(food_df, water_df_raw, tf_days, water_goal):
    if not food_df.empty:
        today_ts = pd.Timestamp.now().normalize()
        last_14  = food_df[food_df["date"] >= (today_ts - datetime.timedelta(days=tf_days))]
        m_daily  = last_14.groupby(last_14["date"].dt.date)[["protein","carbs","fats","fiber"]].sum().reset_index()
        m_daily.columns = ["Date","Protein","Carbs","Fats","Fiber"]
        m_daily["Date"] = pd.to_datetime(m_daily["Date"])

        fig_stack = go.Figure()
        macro_colors = {"Protein": "#ff79c6", "Carbs": "#8B4FEC", "Fats": "#f1fa8c", "Fiber": "#50fa7b"}
        for macro, color in macro_colors.items():
            fig_stack.add_trace(go.Bar(
                x=m_daily["Date"], y=m_daily[macro], name=macro, marker_color=color,
                hovertemplate=f"<b>%{{x|%d %b}}</b><br>{macro}: %{{y}}g<extra></extra>"
            ))
        chart_title_stack = f"📊 Daily Macros — Last {tf_days} Days" if tf_days < 9999 else "📊 Daily Macros — All Time"
        fig_stack.update_layout(**cl(barmode="stack", title=dict(text=chart_title_stack, font=dict(size=16, color="#f1fa8c")), yaxis_title="Grams (g)"))
        st.plotly_chart(fig_stack, use_container_width=True, config=CHART_CONFIG)

    # Hydration history
    if not water_df_raw.empty:
        wh = water_df_raw.copy()
        wh["date"] = pd.to_datetime(wh["date"])
        today_ts   = pd.Timestamp.now().normalize()
        wh_7 = wh[wh["date"] >= (today_ts - datetime.timedelta(days=tf_days))]
        wh_7 = wh_7.groupby(wh_7["date"].dt.date)["cups"].sum().reset_index()
        wh_7.columns = ["Date", "Cups"]
        wh_7["Date"] = pd.to_datetime(wh_7["Date"])

        fig_water = go.Figure(go.Bar(
            x=wh_7["Date"], y=wh_7["Cups"],
            marker=dict(color=wh_7["Cups"], colorscale="Blues", showscale=False, line=dict(color="rgba(255,255,255,0.1)", width=0.5)),
            hovertemplate="<b>%{x|%d %b}</b><br>Cups: %{y}<extra></extra>"
        ))
        fig_water.add_hline(y=water_goal, line_dash="dot", line_color="cyan", annotation_text="Daily Goal", annotation_font_color="cyan")
        chart_title_water = f"💧 Hydration — Last {tf_days} Days" if tf_days < 9999 else "💧 Hydration — All Time"
        fig_water.update_layout(**cl(title=dict(text=chart_title_water, font=dict(size=16, color="#00d2ff")), yaxis_title="Cups"))
        st.plotly_chart(fig_water, use_container_width=True, config=CHART_CONFIG)
    elif food_df.empty and water_df_raw.empty:
        st.info("Log food and water to see history charts.")


def render_bca_engine(latest_weight):
    st.markdown("##### 🧬 Biological Engine")
    st.markdown("Using your Body Composition Analysis (BCA) to calculate exact metabolic needs.")
    
    current_wt = latest_weight if latest_weight else 89.3
    engine = BCA_Engine(current_wt)
    
    metrics = engine.estimate_current_metrics()
    bmr = engine.get_dynamic_bmr()
    macros = engine.get_macro_targets(goal="cut")
    
    st.markdown(f"**Current Weight:** {current_wt} kg")
    c1, c2, c3 = st.columns(3)
    c1.metric("🔥 Precise BMR", f"{bmr} kcal", help="Katch-McArdle Formula")
    c2.metric("🥩 Lean Mass", f"{metrics['estimated_smm_kg']} kg", help="Skeletal Muscle Mass")
    c3.metric("🧈 Body Fat", f"{metrics['estimated_pbf_percent']}%", help="Estimated based on weight loss")
    
    st.markdown("---")
    st.markdown("###### 📊 Precision Macro Targets (Cutting Phase)")
    st.info(f"Target Calories: **{macros['target_calories']} kcal/day**")
    
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Protein", f"{macros['protein_g']}g", "Preserve Muscle")
    mc2.metric("Fats", f"{macros['fat_g']}g", "Hormones")
    mc3.metric("Carbs", f"{macros['carbs_g']}g", "Workout Energy")
    st.caption("Note: These macros are dynamically calculated against your live Lean Body Mass via `core/bca_engine.py`.")
    
    st.markdown("---")
    st.markdown("##### 🚀 Road to 72.1 kg (Weight Projection)")
    
    if current_wt > 72.1:
        kg_to_lose = current_wt - 72.1
        weeks_needed = int(kg_to_lose / 0.5)
        target_date = datetime.date.today() + datetime.timedelta(weeks=weeks_needed)
        
        st.success(f"🎯 **Target:** Based on your current BMR/Macros, you are on track to hit **72.1 kg** in approximately **{weeks_needed} weeks** ({target_date.strftime('%B %Y')}).")
        
        dates = [datetime.date.today() + datetime.timedelta(weeks=i) for i in range(weeks_needed + 1)]
        weights = [current_wt - (0.5 * i) for i in range(weeks_needed + 1)]
        
        fig_proj = go.Figure()
        fig_proj.add_trace(go.Scatter(
            x=dates, y=weights, mode='lines', name='Estimated Path',
            line=dict(color='#f59e0b', width=3, dash='dash'),
            fill='tozeroy', fillcolor='rgba(245, 158, 11, 0.05)'
        ))
        fig_proj.add_hline(y=72.1, line_dash="dot", line_color="#00d2ff", annotation_text="Goal: 72.1kg")
        fig_proj.update_layout(**cl(title="📈 Scientific Weight Projection", yaxis_title="Weight (kg)", height=350, margin=dict(t=30, b=20, l=10, r=10)))
        st.plotly_chart(fig_proj, use_container_width=True, config=CHART_CONFIG)
    else:
        st.balloons()
        st.success("🎉 You've hit your target weight! Switching to Maintenance/Bulk mode.")
