from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.conf.logger_config import api_logger
from app.conf.settings import settings

DATABASE_URL = str(settings.SQLALCHEMY_DATABASE_URI)


# Use connection pooling locally; disable pooling in non-local (serverless) to avoid
# sharing connections across per-request event loops/threads.
if settings.ENVIRONMENT == "local":
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True,
    )
else:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        pool_size=10,  # Number of connections to keep open in the pool
        max_overflow=20,  # Max additional connections to open under load
        pool_timeout=30,  # Seconds to wait before giving up on getting a connection
        pool_recycle=1800,  # Recycle connections after 30 minutes (1800s)
        pool_pre_ping=True,  # Checks if a connection is alive before using it
    )

# Async Session Factory
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Async session generator
async def get_async_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as async_session:
        yield async_session


# Health check
async def db_health_check(session: AsyncSession):
    try:
        await session.exec(select(1))
        # await seed_data(session)
        return True
    except Exception:
        api_logger.exception("Database health check failed")
        return False
