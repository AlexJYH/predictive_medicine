from backend.common.model.contract_model import ContractModel


class IdentityContext(ContractModel):
    tenant_id: int
    user_id: int
