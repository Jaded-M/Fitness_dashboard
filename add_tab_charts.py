import os
import ast

def append_to_charts():
    with open("ui/charts.py", "a", encoding="utf-8") as f:
        f.write('''
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
            fig_i.update_layout(
                **CHART_LAYOUT,
                title=dict(text="Intensity Over Time", font=dict(color="#d1d5db")),
                yaxis_title="kg per minute",
                height=250
            ) 
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
        
    import plotly.express as px
    
    fig_4d = px.scatter(
        df_merged,
        x="calories",
        y="Weight",
        size="Volume" if df_merged["Volume"].sum() > 0 else None,
        color="steps" if df_merged["steps"].sum() > 0 else None,
        color_continuous_scale="Plasma",
        hover_data=["Date", "Volume", "steps"],
        trendline="ols",
        title="Body Weight vs Daily Calories"
    )
    
    fig_4d.update_layout(
        **CHART_LAYOUT,
        xaxis_title="Calories Consumed (kcal)",
        yaxis_title="Body Weight (kg)",
        height=400,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    # Fix trendline color visually
    fig_4d.update_traces(line=dict(color="#00d2ff", dash="dash"), selector=dict(mode="lines"))
    
    st.plotly_chart(fig_4d, use_container_width=True, config=CHART_CONFIG)
''')

if __name__ == "__main__":
    append_to_charts()
