from __future__ import annotations

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.config import Settings, get_settings
from api.models import ApiUser


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> ApiUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required.")

    headers = {
        "apikey": settings.supabase_anon_key,
        "Authorization": f"Bearer {credentials.credentials}",
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{settings.auth_url}/user", headers=headers)
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=503, detail="Authentication service unavailable.") from exc

    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")

    payload = response.json()
    return ApiUser(
        id=str(payload["id"]),
        email=payload.get("email"),
        access_token=credentials.credentials,
    )
