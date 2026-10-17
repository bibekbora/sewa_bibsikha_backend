"""
Storage provider interface
"""

from abc import ABC, abstractmethod


class StorageProvider(ABC):
    """Vendor-agnostic file storage. Business code depends on this, never on a concrete provider."""

    @abstractmethod
    async def upload(self, key: str, data: bytes, content_type: str) -> None:
        """Store ``data`` under ``key``, overwriting any existing object."""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete the object stored under ``key``. Deleting a missing key is not an error."""

    @abstractmethod
    def get_url(self, key: str) -> str:
        """Return the public URL for ``key``."""
