from datetime import datetime

from backend.common.model.contract_model import ContractModel


class ModelRouteDTO(ContractModel):
    id: int | None
    model_id: int
    fallback_id: int | None
    scene: str
    usage: str
    status: int | None
    created_by: int | None
    created_at: datetime | None
    updated_by: int | None
    updated_at: datetime | None
    delete_flg: int | None


class LLMModelDTO(ContractModel):
    model: str
    vendor_id: int
    id: int | None
    status: int | None
    created_by: int | None
    created_at: datetime | None
    updated_by: int | None
    updated_at: datetime | None
    delete_flg: int | None


class LLMVendorDTO(ContractModel):
    vendor: str
    url: str
    passport: str
    api_key: str | None = None
    id: int | None
    status: int | None
    created_by: int | None
    created_at: datetime | None
    updated_by: int | None
    updated_at: datetime | None
    delete_flg: int | None


class LLMModelInfoDTO(ContractModel):
    model_route_dto: ModelRouteDTO
    llm_model_dtos: list[LLMModelDTO]
    llm_vendor_dtos: list[LLMVendorDTO]


class ModelRequest(ContractModel):
    model: str | None
    fallback_model: str | None
    main_vendor: str | None
    fallback_vendor: str | None
    main_url: str | None
    fallback_url: str | None


class RouteRequest(ContractModel):
    model_route_id: int | None
    scene: str | None
    usage: str | None