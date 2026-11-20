from backend.common.model.contract_model import ContractModel


class VendorConfig(ContractModel):
    vendor_name: str
    vendor_api_key: str

class LLMVendorSetting(ContractModel):
    vendor: list[VendorConfig]