from dataclasses import dataclass

from backend.common.model.contract_model import ContractModel


@dataclass(frozen=True,slots=True)
class ModelBinding:
    vendor: str
    model: str

class LLMLocalParamsDTO(ContractModel):
    model: str
    url: str
    api_key: str


class ModelLocalDTO(ContractModel):
    model_name: str
    litellm_params: LLMLocalParamsDTO