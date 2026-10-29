import re
from functools import lru_cache
from pathlib import Path
from typing import *

from pydantic import BaseModel

from backend.common.config.loader import load_yaml_config

T = TypeVar("T", bound=BaseModel)


class ConfigManager:

    def __init__(
            self,
            config_dir: str | None = None,
            env: Mapping[str, str] | None = None,
    ) -> None:
        if config_dir is None:
            self._config_dir = (
                    Path(__file__).resolve().parents[2] / "config"
            )
        else:
            self._config_dir = Path(config_dir).resolve()

        self._env = None if env is None else dict(env)
        self._cache: dict[type[BaseModel], BaseModel] = {}

    def load(self, model_cls: type[T]) -> T:
        if model_cls in self._cache:
            return cast(T, self._cache[model_cls])
        config_key = getattr(model_cls, "__config_key__", None)
        if (
                not isinstance(config_key, str)
                or re.fullmatch(r"[A-Za-z0-9_-]+", config_key) is None
        ):
            raise ValueError(
                f"{model_cls.__name__} must define a valid __config_key__. "
                "Only letters, digits, underscores, and hyphens are allowed."
            )
        config_path = self._config_dir / f"{config_key}.yaml"
        data = load_yaml_config(str(config_path), env=self._env, )
        settings = model_cls.model_validate(data)
        self._cache[model_cls] = settings
        return settings

    def clear_cache(self) -> None:
        self._cache.clear()


@lru_cache
def get_config_manager() -> ConfigManager:
    return ConfigManager()
