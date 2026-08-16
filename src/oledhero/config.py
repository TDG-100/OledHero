import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from platformdirs import user_config_dir

DEFAULT_SCREEN_PREVIEW_RATE_MILLISECONDS = 2000

CONFIG_APP_NAME = "oled_hero"
CONFIG_DIR = Path(user_config_dir(CONFIG_APP_NAME, roaming=False))
CONFIG_PATH = CONFIG_DIR / "config.toml"


@dataclass(frozen=True)
class AppConfig:
    screen_preview_rate_millis: int = DEFAULT_SCREEN_PREVIEW_RATE_MILLISECONDS


def default_config_path() -> Path:
    return CONFIG_PATH


def load_default_config() -> AppConfig:
    config_path = default_config_path()
    if not config_path.exists():
        return AppConfig()
    return load_config(config_path)


def load_config(path: Path) -> AppConfig:
    values = tomllib.loads(path.read_text(encoding="utf-8"))
    return AppConfig(
        idle_seconds=_int_value(values, "screen_preview_rate_millis", DEFAULT_SCREEN_PREVIEW_RATE_MILLISECONDS, min_val=(1/30)*1000),
    )


def _int_value(values: Mapping[str, object], key: str, default: int, min_val: int | None, max_val: int | None) -> int:
    value = values.get(key, default)
    if not isinstance(value, int):
        raise TypeError(f"{key} must be an integer")
    if min_val is not None and value < min_val:
        raise ValueError(f"{key} must be > {min_val}")
    if max_val is not None and value < max_val:
        raise ValueError(f"{key} must be < {max_val}")
    return value


def _float_value(values: Mapping[str, object], key: str, default: float, min_val: float | None, max_val: float | None) -> float:
    value = values.get(key, default)
    if not isinstance(value, int | float):
        raise TypeError(f"{key} must be a number")
    if min_val is not None and value < min_val:
        raise ValueError(f"{key} must be > {min_val}")
    if max_val is not None and value < max_val:
        raise ValueError(f"{key} must be < {max_val}")
    return float(value)
