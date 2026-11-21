import os
from dataclasses import dataclass

from backend.common.config.env_loader import load_runtime_env_vars
from backend.common.config.manager import register_config_manager, ConfigManager
from backend.common.config.model.database import DatabaseSettings
from backend.common.config.model.id_generator import IdGeneratorSettings
from backend.common.config.model.identity import IdentitySettings
from backend.common.config.model.llm_local_params import LLMLocalParamsSettings
from backend.common.config.model.llm_vendor import LLMVendorSetting
from backend.common.config.model.server import ServerSettings
from backend.common.config.model.white_list import RoutersSetting


@dataclass(slots=True)
class BatchConfig:
    server_setting: ServerSettings
    database_setting: DatabaseSettings
    id_generator_setting: IdGeneratorSettings
    identity_setting: IdentitySettings
    routers_setting: RoutersSetting
    llm_local_params_setting: LLMLocalParamsSettings
    llm_vendor_setting: LLMVendorSetting


def load_batch_config(
        env_dir:str,
        config_dir:str,
) -> BatchConfig:
    env_vars = load_runtime_env_vars(
        env_dir=str(env_dir),
        process_env = os.environ,
    )
    config_manager = ConfigManager(config_dir=config_dir, env=env_vars)
    server_setting = config_manager.load(ServerSettings)
    database_setting = config_manager.load(DatabaseSettings)
    id_generator_setting = config_manager.load(IdGeneratorSettings)
    identity_setting = config_manager.load(IdentitySettings)
    routers_setting = config_manager.load(RoutersSetting)
    llm_local_params_setting = config_manager.load(LLMLocalParamsSettings)
    llm_vendor_setting = config_manager.load(LLMVendorSetting)
    register_config_manager(config_manager)

    return BatchConfig(
        server_setting=server_setting,
        database_setting=database_setting,
        id_generator_setting=id_generator_setting,
        identity_setting=identity_setting,
        routers_setting=routers_setting,
        llm_local_params_setting=llm_local_params_setting,
        llm_vendor_setting=llm_vendor_setting,
    )
