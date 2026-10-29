from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator


class ServerSettings(BaseModel):
    __config_key__ = "server"

    model_config = ConfigDict(extra="forbid")

    class ServerConfig(BaseModel):
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
