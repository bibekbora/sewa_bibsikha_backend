"""
Project service
"""

from uuid import UUID

from fastapi import UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession

from app.conf.exceptions import NotFoundException
from app.conf.logger_config import api_logger
from app.conf.settings import settings
from app.models.project import Project, ProjectCategory, ProjectVisibility
from app.repository.project import ProjectFilters, ProjectRepository
from app.schemas.base import PaginationPayload
from app.schemas.project import ProjectForm, ProjectMetric, ProjectResponse
from app.storage import StorageProvider
from app.utils.images import delete_image_quietly, upload_image

PROJECT_IMAGE_PREFIX = "projects"


class ProjectService:
    """Project management workflows."""

    def __init__(self, session: AsyncSession, storage: StorageProvider) -> None:
        self.session = session
        self.storage = storage
        self.project_repository = ProjectRepository(session)

    async def get_project(self, project_id: UUID) -> ProjectResponse:
        """Get a single project (admin)."""
        return self._to_response(await self._get_or_404(project_id))

    async def list_projects(
        self,
        page: int,
        limit: int,
        category: ProjectCategory | None = None,
        visibility: ProjectVisibility | None = None,
    ) -> tuple[list[ProjectResponse], PaginationPayload]:
        """List projects, newest first. ``page`` is zero-based."""
        filters = ProjectFilters(category=category, visibility=visibility)
        projects = await self.project_repository.list_projects(filters, offset=page * limit, limit=limit)
        total_count = await self.project_repository.count_projects(filters)
        pagination = PaginationPayload(total_count=total_count, page=page, limit=limit)
        return [self._to_response(project) for project in projects], pagination

    async def create_project(self, request: ProjectForm, image: UploadFile) -> ProjectResponse:
        """Upload the image, then create the project. The upload is removed again if the insert fails."""
        image_key = await self._upload_image(image)
        project = Project(
            title=request.title,
            location=request.location,
            category=request.category,
            status=request.status,
            summary=request.summary,
            metrics=[metric.model_dump() for metric in request.metrics],
            visibility=request.visibility,
            image_key=image_key,
        )

        try:
            await self.project_repository.add(project)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            await self._delete_image_quietly(image_key)
            raise

        await self.session.refresh(project)
        api_logger.info("Project created: %s", project.id)
        return self._to_response(project)

    async def update_project(self, project_id: UUID, request: ProjectForm, image: UploadFile | None) -> ProjectResponse:
        """Update a project. When a new image is supplied, the old one is deleted after the commit succeeds."""
        project = await self._get_or_404(project_id)
        old_image_key = project.image_key
        new_image_key = await self._upload_image(image) if image is not None else None

        project.title = request.title
        project.location = request.location
        project.category = request.category
        project.status = request.status
        project.summary = request.summary
        project.metrics = [metric.model_dump() for metric in request.metrics]
        project.visibility = request.visibility
        if new_image_key is not None:
            project.image_key = new_image_key

        try:
            await self.project_repository.update(project)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            if new_image_key is not None:
                await self._delete_image_quietly(new_image_key)
            raise

        if new_image_key is not None:
            await self._delete_image_quietly(old_image_key)

        await self.session.refresh(project)
        api_logger.info("Project updated: %s", project.id)
        return self._to_response(project)

    async def delete_project(self, project_id: UUID) -> None:
        """Delete a project and then its image."""
        project = await self._get_or_404(project_id)
        image_key = project.image_key

        try:
            await self.project_repository.delete(project)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        await self._delete_image_quietly(image_key)
        api_logger.info("Project deleted: %s", project_id)

    async def _get_or_404(self, project_id: UUID) -> Project:
        project = await self.project_repository.get_by_id(project_id)
        if project is None:
            raise NotFoundException(detail="Project not found", error_code="PROJECT_NOT_FOUND")
        return project

    async def _upload_image(self, image: UploadFile) -> str:
        return await upload_image(self.storage, image, PROJECT_IMAGE_PREFIX, settings.MAX_IMAGE_UPLOAD_MB)

    async def _delete_image_quietly(self, key: str) -> None:
        await delete_image_quietly(self.storage, key)

    def _to_response(self, project: Project) -> ProjectResponse:
        return ProjectResponse(
            id=project.id,
            title=project.title,
            location=project.location,
            category=project.category,
            status=project.status,
            summary=project.summary,
            metrics=[ProjectMetric.model_validate(metric) for metric in project.metrics or []],
            image_url=self.storage.get_url(project.image_key),
            visibility=project.visibility,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )
