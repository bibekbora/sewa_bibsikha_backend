"""
User schemas
"""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import EmailStr, Field

from app.schemas.base import BaseRequestSchema, BaseResponseSchema


class UserCreateRequest(BaseRequestSchema):
    """Schema for creating an admin user."""

    name: Annotated[str, Field(min_length=1, max_length=255, description="Name of the user")]
    phone_number: Annotated[str, Field(pattern=r"^\+?[0-9]{7,15}$", description="Phone number of the user")]
    email: Annotated[EmailStr, Field(description="Email of the user, used for login")]
    # bcrypt only uses the first 72 bytes of a password.
    password: Annotated[str, Field(min_length=8, max_length=72, description="Password of the user")]


class UserResponse(BaseResponseSchema):
    """Schema for user."""

    id: UUID
    name: str
    email: str
    phone_number: str
    user_type: str
    status: str
    created_at: datetime
