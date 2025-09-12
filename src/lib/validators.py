import datetime

from aiohttp import web

from src.lib.currency_check_exists import check_currency


async def validate_currency(currency: str) -> str:
    if await check_currency.is_currency_exists(currency=currency):
        return currency
    message = f"Unknown {currency!r} currency, try another one."
    raise web.HTTPBadRequest(
        reason=message,
    )


def validate_provided_date(provided_date: str | None) -> datetime.date:
    selected_date = datetime.datetime.now(tz=datetime.UTC).date()
    if provided_date is not None:
        try:
            selected_date = datetime.date.fromisoformat(provided_date)
        except ValueError as exc:
            message = "The date specified must be in ISO format"
            raise web.HTTPUnprocessableEntity(
                reason=message,
            ) from exc
    return selected_date


async def get_currency_and_date(request: web.Request) -> tuple[str, datetime.date]:
    currency: str = await validate_currency(
        currency=request.match_info["currency"].lower(),
    )
    selected_date: datetime.date = validate_provided_date(
        provided_date=request.match_info.get("date"),
    )

    return currency, selected_date
