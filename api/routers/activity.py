from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from api.dependencies import get_gateway
from api.gateway import SupabaseGateway
from api.models import CheckinCreate, MeasurementCreate, StepsUpsert


router = APIRouter(prefix="/activity", tags=["activity"])


@router.get("/steps")
async def list_steps(
    limit: int = Query(default=90, ge=1, le=500),
    gateway: SupabaseGateway = Depends(get_gateway),
):
    return await gateway.select("steps", order="date.desc", limit=limit)


@router.get("/water")
async def list_water_logs(
    limit: int = Query(default=90, ge=1, le=500),
    gateway: SupabaseGateway = Depends(get_gateway),
):
    return await gateway.select("water_logs", order="date.desc", limit=limit)


@router.post("/water", status_code=status.HTTP_201_CREATED)
async def create_water_log(
    cups: int = Query(default=1, ge=1, le=30),
    gateway: SupabaseGateway = Depends(get_gateway),
):
    from datetime import date

    return await gateway.insert("water_logs", {"date": date.today().isoformat(), "cups": cups})


@router.put("/steps")
async def upsert_steps(
    steps: StepsUpsert,
    gateway: SupabaseGateway = Depends(get_gateway),
):
    payload = steps.model_dump()
    payload["date"] = steps.date.isoformat()
    return await gateway.upsert("steps", payload, conflict="user_id,date")


@router.get("/checkins")
async def list_checkins(
    limit: int = Query(default=30, ge=1, le=365),
    gateway: SupabaseGateway = Depends(get_gateway),
):
    return await gateway.select("checkins", order="date.desc", limit=limit)


@router.post("/checkins", status_code=status.HTTP_201_CREATED)
async def create_checkin(
    checkin: CheckinCreate,
    gateway: SupabaseGateway = Depends(get_gateway),
):
    payload = checkin.model_dump()
    payload["date"] = checkin.date.isoformat()
    return await gateway.insert("checkins", payload)


@router.get("/measurements")
async def list_measurements(
    limit: int = Query(default=100, ge=1, le=500),
    gateway: SupabaseGateway = Depends(get_gateway),
):
    return await gateway.select("measurements", order="date.desc", limit=limit)


@router.post("/measurements", status_code=status.HTTP_201_CREATED)
async def create_measurement(
    measurement: MeasurementCreate,
    gateway: SupabaseGateway = Depends(get_gateway),
):
    payload = measurement.model_dump()
    payload["date"] = measurement.date.isoformat()
    return await gateway.insert("measurements", payload)
