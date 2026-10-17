"""
User service
"""

from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.conf.exceptions import ConflictException
from app.conf.logger_config import api_logger
from app.conf.security import get_password_hash
from app.models.user import User, UserStatus, UserType
from app.repository.user import UserRepository
from app.schemas.base import PaginationPayload
from app.schemas.user import UserCreateRequest, UserResponse


class UserService:
    """User management workflows."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repository = UserRepository(session)

    async def create_admin(self, request: UserCreateRequest) -> UserResponse:
        """Create a new admin user."""
        email = request.email.lower()
        if await self.user_repository.get_by_email(email) is not None:
            raise ConflictException(detail="A user with this email already exists", error_code="USER_ALREADY_EXISTS")

        user = User(
            name=request.name,
            email=email,
            phone_number=request.phone_number,
            password=await get_password_hash(request.password),
            user_type=UserType.ADMIN,
            status=UserStatus.ACTIVE,
        )

        try:
            await self.user_repository.add(user)
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise ConflictException(detail="A user with this email already exists", error_code="USER_ALREADY_EXISTS") from e
        except Exception:
            await self.session.rollback()
            raise

        await self.session.refresh(user)
        api_logger.info("Admin user created: %s", user.id)
        return UserResponse.model_validate(user)

    async def list_users(self, page: int, limit: int) -> tuple[list[UserResponse], PaginationPayload]:
        """List users. ``page`` is zero-based."""
        users = await self.user_repository.list_users(offset=page * limit, limit=limit)
        total_count = await self.user_repository.count_users()
        pagination = PaginationPayload(total_count=total_count, page=page, limit=limit)
        return [UserResponse.model_validate(user) for user in users], pagination
