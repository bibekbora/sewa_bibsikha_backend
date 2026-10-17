from enum import StrEnum
from typing import ClassVar

from sqlmodel import Field

from app.models.base import CreateUpdateModel


class UserType(StrEnum):
    ADMIN = "admin"


class UserStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class User(CreateUpdateModel, table=True):
    __tablename__: ClassVar[str] = "users"  # type: ignore[assignment]
    name: str = Field(nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    password: str = Field(nullable=False)
    phone_number: str = Field(nullable=False)
    status: str = Field(nullable=False, default=UserStatus.ACTIVE)
    user_type: str = Field(nullable=False, default=UserType.ADMIN)
