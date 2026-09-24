from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(tags=["system"])


class HealthResponse(BaseModel):
    status: str
    environment: str


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    # Dependency probes will be added with the persistence adapters in Phase 1.
    return HealthResponse(status="ok", environment="configured")
