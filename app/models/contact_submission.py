from enum import StrEnum
from typing import ClassVar

from sqlalchemy import Text
from sqlmodel import Field

from app.models.base import CreateUpdateModel


class ContactStatus(StrEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    SPAM = "spam"


class ContactSubmission(CreateUpdateModel, table=True):
    """A public contact form submission and its admin feedback status."""

    __tablename__: ClassVar[str] = "contact_submissions"  # type: ignore[assignment]
    name: str = Field(nullable=False)
    organisation: str = Field(default="", nullable=False)
    email: str = Field(nullable=False)
    phone: str = Field(default="", nullable=False)
    sector: str = Field(nullable=False)
    service: str = Field(nullable=False)
    message: str = Field(nullable=False, sa_type=Text)
    consent: bool = Field(default=False, nullable=False)
    status: str = Field(default=ContactStatus.NEW, nullable=False, index=True)
