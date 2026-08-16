from pathlib import Path

from platformdirs import user_config_dir
from pydantic import BaseModel, ConfigDict, Field

CONFIG_APP_NAME = "oled_hero"
CONFIG_DIR = Path(user_config_dir(CONFIG_APP_NAME, roaming=False))
CONFIG_PATH = CONFIG_DIR / "config.json"


class ConfigModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="ignore")


class DisplayConfig(ConfigModel):
    brightness_default_value: int = Field(default=100, ge=0, le=100)


class AppConfig(ConfigModel):
    screen_preview_rate_millis: int = Field(default=2000, ge=(1 / 30) * 1000)
    displays: dict[str, DisplayConfig] = Field(default_factory=dict)


def default_config_path() -> Path:
    return CONFIG_PATH


def load_default_config() -> AppConfig:
    config_path = default_config_path()
    if not config_path.exists():
        return AppConfig()
    return load_config(config_path)


def load_config(path: Path) -> AppConfig:
    return AppConfig.model_validate_json(path.read_text(encoding="utf-8"))


def save_default_config(config: AppConfig) -> None:
    save_config(default_config_path(), config)


def save_config(path: Path, config: AppConfig) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{config.model_dump_json(indent=2)}\n", encoding="utf-8", newline="\n")
