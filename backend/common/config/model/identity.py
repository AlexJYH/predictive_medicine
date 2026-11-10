from backend.common.model.contract_model import ContractModel


class IdentityConfig(ContractModel):
    verification_timeout_seconds: int


class IdentitySettings(ContractModel):
    __config_key__ = "identity"
    identity: IdentityConfig