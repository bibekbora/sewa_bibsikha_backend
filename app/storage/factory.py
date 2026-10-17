"""
Storage provider factory
"""

from functools import lru_cache

from app.conf.settings import settings
from app.storage.base import StorageProvider


@lru_cache
def get_storage_provider() -> StorageProvider:
    """Build the provider selected by ``STORAGE_PROVIDER``. Cached so clients are created once per process."""
    match settings.STORAGE_PROVIDER:
        case "s3":
            from app.storage.s3 import S3StorageProvider

            return S3StorageProvider(
                bucket_name=settings.AWS_S3_BUCKET_NAME,
                region=settings.AWS_REGION,
                base_url=settings.AWS_S3_BASE_URL,
                access_key_id=settings.AWS_ACCESS_KEY_ID,
                secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
        case "vercel_blob":
            from app.storage.vercel_blob import VercelBlobStorageProvider

            return VercelBlobStorageProvider(read_write_token=settings.BLOB_READ_WRITE_TOKEN)
    raise ValueError(f"Unsupported STORAGE_PROVIDER: {settings.STORAGE_PROVIDER}")
