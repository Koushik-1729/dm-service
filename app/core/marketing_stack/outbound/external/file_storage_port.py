from abc import ABC, abstractmethod
from typing import Optional


class FileStoragePort(ABC):
    """Abstract interface for file/object storage (S3, R2, etc.)."""

    @abstractmethod
    async def upload(
        self,
        file_path: str,
        content: bytes,
        content_type: Optional[str] = None,
    ) -> str:
        """Upload a file. Returns the storage URL."""
        pass

    @abstractmethod
    async def generate_signed_url(
        self,
        file_path: str,
        expiry_seconds: int = 3600,
    ) -> str:
        """Generate a time-limited signed URL for a file."""
        pass

    @abstractmethod
    async def download(self, file_path: str) -> bytes:
        """Download a file's contents."""
        pass

    @abstractmethod
    async def delete(self, file_path: str) -> bool:
        """Delete a file. Returns True if successful."""
        pass
