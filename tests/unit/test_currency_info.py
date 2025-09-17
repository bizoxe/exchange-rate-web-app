from __future__ import annotations

import datetime
from dataclasses import asdict
from typing import (
    TYPE_CHECKING,
    Literal,
)
from unittest import TestCase

from src.lib.types import CurrencyInfo
from tests.data import DataHelper

if TYPE_CHECKING:
    from decimal import Decimal

    from src.lib.types import ResponseType
    from tests.data import ExchangeRatesDecimal

TARGET_CURRENCIES = {
    "byn",
    "usd",
    "aud",
}
data_helper = DataHelper.get_helper()


class TestCurrencyInfo(TestCase):
    currency: Literal["eur", "rub"]
    date: datetime.date
    currency_data: ExchangeRatesDecimal

    @classmethod
    def setUpClass(cls) -> None:
        cls.currency = "eur"
        cls.date = datetime.date(2024, 5, 11)
        cls.currency_data = data_helper.convert_exchange_rate_values(
            source_currency=cls.currency,
            date=cls.date,
        )

    def test_get_currency_info_response(self) -> None:
        values: dict[str, int | Decimal] = self.currency_data[self.currency]
        info: ResponseType = {
            "date": self.date.isoformat(),
            "values": values,
        }
        expected_len = len(TARGET_CURRENCIES)
        response = CurrencyInfo.get_currency_info_response(
            info=info,
            source_currency=self.currency,
            target_currencies=TARGET_CURRENCIES,
        )
        response_dict = asdict(response)
        self.assertEqual(response_dict["currency"], self.currency)
        self.assertEqual(len(response_dict["values"]), expected_len)
