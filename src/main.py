import logging
import sys

from aiohttp import web

from src.app import create_app
from src.config import get_settings

settings = get_settings()


def main() -> None:
    cache_dir = settings.api.CACHE_DIR
    cache_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        datefmt="%Y:%m:%d %H:%M:%S",
        format=settings.api.DEFAULT_LOG_FORMAT,
    )
    web_app = create_app()
    web.run_app(web_app)


if __name__ == "__main__":
    main()
