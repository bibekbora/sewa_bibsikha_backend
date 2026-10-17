from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Form, Query, status

from app.conf.dependencies import PaginationDep, SessionDep, StorageDep
from app.models.project import ProjectCategory, ProjectVisibility
from app.schemas.base import ApiResponse, PaginatedApiResponse
from app.schemas.project import ProjectCreateForm, ProjectResponse, ProjectUpdateForm
from app.services.project import ProjectService

admin_projects_router = APIRouter(
    tags=["Admin - Projects"],
    prefix="/projects",
)


@admin_projects_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[ProjectResponse],
    summary="Create a project",
)
async def create_project(
    form: Annotated[ProjectCreateForm, Form(media_type="multipart/form-data")],
    session: SessionDep,
    storage: StorageDep,
) -> ApiResponse[ProjectResponse]:
    data = await ProjectService(session=session, storage=storage).create_project(form, form.image)
    return ApiResponse(message="Project created successfully", data=data)


@admin_projects_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedApiResponse[ProjectResponse],
    summary="List all projects",
)
async def list_projects(
    session: SessionDep,
    storage: StorageDep,
    pagination: PaginationDep,
    category: Annotated[ProjectCategory | None, Query(description="Filter by category")] = None,
    visibility: Annotated[ProjectVisibility | None, Query(description="Filter by visibility")] = None,
) -> PaginatedApiResponse[ProjectResponse]:
    data, pagination_payload = await ProjectService(session=session, storage=storage).list_projects(
        page=pagination.page,
        limit=pagination.limit,
        category=category,
        visibility=visibility,
    )
    return PaginatedApiResponse(message="Projects retrieved successfully", data=data, pagination=pagination_payload)


@admin_projects_router.get(
    "/{project_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[ProjectResponse],
    summary="Get a project",
)
async def get_project(project_id: UUID, session: SessionDep, storage: StorageDep) -> ApiResponse[ProjectResponse]:
    data = await ProjectService(session=session, storage=storage).get_project(project_id)
    return ApiResponse(message="Project retrieved successfully", data=data)


@admin_projects_router.put(
    "/{project_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[ProjectResponse],
    summary="Update a project",
)
async def update_project(
    project_id: UUID,
    form: Annotated[ProjectUpdateForm, Form(media_type="multipart/form-data")],
    session: SessionDep,
    storage: StorageDep,
) -> ApiResponse[ProjectResponse]:
    data = await ProjectService(session=session, storage=storage).update_project(project_id, form, form.image)
    return ApiResponse(message="Project updated successfully", data=data)


@admin_projects_router.delete(
    "/{project_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[None],
    summary="Delete a project",
)
async def delete_project(project_id: UUID, session: SessionDep, storage: StorageDep) -> ApiResponse[None]:
    await ProjectService(session=session, storage=storage).delete_project(project_id)
    return ApiResponse(message="Project deleted successfully", data=None)
