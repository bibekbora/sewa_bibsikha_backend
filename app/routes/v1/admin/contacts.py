from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.conf.dependencies import PaginationDep, SessionDep
from app.models.contact_submission import ContactStatus
from app.schemas.base import ApiResponse
from app.schemas.contact_submission import ContactStatusUpdate, ContactSubmissionListResponse, ContactSubmissionResponse
from app.services.contact_submission import ContactSubmissionService

admin_contacts_router = APIRouter(tags=["Admin - Contact Us"], prefix="/contacts")


@admin_contacts_router.get("", status_code=status.HTTP_200_OK, response_model=ContactSubmissionListResponse, summary="List contact submissions")
async def list_submissions(
    session: SessionDep,
    pagination: PaginationDep,
    feedback_status: Annotated[ContactStatus | None, Query(alias="status", description="Filter by feedback status")] = None,
    q: Annotated[str | None, Query(description="Search name, organisation, email, phone or message")] = None,
) -> ContactSubmissionListResponse:
    return await ContactSubmissionService(session).list_submissions(page=pagination.page, limit=pagination.limit, status=feedback_status, query=q)


@admin_contacts_router.patch("/{submission_id}/status", status_code=status.HTTP_200_OK, response_model=ApiResponse[ContactSubmissionResponse], summary="Update feedback status")
async def update_status(submission_id: UUID, request: ContactStatusUpdate, session: SessionDep) -> ApiResponse[ContactSubmissionResponse]:
    data = await ContactSubmissionService(session).update_status(submission_id, request)
    return ApiResponse(message="Feedback status updated successfully", data=data)
