from datetime import datetime

from backend.common.model.contract_model import ContractModel


class IdGeneratorConfig(ContractModel):
    epoch: datetime
    worker_id: int
    sequence_wait_timeout_ms: int


class IdGeneratorSettings(ContractModel):
    __config_key__ = "id_generator"
    id_generator: IdGeneratorConfig