import datetime
from unittest import IsolatedAsyncioTestCase
from unittest.mock import (
    AsyncMock,
    MagicMock,
    patch,
)

from aiohttp.web_exceptions import (
    HTTPBadRequest,
    HTTPUnprocessableEntity,
)

from src.lib import validators
from tests.data import DataHelper

data_helper = DataHelper.get_helper()

AVAILABLE_CURRENCIES = data_helper.available_currencies


class TestCurrencyValidators(IsolatedAsyncioTestCase):
    @patch("src.lib.currency_check_exists.CheckCurrencyExists.is_currency_exists")
    async def test_validate_currency(self, currency_exists: AsyncMock) -> None:
        currency = "usd"
        currency_exists.return_value = True
        res = await validators.validate_currency(currency=currency)
        self.assertEqual(res, currency)

        with self.assertRaises(HTTPBadRequest) as context:
            currency_exists.return_value = False
            await validators.validate_currency(currency=currency)
        self.assertEqual(context.exception.reason, f"Unknown {currency!r} currency, try another one.")

    def test_validate_provided_date(self) -> None:
        current_date = datetime.datetime.now(tz=datetime.UTC).date()
        date_iso_format = current_date.isoformat()
        res = validators.validate_provided_date(provided_date=None)
        self.assertEqual(res, current_date)
        res = validators.validate_provided_date(provided_date=date_iso_format)
        self.assertEqual(res, current_date)

        date_iso_formats = ["2020-1-11", "20-11-12", "2025-05-1"]
        for date in date_iso_formats:
            with self.subTest(date=date):
                with self.assertRaises(HTTPUnprocessableEntity) as context:
                    validators.validate_provided_date(provided_date=date)
                self.assertEqual(context.exception.reason, "The date specified must be in ISO format")

    @patch("src.lib.currency_check_exists.CheckCurrencyExists.get_all_currencies")
    async def test_get_currency_and_date(self, all_currencies: AsyncMock) -> None:
        request = MagicMock()
        data = [
            ("AUD", datetime.date(2024, 1, 1)),
            ("usd", datetime.date(2024, 1, 1)),
        ]
        for currency, date in data:
            with self.subTest(currency=currency, date=date):
                request.match_info = {"currency": currency, "date": date.isoformat()}
                all_currencies.return_value = AVAILABLE_CURRENCIES
                res_currency, res_date = await validators.get_currency_and_date(request=request)
                self.assertEqual(res_currency, currency.lower())
                self.assertEqual(res_date, date)
