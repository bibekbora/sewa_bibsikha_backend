from typing import ClassVar
from uuid import UUID

from sqlmodel import Field, Relationship

from app.models.base import CreateUpdateModel


class HeroSlide(CreateUpdateModel, table=True):
    """A card in the home page hero slider. Slides are shown oldest first."""

    __tablename__: ClassVar[str] = "hero_slides"  # type: ignore[assignment]
    title: str = Field(nullable=False, max_length=60)
    tag: str = Field(nullable=False, max_length=24)
    caption: str = Field(nullable=False, max_length=120)
    images: list[HeroSlideImage] = Relationship(
        back_populates="slide",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "order_by": "HeroSlideImage.position",
            "cascade": "all, delete-orphan",
        },
    )


class HeroSlideImage(CreateUpdateModel, table=True):
    """An image that rotates inside a hero slide, in ``position`` order."""

    __tablename__: ClassVar[str] = "hero_slide_images"  # type: ignore[assignment]
    slide_id: UUID = Field(foreign_key="hero_slides.id", ondelete="CASCADE", nullable=False, index=True)
    # Provider-agnostic object key (e.g. "hero-slides/<uuid>.webp"); the storage adapter builds the public URL.
    image_key: str = Field(nullable=False)
    position: int = Field(nullable=False, default=0)
    slide: HeroSlide | None = Relationship(back_populates="images")
