"""
Vercel Blob storage provider
"""

from vercel import api as vercel_api
from vercel.blob import BlobCredentials, BlobError, BlobNotFoundError, BlobServiceOptions, delete_blob, put_blob

from app.conf.exceptions import StorageException
from app.conf.logger_config import api_logger
from app.storage.base import StorageProvider

_TOKEN_PREFIX = "vercel_blob_rw_"  # noqa: S105


def _store_id_from_token(token: str) -> str:
    """Read-write tokens look like ``vercel_blob_rw_<storeId>_<secret>``."""
    store_id, _, secret = token.removeprefix(_TOKEN_PREFIX).partition("_")
    if not token.startswith(_TOKEN_PREFIX) or not store_id or not secret:
        return ""
    return store_id


class VercelBlobStorageProvider(StorageProvider):
    """Stores files as public objects in a Vercel Blob store."""

    def __init__(self, *, read_write_token: str) -> None:
        self._token = read_write_token.strip()
        self._store_id = _store_id_from_token(self._token)
        if not self._store_id:
            api_logger.warning("BLOB_READ_WRITE_TOKEN is missing or malformed; Vercel Blob uploads will fail")
        self.base_url = f"https://{self._store_id.lower()}.public.blob.vercel-storage.com"
        # Passed explicitly so the SDK never falls back to reading credentials from os.environ.
        self._options = BlobServiceOptions(credentials_factory=self._credentials)

    async def _credentials(self) -> BlobCredentials:
        return BlobCredentials(token=self._token, store_id=self._store_id)

    async def upload(self, key: str, data: bytes, content_type: str) -> None:
        try:
            async with vercel_api.session(service_options=[self._options]):
                await put_blob(key, data, access="public", content_type=content_type, allow_overwrite=True)
        except BlobError as e:
            api_logger.error("Vercel Blob upload failed for %s: %s", key, e)
            raise StorageException(detail="Could not upload file") from e

    async def delete(self, key: str) -> None:
        try:
            async with vercel_api.session(service_options=[self._options]):
                await delete_blob(key)
        except BlobNotFoundError:
            return
        except BlobError as e:
            api_logger.error("Vercel Blob delete failed for %s: %s", key, e)
            raise StorageException(detail="Could not delete file") from e

    def get_url(self, key: str) -> str:
        return f"{self.base_url}/{key}"
