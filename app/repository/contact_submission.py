"""Contact submission persistence. Transactions belong to the service."""

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import col, func, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import SelectOfScalar

from app.conf.exceptions import DatabaseException
from app.conf.logger_config import api_logger
from app.models.contact_submission import ContactStatus, ContactSubmission


@dataclass(frozen=True, slots=True)
class ContactSubmissionFilters:
    status: ContactStatus | None = None
    query: str | None = None


class ContactSubmissionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def _apply_filters[T](statement: SelectOfScalar[T], filters: ContactSubmissionFilters) -> SelectOfScalar[T]:
        if filters.status is not None:
            statement = statement.where(ContactSubmission.status == filters.status)
        if filters.query:
            statement = statement.where(
                or_(
                    col(ContactSubmission.name).icontains(filters.query, autoescape=True),
                    col(ContactSubmission.organisation).icontains(filters.query, autoescape=True),
                    col(ContactSubmission.email).icontains(filters.query, autoescape=True),
                    col(ContactSubmission.phone).icontains(filters.query, autoescape=True),
                    col(ContactSubmission.message).icontains(filters.query, autoescape=True),
                )
            )
        return statement

    async def get_by_id(self, submission_id: UUID) -> ContactSubmission | None:
        try:
            return await self.session.get(ContactSubmission, submission_id)
        except SQLAlchemyError as error:
            api_logger.error("Error getting contact submission (%s)", type(error).__name__)
            raise DatabaseException(detail="Could not retrieve the contact submission") from error

    async def list_submissions(self, filters: ContactSubmissionFilters, offset: int, limit: int) -> list[ContactSubmission]:
        try:
            statement = self._apply_filters(select(ContactSubmission), filters)
            statement = statement.order_by(col(ContactSubmission.created_at).desc(), col(ContactSubmission.id)).offset(offset).limit(limit)
            result = await self.session.exec(statement)
            return list(result.all())
        except SQLAlchemyError as error:
            api_logger.error("Error listing contact submissions (%s)", type(error).__name__)
            raise DatabaseException(detail="Could not list contact submissions") from error

    async def count_submissions(self, filters: ContactSubmissionFilters) -> int:
        try:
            statement = self._apply_filters(select(func.count()).select_from(ContactSubmission), filters)
            result = await self.session.exec(statement)
            return result.one()
        except SQLAlchemyError as error:
            api_logger.error("Error counting contact submissions (%s)", type(error).__name__)
            raise DatabaseException(detail="Could not count contact submissions") from error

    async def count_by_status(self) -> dict[ContactStatus, int]:
        try:
            statement = select(ContactSubmission.status, func.count()).group_by(ContactSubmission.status)
            result = await self.session.exec(statement)
            counts = dict.fromkeys(ContactStatus, 0)
            for status, count in result.all():
                counts[ContactStatus(status)] = count
            return counts
        except SQLAlchemyError as error:
            api_logger.error("Error counting contact statuses (%s)", type(error).__name__)
            raise DatabaseException(detail="Could not count feedback statuses") from error

    async def save(self, submission: ContactSubmission) -> None:
        """Stage a new or updated submission without committing."""
        try:
            self.session.add(submission)
            await self.session.flush()
        except SQLAlchemyError as error:
            api_logger.error("Error saving contact submission (%s)", type(error).__name__)
            raise DatabaseException(detail="Could not save the contact submission") from error
