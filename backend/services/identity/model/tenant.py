from datetime import datetime

from backend.common.model.contract_model import ContractModel


class TenantDTO(ContractModel):
    id: int
    company_name: str
    company_code: str | None
    status: int
    created_by: int
    updated_by: int
    created_at: datetime
    updated_at: datetime
    delete_flg: int