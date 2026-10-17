"""Public contact creation and admin feedback workflows."""

from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.conf.exceptions import DatabaseException, NotFoundException
from app.conf.logger_config import api_logger
from app.models.contact_submission import ContactStatus, ContactSubmission
from app.repository.contact_submission import ContactSubmissionFilters, ContactSubmissionRepository
from app.schemas.base import PaginationPayload
from app.schemas.contact_submission import ContactStatusUpdate, ContactSubmissionCreate, ContactSubmissionListResponse, ContactSubmissionReceipt, ContactSubmissionResponse


class ContactSubmissionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ContactSubmissionRepository(session)

    async def create_submission(self, request: ContactSubmissionCreate) -> ContactSubmissionReceipt:
        submission = ContactSubmission(**request.model_dump(), status=ContactStatus.NEW)
        saved = await self._save_submission(submission)
        return ContactSubmissionReceipt(id=saved.id, created_at=saved.created_at)

    async def list_submissions(self, page: int, limit: int, status: ContactStatus | None = None, query: str | None = None) -> ContactSubmissionListResponse:
        """List matching submissions, newest first. ``page`` is zero-based."""
        filters = ContactSubmissionFilters(status=status, query=query.strip() if query else None)
        submissions = await self.repository.list_submissions(filters, offset=page * limit, limit=limit)
        total_count = await self.repository.count_submissions(filters)
        status_counts = await self.repository.count_by_status()
        return ContactSubmissionListResponse(
            message="Contact submissions retrieved successfully",
            data=[ContactSubmissionResponse.model_validate(submission) for submission in submissions],
            pagination=PaginationPayload(total_count=total_count, page=page, limit=limit),
            status_counts=status_counts,
        )

    async def update_status(self, submission_id: UUID, request: ContactStatusUpdate) -> ContactSubmissionResponse:
        submission = await self.repository.get_by_id(submission_id)
        if submission is None:
            raise NotFoundException(detail="Contact submission not found", error_code="CONTACT_SUBMISSION_NOT_FOUND")
        submission.status = request.status
        return await self._save_submission(submission)

    async def _save_submission(self, submission: ContactSubmission) -> ContactSubmissionResponse:
        try:
            await self.repository.save(submission)
            await self.session.refresh(submission)
            response = ContactSubmissionResponse.model_validate(submission)
            await self.session.commit()
        except SQLAlchemyError as error:
            await self.session.rollback()
            api_logger.error("Error committing contact submission (%s)", type(error).__name__)
            raise DatabaseException(detail="Could not save the contact submission") from error
        except Exception:
            await self.session.rollback()
            raise
        api_logger.info("Contact submission saved: %s", response.id)
        return response
