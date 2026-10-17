import secrets
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    computed_field,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "7ed049e344f73f399ba1f7868cf9494f4b13347ecce02a8e463feb32507b73a5" if ENVIRONMENT == "local" else secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    FRONTEND_HOST: str = "http://localhost:5173"

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [self.FRONTEND_HOST]

    # Postgres
    PROJECT_NAME: str
    POSTGRES_URL: str
    POSTGRES_USER: str
    POSTGRES_HOST: str
    POSTGRES_PASSWORD: str
    POSTGRES_DATABASE: str
    POSTGRES_PORT: int = 5432

    SUPER_ADMIN_EMAIL: str
    SUPER_ADMIN_PASSWORD: str

    # Gmail SMTP
    # GMAIL_USERNAME: str
    # GMAIL_PASSWORD: str

    # AWS
    # AWS_ACCESS_KEY_ID: str
    # AWS_SECRET_KEY_ID: str
    # AWS_REGION: str = "us-east-1"
    # AWS_S3_BUCKET_NAME: str = "kazirangaais3"
    # AWS_S3_BASE_URL: str = "https://kazirangaais3.s3.ap-south-1.amazonaws.com/"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> MultiHostUrl:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DATABASE,
        )


settings = Settings()  # type: ignore
