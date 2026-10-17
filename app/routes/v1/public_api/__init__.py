from fastapi import APIRouter

from app.routes.v1.public_api.contacts import public_contacts_router
from app.routes.v1.public_api.hero_slides import public_hero_slides_router
from app.routes.v1.public_api.projects import public_projects_router

# Vercel excludes **/public/** from Python bundles; keep this package named public_api.
public_router = APIRouter(prefix="/public")

public_router.include_router(public_projects_router)
public_router.include_router(public_hero_slides_router)
public_router.include_router(public_contacts_router)
