import datetime
from pathlib import Path
from unittest import IsolatedAsyncioTestCase
from unittest.mock import (
    MagicMock,
    patch,
)

import aiofiles

from src.lib.cache_storage import FileStorage
from src.lib.coders import json_encoder
from src.lib.types import CurrencyInfo
from tests.data import DataHelper
from tests.helpers import currency_info_response

TARGET_CURRENCIES = ["rub", "aud"]
CURRENT_DATE = datetime.datetime.now(tz=datetime.UTC).date()

data_helper = DataHelper.get_helper()

aiofiles.threadpool.wrap.register(MagicMock)(  # type: ignore[attr-defined]
    lambda *args, **kwargs: aiofiles.threadpool.AsyncBufferedIOBase(*args, **kwargs)  # type: ignore[attr-defined]
)


class TestFileStorage(IsolatedAsyncioTestCase):
    currency_info: CurrencyInfo

    @classmethod
    def setUpClass(cls) -> None:
        cls.currency_info = currency_info_response(
            date=CURRENT_DATE,
            helper=data_helper,
            currency="rub",
            target_currencies=TARGET_CURRENCIES,
        )

    def setUp(self) -> None:
        self.cache_dir = Path("/test")
        self.key = "test_key"
        self.mock_currency_file = MagicMock()
        self.file_storage = FileStorage(cache_dir=self.cache_dir)

    async def test_cache_currency_info(self) -> None:
        currency_info_bytes = json_encoder.encode(self.currency_info)

        with patch("aiofiles.threadpool.sync_open", return_value=self.mock_currency_file):
            res = await self.file_storage.cache_currency_info(
                info=self.currency_info,
                key=self.key,
            )
        self.mock_currency_file.write.assert_called_once_with(currency_info_bytes)
        self.assertEqual(res, currency_info_bytes)

    @patch.object(Path, "exists")
    async def test_read_currency_info(self, path_exists: MagicMock) -> None:
        currency_info_bytes = json_encoder.encode(self.currency_info)

        with patch("aiofiles.threadpool.sync_open", return_value=self.mock_currency_file):
            path_exists.return_value = True
            self.mock_currency_file.read.return_value = json_encoder.encode(self.currency_info)
            res = await self.file_storage.read_currency_info(self.key)

        self.mock_currency_file.read.assert_called_once()
        self.assertEqual(res, currency_info_bytes)

    @patch.object(Path, "exists")
    async def test_read_currency_info_not_found(self, patch_exists: MagicMock) -> None:
        with patch("aiofiles.threadpool.sync_open", return_value=self.mock_currency_file):
            patch_exists.return_value = False
            res = await self.file_storage.read_currency_info(self.key)
        self.mock_currency_file.read.assert_not_called()
        self.assertIsNone(res)
