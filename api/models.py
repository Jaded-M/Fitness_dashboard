from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class ApiUser(BaseModel):
    id: str
    email: str | None = None
    access_token: str = Field(exclude=True)


class WorkoutSet(BaseModel):
    weight: float = Field(default=0, ge=0)
    reps: int = Field(default=0, ge=0)
    rpe: float = Field(default=7, ge=0, le=10)
    note: str = ""


class WorkoutCreate(BaseModel):
    date: date
    split: str = Field(min_length=1, max_length=80)
    exercise: str = Field(min_length=1, max_length=160)
    sets: list[WorkoutSet] = Field(min_length=1)


class FoodLogCreate(BaseModel):
    date: date
    food_item: str = Field(min_length=1, max_length=200)
    calories: int = Field(default=0, ge=0, le=10000)
    protein: int = Field(default=0, ge=0, le=1000)
    carbs: int = Field(default=0, ge=0, le=1500)
    fats: int = Field(default=0, ge=0, le=1000)
    fiber: int = Field(default=0, ge=0, le=500)
    meal_type: str = Field(default="Snack", max_length=40)


class StepsUpsert(BaseModel):
    date: date
    steps: int = Field(ge=0, le=200000)
    distance: float = Field(default=0, ge=0)
    active_minutes: int = Field(default=0, ge=0, le=1440)


class CheckinCreate(BaseModel):
    date: date
    mood: int = Field(default=3, ge=1, le=5)
    energy: int = Field(default=3, ge=1, le=5)
    sleep_hours: float | None = Field(default=None, ge=0, le=24)
    note: str = Field(default="", max_length=2000)


class MeasurementCreate(BaseModel):
    date: date
    weight: float = Field(gt=0, le=500)
    waist: float | None = Field(default=None, ge=0)
    hips: float | None = Field(default=None, ge=0)
    thigh: float | None = Field(default=None, ge=0)
    chest: float | None = Field(default=None, ge=0)
    arms: float | None = Field(default=None, ge=0)


class ReadinessResponse(BaseModel):
    score: int
    label: str
    training_load_score: int
    recovery_score: int
    activity_score: int
    nutrition_score: int
    subjective_score: int
    recommended_split: str
    key_action: str
    warnings: list[str]
    insights: list[str]
    muscle_status: list[dict[str, Any]]
