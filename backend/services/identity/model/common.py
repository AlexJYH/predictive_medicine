from backend.common.model.contract_model import ContractModel


class IdentityRequest(ContractModel):
    username: str
    password: str
    tenant_id: int


class TenantRequest(ContractModel):
    company_name: str
    company_code: str | None


class RegisterRequest(ContractModel):
    username:str | None
    password:str | None
    company_name:str | None
    company_code:str | None
    mail:str | None


class RegisterVO(ContractModel):
    tenant_id: int | None
    user_id: int | None
    username: str | None
    mail: str | None

