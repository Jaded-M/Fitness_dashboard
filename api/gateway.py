from __future__ import annotations

from typing import Any

import httpx
from fastapi import HTTPException

from api.config import Settings
from api.models import ApiUser


class SupabaseGateway:
    def __init__(self, settings: Settings, user: ApiUser) -> None:
        self.settings = settings
        self.user = user
        self.headers = {
            "apikey": settings.supabase_anon_key,
            "Authorization": f"Bearer {user.access_token}",
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        table: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        prefer: str | None = None,
    ) -> httpx.Response:
        headers = dict(self.headers)
        if prefer:
            headers["Prefer"] = prefer

        async with httpx.AsyncClient(timeout=20.0) as client:
            try:
                response = await client.request(
                    method,
                    f"{self.settings.rest_url}/{table}",
                    headers=headers,
                    params=params,
                    json=json,
                )
            except httpx.HTTPError as exc:
                raise HTTPException(status_code=503, detail="Database service unavailable.") from exc

        if response.status_code >= 400:
            detail = response.json().get("message", response.text)
            raise HTTPException(status_code=response.status_code, detail=detail)
        return response

    async def select(
        self,
        table: str,
        *,
        columns: str = "*",
        filters: dict[str, str] | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        base_params: dict[str, Any] = {"select": columns, "user_id": f"eq.{self.user.id}"}
        if filters:
            base_params.update(filters)
        if order:
            base_params["order"] = order
        if limit is not None:
            params = {**base_params, "limit": limit}
            response = await self._request("GET", table, params=params)
            return response.json()

        rows: list[dict[str, Any]] = []
        page_size = 1000
        offset = 0
        while True:
            params = {**base_params, "limit": page_size, "offset": offset}
            response = await self._request("GET", table, params=params)
            batch = response.json()
            rows.extend(batch)
            if len(batch) < page_size:
                break
            offset += page_size
        return rows

    async def insert(self, table: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = {**payload, "user_id": self.user.id}
        response = await self._request("POST", table, json=body, prefer="return=representation")
        rows = response.json()
        return rows[0] if rows else body

    async def upsert(self, table: str, payload: dict[str, Any], conflict: str) -> dict[str, Any]:
        body = {**payload, "user_id": self.user.id}
        response = await self._request(
            "POST",
            table,
            params={"on_conflict": conflict},
            json=body,
            prefer="resolution=merge-duplicates,return=representation",
        )
        rows = response.json()
        return rows[0] if rows else body

    async def delete(self, table: str, row_id: int) -> None:
        await self._request(
            "DELETE",
            table,
            params={"id": f"eq.{row_id}", "user_id": f"eq.{self.user.id}"},
        )
