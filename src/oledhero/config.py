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
    screen_preview_rate_millis: int = Field(default=2000, ge=round(1 / 30) * 1000)
    displays: dict[str, DisplayConfig] = Field(default_factory=dict)


def _load_app_config() -> AppConfig:
    if not CONFIG_PATH.exists():
        return AppConfig()
    return AppConfig.model_validate_json(CONFIG_PATH.read_text(encoding="utf-8"))


app_config = _load_app_config()


def save_app_config() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(f"{app_config.model_dump_json(indent=2)}\n", encoding="utf-8", newline="\n")
