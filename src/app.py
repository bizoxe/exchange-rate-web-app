from aiohttp import web
from redis.asyncio import Redis

from src.config import get_settings
from src.lib.cache_storage import (
    FileStorage,
    RedisStorage,
)
from src.lib.currency_rates_getter import CurrencyRatesGetter
from src.lib.validators import get_currency_and_date

routes = web.RouteTableDef()


__all__ = ("create_app",)


STORAGE_KEY: web.AppKey[FileStorage | RedisStorage] = web.AppKey("storage")
REDIS_CLIENT_KEY: web.AppKey[Redis] = web.AppKey("redis_client")

settings = get_settings()


@routes.get("/rates/{currency}")
@routes.get("/rates/{currency}/{date}")
async def get_currency_rates(request: web.Request) -> web.Response:
    currency, date = await get_currency_and_date(request=request)
    currency_getter = CurrencyRatesGetter(
        currency=currency,
        for_date=date,
        storage=request.app[STORAGE_KEY],
    )
    currency_info_bytes = await currency_getter.get_currency_info()
    return web.json_response(
        body=currency_info_bytes,
        status=200,
    )


def create_app() -> web.Application:
    app = web.Application()
    app.on_startup.append(initialize_storage)
    app.on_cleanup.append(close_redis_client)
    app.add_routes(routes=routes)

    return app


async def initialize_storage(_app: web.Application) -> None:
    storage_type = settings.api.STORAGE_TYPE
    if storage_type == "file":
        _app[STORAGE_KEY] = FileStorage()
    else:
        redis_client = settings.redis.client
        _app[STORAGE_KEY] = RedisStorage(
            redis_client=redis_client,
        )
        _app[REDIS_CLIENT_KEY] = redis_client


async def close_redis_client(_app: web.Application) -> None:
    redis_client = _app.get(REDIS_CLIENT_KEY, None)
    if redis_client is not None:
        await redis_client.aclose()
        await redis_client.connection_pool.disconnect()
