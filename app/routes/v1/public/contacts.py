from fastapi import APIRouter, status

from app.conf.dependencies import SessionDep
from app.schemas.base import ApiResponse
from app.schemas.contact_submission import ContactSubmissionCreate, ContactSubmissionReceipt
from app.services.contact_submission import ContactSubmissionService

public_contacts_router = APIRouter(tags=["Public - Contact Us"], prefix="/contacts")


@public_contacts_router.post("", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[ContactSubmissionReceipt], summary="Submit a contact enquiry")
async def create_submission(request: ContactSubmissionCreate, session: SessionDep) -> ApiResponse[ContactSubmissionReceipt]:
    data = await ContactSubmissionService(session).create_submission(request)
    return ApiResponse(message="Your message has been received", data=data)
