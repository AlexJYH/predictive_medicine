from fastapi import APIRouter

from backend.services.llm.runtime import get_silicon_service
from backend.services.llm.silicon_flow.model.silicon_response import ModelListResponse

router = APIRouter(prefix="/silicon_flow",tags=["silicon_flow"])

@router.get("/model_list")
async def get_silicon_flow_model_list(
    vendor_name: str,
    model_type: str | None = None,
    sub_type: str | None = None,
) -> list[ModelListResponse]:
    return await get_silicon_service().model_list(model_type=model_type,sub_type=sub_type,vendor_name=vendor_name)