from fastapi import APIRouter

from backend.services.llm.runtime import get_silicon_service, get_llm_model_service
from backend.services.llm.silicon_flow.model.silicon_response import ModelListResponse

router = APIRouter(prefix="/silicon_flow",tags=["silicon_flow"])

@router.get("/model_list")
async def get_silicon_flow_model_list(
    vendor_name: str,
    model_type: str | None = None,
    sub_type: str | None = None,
) -> list[ModelListResponse]:
    vendor_dto = await get_llm_model_service().get_vendor_info(vendor_name)
    if not vendor_dto:
        raise Exception(f"Vendor {vendor_name} not found")
    return await get_silicon_service().model_list(model_type=model_type,vendor_dto=vendor_dto,sub_type=sub_type,)