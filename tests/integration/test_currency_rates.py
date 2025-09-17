from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
from unittest.mock import patch

from aiohttp.test_utils import AioHTTPTestCase

from tests.helpers import (
    clear_cache_dir,
    override_settings,
)
from tests.integration.exchange_rate_service import ExchangeRateService

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from aiohttp.web import Application

settings = override_settings()


def setUpModule() -> None:
    test_cache_dir = settings.api.CACHE_DIR
    test_cache_dir.mkdir(exist_ok=True)


def tearDownModule() -> None:
    test_cache_dir = settings.api.CACHE_DIR
    clear_cache_dir(path_to_dir=test_cache_dir)


@patch("src.lib.currency_check_exists.CheckCurrencyExists.get_all_currencies")
@patch("src.lib.currency_rates_getter.CurrencyRatesGetter.request_currency_info")
class TestCurrencyRates(AioHTTPTestCase):
    exchange_rate_service: ExchangeRateService

    @classmethod
    def setUpClass(cls) -> None:
        cls.exchange_rate_service = ExchangeRateService()

    async def get_application(self) -> Application:
        """Get an application instance.

        We import an instance inside the function in order to replace the initialization
        of environment variables with test ones.
        """
        from src.app import create_app  # noqa: PLC0415

        return create_app()

    async def test_get_currency_rates(
        self,
        req_currency_info: AsyncMock,
        all_currencies: AsyncMock,
    ) -> None:
        request_data = [
            ("rub", None),
            ("rub", datetime.date(2024, 6, 11)),
            ("eur", None),
            ("eur", datetime.date(2023, 7, 18)),
        ]
        for currency, date in request_data:
            with self.subTest(currency=currency, date=date):
                req_currency_info.return_value = await self.exchange_rate_service.mock_currency_api_url(  # type: ignore[call-arg]
                    currency=currency,
                    date=date,
                )
                all_currencies.return_value = await self.exchange_rate_service.mock_all_currencies_api_url()  # type: ignore[call-arg]
                prepare_url = f"/rates/{currency}/{date}" if date is not None else f"/rates/{currency}"
                async with self.client.get(prepare_url) as response:
                    self.assertEqual(response.status, 200)

    async def test_get_currency_rates_404(
        self,
        req_currency_info: AsyncMock,
        all_currencies: AsyncMock,
    ) -> None:
        date = datetime.date(2022, 12, 1)
        currency = "rub"
        req_currency_info.side_effect = await self.exchange_rate_service.mock_currency_api_url_404(  # type: ignore[call-arg]
            currency=currency,
            date=date,
        )
        all_currencies.return_value = await self.exchange_rate_service.mock_all_currencies_api_url()  # type: ignore[call-arg]
        async with self.client.get(f"/rates/{currency}/{date.isoformat()}") as response:
            self.assertEqual(response.status, 404)

    async def test_currency_rates_currency_and_date(
        self,
        req_currency_info: AsyncMock,
        all_currencies: AsyncMock,
    ) -> None:
        currency = "AUD"
        date = datetime.date(2022, 1, 22)
        req_currency_info.return_value = await self.exchange_rate_service.mock_currency_api_url(  # type: ignore[call-arg]
            currency=currency,
            date=date,
        )
        all_currencies.return_value = await self.exchange_rate_service.mock_all_currencies_api_url()  # type: ignore[call-arg]
        async with self.client.get(f"/rates/{currency}/{date.isoformat()}") as response:
            self.assertEqual(response.status, 200)
            result = await response.json()
            self.assertEqual(result["date"], date.isoformat())
            self.assertEqual(result["currency"], currency.lower())

        requested_data = [(("eur", "2011-1-1"), 422), (("ops", "2012-06-08"), 400), (("aad", None), 400)]
        for first, status in requested_data:
            with self.subTest(first=first, status=status):
                req_currency_info.return_value = await self.exchange_rate_service.mock_currency_api_url(  # type: ignore[call-arg]
                    currency=first[0],
                )
                all_currencies.return_value = await self.exchange_rate_service.mock_all_currencies_api_url()  # type: ignore[call-arg]
                url = f"/rates/{first[0]}/{first[1]}" if first[1] is not None else f"/rates/{first[0]}"
                async with self.client.get(url) as response:
                    self.assertEqual(response.status, status)
