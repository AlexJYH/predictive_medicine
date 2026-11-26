from datetime import datetime

from backend.common.model.contract_model import ContractModel


class TenantUserRelationDTO(ContractModel):
    user_id: int
    status: int
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    delete_flg: int
