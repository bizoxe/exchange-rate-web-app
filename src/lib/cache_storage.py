from __future__ import annotations

from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import asdict
from typing import TYPE_CHECKING

import aiofiles

from src.config import get_settings
from src.lib.coders import json_encoder

if TYPE_CHECKING:
    from pathlib import Path

    from redis.asyncio import Redis

    from src.lib.types import CurrencyInfo

__all__ = (
    "CacheStorage",
    "FileStorage",
    "RedisStorage",
    "storage_getter",
)

settings = get_settings()


class CacheStorage(ABC):
    @abstractmethod
    async def cache_currency_info(self, info: CurrencyInfo, key: str) -> bytes:
        pass

    @abstractmethod
    async def read_currency_info(self, key: str) -> bytes | None:
        pass


class FileStorage(CacheStorage):
    def __init__(
        self,
        cache_dir: Path = settings.api.CACHE_DIR,
    ) -> None:
        self._cache_dir = cache_dir

    async def cache_currency_info(self, info: CurrencyInfo, key: str) -> bytes:
        filepath = self._cache_dir / key
        currency_info_bytes: bytes = json_encoder.encode(asdict(info))
        async with aiofiles.open(filepath, "wb") as in_f:
            await in_f.write(currency_info_bytes)

        return currency_info_bytes

    async def read_currency_info(self, key: str) -> bytes | None:
        filepath = self._cache_dir / key
        if filepath.exists():
            async with aiofiles.open(filepath, "rb") as out_f:
                return await out_f.read()

        return None


class RedisStorage(CacheStorage):
    def __init__(
        self,
        redis_client: Redis = settings.redis.client,
        expire: int = settings.redis.KEY_EXPIRE_SECONDS,
    ) -> None:
        self._redis_client = redis_client
        self._expire = expire

    async def cache_currency_info(self, info: CurrencyInfo, key: str) -> bytes:
        currency_info_bytes: bytes = json_encoder.encode(asdict(info))
        await self._redis_client.setex(
            name=key,
            time=self._expire,
            value=currency_info_bytes,
        )
        return currency_info_bytes

    async def read_currency_info(self, key: str) -> bytes | None:
        cached_currency: bytes = await self._redis_client.get(name=key)
        if cached_currency:
            return cached_currency

        return None


def storage_getter(storage_type: str = settings.api.STORAGE_TYPE) -> CacheStorage:
    storages: dict[str, type[CacheStorage]] = {
        "file": FileStorage,
        "redis": RedisStorage,
    }
    return storages[storage_type]()
