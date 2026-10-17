"""
Hero slide schemas
"""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import UploadFile
from pydantic import Field, Json

from app.schemas.base import BaseRequestSchema, BaseResponseSchema

# Keeps one save under Vercel's ~4.5 MB request limit at MAX_HERO_SLIDE_IMAGE_MB per image.
MAX_NEW_IMAGES_PER_SAVE = 4
MAX_HERO_SLIDES = 50


class HeroSlideForm(BaseRequestSchema):
    """Multipart form fields shared by create and update."""

    title: Annotated[str, Field(min_length=1, max_length=60, description="Card title")]
    tag: Annotated[str, Field(min_length=1, max_length=24, description="Short label shown on the card")]
    caption: Annotated[str, Field(min_length=1, max_length=120, description="Text shown below the slider while the card is in front")]


class HeroSlideCreateForm(HeroSlideForm):
    """Create a slide; at least one image is required."""

    images: Annotated[
        list[UploadFile],
        Field(min_length=1, max_length=MAX_NEW_IMAGES_PER_SAVE, description=f"1 to {MAX_NEW_IMAGES_PER_SAVE} images (JPG, PNG or WEBP)"),
    ]


class HeroSlideUpdateForm(HeroSlideForm):
    """Update a slide. Existing images not listed in ``existing_image_ids`` are removed; new ones are appended."""

    # Multipart can't carry nested values, so the kept IDs arrive as a JSON-encoded string.
    existing_image_ids: Annotated[
        Json[list[UUID]],
        Field(validate_default=True, description="JSON array of current image IDs to keep, in display order"),
    ] = "[]"
    images: Annotated[
        list[UploadFile],
        Field(max_length=MAX_NEW_IMAGES_PER_SAVE, description=f"Up to {MAX_NEW_IMAGES_PER_SAVE} new images (JPG, PNG or WEBP)"),
    ] = []


class HeroSlideImageResponse(BaseResponseSchema):
    """An image inside a hero slide."""

    id: UUID
    image_url: str


class HeroSlideResponse(BaseResponseSchema):
    """Hero slide as returned by the admin and public APIs."""

    id: UUID
    title: str
    tag: str
    caption: str
    images: list[HeroSlideImageResponse]
    created_at: datetime
    updated_at: datetime
