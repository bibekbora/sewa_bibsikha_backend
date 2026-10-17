from fastapi import APIRouter

from app.routes.v1.public.contacts import public_contacts_router
from app.routes.v1.public.hero_slides import public_hero_slides_router
from app.routes.v1.public.projects import public_projects_router

public_router = APIRouter(prefix="/public")

public_router.include_router(public_projects_router)
public_router.include_router(public_hero_slides_router)
public_router.include_router(public_contacts_router)
