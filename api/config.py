from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    supabase_url: str
    supabase_anon_key: str
    allowed_origins: tuple[str, ...]

    @property
    def auth_url(self) -> str:
        return f"{self.supabase_url.rstrip('/')}/auth/v1"

    @property
    def rest_url(self) -> str:
        return f"{self.supabase_url.rstrip('/')}/rest/v1"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    url = os.environ.get("SUPABASE_URL", "").strip()
    anon_key = os.environ.get("SUPABASE_ANON_KEY", os.environ.get("SUPABASE_KEY", "")).strip()
    origins = tuple(
        origin.strip()
        for origin in os.environ.get("PHI_ALLOWED_ORIGINS", "").split(",")
        if origin.strip()
    )

    if not url or not anon_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_ANON_KEY must be configured.")

    return Settings(
        supabase_url=url,
        supabase_anon_key=anon_key,
        allowed_origins=origins,
    )
