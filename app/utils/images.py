"""
Image upload helpers shared by services that store images
"""

import uuid

from fastapi import UploadFile

from app.conf.exceptions import BadRequestException, StorageException
from app.conf.logger_config import api_logger
from app.storage import StorageProvider

# Detected from file signatures; the client-supplied content type is not trusted.
IMAGE_EXTENSIONS = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


def detect_image_type(data: bytes) -> str | None:
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


async def upload_image(storage: StorageProvider, image: UploadFile, prefix: str, max_mb: int) -> str:
    """Validate ``image`` and store it under ``<prefix>/<uuid>.<ext>``. Returns the object key."""
    max_bytes = max_mb * 1024 * 1024
    data = await image.read(max_bytes + 1)
    if not data:
        raise BadRequestException(detail="Image file is empty", error_code="INVALID_IMAGE")
    if len(data) > max_bytes:
        raise BadRequestException(detail=f"Image must be {max_mb} MB or smaller", error_code="IMAGE_TOO_LARGE")

    content_type = detect_image_type(data)
    if content_type is None:
        raise BadRequestException(detail="Upload a JPG, PNG or WEBP image", error_code="INVALID_IMAGE")

    key = f"{prefix}/{uuid.uuid4()}.{IMAGE_EXTENSIONS[content_type]}"
    await storage.upload(key, data, content_type)
    return key


async def delete_image_quietly(storage: StorageProvider, key: str) -> None:
    """Best-effort cleanup: a leftover object must not fail an otherwise successful request."""
    try:
        await storage.delete(key)
    except StorageException:
        api_logger.warning("Orphaned image left in storage: %s", key)
