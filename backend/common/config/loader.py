import os
import re
from pathlib import Path
from typing import Mapping, Any

import yaml

# accept ${NAME} and ${NAME:-default}
_ENV_PATTERN = re.compile(
    r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}"
)


def load_yaml_config(
        path: str,
        env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """read the information of YAML file, replace environment variable, response dict"""
    config_path = Path(path)

    with config_path.open("r", encoding="utf-8") as file:
        try:
            data = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            raise ValueError(
                f"YAML format error: {config_path.name}"
            ) from None
    if data is None:
        raise ValueError(f"YAML information is empty:{config_path.name}")
    if not isinstance(data, dict):
        raise ValueError(f"YAML information must be dict:{config_path.name}")
    variables = dict(os.environ if env is None else env)
    return _resolve_env(data, variables)


def _resolve_env(value: Any, env: Mapping[str, str]) -> Any:
    """recurse deal dict,list and environment of string variable"""

    if isinstance(value, dict):
        result = {}
        for key,item in value.items():
            result[key] = _resolve_env(item, env)
        return result

    if isinstance(value, list):
        return [_resolve_env(item, env) for item in value]

    if isinstance(value, str):
        def replace(match: re.Match[str]) -> str:
            name, default = match.groups()
            if name in env:
                return env[name]
            if default is not None:
                return default
            raise ValueError(f"missing vital environment variable: {name}")

        return _ENV_PATTERN.sub(replace, value)

    return value
