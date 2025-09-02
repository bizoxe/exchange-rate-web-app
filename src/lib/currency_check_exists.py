from dataclasses import (
    dataclass,
    field,
)

import aiohttp

from src.config import get_settings

__all__ = ("check_currency",)

settings = get_settings()


@dataclass
class CheckCurrencyExists:
    cached_currencies: set[str] = field(default_factory=set)

    @classmethod
    async def get_all_currencies(cls) -> dict[str, str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(settings.api.CURRENCIES_API_LIST_URL) as response:
                result: dict[str, str] = await response.json()
                return result

    async def is_currency_exists(self, currency: str) -> bool:
        if not self.cached_currencies:
            all_currencies: dict[str, str] = await self.get_all_currencies()
            self.cached_currencies.update(set(all_currencies))
        return currency in self.cached_currencies


check_currency = CheckCurrencyExists()
