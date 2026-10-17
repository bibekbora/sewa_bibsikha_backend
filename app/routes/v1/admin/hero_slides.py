from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Form, status

from app.conf.dependencies import SessionDep, StorageDep
from app.schemas.base import ApiResponse
from app.schemas.hero_slide import HeroSlideCreateForm, HeroSlideResponse, HeroSlideUpdateForm
from app.services.hero_slide import HeroSlideService

admin_hero_slides_router = APIRouter(
    tags=["Admin - Hero Slides"],
    prefix="/hero-slides",
)


@admin_hero_slides_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[HeroSlideResponse],
    summary="Create a hero slide",
)
async def create_hero_slide(
    form: Annotated[HeroSlideCreateForm, Form(media_type="multipart/form-data")],
    session: SessionDep,
    storage: StorageDep,
) -> ApiResponse[HeroSlideResponse]:
    data = await HeroSlideService(session=session, storage=storage).create_slide(form, form.images)
    return ApiResponse(message="Hero slide created successfully", data=data)


@admin_hero_slides_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[list[HeroSlideResponse]],
    summary="List all hero slides",
)
async def list_hero_slides(session: SessionDep, storage: StorageDep) -> ApiResponse[list[HeroSlideResponse]]:
    data = await HeroSlideService(session=session, storage=storage).list_slides()
    return ApiResponse(message="Hero slides retrieved successfully", data=data)


@admin_hero_slides_router.get(
    "/{slide_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[HeroSlideResponse],
    summary="Get a hero slide",
)
async def get_hero_slide(slide_id: UUID, session: SessionDep, storage: StorageDep) -> ApiResponse[HeroSlideResponse]:
    data = await HeroSlideService(session=session, storage=storage).get_slide(slide_id)
    return ApiResponse(message="Hero slide retrieved successfully", data=data)


@admin_hero_slides_router.put(
    "/{slide_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[HeroSlideResponse],
    summary="Update a hero slide",
)
async def update_hero_slide(
    slide_id: UUID,
    form: Annotated[HeroSlideUpdateForm, Form(media_type="multipart/form-data")],
    session: SessionDep,
    storage: StorageDep,
) -> ApiResponse[HeroSlideResponse]:
    data = await HeroSlideService(session=session, storage=storage).update_slide(slide_id, form, form.existing_image_ids, form.images)
    return ApiResponse(message="Hero slide updated successfully", data=data)


@admin_hero_slides_router.delete(
    "/{slide_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[None],
    summary="Delete a hero slide",
)
async def delete_hero_slide(slide_id: UUID, session: SessionDep, storage: StorageDep) -> ApiResponse[None]:
    await HeroSlideService(session=session, storage=storage).delete_slide(slide_id)
    return ApiResponse(message="Hero slide deleted successfully", data=None)
