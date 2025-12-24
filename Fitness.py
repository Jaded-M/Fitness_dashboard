import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import database  # Our new database file

# Initialize Database on startup
database.init_db()

# ============================================
# EXERCISE LIBRARY (Splits)
# LEARNING MOMENT: Dictionaries and Lists
# ============================================
# ============================================
# EXERCISE LIBRARY (User's Custom Split)
# LEARNING MOMENT: Data Structures
# We organize data exactly how we want to use it.
# ============================================
EXERCISE_LIBRARY = {
    "Day A (Power & Push)": [
        "Leg Press",
        "Dumbbell Bench Press",
        "Lat Pulldown",
        "Machine Row",
        "Machine Shoulder Press",
        "Tricep Rope Pushdowns",
        "Bicep Hammer Curls"
    ],
    "Day B (Glutes, Pull, Core)": [
        "Romanian Deadlift (DB)",
        "Goblet Squat",
        "Seated Row",
        "Incline Dumbbell/Chest Machine",
        "Face Pulls",
        "Cable Crunch",
        "Calf Raises"
    ],
    "Day C (Balanced Strength)": [
        "Leg Press / Hack Squat",
        "Dumbbell Shoulder Press",
        "Single-Arm Row",
        "Pec Deck / Cable Fly",
        "Biceps Curls (Left Focus)",
        "Tricep Overhead DB",
        "Lateral Raises"
    ],
    "Cardio / Other": [
        "Walking (Target 7-10k)",
        "Mobility Work",
        "Light Cardio"
    ]
}

# ============================================
# PAGE SETUP
# TINKER: Change page_title and page_icon below
# ============================================
st.set_page_config(page_title="Fitness Dashboard", layout="wide", page_icon="💪")

# ============================================
# PRETTY STYLING
# TINKER: Change colors by replacing the # color codes
# Example: #667eea (purple) → #ff6b6b (red) or #4ecdc4 (teal)
# ============================================
st.markdown("""
<style>
    .main {
        background-color: #f0f2f6;
        padding: 2rem;
    }
    
    h1 {
        color: #1f1f1f !important;
        font-size: 3rem;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    h3 {
        color: #4a4a4a !important;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    h2, h4 {
        color: #2c3e50 !important;
        border-bottom: 3px solid #667eea;
        padding-bottom: 10px;
        margin-top: 2rem;
    }
    
    [data-testid="stMetricValue"] {
        color: #1f1f1f !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #4a4a4a !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    .stAlert {
        background-color: white;
        color: #2c3e50;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-radius: 5px;
    }
    
    /* Card-like look for metrics */
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNCTION: Load Google Sheets
# TINKER: Change sheet_name or worksheet_name if yours is different
# ============================================
def load_google_sheet(sheet_name="Fitness Tracker", worksheet_name="Fitness", creds_file="creds.json"):
    """
    Gets workout data from Google Sheets
    Returns: DataFrame with your workout data
    """
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        client = gspread.authorize(creds)
        sheet = client.open(sheet_name).worksheet(worksheet_name)
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.sidebar.error(f"❌ Google Sheets error: {e}")
        return None

# ============================================
# FUNCTION: Load Google Fit Steps
# TINKER: Change days parameter to get more/less history
# ============================================
def load_google_fit_steps(days=30):
    """
    Gets step count from Google Fit
    Returns: DataFrame with date and steps columns
    """
    # Fix: Check for credentials first to avoid ugly errors
    if not os.path.exists('fitness_credentials.json'):
        # Silent return or sidebar info
        # st.sidebar.info("ℹ️ steps: fitness_credentials.json not found")
        return None

    try:
        SCOPES = ['https://www.googleapis.com/auth/fitness.activity.read']
        creds = None
        
        # Check if we have saved login
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # Login if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('fitness_credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        # Get steps data
        service = build('fitness', 'v1', credentials=creds)
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        start_ms = int(start_time.timestamp() * 1000)
        end_ms = int(end_time.timestamp() * 1000)
        
        dataset = f"{start_ms}000000-{end_ms}000000"
        data_source = "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
        
        response = service.users().dataSources().datasets().get(
            userId='me',
            dataSourceId=data_source,
            datasetId=dataset
        ).execute()
        
        # Convert to DataFrame
        steps_data = []
        if 'point' in response:
            for point in response['point']:
                date = datetime.fromtimestamp(int(point['startTimeNanos']) / 1e9)
                steps = point['value'][0]['intVal']
                steps_data.append({'date': date.date(), 'steps': steps})
        
        if steps_data:
            df = pd.DataFrame(steps_data)
            df = df.groupby('date', as_index=False)['steps'].sum()
            df['date'] = pd.to_datetime(df['date'])
            return df.sort_values('date')
        return None
            
    except Exception as e:
        st.error(f"Steps error: {e}")
        return None

# ============================================
# FUNCTION: Load Excel File
# ============================================
def load_excel_file(filename):
    """Load from uploaded Excel file"""
    try:
        df = pd.read_excel(filename)
        return df
    except Exception as e:
        st.sidebar.error(f"❌ Excel error: {e}")
        return None

# ============================================
# SIDEBAR CONTROLS
# TINKER: Add more options here like date filters
# ============================================
st.sidebar.title("⚙️ Dashboard Settings")
st.sidebar.markdown("---")

# LEARNING MOMENT: Displaying Images
# We check if the file exists first to avoid errors
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)
else:
    st.sidebar.write("🖼️ (Logo Placeholder)")

st.sidebar.markdown("---")

# ============================================
# NEW FEATURE: BMI Calculator
# LEARNING MOMENT: Input -> Logic -> Output
# ============================================
with st.sidebar.expander("🧮 BMI Calculator", expanded=False):
    st.write("Quick Check:")
    # Input
    weight_kg = st.number_input("Weight (kg)", 50, 150, 70)
    height_m = st.number_input("Height (m)", 1.0, 2.5, 1.75)
    
    # Logic / Calculation
    bmi = weight_kg / (height_m ** 2)
    
    # Output with logic (if/else)
    st.metric("Your BMI", f"{bmi:.1f}")
    
    if bmi < 18.5:
        st.warning("Underweight")
    elif 18.5 <= bmi < 25:
        st.success("Healthy Weight")
    elif 25 <= bmi < 30:
        st.warning("Overweight")
    else:
        st.error("Obese")

st.sidebar.markdown("---")

# Choose workout data source
data_source = st.sidebar.radio(
    "📊 Workout Data:",
    ["Local Database (New)", "Google Sheets", "Upload Excel"]
)

uploaded_file = None
if data_source == "Upload Excel":
    uploaded_file = st.sidebar.file_uploader("📁 Choose file", type=['xlsx', 'xls'])

st.sidebar.markdown("---")

# Steps data option
load_steps = st.sidebar.checkbox("👟 Load Google Fit Steps", value=True)

if load_steps:
    # TINKER: Change these numbers to get more/less step history
    days_history = st.sidebar.slider("Days of step history:", 7, 90, 30)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip**: Check boxes above to load different data sources")
st.sidebar.markdown("---")
st.sidebar.success("Made by Mihir 💪")

# ============================================
# LOAD WORKOUT DATA
# ============================================
# ============================================
# LOAD WORKOUT DATA
# ============================================
workout_df = None

# New Database Source
if data_source == "Local Database (New)":
    workout_df = database.get_all_workouts()
    
    # Simple cleaner for DB data
    if not workout_df.empty:
        workout_df["Date"] = pd.to_datetime(workout_df["date"])
        # Rename lower case db columns to Title Case for UI consistency if needed
        workout_df = workout_df.rename(columns={
            "split": "Split", 
            "exercise": "Workout", # Mapping 'exercise' to 'Workout' for existing charts
            "weight": "Weight",
            "duration": "Duration" # Not in DB yet, but prevents errors
        })
        # Mock duration for now so charts work (since we track sets/reps instead)
        workout_df["Duration"] = workout_df["sets"] * workout_df["reps"] * 0.5 

elif data_source == "Google Sheets":
    with st.spinner("Loading workouts from Google Sheets..."):
        workout_df = load_google_sheet()
elif data_source == "Upload Excel" and uploaded_file is not None:
    workout_df = load_excel_file(uploaded_file)

# ============================================
# LOAD STEPS DATA
# ============================================
steps_df = None

if load_steps:
    with st.spinner("Loading steps from Google Fit..."):
        steps_df = load_google_fit_steps(days=days_history)
        if steps_df is not None:
            st.sidebar.success(f"✅ {len(steps_df)} days of steps loaded")

# ============================================
# CLEAN WORKOUT DATA
# TINKER: This section prepares data for charts
# ============================================
workout_ready = False

if workout_df is not None and not workout_df.empty:
    # Show what columns we found (for debugging)
    st.sidebar.write("📋 Found columns:")
    st.sidebar.write(list(workout_df.columns)[:5])
    
    # Clean up column names
    workout_df.columns = [str(c).strip() for c in workout_df.columns]
    
    # Convert Date column to proper date format
    if "Date" in workout_df.columns:
        workout_df["Date"] = pd.to_datetime(workout_df["Date"], errors="coerce")
        workout_df = workout_df.dropna(subset=["Date"])
    
    # Convert Duration and Calories to numbers
    if "Duration" in workout_df.columns:
        workout_df["Duration"] = pd.to_numeric(workout_df["Duration"], errors="coerce")
    if "Calories" in workout_df.columns:
        workout_df["Calories"] = pd.to_numeric(workout_df["Calories"], errors="coerce")
    
    # Remove completely empty rows
    workout_df = workout_df.dropna(how='all')
    
    # Only keep rows with actual workout duration
    if "Duration" in workout_df.columns:
        workout_df = workout_df[workout_df["Duration"] > 0]
    
st.sidebar.markdown("---")

# ============================================
# REST TIMER (NEW FEATURE)
# LEARNING MOMENT: Loops and Time
# ============================================
with st.sidebar.expander("⏱️ Rest Timer", expanded=True):
    col1, col2, col3 = st.columns(3)
    
    # We use session state to track if timer is running
    if "timer_end" not in st.session_state:
        st.session_state.timer_end = 0
    
    start_60 = col1.button("60s")
    start_90 = col2.button("90s")
    start_120 = col3.button("120s")
    
    import time
    
    duration = 0
    if start_60: duration = 60
    if start_90: duration = 90
    if start_120: duration = 120
    
    if duration > 0:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(duration):
            # Calculate percentage
            percent = (i + 1) / duration
            progress_bar.progress(percent)
            status_text.text(f"Rest: {duration - i}s left")
            time.sleep(1)
            
        status_text.success("🔔 GO!")
        st.balloons()

# ============================================
# HEADER
# ============================================
st.title("💪 FITNESS DASHBOARD v1.0")

# ============================================
# LOG WORKOUT SECTION (NEW LOGIC)
# ============================================
with st.expander("📝 Log a New Workout", expanded=False):
    st.markdown("### Add to Database")
    
    # 1. Select Date
    log_date = st.date_input("Date", datetime.now())
    
    # 2. Select Split (Keys of our dictionary)
    selected_split = st.selectbox("Split Type", list(EXERCISE_LIBRARY.keys()))
    
    # 3. Select Exercise
    # LEARNING MOMENT: List Manipulation
    # We take the list of exercises AND add a "Custom" option to it.
    available_exercises = EXERCISE_LIBRARY[selected_split] + ["+ Custom / Other..."]
    selected_exercise = st.selectbox("Exercise", available_exercises)
    
    # Logic: If they chose "Custom", we need to ask what it is.
    # Otherwise, we just use what they picked.
    final_exercise_name = selected_exercise
    
    if selected_exercise == "+ Custom / Other...":
        final_exercise_name = st.text_input("Enter Exercise Name", "My Custom Exercise")
    
    # 4. Enter Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        sets = st.number_input("Sets", 1, 10, 3)
        reps = st.number_input("Reps", 1, 50, 10)
    with col2:
        weight = st.number_input("Weight (kg)", 0.0, 500.0, 20.0, step=2.5)
    with col3:
        # Optional fields
        rpe = st.slider("RPE (1-10) [Optional]", 1, 10, 7)
        fatigue = st.select_slider(
            "Fatigue Level [Optional]", 
            options=["Low", "Medium", "High", "Exhausted"],
            value="Medium"
        )
    
    # 5. Submit Button
    if st.button("💾 Save Workout"):
        database.add_workout(
            date=log_date,
            split=selected_split,
            exercise=final_exercise_name,  # Use the dynamic name
            sets=sets,
            reps=reps,
            weight=weight,
            rpe=rpe,
            fatigue=fatigue
        )
        st.success(f"Saved: {final_exercise_name} ({sets}x{reps} @ {weight}kg)")
        # Rerun to update the charts immediately
        st.rerun()
st.markdown("### Track Every Rep, Own Every Gain")
st.markdown("---")

# ============================================
# TOP METRICS ROW
# TINKER: Add more metrics by copying a col block
# ============================================
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if workout_ready:
        total = len(workout_df)
        st.metric("🏋️ WORKOUTS", total)
    else:
        st.metric("🏋️ WORKOUTS", "—")

with col2:
    if workout_ready and "Duration" in workout_df.columns:
        avg = workout_df["Duration"].mean()
        st.metric("⏱️ AVG TIME", f"{int(avg)} min")
    else:
        st.metric("⏱️ AVG TIME", "—")

with col3:
    if workout_ready and "Calories" in workout_df.columns:
        total = int(workout_df["Calories"].sum())
        st.metric("🔥 CALORIES", f"{total:,}")
    else:
        st.metric("🔥 CALORIES", "—")

with col4:
    if steps_df is not None:
        total_steps = int(steps_df["steps"].sum())
        st.metric("👟 TOTAL STEPS", f"{total_steps:,}")
    else:
        st.metric("👟 TOTAL STEPS", "—")

with col5:
    if workout_ready:
        # Find weight column
        weight_col = None
        for col in workout_df.columns:
            if "weight" in col.lower():
                weight_col = col
                break
        
        if weight_col:
            workout_df[weight_col] = pd.to_numeric(workout_df[weight_col], errors='coerce')
            max_weight = workout_df[weight_col].max()
            
            if not pd.isna(max_weight):
                st.metric("💪 MAX WEIGHT", f"{max_weight} kg")
            else:
                st.metric("💪 MAX WEIGHT", "—")
        else:
            st.metric("💪 MAX WEIGHT", "—")
    else:
        st.metric("💪 MAX WEIGHT", "—")

st.markdown("---")

# ============================================
# INSIGHT CARDS
# TINKER: Add more insights by creating new columns
# ============================================
if workout_ready or steps_df is not None:
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        if workout_ready:
            last_date = workout_df["Date"].max()
            days_ago = (pd.Timestamp.today().normalize() - last_date).days
            
            if days_ago == 0:
                st.success(f"🎯 **Last Workout**: Today! 🔥")
            elif days_ago == 1:
                st.info(f"🎯 **Last Workout**: Yesterday")
            else:
                st.warning(f"🎯 **Last Workout**: {days_ago} days ago")
    
    with insight_col2:
        if steps_df is not None and not steps_df.empty:
            # Find best step day
            best_idx = steps_df["steps"].idxmax()
            best_day = steps_df.loc[best_idx, "date"].strftime("%b %d")
            best_steps = int(steps_df.loc[best_idx, "steps"])
            st.success(f"🏆 **Best Day**: {best_day} ({best_steps:,} steps)")
    
    with insight_col3:
        if workout_ready:
            # Find most common workout type
            workout_col = None
            for col in ["Day", "Workout", "Exercise", "Excercise"]:
                if col in workout_df.columns:
                    workout_col = col
                    break
            
            if workout_col:
                most_common = workout_df[workout_col].value_counts().index[0]
                count = workout_df[workout_col].value_counts().values[0]
                st.info(f"💪 **Favorite**: {most_common} ({count}x)")

st.markdown("---")

# ============================================
# PROGRESS TRACKER (NEW FEATURE)
# LEARNING MOMENT: Filtering DataFrames
# ============================================
st.subheader("📈 Exercise Progression")

if workout_ready:
    # 1. Get unique exercises from the data
    # (We lowercase them first to avoid duplicates like "BENCH" vs "bench")
    unique_exercises = sorted(workout_df["Workout"].unique())
    
    # 2. Select Exercise to Analyze
    exercise_choice = st.selectbox("Select Exercise to Analyze:", unique_exercises)
    
    if exercise_choice:
        # 3. Filter Data for just this exercise
        ex_df = workout_df[workout_df["Workout"] == exercise_choice].copy()
        ex_df = ex_df.sort_values("Date")
        
        # 4. Show Stats
        col1, col2 = st.columns(2)
        with col1:
            max_weight = ex_df["Weight"].max()
            st.metric("Personal Best (Weight)", f"{max_weight} kg")
        with col2:
            max_reps = ex_df["reps"].max() if "reps" in ex_df.columns else 0
            st.metric("Max Reps in a Set", max_reps)
            
        # 5. Chart: Progress over time
        st.caption("Strength Progress (Max Weight per Day)")
        
        # We group by date to handle multiple sets in one day (taking the max weight)
        daily_max = ex_df.groupby("Date")["Weight"].max()
        
        st.line_chart(daily_max, color="#FF4B4B")
        
else:
    st.info("Log some workouts to see progression charts!")

st.markdown("---")

# ============================================
# CHART 1: Workout Duration
# TINKER: Change color='#667eea' to any color you like
# ============================================
st.subheader("📊 Workout Duration Over Time")

if workout_ready and "Date" in workout_df.columns and "Duration" in workout_df.columns:
    daily = workout_df.groupby("Date")["Duration"].sum()
    
    if not daily.empty:
        # LEARNING MOMENT: 
        # Instead of 20 lines of matplotlib code, we use 1 line of Streamlit!
        # It's interactive (zoom/hover) out of the box.
        st.area_chart(daily, color="#667eea")
    else:
        st.info("No duration data available")
else:
    st.info("Load workout data to see this chart")

st.markdown("---")

# ============================================
# CHART 2: Steps Progress
# TINKER: Change the goal line value (10000) to your goal
# ============================================
st.subheader("👟 Daily Steps Progress")

if steps_df is not None and not steps_df.empty:
    # LEARNING MOMENT:
    # We can perform quick calculations right inside the chart argument
    st.line_chart(steps_df.set_index("date")["steps"], color="#4facfe")
    
    avg_steps = int(steps_df["steps"].mean())
    st.caption(f"Average Steps: {avg_steps:,}")
else:
    st.info("Enable Google Fit in sidebar to see steps")

st.markdown("---")

# ============================================
# CHART 3: Calories Bubble Chart
# TINKER: Change cmap to 'Blues', 'Greens', 'Purples'
# ============================================
st.subheader("🔥 Calories Burned (Bubble Size = Calories)")

if workout_ready and "Date" in workout_df.columns and "Calories" in workout_df.columns:
    daily_cal = workout_df.groupby("Date")["Calories"].sum()
    
    if not daily_cal.empty:
        fig, ax = plt.subplots(figsize=(12, 5))
        
        # TINKER: Change 0.8 to make bubbles bigger (1.0) or smaller (0.5)
        sizes = daily_cal.values * 0.8
        
        # TINKER: Change cmap to different color schemes
        scatter = ax.scatter(daily_cal.index, daily_cal.values, 
                            s=sizes, alpha=0.6, 
                            c=daily_cal.values, cmap='Reds',
                            edgecolors='white', linewidths=3)
        
        ax.plot(daily_cal.index, daily_cal.values, 
                color='#f093fb', linewidth=2, alpha=0.4, linestyle='--')
        
        ax.set_facecolor('#f8f9fa')
        ax.set_xlabel("Date", fontsize=12, fontweight='bold', color='#2c3e50')
        ax.set_ylabel("Calories", fontsize=12, fontweight='bold', color='#2c3e50')
        ax.grid(True, alpha=0.3, linestyle=':', linewidth=1.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.xticks(rotation=30, fontsize=10)
        plt.tight_layout()
        
        st.pyplot(fig)
        plt.close
