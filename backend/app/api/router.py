from fastapi import APIRouter

from backend.app.api.health import health
from backend.app.api.identity import identity

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(identity.router)