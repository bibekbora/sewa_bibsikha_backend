from fastapi import APIRouter

from app.conf.settings import settings
from app.routes.v1.auth import authentication_router
from app.routes.v1.users import users_router

router = APIRouter(prefix=settings.API_V1_STR)


router.include_router(authentication_router)
router.include_router(users_router)
