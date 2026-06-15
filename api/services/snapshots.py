from __future__ import annotations

import asyncio
from dataclasses import dataclass

import pandas as pd

from api.gateway import SupabaseGateway


@dataclass
class MobileSnapshot:
    workouts: pd.DataFrame
    food: pd.DataFrame
    steps: pd.DataFrame
    checkins: pd.DataFrame
    measurements: pd.DataFrame


def _frame(rows: list[dict], date_column: str = "date") -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if not df.empty and date_column in df.columns:
        df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
    return df


async def load_mobile_snapshot(gateway: SupabaseGateway) -> MobileSnapshot:
    workouts, food, steps, checkins, measurements = await asyncio.gather(
        gateway.select("workouts", order="date.desc"),
        gateway.select("food_logs", order="date.desc"),
        gateway.select("steps", order="date.desc"),
        gateway.select("checkins", order="date.desc"),
        gateway.select("measurements", order="date.desc"),
    )

    return MobileSnapshot(
        workouts=_frame(workouts),
        food=_frame(food),
        steps=_frame(steps),
        checkins=_frame(checkins),
        measurements=_frame(measurements),
    )
