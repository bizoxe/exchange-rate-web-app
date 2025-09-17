from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TypedDict


class ResponseType(TypedDict):
    date: str
    values: dict[str, Decimal | int]

InnerRates = dict[str, int | Decimal]
ResponseCurrency = dict[str, str | InnerRates]


@dataclass(frozen=True)
class CurrencyValue:
    currency: str
    value: Decimal | int


@dataclass(frozen=True)
class CurrencyInfo:
    date: date
    currency: str
    values: list[CurrencyValue]

    @classmethod
    def get_currency_info_response(
        cls,
        info: ResponseType,
        source_currency: str,
        target_currencies: set[str],
    ) -> "CurrencyInfo":
        return cls(
            date=date.fromisoformat(info["date"]),
            currency=source_currency,
            values=[
                CurrencyValue(currency=name, value=value)
                for name, value in info["values"].items()
                if name in target_currencies
            ],
        )
