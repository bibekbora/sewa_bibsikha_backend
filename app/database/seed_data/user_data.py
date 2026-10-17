"""
User data
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.conf.logger_config import api_logger
from app.conf.security import get_password_hash
from app.conf.settings import settings
from app.models.user import User

SUPER_ADMIN_EMAIL = settings.SUPER_ADMIN_EMAIL
SUPER_ADMIN_PASSWORD = settings.SUPER_ADMIN_PASSWORD


async def seed_admin_user(async_session: AsyncSession) -> None:
    """
    Seed the admin user into the database.
    """
    # check if admin user already exists
    result = await async_session.execute(select(User).where(User.email == SUPER_ADMIN_EMAIL))
    admin_user = result.scalar_one_or_none()
    if admin_user:
        api_logger.info("Admin user already exists")
        return

    # Hash the password
    hashed_password = await get_password_hash(SUPER_ADMIN_PASSWORD)
    user = User(
        email=SUPER_ADMIN_EMAIL,
        password=hashed_password,
        user_type="admin",
        status="active",
        name="Super Admin",
        phone_number="1234567890",
    )
    async_session.add(user)
    await async_session.commit()


async def seed_all(async_session: AsyncSession) -> None:
    """
    Seed all default data into the database.
    """
    try:
        api_logger.info("Seeding all default data")
        api_logger.info("Seeding user data")
        await seed_admin_user(async_session)
        api_logger.info("All default data seeded")
    except Exception as e:
        api_logger.error(e)
        raise e
    finally:
        api_logger.info("All default data seeding completed")
