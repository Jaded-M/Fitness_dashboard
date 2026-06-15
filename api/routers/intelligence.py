from __future__ import annotations

from datetime import date

import pandas as pd
from fastapi import APIRouter, Depends, Query

from api.dependencies import get_gateway
from api.gateway import SupabaseGateway
from api.models import ReadinessResponse
from api.services.snapshots import load_mobile_snapshot
from core.bca_engine import BCA_Engine
from core.readiness_engine import ReadinessInputs, calculate_readiness


router = APIRouter(prefix="/intelligence", tags=["intelligence"])


@router.get("/readiness", response_model=ReadinessResponse)
async def readiness(
    calorie_goal: int = Query(default=2300, ge=1000, le=6000),
    step_goal: int = Query(default=8000, ge=1000, le=50000),
    gateway: SupabaseGateway = Depends(get_gateway),
):
    snapshot = await load_mobile_snapshot(gateway)
    report = calculate_readiness(
        ReadinessInputs(
            workouts=snapshot.workouts,
            food=snapshot.food,
            steps=snapshot.steps,
            checkins=snapshot.checkins,
            calorie_goal=calorie_goal,
            step_goal=step_goal,
            today=date.today(),
        )
    )
    return report


@router.get("/today")
async def today_summary(
    calorie_goal: int = Query(default=2300, ge=1000, le=6000),
    step_goal: int = Query(default=8000, ge=1000, le=50000),
    gateway: SupabaseGateway = Depends(get_gateway),
):
    snapshot = await load_mobile_snapshot(gateway)
    today = pd.Timestamp(date.today())

    day_food = (
        snapshot.food[snapshot.food["date"].dt.normalize() == today]
        if not snapshot.food.empty
        else pd.DataFrame()
    )
    day_steps = (
        snapshot.steps[snapshot.steps["date"].dt.normalize() == today]
        if not snapshot.steps.empty
        else pd.DataFrame()
    )
    readiness_report = calculate_readiness(
        ReadinessInputs(
            workouts=snapshot.workouts,
            food=snapshot.food,
            steps=snapshot.steps,
            checkins=snapshot.checkins,
            calorie_goal=calorie_goal,
            step_goal=step_goal,
        )
    )

    return {
        "calories": int(day_food["calories"].sum()) if not day_food.empty else 0,
        "protein": int(day_food["protein"].sum()) if not day_food.empty else 0,
        "steps": int(day_steps["steps"].sum()) if not day_steps.empty else 0,
        "calorie_goal": calorie_goal,
        "step_goal": step_goal,
        "readiness": readiness_report,
    }


@router.get("/body-composition")
async def body_composition(
    current_weight_kg: float = Query(gt=0, le=500),
    goal: str = Query(default="cut", pattern="^(cut|maintenance|bulk)$"),
    target_weight_kg: float | None = Query(default=None, gt=0, le=500),
):
    engine = BCA_Engine(current_weight_kg=current_weight_kg)
    return {
        "metrics": engine.estimate_current_metrics(),
        "targets": engine.get_macro_targets(goal=goal, target_weight_kg=target_weight_kg),
    }
