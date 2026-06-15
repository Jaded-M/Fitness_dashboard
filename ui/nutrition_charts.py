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
from ui.theme import CHART_CONFIG, PHI_COLORS, chart_layout as cl_fn
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
        PHI_COLORS["green"] if c <= cal_goal else PHI_COLORS["rose"]
        for c in daily_cal["Calories"]
    ]

    fig_cal = go.Figure(go.Bar(
        x=daily_cal["Date"], y=daily_cal["Calories"],
        marker=dict(color=bar_colors, line=dict(color="rgba(255,255,255,0.1)", width=0.5)),
        hovertemplate="<b>%{x|%d %b}</b><br>Calories: %{y:,} kcal<extra></extra>"
    ))
    
    fig_cal.add_hline(
        y=cal_goal, line_dash="dot", line_color=PHI_COLORS["amber"],
        annotation_text="Daily goal", annotation_font_color=PHI_COLORS["amber"]
    )
    
    if len(daily_cal) > 0:
        avg_cal = daily_cal["Calories"].mean()
        fig_cal.add_hline(
            y=avg_cal, line_dash="dash", line_color=PHI_COLORS["blue"],
            annotation_text=f"Average {int(avg_cal)}", annotation_font_color=PHI_COLORS["blue"]
        )
    
    chart_title = f"Calorie intake - last {tf_days} days" if tf_days < 9999 else "Calorie intake - all time"
    fig_cal.update_layout(**cl(title=dict(text=chart_title, font=dict(size=16, color=PHI_COLORS["blue"])), yaxis_title="Calories (kcal)"))
    st.plotly_chart(fig_cal, use_container_width=True, config=CHART_CONFIG)

    # ── Protein Trend ──
    daily_p = last_7.groupby(last_7["date"].dt.date)["protein"].sum().reset_index()
    daily_p.columns = ["Date", "Protein"]
    daily_p["Date"] = pd.to_datetime(daily_p["Date"])

    fig_prot = go.Figure()
    fig_prot.add_trace(go.Scatter(
        x=daily_p["Date"], y=daily_p["Protein"],
        mode="lines+markers", name="Protein",
        line=dict(color=PHI_COLORS["green"], width=3),
        marker=dict(size=8, color=PHI_COLORS["green"], line=dict(color="rgba(23,32,28,0.20)", width=1.2)),
        fill="tozeroy", fillcolor="rgba(47,159,104,0.10)",
        hovertemplate="<b>%{x|%d %b}</b><br>Protein: %{y}g<extra></extra>"
    ))
    chart_title_prot = f"Protein intake - last {tf_days} days" if tf_days < 9999 else "Protein intake - all time"
    fig_prot.update_layout(**cl(title=dict(text=chart_title_prot, font=dict(size=16, color=PHI_COLORS["green"])), yaxis_title="Protein (g)"))
    st.plotly_chart(fig_prot, use_container_width=True, config=CHART_CONFIG)


def render_day_breakdown(food_df, cal_goal, MACRO_SPLIT_PROTEIN, MACRO_SPLIT_CARBS, MACRO_SPLIT_FATS):
    if food_df.empty:
        st.info("Log meals to see the day breakdown.")
        return

    today_date = datetime.date.today()
    selected_day = st.date_input("View metrics for", today_date, key="day_picker")
    
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
    d1.metric("Calories",  s_cal, f"{tgt_cal - s_cal:+} kcal remaining", delta_color="inverse")
    d2.metric("Protein",   s_prot, f"{tgt_prot - s_prot:+} g remaining", delta_color="inverse")
    d3.metric("Carbs",     s_carb, f"{tgt_carb - s_carb:+} g remaining", delta_color="inverse")
    d4.metric("Fats",      s_fat, f"{tgt_fat - s_fat:+} g remaining", delta_color="inverse")

    st.markdown("##### Macro Progress")
    
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
        delta={"reference": cal_goal, "decreasing": {"color": PHI_COLORS["green"]}, "increasing": {"color": PHI_COLORS["rose"]}},
        title={"text": f"Calories - {selected_day.strftime('%d %b %Y')}", "font": {"color": PHI_COLORS["ink"]}},
        gauge={
            "axis": {"range": [0, cal_goal * 1.5], "tickcolor": "#94a3b8"},
            "bar":  {"color": PHI_COLORS["blue"]},
            "steps": [
                {"range": [0, cal_goal * 0.75], "color": "rgba(94,226,160,0.15)"},
                {"range": [cal_goal * 0.75, cal_goal], "color": "rgba(86,199,216,0.15)"},
                {"range": [cal_goal, cal_goal * 1.5], "color": "rgba(255,107,122,0.15)"},
            ],
            "threshold": {"line": {"color": PHI_COLORS["amber"], "width": 3}, "value": cal_goal}
        },
        number={"suffix": " kcal", "font": {"color": PHI_COLORS["ink"]}}
    ))
    fig_gauge.update_layout(**cl(height=400, margin=dict(t=30, b=15, l=40, r=35), hovermode=False))
    st.plotly_chart(fig_gauge, use_container_width=True, config=CHART_CONFIG)

    gc1, gc2 = st.columns(2)
    with gc1:
        fig_donut = go.Figure(go.Pie(
            labels=["Protein", "Carbs", "Fats"],
            values=[s_prot, s_carb, s_fat],
            hole=0.5,
            marker=dict(colors=[PHI_COLORS["green"], PHI_COLORS["blue"], PHI_COLORS["amber"]], line=dict(color="rgba(23,32,28,0.10)", width=2)),
            hovertemplate="<b>%{label}</b>: %{value}g (%{percent})<extra></extra>", textinfo="label+percent"
        ))
        fig_donut.update_layout(**cl(height=280, margin=dict(t=40, b=10, l=10, r=10), hovermode=False,
            title=dict(text="Consumed macro split", font=dict(size=14, color=PHI_COLORS["amber"])),
            annotations=[dict(text=f"<b>{s_cal}</b><br>kcal", x=0.5, y=0.5, font_size=13, showarrow=False, font=dict(color=PHI_COLORS["ink"]))]
        ))
        st.plotly_chart(fig_donut, use_container_width=True, config=CHART_CONFIG)
        
    with gc2:
        meal_split = day_df.groupby("meal_type")["calories"].sum().reset_index()
        meal_split.columns = ["Meal", "Calories"]
        fig_meal = go.Figure(go.Bar(
            x=meal_split["Calories"], y=meal_split["Meal"], orientation="h",
            marker=dict(color=PHI_COLORS["blue"], line=dict(color="rgba(23,32,28,0.1)", width=0.5)),
            text=meal_split["Calories"].apply(lambda v: f"{v} kcal"), textposition="inside", textfont=dict(color="#ffffff")
        ))
        fig_meal.update_layout(**cl(height=280, margin=dict(t=40, b=10, l=10, r=10), hovermode="y unified", title=dict(text="By meal", font=dict(size=14, color=PHI_COLORS["blue"])), xaxis_title="kcal"))
        st.plotly_chart(fig_meal, use_container_width=True, config=CHART_CONFIG)

    st.markdown("##### Food Log")
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
        line=dict(color=PHI_COLORS["blue"], width=3),
        marker=dict(size=9, color=PHI_COLORS["blue"], line=dict(color="rgba(23,32,28,0.20)", width=1.2)),
        fill="tozeroy", fillcolor="rgba(25,127,150,0.09)",
        hovertemplate="<b>%{x|%d %b %Y}</b><br>%{y:.1f} kg<extra></extra>"
    ))
    
    if len(phys) > 1:
        delta = phys["Weight"].iloc[-1] - phys["Weight"].iloc[0]
        fig_w.add_annotation(
            x=phys["Date"].iloc[-1], y=phys["Weight"].iloc[-1],
            text=(f"{'down' if delta <= 0 else 'up'} {abs(delta):.1f} kg {'lost' if delta <= 0 else 'gained'}"),
            showarrow=True, arrowhead=2,
            font=dict(color=PHI_COLORS["green"] if delta <= 0 else PHI_COLORS["rose"], size=12),
            bgcolor="rgba(255,255,255,0.92)", borderpad=4
        )
        
    fig_w.update_layout(**cl(title=dict(text="Weight trend", font=dict(size=16, color=PHI_COLORS["blue"])), yaxis_title="Weight (kg)"))
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
                marker=dict(size=9, color=color, line=dict(color="rgba(255,255,255,0.55)", width=1.2)),
                fill="tozeroy", fillcolor=color.replace(")", ",0.07)").replace("rgb", "rgba"),
                hovertemplate="<b>%{x|%d %b %Y}</b><br>%{y:.1f} in<extra></extra>"
            ))
            fig.update_layout(**cl(title=dict(text=f"{measurement} trend", font=dict(size=16, color=color)), yaxis_title=f"{measurement} (inches)"))
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    render_measurement_chart("Waist", PHI_COLORS["rose"], "")
    render_measurement_chart("Hips", "#b9a7ff", "")
    render_measurement_chart("Thigh", PHI_COLORS["amber"], "")
    render_measurement_chart("Chest", PHI_COLORS["green"], "")
    render_measurement_chart("Arms", PHI_COLORS["blue"], "")

    st.markdown("##### All Measurements")
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
        macro_colors = {"Protein": PHI_COLORS["green"], "Carbs": PHI_COLORS["blue"], "Fats": PHI_COLORS["amber"], "Fiber": PHI_COLORS["violet"]}
        for macro, color in macro_colors.items():
            fig_stack.add_trace(go.Bar(
                x=m_daily["Date"], y=m_daily[macro], name=macro, marker_color=color,
                hovertemplate=f"<b>%{{x|%d %b}}</b><br>{macro}: %{{y}}g<extra></extra>"
            ))
        chart_title_stack = f"Daily macros - last {tf_days} days" if tf_days < 9999 else "Daily macros - all time"
        fig_stack.update_layout(**cl(barmode="stack", title=dict(text=chart_title_stack, font=dict(size=16, color=PHI_COLORS["amber"])), yaxis_title="Grams (g)"))
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
            marker=dict(color=PHI_COLORS["blue"], line=dict(color="rgba(23,32,28,0.1)", width=0.5)),
            hovertemplate="<b>%{x|%d %b}</b><br>Cups: %{y}<extra></extra>"
        ))
        fig_water.add_hline(y=water_goal, line_dash="dot", line_color=PHI_COLORS["blue"], annotation_text="Daily goal", annotation_font_color=PHI_COLORS["blue"])
        chart_title_water = f"Hydration - last {tf_days} days" if tf_days < 9999 else "Hydration - all time"
        fig_water.update_layout(**cl(title=dict(text=chart_title_water, font=dict(size=16, color=PHI_COLORS["blue"])), yaxis_title="Cups"))
        st.plotly_chart(fig_water, use_container_width=True, config=CHART_CONFIG)
    elif food_df.empty and water_df_raw.empty:
        st.info("Log food and water to see history charts.")


def render_bca_engine(latest_weight: float) -> None:
    """
    Dynamic Biological Composition Analysis panel.

    All inputs are editable by the user at runtime — no hardcoded personal
    values.  The engine recalculates BMR, TDEE, macros, and a weight-
    projection chart whenever any input changes.
    """
    import datetime
    from core.bca_engine import BCA_Engine, ACTIVITY_MULTIPLIERS

    st.markdown(
        """
        <div style="margin-bottom:1.1rem;">
            <div style="color:var(--muted);font-size:0.72rem;font-weight:700;
                        letter-spacing:0.08em;text-transform:uppercase;
                        margin-bottom:0.3rem;">Biological Engine</div>
            <div style="color:#f5f1e8;font-size:1.05rem;font-weight:700;
                        margin-bottom:0.25rem;">Precision Metabolic Calculator</div>
            <div style="color:var(--muted);font-size:0.85rem;">
                Katch-McArdle BMR blended with Mifflin-St Jeor when profile data
                is provided. All figures update in real time.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Input panel ───────────────────────────────────────────────────────────
    with st.expander("Configure your biometric profile", expanded=True):
        col_a, col_b = st.columns(2)
        with col_a:
            current_wt = st.number_input(
                "Current weight (kg)", min_value=40.0, max_value=200.0,
                value=float(latest_weight) if latest_weight else 80.0,
                step=0.1, key="bca_wt",
            )
            age = st.number_input(
                "Age (years)", min_value=15, max_value=80,
                value=25, step=1, key="bca_age",
            )
            sex = st.selectbox(
                "Biological sex", ["Male", "Female"], key="bca_sex",
            )
        with col_b:
            height_cm = st.number_input(
                "Height (cm)", min_value=140.0, max_value=220.0,
                value=175.0, step=0.5, key="bca_height",
            )
            activity_label = st.selectbox(
                "Activity level",
                options=list(ACTIVITY_MULTIPLIERS.keys()),
                index=2,  # "moderate" default
                format_func=lambda k: {
                    "sedentary":   "Sedentary (desk job, no gym)",
                    "light":       "Light (1-3 workouts/week)",
                    "moderate":    "Moderate (3-5 workouts/week)",
                    "active":      "Active (6-7 workouts/week)",
                    "very_active": "Very active (physical job + gym)",
                }[k],
                key="bca_activity",
            )
            goal = st.selectbox(
                "Goal", ["cut", "maintenance", "bulk"], index=0, key="bca_goal",
                format_func=lambda g: {
                    "cut":         "Cut - lose fat (~0.5 kg/week)",
                    "maintenance": "Maintenance - hold weight",
                    "bulk":        "Bulk - lean gain (~0.25 kg/week)",
                }[g],
            )

        st.markdown("**Baseline BCA scan values** (from your last InBody / DEXA report)")
        bc1, bc2, bc3 = st.columns(3)
        with bc1:
            base_weight  = st.number_input("Scan weight (kg)",   40.0, 200.0, 89.3, 0.1, key="bca_bw")
            base_bf_mass = st.number_input("Body fat mass (kg)",  0.0, 100.0, 33.5, 0.1, key="bca_bf")
        with bc2:
            base_smm = st.number_input("Skeletal muscle (kg)", 0.0, 80.0, 30.9, 0.1, key="bca_smm")
            base_ffm = st.number_input("Fat-free mass (kg)",   0.0, 150.0, 55.8, 0.1, key="bca_ffm")
        with bc3:
            base_pbf = st.number_input("Body fat %",            0.0, 70.0,  37.6, 0.1, key="bca_pbf")
            base_bmr = st.number_input("Scan BMR (kcal)",       800, 4000, 1575, 10,  key="bca_bmr")

        target_wt = st.number_input(
            "Target weight (kg) - projection target",
            min_value=40.0, max_value=200.0,
            value=max(40.0, current_wt - 10.0),
            step=0.5, key="bca_target",
        )

    # ── Build engine ─────────────────────────────────────────────────────────
    engine = BCA_Engine(
        current_weight_kg=current_wt,
        base_weight=base_weight,
        base_bf_mass=base_bf_mass,
        base_smm=base_smm,
        base_bmr=base_bmr,
        base_pbf=base_pbf,
        base_ffm=base_ffm,
        age=int(age),
        sex=sex.lower(),
        height_cm=float(height_cm),
        activity_level=activity_label,
    )

    metrics = engine.estimate_current_metrics()
    targets = engine.get_macro_targets(goal=goal, target_weight_kg=target_wt)

    # ── KPI row 1: composition ────────────────────────────────────────────────
    st.markdown("")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("BMR",       f"{targets['bmr']:,} kcal",  help="Katch-McArdle (lean-mass weighted)")
    k2.metric("TDEE",      f"{targets['tdee']:,} kcal", help="Total Daily Energy Expenditure")
    k3.metric("Lean mass", f"{metrics['estimated_lbm_kg']} kg")
    k4.metric("Body fat",  f"{metrics['estimated_pbf_percent']}%")

    # ── KPI row 2: macro targets ──────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="background:var(--panel);border:1px solid var(--line);
                    border-radius:10px;padding:1rem;margin:0.75rem 0;">
            <div style="color:var(--muted);font-size:0.72rem;font-weight:700;
                        letter-spacing:0.08em;text-transform:uppercase;margin-bottom:0.6rem;">
                Precision macro targets - {goal.capitalize()} phase
                &nbsp;/&nbsp; {targets['target_calories']:,} kcal/day
            </div>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.75rem;">
                <div>
                    <div style="color:var(--muted);font-size:0.72rem;font-weight:700;
                                letter-spacing:0.06em;text-transform:uppercase;">Protein</div>
                    <div style="color:var(--green);font-size:1.6rem;font-weight:800;
                                margin:0.3rem 0 0.1rem;">{targets['protein_g']}g</div>
                    <div style="color:var(--muted);font-size:0.8rem;">Preserve muscle</div>
                </div>
                <div>
                    <div style="color:var(--muted);font-size:0.72rem;font-weight:700;
                                letter-spacing:0.06em;text-transform:uppercase;">Fats</div>
                    <div style="color:var(--amber);font-size:1.6rem;font-weight:800;
                                margin:0.3rem 0 0.1rem;">{targets['fat_g']}g</div>
                    <div style="color:var(--muted);font-size:0.8rem;">Hormone health</div>
                </div>
                <div>
                    <div style="color:var(--muted);font-size:0.72rem;font-weight:700;
                                letter-spacing:0.06em;text-transform:uppercase;">Carbs</div>
                    <div style="color:var(--blue);font-size:1.6rem;font-weight:800;
                                margin:0.3rem 0 0.1rem;">{targets['carbs_g']}g</div>
                    <div style="color:var(--muted);font-size:0.8rem;">Workout fuel</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Projection chart ──────────────────────────────────────────────────────
    st.markdown("##### Weight Projection")

    weeks = targets.get("weeks_to_goal")
    target_date_str = targets.get("target_date")

    if weeks and target_date_str:
        target_date = datetime.date.fromisoformat(target_date_str)
        wkly = targets["weekly_change_kg"]

        st.success(
            f"Target **{target_wt} kg** reachable in approximately **{weeks} weeks** "
            f"({target_date.strftime('%B %Y')}) at {wkly:+.2f} kg/week."
        )

        projection_dates   = [datetime.date.today() + datetime.timedelta(weeks=i) for i in range(weeks + 1)]
        projection_weights = [current_wt + (wkly * i) for i in range(weeks + 1)]

        # Optional: smooth to target exactly
        if projection_weights:
            projection_weights[-1] = target_wt

        fig_proj = go.Figure()
        fig_proj.add_trace(go.Scatter(
            x=projection_dates,
            y=projection_weights,
            mode="lines",
            name="Projection",
            line=dict(color="#e5b35d", width=3, dash="dash"),
            fill="tozeroy",
            fillcolor="rgba(229,179,93,0.05)",
            hovertemplate="<b>%{x|%d %b %Y}</b><br>Est. weight: %{y:.1f} kg<extra></extra>",
        ))
        fig_proj.add_hline(
            y=target_wt,
            line_dash="dot", line_color=PHI_COLORS["blue"], line_width=1.5,
            annotation_text=f"Target {target_wt} kg",
            annotation_font_color=PHI_COLORS["blue"], annotation_font_size=11,
        )
        fig_proj.update_layout(**cl(
            title=f"Scientific weight projection - {goal.capitalize()} phase",
            yaxis_title="Weight (kg)",
            height=320,
            margin=dict(t=45, b=20, l=10, r=10),
        ))
        st.plotly_chart(fig_proj, use_container_width=True, config=CHART_CONFIG)
    elif goal == "maintenance":
        st.info("Maintenance mode selected - no weight projection needed.")
    else:
        st.info(
            "Set a target weight that's lower than current weight (cut) "
            "or higher (bulk) to generate a projection."
        )

    st.caption(
        "BMR blends Katch-McArdle (70 %) and Mifflin-St Jeor (30 %) when age, "
        "sex, and height are provided.  All calculations update instantly."
    )
