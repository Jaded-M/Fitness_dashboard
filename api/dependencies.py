from __future__ import annotations

from fastapi import Depends

from api.auth import get_current_user
from api.config import Settings, get_settings
from api.gateway import SupabaseGateway
from api.models import ApiUser


def get_gateway(
    user: ApiUser = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> SupabaseGateway:
    return SupabaseGateway(settings, user)
