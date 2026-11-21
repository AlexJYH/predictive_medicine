from backend.common.model.contract_model import ContractModel


class ModelListResponse(ContractModel):
    model_name: str
    object: str
    created: int
    owned_by: str