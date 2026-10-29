from fastapi import APIRouter

from backend.app.api.health import health

api_router = APIRouter()

api_router.include_router(health.router)