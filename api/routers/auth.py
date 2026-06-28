from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.config import Settings, get_settings


router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    headers = {
        "apikey": settings.supabase_anon_key,
        "Content-Type": "application/json",
    }
    payload = {
        "email": body.email,
        "password": body.password,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                f"{settings.auth_url}/token",
                params={"grant_type": "password"},
                headers=headers,
                json=payload,
            )
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable",
            ) from exc

    if response.status_code == 400:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        )

    data = response.json()
    return TokenResponse(
        access_token=data["access_token"],
        token_type="bearer",
        expires_in=data.get("expires_in", 3600),
    )
