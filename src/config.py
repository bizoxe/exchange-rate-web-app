import os
from dataclasses import (
    dataclass,
    field,
)
from functools import lru_cache
from pathlib import Path
from typing import Final

from redis.asyncio import Redis

BASE_DIR: Final[Path] = Path(__file__).resolve().parent


@dataclass
class ApplicationConfig:
    """Application configuration."""

    TARGET_CURRENCIES: tuple[str, ...] = (
        "rub",
        "eur",
        "byn",
        "usd",
        "pln",
    )
    CACHE_DIR: Path = field(default=BASE_DIR.joinpath("currencies-cache"))
    CURRENCIES_API_LIST_URL: str = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies.json"
    CURRENCY_API_WITH_DATE_URL: str = (
        "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date}/v1/currencies/{currency}.json"
    )
    DEFAULT_LOG_FORMAT = "[%(asctime)s.%(msecs)03d] %(module)s:%(lineno)d %(levelname)s - %(message)s"
    STORAGE_TYPE: str = field(default_factory=lambda: os.getenv("STORAGE_TYPE", "redis"))

    @property
    def key_template(self) -> str:
        templates: dict[str, str] = {
            "file": "{for_date}-{currency}.json",
            "redis": "{for_date}-{currency}",
        }
        return templates[self.STORAGE_TYPE]


@dataclass
class RedisConfig:
    """Redis configuration."""

    URL: str = "redis://localhost:6379/0"
    """Redis connection URL."""
    SOCKET_CONNECT_TIMEOUT: int = 5
    """Length of time to wait (in seconds) for a connection to become active."""
    HEALTH_CHECK_INTERVAL: int = 5
    """Length of time to wait (in seconds) before testing connection health."""
    SOCKET_KEEPALIVE: bool = True
    """Length of time to wait (in seconds) between keepalive commands."""
    KEY_EXPIRE_SECONDS: int = 60

    @property
    def client(self) -> Redis:
        return self.get_client()

    def get_client(self) -> Redis:
        redis: Redis = Redis.from_url(
            url=self.URL,
            encoding="utf-8",
            decode_responses=False,
            socket_connect_timeout=self.SOCKET_CONNECT_TIMEOUT,
            socket_keepalive=self.SOCKET_KEEPALIVE,
            health_check_interval=self.HEALTH_CHECK_INTERVAL,
        )
        return redis


@dataclass
class Settings:
    api: ApplicationConfig = field(default_factory=ApplicationConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)


@lru_cache(maxsize=1, typed=True)
def get_settings() -> Settings:
    return Settings()
