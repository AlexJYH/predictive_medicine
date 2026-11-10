from fastapi import APIRouter

from backend.services.health.model.health import HealthResponse
from backend.services.health.runtime import get_health_service

router = APIRouter(prefix="/check",tags=["system"])


@router.post("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return await get_health_service().get_health()
