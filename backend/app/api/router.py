from fastapi import APIRouter

from backend.app.api.health import health
from backend.app.api.identity import identity
from backend.app.api.llm import silicon_flow, llm_vendor

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(identity.router)
api_router.include_router(silicon_flow.router)
api_router.include_router(llm_vendor.router)