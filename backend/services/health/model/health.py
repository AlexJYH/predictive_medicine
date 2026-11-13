from datetime import datetime

from backend.common.model.contract_model import ContractModel


class HealthResponse(ContractModel):
    id: int
    status: int
    message: str


class HealthCheckDTO(ContractModel):
    status: int
    message: str
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    delete_flg: int
