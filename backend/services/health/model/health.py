from backend.common.model.contract_model import ContractModel


class HealthResponse(ContractModel):
    status: str
    environment: str