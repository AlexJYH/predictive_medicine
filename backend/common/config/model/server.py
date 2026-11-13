from __future__ import annotations

from pydantic import ConfigDict, field_validator

from backend.common.model.contract_model import ContractModel


class ServerSettings(ContractModel):
    __config_key__ = "server"

    class ServerConfig(ContractModel):
        model_config = ConfigDict(extra="forbid")

        host: str
        port: int
        prefix: str

        @field_validator("prefix")
        @classmethod
        def validate_prefix(cls, value: str):
            if not value.startswith("/") or value.endswith("/"):
                raise ValueError("Prefix must start and end with '/'")
            return value

    server: ServerConfig
