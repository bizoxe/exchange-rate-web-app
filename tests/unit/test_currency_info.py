from __future__ import annotations

import datetime
from dataclasses import asdict
from typing import (
    TYPE_CHECKING,
    Any,
)
from unittest import TestCase

from src.lib.types import CurrencyInfo

from tests.data import data_helper

if TYPE_CHECKING:
    from decimal import Decimal

    from src.lib.types import ResponseType

TARGET_CURRENCIES = {
    "byn",
    "usd",
    "aud",
}


class TestCurrencyInfo(TestCase):
    currency: str
    date: datetime.date
    currency_data: dict[str, Any]

    @classmethod
    def setUpClass(cls) -> None:
        cls.currency = "eur"
        cls.date = datetime.date(2024, 5, 11)
        convert_currencies_values = data_helper.update_currency_dict(
            currency=cls.currency,
            selected_date=cls.date,
        )
        cls.currency_data = convert_currencies_values

    def test_get_currency_info_response(self) -> None:
        values: dict[str, int | Decimal] = self.currency_data[self.currency]
        info: ResponseType = {"date": self.date.isoformat(), "values": values}
        expected_len = len(TARGET_CURRENCIES)
        response = CurrencyInfo.get_currency_info_response(
            info=info,
            source_currency=self.currency,
            target_currencies=TARGET_CURRENCIES,
        )
        response_dict = asdict(response)
        self.assertEqual(response_dict["currency"], self.currency)
        self.assertEqual(len(response_dict["values"]), expected_len)
