"""
Auth service
"""

from datetime import timedelta

from sqlmodel.ext.asyncio.session import AsyncSession

from app.conf.exceptions import ForbiddenException, UnauthorizedException
from app.conf.security import create_access_token, verify_password
from app.conf.settings import settings
from app.models.user import UserStatus
from app.repository.user import UserRepository
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.user import UserResponse


class AuthService:
    """Authentication workflows."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repository = UserRepository(session)

    async def login(self, request: LoginRequest) -> LoginResponse:
        """Validate credentials and issue an access token."""
        user = await self.user_repository.get_by_email(request.email.lower())
        # Same message for unknown email and wrong password to avoid account enumeration.
        if user is None or not await verify_password(request.password, user.password):
            raise UnauthorizedException(detail="Invalid email or password", error_code="INVALID_CREDENTIALS")

        if user.status != UserStatus.ACTIVE:
            raise ForbiddenException(detail="User account is inactive", error_code="USER_INACTIVE")

        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await create_access_token(subject=user.id, expires_delta=expires_delta)

        return LoginResponse(
            access_token=access_token,
            expires_in=int(expires_delta.total_seconds()),
            user=UserResponse.model_validate(user),
        )
