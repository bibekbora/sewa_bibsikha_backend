"""
Hero slide service
"""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession

from app.conf.exceptions import BadRequestException, NotFoundException
from app.conf.logger_config import api_logger
from app.conf.settings import settings
from app.models.hero_slide import HeroSlide, HeroSlideImage
from app.repository.hero_slide import HeroSlideRepository
from app.schemas.hero_slide import MAX_HERO_SLIDES, HeroSlideForm, HeroSlideImageResponse, HeroSlideResponse
from app.storage import StorageProvider
from app.utils.images import delete_image_quietly, upload_image

HERO_SLIDE_IMAGE_PREFIX = "hero-slides"


class HeroSlideService:
    """Hero slider management workflows."""

    def __init__(self, session: AsyncSession, storage: StorageProvider) -> None:
        self.session = session
        self.storage = storage
        self.hero_slide_repository = HeroSlideRepository(session)

    async def get_slide(self, slide_id: UUID) -> HeroSlideResponse:
        """Get a single slide (admin)."""
        return self._to_response(await self._get_or_404(slide_id))

    async def list_slides(self) -> list[HeroSlideResponse]:
        """List slides, oldest first, up to ``MAX_HERO_SLIDES``."""
        slides = await self.hero_slide_repository.list_slides(limit=MAX_HERO_SLIDES)
        return [self._to_response(slide) for slide in slides]

    async def create_slide(self, request: HeroSlideForm, images: list[UploadFile]) -> HeroSlideResponse:
        """Upload the images, then create the slide. The uploads are removed again if the insert fails."""
        image_keys = await self._upload_images(images)
        slide = HeroSlide(
            title=request.title,
            tag=request.tag,
            caption=request.caption,
            images=[HeroSlideImage(image_key=key, position=position) for position, key in enumerate(image_keys)],
        )

        try:
            await self.hero_slide_repository.add(slide)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            await self._delete_images_quietly(image_keys)
            raise

        await self.session.refresh(slide)
        api_logger.info("Hero slide created: %s", slide.id)
        return self._to_response(slide)

    async def update_slide(self, slide_id: UUID, request: HeroSlideForm, existing_image_ids: list[UUID], new_images: list[UploadFile]) -> HeroSlideResponse:
        """
        Update a slide. Kept images follow the order of ``existing_image_ids`` and new images are appended.
        Images left out are deleted from storage after the commit succeeds.
        """
        slide = await self._get_or_404(slide_id)
        current_images = {image.id: image for image in slide.images}
        kept_ids = list(dict.fromkeys(existing_image_ids))

        if any(image_id not in current_images for image_id in kept_ids):
            raise BadRequestException(
                detail="Some of the images no longer belong to this slide. Reload and try again.",
                error_code="INVALID_IMAGE_IDS",
                details=[{"field": "existingImageIds", "message": "Unknown image ID"}],
            )
        if not kept_ids and not new_images:
            raise BadRequestException(
                detail="Add at least one image",
                error_code="IMAGES_REQUIRED",
                details=[{"field": "images", "message": "Add at least one image"}],
            )

        new_image_keys = await self._upload_images(new_images)
        removed_image_keys = [image.image_key for image_id, image in current_images.items() if image_id not in kept_ids]

        kept_images = [current_images[image_id] for image_id in kept_ids]
        for position, image in enumerate(kept_images):
            image.position = position
        added_images = [HeroSlideImage(image_key=key, position=len(kept_images) + offset) for offset, key in enumerate(new_image_keys)]

        slide.title = request.title
        slide.tag = request.tag
        slide.caption = request.caption
        slide.images = kept_images + added_images
        # Image-only edits don't touch the slide row, so its onupdate timestamp wouldn't fire.
        slide.updated_at = datetime.now(UTC)

        try:
            await self.hero_slide_repository.update(slide)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            await self._delete_images_quietly(new_image_keys)
            raise

        await self._delete_images_quietly(removed_image_keys)
        await self.session.refresh(slide)
        api_logger.info("Hero slide updated: %s", slide.id)
        return self._to_response(slide)

    async def delete_slide(self, slide_id: UUID) -> None:
        """Delete a slide with its images, then remove the image files."""
        slide = await self._get_or_404(slide_id)
        image_keys = [image.image_key for image in slide.images]

        try:
            await self.hero_slide_repository.delete(slide)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        await self._delete_images_quietly(image_keys)
        api_logger.info("Hero slide deleted: %s", slide_id)

    async def _get_or_404(self, slide_id: UUID) -> HeroSlide:
        slide = await self.hero_slide_repository.get_by_id(slide_id)
        if slide is None:
            raise NotFoundException(detail="Hero slide not found", error_code="HERO_SLIDE_NOT_FOUND")
        return slide

    async def _upload_images(self, images: list[UploadFile]) -> list[str]:
        """Upload all images or none: if one fails, the ones already stored are removed."""
        keys: list[str] = []
        try:
            for image in images:
                keys.append(await upload_image(self.storage, image, HERO_SLIDE_IMAGE_PREFIX, settings.MAX_HERO_SLIDE_IMAGE_MB))
        except Exception:
            await self._delete_images_quietly(keys)
            raise
        return keys

    async def _delete_images_quietly(self, keys: list[str]) -> None:
        for key in keys:
            await delete_image_quietly(self.storage, key)

    def _to_response(self, slide: HeroSlide) -> HeroSlideResponse:
        return HeroSlideResponse(
            id=slide.id,
            title=slide.title,
            tag=slide.tag,
            caption=slide.caption,
            images=[HeroSlideImageResponse(id=image.id, image_url=self.storage.get_url(image.image_key)) for image in slide.images],
            created_at=slide.created_at,
            updated_at=slide.updated_at,
        )
