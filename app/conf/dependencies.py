from typing import Annotated
from uuid import UUID

from fastapi import Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.conf.exceptions import ForbiddenException, UnauthorizedException
from app.conf.security import ACCESS_TOKEN_TYPE, decode_jwt_token
from app.database.connection import get_async_session
from app.models.user import User, UserStatus, UserType
from app.repository.user import UserRepository
from app.schemas.user import UserResponse
from app.storage import StorageProvider, get_storage_provider

bearer_scheme = HTTPBearer(auto_error=False)

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
StorageDep = Annotated[StorageProvider, Depends(get_storage_provider)]
BearerCredentialsDep = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]


async def get_current_user(session: SessionDep, credentials: BearerCredentialsDep) -> UserResponse:
    """
    Resolve the active user from the Bearer access token.
    """
    if credentials is None:
        raise UnauthorizedException(detail="Not authenticated")

    payload = await decode_jwt_token(credentials.credentials)
    if payload.get("type") != ACCESS_TOKEN_TYPE:
        raise UnauthorizedException(detail="Invalid token")

    try:
        user_id = UUID(str(payload.get("sub")))
    except ValueError as e:
        raise UnauthorizedException(detail="Invalid token") from e

    user: User | None = await UserRepository(session).get_by_id(user_id)
    if user is None:
        raise UnauthorizedException(detail="Could not validate credentials")
    if user.status != UserStatus.ACTIVE:
        raise ForbiddenException(detail="User account is inactive", error_code="USER_INACTIVE")

    return UserResponse.model_validate(user)


CurrentUser = Annotated[UserResponse, Depends(get_current_user)]


async def get_current_admin(current_user: CurrentUser) -> UserResponse:
    """
    Ensure the current user is an admin.
    """
    if current_user.user_type != UserType.ADMIN:
        raise ForbiddenException(detail="Admin access required")
    return current_user


CurrentAdmin = Annotated[UserResponse, Depends(get_current_admin)]


class PaginationParams(BaseModel):
    """Pagination input. ``page`` is zero-based internally."""

    page: int
    limit: int


async def pagination_params(
    page: Annotated[int, Query(ge=1, description="Page number (1-based)")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 10,
) -> PaginationParams:
    return PaginationParams(page=page - 1, limit=limit)


PaginationDep = Annotated[PaginationParams, Depends(pagination_params)]
