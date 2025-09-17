from unittest import IsolatedAsyncioTestCase
from unittest.mock import (
    AsyncMock,
    patch,
)

from src.lib.currency_check_exists import CheckCurrencyExists
from tests.data import DataHelper

data_helper = DataHelper.get_helper()
AVAILABLE_CURRENCIES = data_helper.available_currencies


class TestCurrencyExists(IsolatedAsyncioTestCase):
    check_currency: CheckCurrencyExists

    @classmethod
    def setUpClass(cls) -> None:
        cls.check_currency = CheckCurrencyExists()

    @patch("aiohttp.ClientSession.get")
    async def test_is_currency_exists(self, mock_get: AsyncMock) -> None:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=AVAILABLE_CURRENCIES)
        self.assertFalse(self.check_currency.cached_currencies)
        res_true = await self.check_currency.is_currency_exists(currency="aud")
        self.assertTrue(self.check_currency.cached_currencies)
        self.assertTrue(res_true)
        res_false = await self.check_currency.is_currency_exists(currency="blob")
        self.assertFalse(res_false)
