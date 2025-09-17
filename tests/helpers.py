from __future__ import annotations

from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Literal,
)

from src import config
from src.lib.types import CurrencyInfo

if TYPE_CHECKING:
    import datetime
    from collections.abc import Iterable

    from src.lib.types import ResponseType
    from tests.data import DataHelper

root_dir = Path(__file__).resolve().parent.parent
env_file = root_dir / ".env.testing"


def override_settings() -> config.Settings:
    return config.Settings.from_env(env_file=env_file)


def clear_cache_dir(path_to_dir: Path) -> None:
    for cached in path_to_dir.iterdir():
        if cached.is_file():
            cached.unlink()

    path_to_dir.rmdir()


def currency_info_response(
    date: datetime.date,
    helper: DataHelper,
    target_currencies: Iterable[str],
    currency: Literal["eur", "rub"] = "eur",
) -> CurrencyInfo:
    currency_data = helper.convert_exchange_rate_values(
        source_currency=currency,
        date=date,
    )
    info: ResponseType = {
        "date": currency_data["date"],
        "values": currency_data[currency],
    }
    return CurrencyInfo.get_currency_info_response(
        info=info,
        source_currency=currency,
        target_currencies=set(target_currencies),
    )
