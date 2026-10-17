"""
AWS S3 storage provider
"""

from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from starlette.concurrency import run_in_threadpool

from app.conf.exceptions import StorageException
from app.conf.logger_config import api_logger
from app.storage.base import StorageProvider


class S3StorageProvider(StorageProvider):
    """Stores files in an S3 bucket. boto3 is synchronous, so calls run in a threadpool."""

    def __init__(self, *, bucket_name: str, region: str, base_url: str, access_key_id: str, secret_access_key: str) -> None:
        self.bucket_name = bucket_name
        self.base_url = base_url.rstrip("/")
        self._client: Any = boto3.client(
            "s3",
            region_name=region,
            aws_access_key_id=access_key_id or None,
            aws_secret_access_key=secret_access_key or None,
        )

    async def upload(self, key: str, data: bytes, content_type: str) -> None:
        try:
            await run_in_threadpool(self._client.put_object, Bucket=self.bucket_name, Key=key, Body=data, ContentType=content_type)
        except (BotoCoreError, ClientError) as e:
            api_logger.error("S3 upload failed for %s: %s", key, e)
            raise StorageException(detail="Could not upload file") from e

    async def delete(self, key: str) -> None:
        try:
            await run_in_threadpool(self._client.delete_object, Bucket=self.bucket_name, Key=key)
        except (BotoCoreError, ClientError) as e:
            api_logger.error("S3 delete failed for %s: %s", key, e)
            raise StorageException(detail="Could not delete file") from e

    def get_url(self, key: str) -> str:
        return f"{self.base_url}/{key}"
