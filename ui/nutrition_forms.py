"""
# ════════════════════════════════════════════════════════════════
# MODULE: ui/nutrition_forms.py
# ════════════════════════════════════════════════════════════════
# // WHAT IT DOES:
#    Contains all the data-entry forms for the Nutrition page:
#    Water logging, Food logging (Quick & Builder), and Body Measurements.
#
# // HOW IT WORKS:
#    Streamlit UI widgets are grouped into functions. When a user
#    clicks "Save", the function talks directly to database.py to
#    save the data, then calls st.rerun() to refresh the screen.
#
# // WHY EXTRACT THIS:
#    Nutrition.py was 900+ lines. By separating the forms (Inputs)
#    from the charts (Outputs), the code is massively easier to read
#    and maintain. If the water button breaks, you know exactly
#    which file to check.
# ════════════════════════════════════════════════════════════════
"""
import streamlit as st
import pandas as pd
import datetime
import time
import database
from pathlib import Path

# Path to the old Excel measurements file
PHYSICAL_DATA_PATH = Path(__file__).resolve().parent.parent / "Physical_attribute.xlsx"

def render_hydration_form(today_date, today_water, water_goal):
    """Renders the single-click hydration tracking buttons."""
    st.markdown("### 💧 Hydration")
    water_pct = min(today_water / water_goal, 1.0) if water_goal else 0
    st.progress(water_pct)
    
    w1, w2, w3 = st.columns(3)
    if w1.button("💧 +1",  use_container_width=True): 
        database.log_water(today_date, 1)
        st.rerun()
    if w2.button("🥤 +2",  use_container_width=True): 
        database.log_water(today_date, 2)
        st.rerun()
    if w3.button("🚿 +3",  use_container_width=True): 
        database.log_water(today_date, 3)
        st.rerun()
        
    if today_water >= water_goal:
        st.success("🌊 Hydration goal smashed!")
    else:
        st.caption(f"{water_goal - today_water} cup(s) to go!")
    st.markdown("---")


@st.dialog("🍽️ Log Meal")
def render_food_log_form(today_date):
    """
    // WHAT IT DOES: Renders the Quick Log and Meal Builder tabs in a popup Modal.
    """
    log_date  = st.date_input("Date", today_date, key="food_date")
    meal_type = st.radio("Meal", ["Breakfast", "Lunch", "Snack", "Dinner"], horizontal=True)
    
    tab_quick, tab_builder = st.tabs(["⚡ Quick Log", "🛒 Meal Builder (Beta)"])
    
    # ── Quick Log ──
    with tab_quick:
        q_name = st.text_input("Food Item", placeholder="e.g., Chicken & Rice", key="q_name")
        q_fc1, q_fc2 = st.columns(2)
        with q_fc1: q_cal  = st.number_input("Calories",    0.0, 5000.0, 0.0, step=10.0, key="q_cal")
        with q_fc2: q_prot = st.number_input("Protein (g)", 0.0,  500.0, 0.0, key="q_prot")
        
        q_fc3, q_fc4, q_fc5 = st.columns(3)
        with q_fc3: q_carb = st.number_input("Carbs (g)", 0.0, 500.0, 0.0, key="q_carb")
        with q_fc4: q_fat  = st.number_input("Fats (g)",  0.0, 500.0, 0.0, key="q_fat")
        with q_fc5: q_fib  = st.number_input("Fiber (g)", 0.0, 500.0, 0.0, key="q_fib")

        cc_col1, cc_col2 = st.columns([2, 1])
        if cc_col1.button("➕ Log Entry", type="primary", use_container_width=True):
            if q_name and q_cal > 0:
                database.add_food_log(log_date, q_name, int(q_cal), int(q_prot), int(q_carb), int(q_fat), int(q_fib), meal_type)
                st.success(f"✅ Added {q_name}!")
                time.sleep(0.5); st.rerun()
            else:
                st.warning("Food name and calories are required.")
                
        if cc_col2.button("🍕 Cheat Meal", use_container_width=True, help="Logs 1000 calories instantly"):
            database.add_food_log(log_date, "Cheat Meal (Quick)", 1000, 0, 0, 0, 0, meal_type)
            st.toast("Logged Cheat Meal! Tomorrow is a new day 🍕")
            time.sleep(1); st.rerun()

    # ── Meal Builder (Draft Table) ──
    with tab_builder:
        st.info("💡 **Future Update:** This will connect to an AI database that knows Indian macros automatically.")
        food_name = st.text_input("Item Name", placeholder="e.g., Paneer Tikka", key="b_name")
        
        fc1, fc2 = st.columns(2)
        with fc1: grams    = st.number_input("Grams", 0, 5000, 0, step=10, help="Amount eaten", key="b_grams")
        with fc2: calories = st.number_input("Calories (Optional)", 0, 5000, 0, step=10, help="Leave 0 to auto-calculate from macros", key="b_cal")
        
        fc3, fc4, fc5 = st.columns(3)
        with fc3: protein = st.number_input("Protein (g)", 0.0, 500.0, 0.0, key="b_prot")
        with fc4: carbs   = st.number_input("Carbs (g)", 0.0, 500.0, 0.0, key="b_carb")
        with fc5: fats    = st.number_input("Fats (g)",  0.0, 500.0, 0.0, key="b_fat")

        draft_df = database.get_draft_foods()

        if st.button("➕ Add Food Item", use_container_width=True):
            if food_name:
                calc_cals = calories if calories > 0 else (protein * 4) + (carbs * 4) + (fats * 9)
                final_name = food_name.strip()
                if grams > 0:
                    final_name += f" ({grams}g)"
                database.add_draft_food(final_name, int(calc_cals), int(protein), int(carbs), int(fats), 0)
                st.rerun()
            else:
                st.warning("Please enter an item name.")

        if not draft_df.empty:
            st.markdown(f"#### 🛒 Current {meal_type}")
            tot_cal = tot_prot = tot_carb = tot_fat = 0
            for _, item in draft_df.iterrows():
                st.markdown(f"- **{item['food_item']}**: {item['calories']} kcal  |  {item['protein']}g P  |  {item['carbs']}g C  |  {item['fats']}g F")
                tot_cal += item['calories']; tot_prot += item['protein']
                tot_carb += item['carbs']; tot_fat += item['fats']
                
            st.info(f"**Meal Total:** {tot_cal} kcal  |  {tot_prot}g P  |  {tot_carb}g C  |  {tot_fat}g F")
            
            c1, c2 = st.columns(2)
            if c1.button("🗑️ Clear Meal", use_container_width=True):
                database.clear_draft_foods()
                st.rerun()
            if c2.button("💾 Save Meal", type="primary", use_container_width=True):
                for _, item in draft_df.iterrows():
                    database.add_food_log(log_date, item['food_item'], item['calories'], item['protein'], item['carbs'], item['fats'], 0, meal_type)
                st.success(f"✅ Saved meal with {len(draft_df)} items!")
                database.clear_draft_foods()
                time.sleep(1); st.rerun()

@st.dialog("⚖️ Log Measurements")
def render_measurements_form(today_date):
    """Renders the physical measurement logging form in a popup Modal."""
    w_date    = st.date_input("Date", today_date, key="weight_date")
    weight_kg = st.number_input("Weight (kg)", 0.0, 300.0, 0.0, step=0.1, format="%.1f")
    
    fc6, fc7, fc8 = st.columns(3)
    with fc6: waist_in = st.number_input("Waist (in)",  0.0, 100.0, 0.0, step=0.1, format="%.1f")
    with fc7: hips_in  = st.number_input("Hips (in)", 0.0, 100.0, 0.0, step=0.1, format="%.1f")
    with fc8: thigh_in = st.number_input("Thigh (in)", 0.0, 100.0, 0.0, step=0.1, format="%.1f")

    fc9, fc10 = st.columns(2)
    with fc9: chest_in = st.number_input("Chest (in)", 0.0, 100.0, 0.0, step=0.1, format="%.1f")
    with fc10: arms_in = st.number_input("Arms (in)", 0.0, 100.0, 0.0, step=0.1, format="%.1f")

    if st.button("💾 Save Measurements", use_container_width=True):
        if weight_kg > 0:
            database.add_measurement(
                date=w_date, 
                weight=weight_kg, 
                waist=waist_in or None, 
                hips=hips_in or None, 
                thigh=thigh_in or None, 
                chest=chest_in or None, 
                arms=arms_in or None
            )
            st.success("Saved! 💪")
            time.sleep(0.5); st.rerun()
        else:
            st.warning("Enter a weight value.")
