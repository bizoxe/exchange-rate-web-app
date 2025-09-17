import asyncio
import datetime
from unittest import IsolatedAsyncioTestCase

from fakeredis import FakeAsyncRedis

from src.lib.cache_storage import RedisStorage
from src.lib.coders import json_encoder
from src.lib.types import CurrencyInfo
from tests.data import DataHelper
from tests.helpers import currency_info_response

TARGET_CURRENCIES = ["rub", "aud"]
CURRENT_DATE = datetime.datetime.now(tz=datetime.UTC).date()

data_helper = DataHelper.get_helper()


class TestRedisStorage(IsolatedAsyncioTestCase):
    currency_info: CurrencyInfo
    redis_client: FakeAsyncRedis
    redis_storage: RedisStorage
    key: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.currency_info = currency_info_response(
            date=CURRENT_DATE,
            helper=data_helper,
            currency="rub",
            target_currencies=TARGET_CURRENCIES,
        )
        cls.redis_client = FakeAsyncRedis()
        cls.redis_storage = RedisStorage(
            redis_client=cls.redis_client,
            expire=60,
        )
        cls.key = "test_key"

    @classmethod
    def tearDownClass(cls) -> None:
        """Closes Redis connection pool to avoid ResourceWarning.

        FakeAsyncRedis may leave open connections (FakeConnection),
        causing: ResourceWarning: unclosed Connection (...)

        Manually disconnecting the connection pool ensures all
        async Redis connections are properly closed after tests.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop=loop)
        loop.run_until_complete(cls.redis_client.connection_pool.disconnect())
        loop.close()

    async def asyncTearDown(self) -> None:
        await self.redis_storage._redis_client.delete(self.key)  # noqa: SLF001

    async def test_cache_currency_info(self) -> None:
        currency_info_bytes = json_encoder.encode(self.currency_info)
        res = await self.redis_storage.cache_currency_info(
            info=self.currency_info,
            key=self.key,
        )
        self.assertEqual(res, currency_info_bytes)

    async def test_read_currency_info(self) -> None:
        currency_info_bytes = json_encoder.encode(self.currency_info)
        await self.redis_storage._redis_client.set(  # noqa: SLF001
            name=self.key,
            value=currency_info_bytes,
        )
        res = await self.redis_storage.read_currency_info(key=self.key)
        self.assertEqual(res, currency_info_bytes)
        await self.redis_storage._redis_client.delete(self.key)  # noqa: SLF001
        res_none = await self.redis_storage.read_currency_info(self.key)
        self.assertIsNone(res_none)
