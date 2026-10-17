"""
Project schemas
"""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import UploadFile
from pydantic import Field, Json

from app.models.project import ProjectCategory, ProjectStatus, ProjectVisibility
from app.schemas.base import BaseRequestSchema, BaseResponseSchema

MAX_PROJECT_METRICS = 4


class ProjectMetric(BaseResponseSchema):
    """A headline number shown on the project card, e.g. "3,00,000" / "Households reached"."""

    value: Annotated[str, Field(min_length=1, max_length=20, description="Metric value")]
    label: Annotated[str, Field(min_length=1, max_length=40, description="Metric label")]


class ProjectForm(BaseRequestSchema):
    """Multipart form fields shared by create and update."""

    title: Annotated[str, Field(min_length=1, max_length=120, description="Project title")]
    location: Annotated[str, Field(min_length=1, max_length=120, description="Where the project runs")]
    category: Annotated[ProjectCategory, Field(description="Project category")]
    status: Annotated[ProjectStatus, Field(description="Progress status")] = ProjectStatus.ONGOING
    summary: Annotated[str, Field(min_length=20, max_length=300, description="Short project summary")]
    # Multipart can't carry nested objects, so metrics arrive as a JSON-encoded string.
    metrics: Annotated[
        Json[Annotated[list[ProjectMetric], Field(max_length=MAX_PROJECT_METRICS)]],
        Field(validate_default=True, description=f'JSON array of up to {MAX_PROJECT_METRICS} {{"value", "label"}} objects'),
    ] = "[]"
    visibility: Annotated[ProjectVisibility, Field(description="Whether the project is shown on the public site")] = ProjectVisibility.ACTIVE


class ProjectCreateForm(ProjectForm):
    """Create a project; the image is required."""

    image: Annotated[UploadFile, Field(description="Project image (JPG, PNG or WEBP)")]


class ProjectUpdateForm(ProjectForm):
    """Update a project; omit the image to keep the current one."""

    image: Annotated[UploadFile | None, Field(description="New project image (JPG, PNG or WEBP)")] = None


class ProjectResponse(BaseResponseSchema):
    """Project as returned by the admin and public APIs."""

    id: UUID
    title: str
    location: str
    category: str
    status: str
    summary: str
    metrics: list[ProjectMetric]
    image_url: str
    visibility: str
    created_at: datetime
    updated_at: datetime
