from aiohttp import web

from src.config import get_settings
from src.lib.currency_rates_getter import CurrencyRatesGetter
from src.lib.validators import get_currency_and_date

routes = web.RouteTableDef()

__all__ = ("create_app",)


settings = get_settings()


@routes.get("/rates/{currency}")
@routes.get("/rates/{currency}/{date}")
async def get_currency_rates(request: web.Request) -> web.Response:
    currency, date = await get_currency_and_date(request=request)
    currency_getter = CurrencyRatesGetter(currency=currency, for_date=date)
    currency_info_bytes = await currency_getter.get_currency_info()

    return web.json_response(body=currency_info_bytes, status=200)


def create_app() -> web.Application:
    app = web.Application()
    app.add_routes(routes=routes)

    return app
