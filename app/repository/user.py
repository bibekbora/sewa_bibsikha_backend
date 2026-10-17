"""
User repository
"""

from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import col, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.conf.exceptions import DatabaseException
from app.conf.logger_config import api_logger
from app.models.user import User


class UserRepository:
    """User repository. Does not commit; the service layer owns transactions."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository."""
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get a user by ID."""
        try:
            return await self.session.get(User, user_id)
        except SQLAlchemyError as e:
            api_logger.error("Error getting user by id: %s", e)
            raise DatabaseException(detail="Error getting user") from e

    async def get_by_email(self, email: str) -> User | None:
        """Get a user by email."""
        try:
            result = await self.session.exec(select(User).where(User.email == email))
            return result.first()
        except SQLAlchemyError as e:
            api_logger.error("Error getting user by email: %s", e)
            raise DatabaseException(detail="Error getting user") from e

    async def list_users(self, offset: int, limit: int) -> list[User]:
        """List users, newest first."""
        try:
            statement = select(User).order_by(col(User.created_at).desc(), col(User.id)).offset(offset).limit(limit)
            result = await self.session.exec(statement)
            return list(result.all())
        except SQLAlchemyError as e:
            api_logger.error("Error listing users: %s", e)
            raise DatabaseException(detail="Error listing users") from e

    async def count_users(self) -> int:
        """Count all users."""
        try:
            result = await self.session.exec(select(func.count()).select_from(User))
            return result.one()
        except SQLAlchemyError as e:
            api_logger.error("Error counting users: %s", e)
            raise DatabaseException(detail="Error counting users") from e

    async def add(self, user: User) -> User:
        """Stage a new user and flush it so DB constraints are checked."""
        try:
            self.session.add(user)
            await self.session.flush()
            return user
        except IntegrityError:
            raise
        except SQLAlchemyError as e:
            api_logger.error("Error adding user: %s", e)
            raise DatabaseException(detail="Error creating user") from e
