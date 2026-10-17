from fastapi import APIRouter, Depends

from app.conf.dependencies import get_current_admin
from app.routes.v1.admin.contacts import admin_contacts_router
from app.routes.v1.admin.hero_slides import admin_hero_slides_router
from app.routes.v1.admin.projects import admin_projects_router

admin_router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(get_current_admin)],
)

admin_router.include_router(admin_projects_router)
admin_router.include_router(admin_hero_slides_router)
admin_router.include_router(admin_contacts_router)
