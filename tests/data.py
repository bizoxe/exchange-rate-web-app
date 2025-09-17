import datetime
from dataclasses import dataclass
from decimal import Decimal
from typing import (
    Any,
    Literal,
    NotRequired,
    TypedDict,
)

from tests import currencies_raw_data as raw_data


class ExchangeRatesDecimal(TypedDict):
    date: str
    rub: NotRequired[dict[str, int | Decimal]]
    eur: NotRequired[dict[str, int | Decimal]]


class CurrencyDataBase(TypedDict):
    date: str
    rub: NotRequired[dict[str, int | float]]
    eur: NotRequired[dict[str, int | float]]


@dataclass
class DataHelper:
    all_currencies: dict[str, str]
    rub_data: dict[str, float]
    eur_data: dict[str, float]

    @property
    def available_currencies(self) -> dict[str, str]:
        return self.all_currencies

    @staticmethod
    def get_stub_currency(currency: str, date: datetime.date) -> dict[str, Any]:
        return {
            "date": date.isoformat(),
            currency: {},
        }

    def update_currency_dict(
        self,
        currency: Literal["rub", "eur"],
        selected_date: datetime.date | None = None,
    ) -> CurrencyDataBase:
        if selected_date is None:
            selected_date = datetime.datetime.now(tz=datetime.UTC).date()

        exchange_data = {"eur": self.eur_data, "rub": self.rub_data}
        if currency == "rub":
            return {"date": selected_date.isoformat(), "rub": exchange_data["rub"]}
        return {
            "date": selected_date.isoformat(),
            "eur": exchange_data["eur"],
        }

    def convert_exchange_rate_values(
        self,
        source_currency: Literal["rub", "eur"],
        date: datetime.date,
    ) -> ExchangeRatesDecimal:
        """Convert exchange rate values to the decimal type for the source currency."""
        currency_data = self.update_currency_dict(
            currency=source_currency,
            selected_date=date,
        )

        def prepare_values(items: tuple[str, int | float]) -> tuple[str, int | Decimal]:
            key, value = items
            if isinstance(value, int):
                return key, value
            if isinstance(value, float):
                return key, Decimal(str(value))
            raise TypeError(f"Unsupported type for value: {type(value)}")  # noqa: EM102, TRY003

        exchange_rate_values = currency_data[source_currency]
        convert_to_decimal = dict(map(prepare_values, exchange_rate_values.items()))
        if source_currency == "rub":
            return {
                "date": currency_data["date"],
                "rub": convert_to_decimal,
            }
        return {
            "date": currency_data["date"],
            "eur": convert_to_decimal,
        }

    @classmethod
    def get_helper(cls) -> "DataHelper":
        return cls(
            all_currencies=raw_data.AVAILABLE_CURRENCIES,
            rub_data=raw_data.RUB_EXCHANGE,
            eur_data=raw_data.EUR_EXCHANGE,
        )
