from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from api.dependencies import get_gateway
from api.gateway import SupabaseGateway
from api.models import FoodLogCreate


router = APIRouter(prefix="/nutrition", tags=["nutrition"])


@router.get("/logs")
async def list_food_logs(
    limit: int = Query(default=100, ge=1, le=500),
    gateway: SupabaseGateway = Depends(get_gateway),
):
    return await gateway.select("food_logs", order="date.desc", limit=limit)


@router.post("/logs", status_code=status.HTTP_201_CREATED)
async def create_food_log(
    food: FoodLogCreate,
    gateway: SupabaseGateway = Depends(get_gateway),
):
    payload = food.model_dump()
    payload["date"] = food.date.isoformat()
    payload["food_item"] = food.food_item.strip()
    return await gateway.insert("food_logs", payload)


@router.delete("/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_food_log(
    log_id: int,
    gateway: SupabaseGateway = Depends(get_gateway),
):
    await gateway.delete("food_logs", log_id)
