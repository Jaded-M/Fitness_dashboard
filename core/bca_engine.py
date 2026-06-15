"""
core/bca_engine.py — Biological Composition Analysis Engine
============================================================
Stateless, pure-Python calculation module.  Zero Streamlit dependencies.

Usage
-----
engine = BCA_Engine(
    current_weight_kg=82.0,
    base_weight=89.3,
    base_bf_mass=33.5,
    base_smm=30.9,
    base_bmr=1575,
    base_pbf=37.6,
    base_ffm=55.8,
    age=25,
    sex="male",          # "male" | "female"
    height_cm=178.0,
    activity_level="moderate",  # sedentary | light | moderate | active | very_active
)
metrics  = engine.estimate_current_metrics()
bmr      = engine.get_dynamic_bmr()
targets  = engine.get_macro_targets(goal="cut", target_weight_kg=72.0)
"""
from __future__ import annotations

# ── TDEE activity multipliers (PAL factors) ───────────────────────────────────
ACTIVITY_MULTIPLIERS: dict[str, float] = {
    "sedentary":   1.20,   # desk job, little or no exercise
    "light":       1.375,  # light exercise 1–3 days/week
    "moderate":    1.55,   # moderate exercise 3–5 days/week  ← gym default
    "active":      1.725,  # hard exercise 6–7 days/week
    "very_active": 1.90,   # physical job + hard training
}


class BCA_Engine:
    """
    Body Composition Analysis engine.

    Uses the Katch-McArdle formula (BMR from lean mass) for maximum accuracy.
    Falls back to the Mifflin-St Jeor formula when age / sex / height are
    provided but a baseline scan is unavailable.

    Parameters
    ----------
    current_weight_kg : float
        Today's bodyweight in kilograms.
    base_weight : float
        Bodyweight at the time of the BCA scan (kg). Default: 89.3 kg.
    base_bf_mass : float
        Body-fat mass at scan time (kg). Default: 33.5 kg.
    base_smm : float
        Skeletal muscle mass at scan time (kg). Default: 30.9 kg.
    base_bmr : float
        BMR recorded at scan time (kcal/day). Default: 1 575 kcal.
    base_pbf : float
        Percent body fat at scan time (%). Default: 37.6 %.
    base_ffm : float
        Fat-free mass at scan time (kg). Default: 55.8 kg.
    age : int | None
        Age in years — used for Mifflin-St Jeor fallback.
    sex : str
        ``"male"`` or ``"female"``.
    height_cm : float | None
        Height in centimetres — used for Mifflin-St Jeor fallback.
    activity_level : str
        One of ``sedentary | light | moderate | active | very_active``.
    """

    def __init__(
        self,
        current_weight_kg: float,
        base_weight: float = 89.3,
        base_bf_mass: float = 33.5,
        base_smm: float = 30.9,
        base_bmr: float = 1_575,
        base_pbf: float = 37.6,
        base_ffm: float = 55.8,
        age: int | None = None,
        sex: str = "male",
        height_cm: float | None = None,
        activity_level: str = "moderate",
    ) -> None:
        # Baseline BCA scan values
        self.base_weight   = base_weight
        self.base_bf_mass  = base_bf_mass
        self.base_smm      = base_smm
        self.base_bmr      = base_bmr
        self.base_pbf      = base_pbf
        self.base_ffm      = base_ffm

        # Current biometrics
        self.current_weight    = current_weight_kg
        self.weight_delta      = current_weight_kg - base_weight

        # User profile
        self.age            = age
        self.sex            = sex.lower()
        self.height_cm      = height_cm
        self.activity_level = activity_level.lower()

    # ── Body composition estimation ──────────────────────────────────────────

    def estimate_current_metrics(self) -> dict:
        """
        Estimate today's body fat mass, skeletal muscle mass, and PBF% by
        extrapolating from the baseline BCA scan.

        Assumptions (sports-science heuristics for trained natural lifters):
        - Weight loss: 80 % fat lost, 20 % other (glycogen / water / trace LBM).
        - Weight gain: 60 % fat, 40 % muscle (beginner-to-intermediate gains).
        """
        delta = self.weight_delta

        if delta < 0:
            fat_lost      = abs(delta) * 0.80
            other_lost    = abs(delta) * 0.20
            new_bf_mass   = self.base_bf_mass - fat_lost
            new_smm       = self.base_smm - (other_lost * 0.50)
        else:
            new_bf_mass   = self.base_bf_mass + delta * 0.60
            new_smm       = self.base_smm     + delta * 0.40

        # Clamp BF mass to a physiological floor (~5 % essential fat)
        min_bf = self.current_weight * 0.05
        new_bf_mass = max(new_bf_mass, min_bf)

        new_pbf = (new_bf_mass / self.current_weight) * 100

        return {
            "estimated_bf_mass_kg":  round(new_bf_mass, 1),
            "estimated_smm_kg":      round(new_smm,     1),
            "estimated_pbf_percent": round(new_pbf,     1),
            "estimated_lbm_kg":      round(self.current_weight - new_bf_mass, 1),
        }

    # ── BMR calculation ──────────────────────────────────────────────────────

    def get_dynamic_bmr(self) -> int:
        """
        Calculate Basal Metabolic Rate.

        Primary formula — Katch-McArdle (lean-mass based, most accurate for
        athletes and body-composition-tracked individuals):
            BMR = 370 + 21.6 × LBM (kg)

        Fallback — Mifflin-St Jeor (when age, sex, height are provided but a
        baseline scan is unavailable or the BF estimate seems unreliable):
            Male:   BMR = 10W + 6.25H − 5A + 5
            Female: BMR = 10W + 6.25H − 5A − 161
        """
        metrics = self.estimate_current_metrics()
        lbm     = metrics["estimated_lbm_kg"]

        # Katch-McArdle
        bmr_ka = 370 + 21.6 * lbm

        # Mifflin-St Jeor (only if profile data exists)
        bmr_mfp: float | None = None
        if self.age and self.height_cm:
            w, h, a = self.current_weight, self.height_cm, self.age
            if self.sex == "female":
                bmr_mfp = 10 * w + 6.25 * h - 5 * a - 161
            else:
                bmr_mfp = 10 * w + 6.25 * h - 5 * a + 5

        # Blend when both are available (Katch-McArdle is more reliable here)
        if bmr_mfp is not None:
            bmr = 0.70 * bmr_ka + 0.30 * bmr_mfp
        else:
            bmr = bmr_ka

        return int(bmr)

    # ── TDEE & macro targets ─────────────────────────────────────────────────

    def get_tdee(self) -> int:
        """Return Total Daily Energy Expenditure (TDEE) in kcal."""
        multiplier = ACTIVITY_MULTIPLIERS.get(self.activity_level, 1.55)
        return int(self.get_dynamic_bmr() * multiplier)

    def get_macro_targets(
        self,
        goal: str = "cut",
        target_weight_kg: float | None = None,
    ) -> dict:
        """
        Generate precise macro targets in grams.

        Parameters
        ----------
        goal : str
            ``"cut"`` (−500 kcal deficit, ~0.5 kg/week loss),
            ``"maintenance"`` (TDEE), or
            ``"bulk"`` (+300 kcal surplus, lean gaining).
        target_weight_kg : float | None
            Used only for projection calculations returned alongside macros.

        Returns
        -------
        dict
            target_calories, protein_g, fat_g, carbs_g, tdee, bmr,
            weeks_to_goal (None if target_weight_kg not set),
            target_date (isoformat string or None).
        """
        import datetime

        bmr  = self.get_dynamic_bmr()
        tdee = self.get_tdee()
        lbm  = self.estimate_current_metrics()["estimated_lbm_kg"]

        goal_clean = goal.lower()
        if goal_clean == "cut":
            target_cals = tdee - 500
            weekly_change_kg = -0.50        # projected loss
        elif goal_clean == "bulk":
            target_cals = tdee + 300
            weekly_change_kg = +0.25        # projected lean gain
        else:
            target_cals = tdee
            weekly_change_kg = 0.0

        # Protein: 2.2 g per kg LBM (muscle-sparing in deficit)
        protein_g    = int(lbm * 2.2)
        protein_cals = protein_g * 4

        # Fats: 25 % of target calories (hormone regulation)
        fat_g        = int(target_cals * 0.25 / 9)
        fat_cals     = fat_g * 9

        # Carbs: remaining calories
        carb_g       = max(0, int((target_cals - protein_cals - fat_cals) / 4))

        # Projection to target weight
        weeks_to_goal = target_date = None
        if target_weight_kg is not None and weekly_change_kg != 0:
            kg_to_go = target_weight_kg - self.current_weight
            # Only project if direction matches goal
            if (goal_clean == "cut" and kg_to_go < 0) or \
               (goal_clean == "bulk" and kg_to_go > 0):
                weeks_to_goal = abs(round(kg_to_go / weekly_change_kg))
                target_date = (
                    datetime.date.today()
                    + datetime.timedelta(weeks=weeks_to_goal)
                ).isoformat()

        return {
            "bmr":             bmr,
            "tdee":            tdee,
            "target_calories": target_cals,
            "protein_g":       protein_g,
            "fat_g":           fat_g,
            "carbs_g":         carb_g,
            "weeks_to_goal":   weeks_to_goal,
            "target_date":     target_date,
            "weekly_change_kg": weekly_change_kg,
        }
