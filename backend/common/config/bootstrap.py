from dataclasses import dataclass

from backend.common.config.manager import get_config_manager
from backend.common.config.model.server import ServerSettings


@dataclass(slots=True)
class BatchConfig:
    server_setting: ServerSettings


def load_batch_config() -> BatchConfig:
    config_manager = get_config_manager()
    server_setting = config_manager.load(ServerSettings)
    return BatchConfig(
        server_setting=server_setting
    )
