from backend.common.model.contract_model import ContractModel

class RoutersConfig(ContractModel):
    method: str
    path: str


class RoutersSetting(ContractModel):
    __config_key__ = "white_list"
    routers: list[RoutersConfig]