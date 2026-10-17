import asyncio

import app.database.base  # noqa: F401  # Ensure all models are imported so relationships configure
from app.conf.logger_config import api_logger
from app.database.connection import async_session_factory
from app.database.seed_data.user_data import seed_all as seed_user_data


async def init() -> None:
    """Create initial data in the database."""
    try:
        async with async_session_factory() as async_session:
            await seed_user_data(async_session)
    except Exception as e:
        api_logger.error(e)
        raise e
    finally:
        api_logger.info("Initial data creation completed")


def main() -> None:
    """Main function to create initial data."""
    try:
        api_logger.info("Creating initial data")
        asyncio.run(init())
        api_logger.info("Initial data created")
    except Exception as e:
        api_logger.error(e)
        raise e
    finally:
        api_logger.info("Initial data creation completed")


if __name__ == "__main__":
    main()
