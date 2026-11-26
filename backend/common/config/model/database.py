from pydantic import Field

from backend.common.model.contract_model import ContractModel


class DatabaseConfig(ContractModel):
    url: str = Field()
    echo: bool = True
    pool_size: int = Field(default=5, ge=0)
    max_overflow: int = Field(default=10, ge=0)
    pool_pre_ping: bool = True


class DatabaseSettings(ContractModel):
    __config_key__ = "database"
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
