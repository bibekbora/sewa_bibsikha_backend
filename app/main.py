from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.conf.dependencies import SessionDep
from app.conf.exceptions import DatabaseException
from app.conf.settings import settings
from app.database.connection import db_health_check
from app.routes.v1.routes import router
from app.utils.exception_handlers import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)

app = FastAPI(title=f"{settings.PROJECT_NAME} Backend", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.all_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(router)


@app.get("/", status_code=status.HTTP_200_OK)
async def root() -> dict[str, str]:
    return {"message": f"{settings.PROJECT_NAME} Backend is running!", "status": "healthy"}


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check(session: SessionDep) -> dict[str, str]:
    if not await db_health_check(session):
        raise DatabaseException(detail="Database connection failed")
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": f"{settings.PROJECT_NAME} Backend",
    }
