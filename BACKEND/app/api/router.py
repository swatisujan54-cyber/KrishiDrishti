"""Aggregated API router.

All endpoint routers are mounted here under a common prefix.  ``main.py``
includes this single router.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings
from app.api import (
    auth,
    users,
    crops,
    diseases,
    advisories,
    scans,
    sync,
    expert_requests,
    feedback,
    system,
)

api_router = APIRouter(prefix=settings.API_V1_PREFIX)
api_router.include_router(system.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(crops.router)
api_router.include_router(diseases.router)
api_router.include_router(advisories.router)
api_router.include_router(scans.router)
api_router.include_router(sync.router)
api_router.include_router(expert_requests.router)
api_router.include_router(feedback.router)
