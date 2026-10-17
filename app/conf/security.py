from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext
from starlette.concurrency import run_in_threadpool

from app.conf.exceptions import UnauthorizedException
from app.conf.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_TYPE = "access"  # noqa: S105
REFRESH_TOKEN_TYPE = "refresh"  # noqa: S105


async def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    """
    Create an access token for the user.
    """
    expire = datetime.now(UTC) + expires_delta
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": ACCESS_TOKEN_TYPE,
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def create_refresh_token(subject: str | Any, expires_delta: timedelta) -> str:
    """
    Create a refresh token for admin and user.
    """
    expire = datetime.now(UTC) + expires_delta
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": REFRESH_TOKEN_TYPE,
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def decode_jwt_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT token.
    Returns the payload if valid.
    Raises UnauthorizedException if invalid/expired.
    """
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError as err:
        raise UnauthorizedException(detail="Token has expired") from err
    except jwt.InvalidTokenError as err:
        raise UnauthorizedException(detail="Invalid token") from err


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hashed password.
    """
    return bool(await run_in_threadpool(pwd_context.verify, plain_password, hashed_password))


async def get_password_hash(password: str) -> str:
    """
    Get a password hash.
    """
    return str(await run_in_threadpool(pwd_context.hash, password))
