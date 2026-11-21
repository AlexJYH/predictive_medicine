from backend.common.model.contract_model import ContractModel

class SiliconModelListResponse(ContractModel):
    id: str
    object: str | None = None
    created: int | None = None
    owned_by: str | None = None