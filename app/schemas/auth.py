"""
Auth schemas
"""

from typing import Annotated

from pydantic import EmailStr, Field

from app.schemas.base import BaseRequestSchema, BaseResponseSchema
from app.schemas.user import UserResponse


class LoginRequest(BaseRequestSchema):
    """Schema for login request."""

    email: Annotated[EmailStr, Field(description="Email of the user")]
    password: Annotated[str, Field(min_length=1, description="Password of the user")]


class LoginResponse(BaseResponseSchema):
    """Schema for login response."""

    access_token: Annotated[str, Field(description="JWT access token")]
    token_type: Annotated[str, Field(description="Token type for the Authorization header")] = "bearer"  # noqa: S105
    expires_in: Annotated[int, Field(description="Access token lifetime in seconds")]
    user: Annotated[UserResponse, Field(description="Logged in user")]
