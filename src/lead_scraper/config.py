from __future__ import annotations

from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфигурация приложения. Тянется из .env и переменных окружения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # 2GIS
    dgis_api_key: SecretStr = Field(default=SecretStr(""))
    dgis_base_url: str = "https://catalog.api.2gis.com/3.0"

    # Telegram
    telegram_bot_token: SecretStr = Field(default=SecretStr(""))
    telegram_chat_id: str = ""

    # Поиск
    default_city: str = "Москва"
    default_rubrics: str = (
        "кафе,ресторан,салон красоты,барбершоп,отель,хостел,магазин одежды,автосервис"
    )

    # Лимиты
    max_places_per_rubric: int = 200
    request_timeout: float = 20.0
    concurrency: int = 8

    # Хранилище
    seen_storage: Path = Path("data/seen.json")
    leads_storage: Path = Path("data/leads.jsonl")

    @property
    def rubrics_list(self) -> list[str]:
        return [r.strip() for r in self.default_rubrics.split(",") if r.strip()]

    @property
    def telegram_enabled(self) -> bool:
        return bool(self.telegram_bot_token.get_secret_value() and self.telegram_chat_id)


settings = Settings()
