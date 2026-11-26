from fastapi import APIRouter

from backend.common.enums.router import LLMVendor, SiliconFlowModel
from backend.services.llm.runtime import get_llm_model_service, get_silicon_service
from backend.services.llm.vendor_model.model.llm_model import LLMVendorDTO, ModelRouteDTO

router = APIRouter(prefix="/llm_vendor", tags=["LLM Vendor"])


@router.post("/create_llm_vendor")
async def create_llm_vendor(
        request: list[LLMVendorDTO],
) -> None:
    return await get_llm_model_service().create_vendor(request)


@router.post("/batch_create_llm_model")
async def batch_create_llm_model(vendor_name: str) -> None:
    vendor_dto = await get_llm_model_service().get_vendor_info(vendor_name=vendor_name)
    model_list_responses = []
    match vendor_name:
        case LLMVendor.SILICON_FLOW.code:
            for item in SiliconFlowModel:
                response = await get_silicon_service().model_list(vendor_dto=vendor_dto, model_type=item.code, )
                model_list_responses.extend(response)
        case _:
            raise Exception(f"Vendor {vendor_name} not found")
    if len(model_list_responses) == 0:
        raise Exception(f"Vendor {vendor_name} not found")
    return await get_llm_model_service().create_llm_model(vendor_dto=vendor_dto,
                                                          model_list_responses=model_list_responses)


@router.post("/batch_create_llm_routes")
async def batch_create_llm_route(
        model_route_dtos: list[ModelRouteDTO]
) -> list[ModelRouteDTO]:
    return await get_llm_model_service().create_router_scene(model_route_dtos)
