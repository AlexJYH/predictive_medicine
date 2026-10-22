from fastapi import APIRouter
from pydantic import BaseModel

from app.config import get_settings

router = APIRouter(tags=["application"])


class BootstrapResponse(BaseModel):
    service: str
    environment: str
    capabilities: list[str]


@router.get("/app/bootstrap", response_model=BootstrapResponse)
async def bootstrap() -> BootstrapResponse:
    """Return only public application metadata for BFF page composition."""
    settings = get_settings()
    return BootstrapResponse(
        service=settings.app_name,
        environment=settings.app_env,
        capabilities=["knowledge_bases", "document_ingestion", "cited_answers"],
    )
