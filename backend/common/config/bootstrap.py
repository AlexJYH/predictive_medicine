import os
from dataclasses import dataclass

from backend.common.config.env_loader import load_runtime_env_vars
from backend.common.config.manager import get_config_manager
from backend.common.config.model.database import DatabaseSettings
from backend.common.config.model.id_generator import IdGeneratorSettings
from backend.common.config.model.server import ServerSettings


@dataclass(slots=True)
class BatchConfig:
    server_setting: ServerSettings
    database_setting: DatabaseSettings
    id_generator_setting: IdGeneratorSettings


def load_batch_config(
        env_dir:str,
        config_dir:str,
) -> BatchConfig:
    env_vars = load_runtime_env_vars(
        env_dir=str(env_dir),
        process_env = os.environ,
    )

    config_manager = get_config_manager(
        config_dir=config_dir,
        env=env_vars,
    )

    server_setting = config_manager.load(ServerSettings)
    database_setting = config_manager.load(DatabaseSettings)
    id_generator_setting = config_manager.load(IdGeneratorSettings)

    return BatchConfig(
        server_setting=server_setting,
        database_setting=database_setting,
        id_generator_setting=id_generator_setting,
    )
