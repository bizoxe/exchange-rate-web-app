from __future__ import annotations

import datetime
from dataclasses import asdict
from typing import (
    TYPE_CHECKING,
    Literal,
)
from unittest import IsolatedAsyncioTestCase
from unittest.mock import (
    AsyncMock,
    patch,
)

from aiohttp.web_exceptions import HTTPNotFound

from src.lib.coders import json_encoder
from src.lib.currency_rates_getter import CurrencyRatesGetter
from tests.data import DataHelper
from tests.helpers import currency_info_response

if TYPE_CHECKING:
    from collections.abc import Iterable

    from src.lib.types import CurrencyInfo


TARGET_CURRENCIES = (
    "rub",
    "eur",
    "byn",
    "usd",
    "cad",
    "gbp",
)

DATE_AND_CURRENCY_API_URL = (
    "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date}/v1/currencies/{currency}.json"
)
CURRENT_DATE = datetime.datetime.now(tz=datetime.UTC).date()
DEFAULT_CURRENCY: Literal["rub", "eur"] = "rub"

data_helper = DataHelper.get_helper()


class TestCurrencyRatesGetter(IsolatedAsyncioTestCase):
    test_date: datetime.date
    currency: Literal["eur", "rub"]
    target_currencies: Iterable[str]
    storage: AsyncMock
    rates_getter: CurrencyRatesGetter
    currency_info: CurrencyInfo

    @classmethod
    def setUpClass(cls) -> None:
        cls.test_date = CURRENT_DATE
        cls.currency = DEFAULT_CURRENCY
        cls.target_currencies = TARGET_CURRENCIES
        cls.storage = AsyncMock()

        cls.currency_info = currency_info_response(
            date=cls.test_date,
            helper=data_helper,
            target_currencies=cls.target_currencies,
            currency=cls.currency,
        )

        cls.rates_getter = CurrencyRatesGetter(
            currency=cls.currency,
            to_currencies=cls.target_currencies,
            for_date=cls.test_date,
            storage=cls.storage,
            key_template="",
        )

    def test_cache_key(self) -> None:
        templates = (
            ("{for_date}-{currency}.json", "usd"),
            ("{for_date}-{currency}", "rub"),
        )
        for template, currency in templates:
            with self.subTest(template=template, currency=currency):
                setattr(self.rates_getter, "_key_template", template)  # noqa: B010
                cache_key = self.rates_getter.get_cache_key(
                    for_date=self.test_date,
                    currency=currency,
                )
                self.assertEqual(template.format(for_date=self.test_date, currency=currency), cache_key)

    @patch("aiohttp.ClientSession.get")
    async def test_request_currency_info(self, mock_get: AsyncMock) -> None:
        prepare_url = DATE_AND_CURRENCY_API_URL.format(
            date=self.test_date,
            currency=self.currency,
        )
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value={})
        res = await CurrencyRatesGetter.request_currency_info(url=prepare_url)
        self.assertIsNotNone(res)
        with self.assertRaises(HTTPNotFound):
            mock_get.return_value.__aenter__.return_value.status = 404
            await CurrencyRatesGetter.request_currency_info(url=prepare_url)


    @patch("src.lib.currency_rates_getter.settings.api.CURRENCY_API_WITH_DATE_URL", DATE_AND_CURRENCY_API_URL)
    @patch.object(CurrencyRatesGetter, "request_currency_info")
    async def test_read_currency_info_for_date(self, req_currency_info: AsyncMock) -> None:
        decimal_exchange_rates = data_helper.convert_exchange_rate_values(
            source_currency=self.currency,
            date=self.test_date,
        )
        req_currency_info.return_value = decimal_exchange_rates
        res = await self.rates_getter.read_currency_info_for_date()
        self.assertEqual(asdict(res), asdict(self.currency_info))

    @patch.object(CurrencyRatesGetter, "read_currency_info_for_date")
    async def test_get_and_cache_currency_info(self, currency_info_for_date: AsyncMock) -> None:
        currency_info_for_date.return_value = self.currency_info
        setattr(self.rates_getter, "_key_template", "{for_date}-{currency}")  # noqa: B010
        self.storage.cache_currency_info.return_value = json_encoder.encode(self.currency_info)
        res: bytes = await self.rates_getter.get_and_cache_currency_info()
        self.assertEqual(res, json_encoder.encode(self.currency_info))

    async def test_get_currency_info_from_cache(self) -> None:
        setattr(self.rates_getter, "_key_template", "{for_date}-{currency}")  # noqa: B010
        self.storage.read_currency_info.return_value = None
        res_none = await self.rates_getter.get_currency_info_from_cache()
        self.assertIsNone(res_none)
        self.storage.read_currency_info.return_value = json_encoder.encode(self.currency_info)
        res = await self.rates_getter.get_currency_info_from_cache()
        self.assertIsNotNone(res)

    @patch.object(CurrencyRatesGetter, "get_and_cache_currency_info")
    @patch.object(CurrencyRatesGetter, "get_currency_info_from_cache")
    async def test_get_currency_info(
        self,
        currency_info_from_cache: AsyncMock,
        get_and_cache: AsyncMock,
    ) -> None:
        currency_info_from_cache.return_value = json_encoder.encode(self.currency_info)
        res = await self.rates_getter.get_currency_info()
        get_and_cache.assert_not_called()
        self.assertEqual(res, json_encoder.encode(self.currency_info))
        currency_info_from_cache.return_value = None
        await self.rates_getter.get_currency_info()
        get_and_cache.assert_called_once()
