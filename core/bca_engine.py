"""
# --------------------------------------------------------------------------------
# MODULE: core/bca_engine.py
# --------------------------------------------------------------------------------
# // WHAT IT DOES: 
# This file is the "Biological Engine". It takes your Body Composition Analysis (BCA)
# data from last year and your *current* weight today, and calculates your 
# highly-accurate daily Caloric needs, expected Body Fat %, and Lean Mass.
#
# // HOW IT WORKS:
# Notice there is ZERO Streamlit (UI) code in here. This is a "Pure Python" module.
# It defines a Class (an Object) that stores your stats. It has "methods" (functions
# attached to the object) that run math formulas.
#
# // WHY WE DO IT THIS WAY:
# Separation of Concerns. By keeping the math trapped in this file, we can test it 
# instantly without having to load the whole web app. If the math is wrong, we only
# fix it here.
# --------------------------------------------------------------------------------
"""

class BCA_Engine:
    def __init__(self, current_weight_kg: float, 
                 base_weight=89.3, base_bf_mass=33.5, 
                 base_smm=30.9, base_bmr=1575, base_pbf=37.6, base_ffm=55.8):
        """
        // WHAT IT DOES: Initializes the data using provided baseline metrics.
        // Defaults to the 2025.08.13 report if no baseline is provided from DB.
        """
        self.base_weight = base_weight        # kg
        self.base_bf_mass = base_bf_mass       # kg (Body Fat Mass)
        self.base_smm = base_smm           # kg (Skeletal Muscle Mass)
        self.base_bmr = base_bmr           # kcal/day
        self.base_pbf = base_pbf           # % (Percent Body Fat)
        self.base_ffm = base_ffm           # kg (Fat Free Mass)
        
        # --- CURRENT STATS ---
        self.current_weight = current_weight_kg
        
        # Calculate the delta (how much weight lost or gained)
        self.weight_delta = self.current_weight - self.base_weight

    def estimate_current_metrics(self):
        """
        // WHAT IT DOES: Estimates your current Body Fat % and Muscle Mass.
        // HOW IT WORKS: If you are lifting weights + eating protein, we assume
        // ~80% of weight lost is fat, and ~20% is water/glycogen/trace muscle. 
        // This is a standard sports science heuristic for novice lifters.
        """
        # If weight went down (negative delta)
        if self.weight_delta < 0:
            fat_lost = abs(self.weight_delta) * 0.80
            other_lost = abs(self.weight_delta) * 0.20
            
            new_bf_mass = self.base_bf_mass - fat_lost
            # SMM (Skeletal Muscle Mass) usually stays mostly intact if training
            new_smm = self.base_smm - (other_lost * 0.5) 
        else:
            # If weight went up, assume 60% fat / 40% muscle gain (newbie gains)
            fat_gained = self.weight_delta * 0.60
            muscle_gained = self.weight_delta * 0.40
            
            new_bf_mass = self.base_bf_mass + fat_gained
            new_smm = self.base_smm + muscle_gained

        # Calculate new percentages based on your *current* weight
        new_pbf = (new_bf_mass / self.current_weight) * 100
        
        return {
            "estimated_bf_mass_kg": round(new_bf_mass, 1),
            "estimated_smm_kg": round(new_smm, 1),
            "estimated_pbf_percent": round(new_pbf, 1)
        }

    def get_dynamic_bmr(self):
        """
        // WHAT IT DOES: Calculates your new Basal Metabolic Rate (BMR).
        // HOW IT WORKS: We use the Katch-McArdle formula, which is considered the 
        // most accurate formula in the world because it uses Lean Mass, not just 
        // total weight. (Standard formulas penalize heavy muscular people).
        // Formula: BMR = 370 + (21.6 * Lean Body Mass in kg)
        """
        metrics = self.estimate_current_metrics()
        
        # Lean Body Mass = Current Weight - Fat Mass
        lbm = self.current_weight - metrics["estimated_bf_mass_kg"]
        
        # The Katch-McArdle Formula
        current_bmr = 370 + (21.6 * lbm)
        return int(current_bmr)

    def get_macro_targets(self, goal="cut"):
        """
        // WHAT IT DOES: Generates your exact macro needs in grams.
        // HOW IT WORKS: Returns a dictionary of Protein, Fat, and Carbs based
        // on whether you want to "cut" (lose fat) or "bulk" (gain muscle).
        """
        bmr = self.get_dynamic_bmr()
        
        # Total Daily Energy Expenditure (TDEE)
        # Assuming light/moderate activity (lifting 3-4x a week) = BMR * 1.375
        tdee = int(bmr * 1.375)
        
        if goal == "cut":
            target_cals = tdee - 500  # 500 cal deficit for ~0.5kg loss per week
        elif goal == "bulk":
            target_cals = tdee + 300  # 300 cal surplus for lean mass gain
        else:
            target_cals = tdee        # Maintenance
            
        # ----------------------------------------------------
        # THE MACRO SPLIT (SPORTS SCIENCE)
        # ----------------------------------------------------
        # Protein (4 kcals/g): Highly protective of muscle in a deficit. 
        #   Rule: ~2.2g per kg of LEAN body mass (not total weight).
        lbm = self.current_weight - self.estimate_current_metrics()["estimated_bf_mass_kg"]
        protein_g = int(lbm * 2.2)
        protein_cals = protein_g * 4
        
        # Fats (9 kcals/g): Needed for hormone regulation (testosterone).
        #   Rule: ~25% of your total calories.
        fat_cals = target_cals * 0.25
        fat_g = int(fat_cals / 9)
        
        # Carbs (4 kcals/g): Whatever calories are left over after Protein + Fat.
        #   Needed to fuel your workouts.
        remaining_cals = target_cals - (protein_cals + fat_cals)
        carb_g = int(remaining_cals / 4)
        
        return {
            "target_calories": target_cals,
            "protein_g": protein_g,
            "fat_g": fat_g,
            "carbs_g": carb_g
        }
