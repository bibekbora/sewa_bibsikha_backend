from fastapi import APIRouter, status

from app.conf.dependencies import CurrentUser, SessionDep
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.base import ApiResponse
from app.schemas.user import UserResponse
from app.services.auth import AuthService

authentication_router = APIRouter(
    tags=["Authentication"],
    prefix="/auth",
)


@authentication_router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[LoginResponse],
    summary="Login with email and password",
)
async def login(request: LoginRequest, session: SessionDep) -> ApiResponse[LoginResponse]:
    data = await AuthService(session=session).login(request)
    return ApiResponse(message="Login successful", data=data)


@authentication_router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[UserResponse],
    summary="Get current user",
)
async def current_user(current_user: CurrentUser) -> ApiResponse[UserResponse]:
    return ApiResponse(message="User retrieved successfully", data=current_user)
