"""
Project repository
"""

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import col, func, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import SelectOfScalar

from app.conf.exceptions import DatabaseException
from app.conf.logger_config import api_logger
from app.models.project import Project, ProjectCategory, ProjectVisibility


@dataclass(frozen=True, slots=True)
class ProjectFilters:
    """Optional list filters; ``None`` means "do not filter"."""

    category: ProjectCategory | None = None
    visibility: ProjectVisibility | None = None


class ProjectRepository:
    """Project repository. Does not commit; the service layer owns transactions."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository."""
        self.session = session

    @staticmethod
    def _apply_filters[T](statement: SelectOfScalar[T], filters: ProjectFilters) -> SelectOfScalar[T]:
        if filters.category is not None:
            statement = statement.where(Project.category == filters.category)
        if filters.visibility is not None:
            statement = statement.where(Project.visibility == filters.visibility)
        return statement

    async def get_by_id(self, project_id: UUID) -> Project | None:
        """Get a project by ID."""
        try:
            return await self.session.get(Project, project_id)
        except SQLAlchemyError as e:
            api_logger.error("Error getting project by id: %s", e)
            raise DatabaseException(detail="Error getting project") from e

    async def list_projects(self, filters: ProjectFilters, offset: int, limit: int) -> list[Project]:
        """List projects matching ``filters``, newest first."""
        try:
            statement = self._apply_filters(select(Project), filters)
            statement = statement.order_by(col(Project.created_at).desc(), col(Project.id)).offset(offset).limit(limit)
            result = await self.session.exec(statement)
            return list(result.all())
        except SQLAlchemyError as e:
            api_logger.error("Error listing projects: %s", e)
            raise DatabaseException(detail="Error listing projects") from e

    async def count_projects(self, filters: ProjectFilters) -> int:
        """Count projects matching ``filters``."""
        try:
            statement = self._apply_filters(select(func.count()).select_from(Project), filters)
            result = await self.session.exec(statement)
            return result.one()
        except SQLAlchemyError as e:
            api_logger.error("Error counting projects: %s", e)
            raise DatabaseException(detail="Error counting projects") from e

    async def add(self, project: Project) -> Project:
        """Stage a new project and flush it so DB constraints are checked."""
        try:
            self.session.add(project)
            await self.session.flush()
            return project
        except SQLAlchemyError as e:
            api_logger.error("Error adding project: %s", e)
            raise DatabaseException(detail="Error creating project") from e

    async def update(self, project: Project) -> Project:
        """Flush pending changes on an already-loaded project."""
        try:
            self.session.add(project)
            await self.session.flush()
            return project
        except SQLAlchemyError as e:
            api_logger.error("Error updating project: %s", e)
            raise DatabaseException(detail="Error updating project") from e

    async def delete(self, project: Project) -> None:
        """Stage deletion of a project."""
        try:
            await self.session.delete(project)
            await self.session.flush()
        except SQLAlchemyError as e:
            api_logger.error("Error deleting project: %s", e)
            raise DatabaseException(detail="Error deleting project") from e
