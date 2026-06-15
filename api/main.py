from __future__ import annotations

import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth import get_current_user
from api.models import ApiUser
from api.routers import activity, intelligence, nutrition, workouts


app = FastAPI(
    title="PHI Mobile API",
    version="0.1.0",
    description="Authenticated API for the PHI native mobile client.",
)

allowed_origins = [
    origin.strip()
    for origin in os.environ.get("PHI_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=bool(allowed_origins),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "phi-mobile-api", "version": app.version}


@app.get("/api/v1/me")
def me(user: ApiUser = Depends(get_current_user)):
    return {"id": user.id, "email": user.email}


app.include_router(workouts.router, prefix="/api/v1")
app.include_router(nutrition.router, prefix="/api/v1")
app.include_router(activity.router, prefix="/api/v1")
app.include_router(intelligence.router, prefix="/api/v1")
