from backend.common.model.contract_model import ContractModel


class LLMConfigs(ContractModel):
    first_timeout: int
    retry: int
    stream_status: int
    between_timeout: int
    max_circulate: int
    max_stream_time: int
    fallback_times: int
    max_input_tokens: int
    max_output_tokens: int

class LLMLocalParamsSettings(ContractModel):
    __config_key__ = "llm_local_params"

    llm_configs: LLMConfigs