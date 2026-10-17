from typing import Annotated

from fastapi import APIRouter, Query, status

from app.conf.dependencies import PaginationDep, SessionDep, StorageDep
from app.models.project import ProjectCategory, ProjectVisibility
from app.schemas.base import PaginatedApiResponse
from app.schemas.project import ProjectResponse
from app.services.project import ProjectService

public_projects_router = APIRouter(
    tags=["Public - Projects"],
    prefix="/projects",
)


@public_projects_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedApiResponse[ProjectResponse],
    summary="List visible projects",
)
async def list_projects(
    session: SessionDep,
    storage: StorageDep,
    pagination: PaginationDep,
    category: Annotated[ProjectCategory | None, Query(description="Filter by category")] = None,
) -> PaginatedApiResponse[ProjectResponse]:
    data, pagination_payload = await ProjectService(session=session, storage=storage).list_projects(
        page=pagination.page,
        limit=pagination.limit,
        category=category,
        visibility=ProjectVisibility.ACTIVE,
    )
    return PaginatedApiResponse(message="Projects retrieved successfully", data=data, pagination=pagination_payload)
