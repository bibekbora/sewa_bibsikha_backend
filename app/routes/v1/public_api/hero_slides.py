from fastapi import APIRouter, status

from app.conf.dependencies import SessionDep, StorageDep
from app.schemas.base import ApiResponse
from app.schemas.hero_slide import HeroSlideResponse
from app.services.hero_slide import HeroSlideService

public_hero_slides_router = APIRouter(
    tags=["Public - Hero Slides"],
    prefix="/hero-slides",
)


@public_hero_slides_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[list[HeroSlideResponse]],
    summary="List hero slides for the home page",
)
async def list_hero_slides(session: SessionDep, storage: StorageDep) -> ApiResponse[list[HeroSlideResponse]]:
    data = await HeroSlideService(session=session, storage=storage).list_slides()
    return ApiResponse(message="Hero slides retrieved successfully", data=data)
