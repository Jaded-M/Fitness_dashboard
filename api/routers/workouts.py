from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from api.dependencies import get_gateway
from api.gateway import SupabaseGateway
from api.models import WorkoutCreate
from api.services.records import record_board


router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.get("")
async def list_workouts(
    limit: int = Query(default=50, ge=1, le=500),
    gateway: SupabaseGateway = Depends(get_gateway),
):
    return await gateway.select("workouts", order="date.desc", limit=limit)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_workout(
    workout: WorkoutCreate,
    gateway: SupabaseGateway = Depends(get_gateway),
):
    sets = [item.model_dump() for item in workout.sets]
    weights = [item.weight for item in workout.sets]
    reps = [item.reps for item in workout.sets]
    rpes = [item.rpe for item in workout.sets]
    payload = {
        "date": workout.date.isoformat(),
        "split": workout.split.strip(),
        "exercise": workout.exercise.strip(),
        "sets": len(sets),
        "reps": sum(reps),
        "weight": max(weights, default=0),
        "rpe": sum(rpes) / len(rpes),
        "fatigue": "Medium",
        "duration": 0,
        "set_data": sets,
    }
    return await gateway.insert("workouts", payload)


@router.get("/records")
async def list_records(gateway: SupabaseGateway = Depends(get_gateway)):
    rows = await gateway.select("workouts", order="date.desc")
    return record_board(rows)


@router.get("/{exercise}/last")
async def last_session(
    exercise: str,
    gateway: SupabaseGateway = Depends(get_gateway),
):
    rows = await gateway.select(
        "workouts",
        filters={"exercise": f"eq.{exercise}"},
        order="date.desc",
        limit=1,
    )
    return rows[0] if rows else None


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(
    workout_id: int,
    gateway: SupabaseGateway = Depends(get_gateway),
):
    await gateway.delete("workouts", workout_id)
