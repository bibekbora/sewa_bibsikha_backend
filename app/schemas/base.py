"""
Base schemas
"""

from math import ceil
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator
from pydantic.alias_generators import to_camel


class BaseResponseSchema(BaseModel):
    """Base schema."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class BaseRequestSchema(BaseModel):
    """Base request schema."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class PaginationPayload(BaseModel):
    """Pagination payload."""

    total_count: Annotated[int, Field(description="Total number of items")]
    page: Annotated[int, Field(description="Current page number")]
    limit: Annotated[int, Field(description="Number of items per page")]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_pages(self) -> int:
        """Total number of pages."""
        return ceil(self.total_count / self.limit) if self.limit > 0 else 1

    # chnage page number to +1
    @field_validator("page", mode="before")
    @classmethod
    def page_validator(cls, value: int) -> int:
        """Validate page number."""
        return value + 1

    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class ApiResponse[T](BaseResponseSchema):
    """Standard response envelope."""

    success: Annotated[bool, Field(description="Whether the request succeeded")] = True
    message: Annotated[str, Field(description="Human readable message")]
    data: Annotated[T, Field(description="Response payload")]


class PaginatedApiResponse[T](BaseResponseSchema):
    """Standard response envelope for paginated lists."""

    success: Annotated[bool, Field(description="Whether the request succeeded")] = True
    message: Annotated[str, Field(description="Human readable message")]
    data: Annotated[list[T], Field(description="Page of items")]
    pagination: Annotated[PaginationPayload, Field(description="Pagination metadata")]
