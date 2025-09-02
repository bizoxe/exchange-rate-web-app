from __future__ import annotations

import datetime
from typing import (
    TYPE_CHECKING,
    Any,
)

from aiohttp import (
    ClientSession,
    web,
)

from src.config import get_settings
from src.lib.cache_storage import storage_getter
from src.lib.coders import (
    encoder,
    json_decoder_decimal,
)
from src.lib.types import CurrencyInfo

if TYPE_CHECKING:
    from collections.abc import Iterable

    from src.lib.cache_storage import CacheStorage
    from src.lib.types import ResponseType


settings = get_settings()
SUCCESS_STATUS_CODE = 200


class CurrencyRatesGetter:
    def __init__(
        self,
        currency: str,
        to_currencies: Iterable[str] = settings.api.TARGET_CURRENCIES,
        for_date: datetime.date | None = None,
        storage: CacheStorage | None = None,
        key_template: str = settings.api.key_template,
    ) -> None:
        self.currency = currency.lower()
        self.target_currencies = set(map(str.lower, to_currencies))
        self.for_date: datetime.date = for_date or datetime.datetime.now(tz=datetime.UTC).date()
        self.selected_date = self.for_date.isoformat()
        self._storage = storage or storage_getter()
        self._key_template = key_template

    def get_cache_key(
        self,
        for_date: datetime.date,
        currency: str,
    ) -> str:
        return self._key_template.format(for_date=for_date.isoformat(), currency=currency)

    async def request_currency_info(self) -> dict[str, Any]:
        url = settings.api.CURRENCY_API_WITH_DATE_URL.format(
            date=self.selected_date,
            currency=self.currency,
        )
        async with ClientSession() as session:
            async with session.get(url) as response:
                if response.status == SUCCESS_STATUS_CODE:
                    result: dict[str, Any] = await response.json(
                        loads=json_decoder_decimal.decode,
                    )
                    return result
                message = "No results were found for your request"
                raise web.HTTPNotFound(
                    body=encoder.encode({"message": message}),
                    reason=message,
                    content_type="application/json",
                )

    async def read_currency_info_for_date(self) -> CurrencyInfo:
        response_data = await self.request_currency_info()
        data: ResponseType = {
            "date": response_data["date"],
            "values": response_data[self.currency],
        }
        return CurrencyInfo.get_currency_info_response(
            info=data,
            source_currency=self.currency,
            target_currencies=self.target_currencies,
        )

    async def get_and_cache_currency_info(self) -> bytes:
        currency_info = await self.read_currency_info_for_date()
        key = self.get_cache_key(
            for_date=currency_info.date,
            currency=currency_info.currency,
        )
        currency_info_bytes: bytes = await self._storage.cache_currency_info(
            info=currency_info,
            key=key,
        )
        return currency_info_bytes

    async def get_currency_info_from_cache(self) -> bytes | None:
        key = self.get_cache_key(
            for_date=self.for_date,
            currency=self.currency,
        )
        currency_info: bytes | None = await self._storage.read_currency_info(key=key)

        return currency_info

    async def get_currency_info(self) -> bytes:
        cache = await self.get_currency_info_from_cache()
        if cache is not None:
            return cache

        return await self.get_and_cache_currency_info()
