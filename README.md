# 💪 Fitness & Nutrition Tracker (Gamified)

## Overview
This is a comprehensive personal health dashboard built with **Python** and **Streamlit**. It tracks workouts, nutrition, hydration, and turns fitness into an RPG game with XP and levels.

## 🛠️ Tech Stack
- **Frontend**: [Streamlit](https://streamlit.io/) (Web UI)
- **Data Manipulation**: [Pandas](https://pandas.pydata.org/)
- **Database**: [SQLite](https://www.sqlite.org/index.html) (Local `.db` files)
- **Visualization**: [Plotly](https://plotly.com/python/) & [Altair](https://altair-viz.github.io/)

## 📂 Project Structure

### 1. Core Application
- **`Fitness.py`**: The **Main Entry Point**.
    - Handles the Sidebar (Gym Bro AI, Rest Timer).
    - Logs Workouts (Sets, Reps, Weight).
    - Displays the **RPG System** (Level, XP, Badges).
    - Renders main dashboard charts.
- **`pages/1_🍎_Nutrition.py`**: The **Nutrition Sub-page**.
    - Logs Food (Macros, Calories) & Water.
    - Features "Editable Cheat Meals" & "Recipe Ideas".
    - Displays Weekly Calorie Trends & Macro Split.

### 2. Logic Modules
- **`database.py`**: The **Backend**.
    - Handles all SQL connections for `gym.db` (workouts) and `nutrition.db` (food/water).
    - Functions: `add_workout`, `get_food_logs`, `delete_food_log`, etc.
- **`charts.py`**: The **Artist**.
    - Contains all plotting logic to keep the main files clean.
    - Renders Donut charts, Heatmaps, and Bar charts.
- **`styles.py`**: The **Designer**.
    - Injects CSS for the "Midnight Gradient" theme and card styling.

## 🎮 Features
- **Gamification**: 
    - XP = Volume (Sets × Reps × Weight).
    - Unlock Badges like "Bulldozer" (100k volume) or "On Fire" (Streaks).
- **Gym Bro AI**: A fun random-response bot in the sidebar.
- **Cheat Meal Config**: Log cheat meals responsibly (or not) with custom calorie edits.
- **Interactive Deletion**: Manage your history directly from the UI.

## 🚀 How to Run
```bash
streamlit run Fitness.py
```
