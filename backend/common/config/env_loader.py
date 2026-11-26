import os
import re
from io import StringIO
from pathlib import Path
from typing import Mapping

from dotenv import dotenv_values

_ASSIGNMENT_PATTERN = re.compile(
    r"(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*="
)


def load_runtime_env_vars(
        env_dir: str,
        *,
        process_env: Mapping[str, str]
) -> dict[str, str]:
    directory = Path(env_dir).expanduser().resolve()
    if not directory.is_dir():
        raise FileNotFoundError(
            f"Environment directory not found: {directory}"
        )
    env_files = []
    for path in directory.glob("*.env"):
        if path.is_file():
            env_files.append(path)
    env_files = sorted(env_files)
    if not env_files:
        raise FileNotFoundError(
            f"No .env files found in: {directory}"
        )

    process = dict(
        os.environ if process_env is None else process_env
    )
    file_values: dict[str, str] = {}
    key_sources: dict[str, Path] = {}

    for path in env_files:
        values = load_env_file(path)

        for key, value in values.items():
            if key in key_sources:
                raise ValueError(
                    f"Duplicate environment variable '{key}' in "
                    f"{path.name}; already defined in "
                    f"{key_sources[key].name}"
                )

            file_values[key] = value
            key_sources[key] = path

    merged = dict(file_values)
    merged.update(process)

    return merged


def load_env_file(path: str | Path) -> dict[str, str]:
    config_path = Path(path)
    content = config_path.read_text(encoding="utf-8-sig")
    values: dict[str, str] = {}

    for line_number, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = _ASSIGNMENT_PATTERN.match(stripped)
        location = f"{config_path.name}:{line_number}"

        if match is None:
            raise ValueError(
                f"Invalid environment assignment at {location}; "
                "expected KEY=value"
            )

        key = match.group(1)

        if key in values:
            raise ValueError(
                f"Duplicate environment variable '{key}' at {location}"
            )

        parsed = dotenv_values(
            stream=StringIO(line),
            interpolate=False,
        )

        if len(parsed) != 1 or key not in parsed:
            raise ValueError(
                f"Invalid environment value at {location}"
            )

        value = parsed[key]

        if value is None:
            raise ValueError(
                f"Missing assignment value for '{key}' at {location}"
            )

        values[key] = value

    return values
