from enum import StrEnum
from typing import ClassVar

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from app.models.base import CreateUpdateModel


class ProjectCategory(StrEnum):
    CARBON = "carbon"
    ENERGY = "energy"
    CONSULTANCY = "consultancy"
    OPERATIONS = "operations"


class ProjectStatus(StrEnum):
    ONGOING = "ongoing"
    COMPLETED = "completed"


class ProjectVisibility(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Project(CreateUpdateModel, table=True):
    __tablename__: ClassVar[str] = "projects"  # type: ignore[assignment]
    title: str = Field(nullable=False, max_length=120)
    location: str = Field(nullable=False, max_length=120)
    category: str = Field(nullable=False, index=True)
    status: str = Field(nullable=False, default=ProjectStatus.ONGOING)
    summary: str = Field(nullable=False, max_length=300)
    # List of {"value": str, "label": str}, at most 4 items (enforced by the request schema).
    metrics: list[dict[str, str]] | None = Field(
        default_factory=list,
        nullable=True,
        sa_type=JSONB,  # type: ignore[arg-type]
        sa_column_kwargs={"server_default": text("'[]'::jsonb")},
    )
    # Provider-agnostic object key (e.g. "projects/<uuid>.webp"); the storage adapter builds the public URL.
    image_key: str = Field(nullable=False)
    # Only "active" projects are returned by the public endpoints.
    visibility: str = Field(nullable=False, default=ProjectVisibility.ACTIVE, index=True)
