"""
Hero slide repository
"""

from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.conf.exceptions import DatabaseException
from app.conf.logger_config import api_logger
from app.models.hero_slide import HeroSlide


class HeroSlideRepository:
    """Hero slide repository. Images load with their slide. Does not commit; the service layer owns transactions."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository."""
        self.session = session

    async def get_by_id(self, slide_id: UUID) -> HeroSlide | None:
        """Get a slide by ID."""
        try:
            return await self.session.get(HeroSlide, slide_id)
        except SQLAlchemyError as e:
            api_logger.error("Error getting hero slide by id: %s", e)
            raise DatabaseException(detail="Error getting hero slide") from e

    async def list_slides(self, limit: int) -> list[HeroSlide]:
        """List slides, oldest first."""
        try:
            statement = select(HeroSlide).order_by(col(HeroSlide.created_at), col(HeroSlide.id)).limit(limit)
            result = await self.session.exec(statement)
            return list(result.all())
        except SQLAlchemyError as e:
            api_logger.error("Error listing hero slides: %s", e)
            raise DatabaseException(detail="Error listing hero slides") from e

    async def add(self, slide: HeroSlide) -> HeroSlide:
        """Stage a new slide with its images and flush it so DB constraints are checked."""
        try:
            self.session.add(slide)
            await self.session.flush()
            return slide
        except SQLAlchemyError as e:
            api_logger.error("Error adding hero slide: %s", e)
            raise DatabaseException(detail="Error creating hero slide") from e

    async def update(self, slide: HeroSlide) -> HeroSlide:
        """Flush pending changes on an already-loaded slide, including added or removed images."""
        try:
            self.session.add(slide)
            await self.session.flush()
            return slide
        except SQLAlchemyError as e:
            api_logger.error("Error updating hero slide: %s", e)
            raise DatabaseException(detail="Error updating hero slide") from e

    async def delete(self, slide: HeroSlide) -> None:
        """Stage deletion of a slide and its images."""
        try:
            await self.session.delete(slide)
            await self.session.flush()
        except SQLAlchemyError as e:
            api_logger.error("Error deleting hero slide: %s", e)
            raise DatabaseException(detail="Error deleting hero slide") from e
