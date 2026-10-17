from fastapi import APIRouter, Depends, status

from app.conf.dependencies import PaginationDep, SessionDep, get_current_admin
from app.schemas.base import ApiResponse, PaginatedApiResponse
from app.schemas.user import UserCreateRequest, UserResponse
from app.services.user import UserService

users_router = APIRouter(
    tags=["Users"],
    prefix="/users",
    dependencies=[Depends(get_current_admin)],
)


@users_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[UserResponse],
    summary="Create a new admin user",
)
async def create_user(request: UserCreateRequest, session: SessionDep) -> ApiResponse[UserResponse]:
    data = await UserService(session=session).create_admin(request)
    return ApiResponse(message="User created successfully", data=data)


@users_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedApiResponse[UserResponse],
    summary="List users",
)
async def list_users(session: SessionDep, pagination: PaginationDep) -> PaginatedApiResponse[UserResponse]:
    data, pagination_payload = await UserService(session=session).list_users(page=pagination.page, limit=pagination.limit)
    return PaginatedApiResponse(message="Users retrieved successfully", data=data, pagination=pagination_payload)
