import asyncio
import logging

from sqlalchemy import text
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.conf.logger_config import api_logger
from app.database.connection import async_session_factory

MAX_TRIES: int = 60 * 5  # 5 minutes
WAIT_SECONDS: int = 1


@retry(
    stop=stop_after_attempt(MAX_TRIES),
    wait=wait_fixed(WAIT_SECONDS),
    before=before_log(api_logger, logging.INFO),
    after=after_log(api_logger, logging.WARN),
)
async def init() -> None:
    """Wait for the DB to be ready and log all existing tables."""
    try:
        async with async_session_factory() as async_session:
            result = await async_session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"))
            tables = [row[0] for row in result]
            api_logger.info(f"Existing tables: {tables}")
    except Exception as e:
        api_logger.error(e)
        raise e


def main() -> None:
    """Main function to initialize the service."""
    try:
        api_logger.info("Initializing service")
        asyncio.run(init())
        api_logger.info("Service finished initializing")
    except Exception as e:
        api_logger.error(e)
        raise e
    finally:
        api_logger.info("Service finished initializing")
