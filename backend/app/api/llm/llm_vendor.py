from fastapi import APIRouter

from backend.services.llm.runtime import get_llm_model_service
from backend.services.llm.vendor_model.model.llm_model import LLMVendorDTO

router = APIRouter(prefix="/llm_vendor", tags=["LLM Vendor"])

@router.post("/create_llm_vendor")
async def create_llm_vendor(
    request: list[LLMVendorDTO],
) -> None:
    return await get_llm_model_service().create_vendor(request)