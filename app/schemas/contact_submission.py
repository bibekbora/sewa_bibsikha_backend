"""Contact submission request and response contracts."""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import ConfigDict, EmailStr, Field, field_validator

from app.models.contact_submission import ContactStatus
from app.schemas.base import BaseRequestSchema, BaseResponseSchema, PaginatedApiResponse


class ContactSubmissionCreate(BaseRequestSchema):
    """Public form fields. Submission status is assigned by the server."""

    model_config = ConfigDict(extra="forbid")

    name: Annotated[str, Field(min_length=1)]
    organisation: str = ""
    email: EmailStr
    phone: Annotated[str, Field(pattern=r"^(?:|\+?[\d\s-]{8,15})$")] = ""
    sector: Literal["government", "industry", "community", "other"]
    service: Literal["carbon-market", "renewable", "consultancy", "manpower", "logistics", "other"]
    message: Annotated[str, Field(min_length=20)]
    consent: Annotated[bool, Field(strict=True)]

    @field_validator("consent")
    @classmethod
    def require_consent(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Please agree to be contacted regarding your enquiry")
        return value


class ContactStatusUpdate(BaseRequestSchema):
    """Only the feedback status can be changed through the admin API."""

    model_config = ConfigDict(extra="forbid")

    status: ContactStatus


class ContactSubmissionReceipt(BaseResponseSchema):
    """Public acknowledgement after a submission has been saved."""

    id: UUID
    created_at: datetime


class ContactSubmissionResponse(BaseResponseSchema):
    """Full contact details, available only to admins."""

    id: UUID
    name: str
    organisation: str
    email: str
    phone: str
    sector: str
    service: str
    message: str
    consent: bool
    status: ContactStatus
    created_at: datetime
    updated_at: datetime


class ContactSubmissionListResponse(PaginatedApiResponse[ContactSubmissionResponse]):
    # Global counts keep the status filter useful even while searching or paging.
    status_counts: dict[ContactStatus, int]
