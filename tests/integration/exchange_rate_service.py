"""This module contains a class that simulates requests to an external service to obtain exchange rates."""

import datetime
from typing import (
    Any,
    Literal,
    cast,
)
from unittest.mock import Mock

import aiohttp
from aiohttp.web_exceptions import HTTPNotFound
from aioresponses import aioresponses

from src.lib.types import ResponseCurrency
from tests.data import CurrencyDataBase, DataHelper
from tests.helpers import override_settings

settings = override_settings()
data_helper = DataHelper.get_helper()


class ExchangeRateService:
    def __init__(
        self,
        all_currencies_url: str = settings.api.CURRENCIES_API_LIST_URL,
        currency_url: str = settings.api.CURRENCY_API_WITH_DATE_URL,
    ) -> None:
        self.all_currencies_url = all_currencies_url
        self.currency_url = currency_url

    @classmethod
    async def request_currency_api_url(cls, url: str) -> ResponseCurrency:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                result: ResponseCurrency = await response.json()
                return result

    @classmethod
    async def request_all_currencies_api_url(cls, url: str) -> dict[str, str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                result: dict[str, str] = await response.json()
                return result

    @aioresponses()
    async def mock_currency_api_url(
        self,
        mocked: aioresponses,
        currency: str,
        date: datetime.date | None = None,
    ) -> CurrencyDataBase | dict[str, Any]:
        lowered_currency = currency.lower()
        currency_data: dict[str, Any] | CurrencyDataBase
        if date is None:
            date = datetime.datetime.now(tz=datetime.UTC).date()
        if lowered_currency not in {"eur", "rub"}:
            currency_data = data_helper.get_stub_currency(currency=lowered_currency, date=date)
        else:
            currency_literal = cast("Literal['eur', 'rub']", lowered_currency)
            currency_data = data_helper.update_currency_dict(currency=currency_literal, selected_date=date)
        url = self.currency_url.format(date=date.isoformat(), currency=lowered_currency)
        mocked.get(
            url,
            payload=currency_data,
        )

        return await self.request_currency_api_url(
            url=url,
        )

    @aioresponses()
    async def mock_all_currencies_api_url(
        self,
        mocked: aioresponses,
    ) -> dict[str, str]:
        url = self.all_currencies_url
        mocked.get(
            url,
            payload=data_helper.all_currencies,
        )
        response: dict[str, str] = await self.request_all_currencies_api_url(url=url)

        return response

    @aioresponses()
    async def mock_currency_api_url_404(
        self,
        mocked: aioresponses,
        currency: str,
        date: datetime.date,
    ) -> Mock:
        """Simulates a failed request to an external currency API for a specific date and currency.

        The method mocks an HTTP 404 (Not Found) response. It calls `request_currency_api_url`,
        which raises an `HTTPNotFound` exception internally. This exception is caught and a `Mock`
        object is returned instead.

        Returns:
            Mock: A mock object simulating the failed response.
        """
        url = self.currency_url.format(date=date, currency=currency)
        mocked.get(url, exception=HTTPNotFound())
        try:
            return await self.request_currency_api_url(url=url)  # type: ignore[return-value]
        except HTTPNotFound:
            return Mock(side_effect=HTTPNotFound(reason="No results were found for your request"))
