from fastapi import APIRouter

from backend.service.health.model.health import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    # Dependency probes will be added with the persistence adapters in Phase 1.
    return HealthResponse(status="ok", environment="configured")
