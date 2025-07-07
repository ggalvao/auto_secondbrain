"""Base classes and interfaces for cloud storage providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import BinaryIO, Dict, List, Optional


@dataclass
class CloudFile:
    """Represents a file in cloud storage."""

    id: str
    name: str
    size: int
    mime_type: str
    modified_time: str
    parent_folder: Optional[str] = None
    download_url: Optional[str] = None


class CloudStorageProvider(ABC):
    """Abstract base class for cloud storage providers."""

    @abstractmethod
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with the cloud storage provider."""
        pass

    @abstractmethod
    async def list_files(self, folder_id: Optional[str] = None) -> List[CloudFile]:
        """List files in a folder."""
        pass

    @abstractmethod
    async def download_file(self, file_id: str) -> BinaryIO:
        """Download a file by ID."""
        pass

    @abstractmethod
    async def upload_file(
        self, file_name: str, file_content: BinaryIO, folder_id: Optional[str] = None
    ) -> CloudFile:
        """Upload a file to cloud storage."""
        pass

    @abstractmethod
    async def delete_file(self, file_id: str) -> bool:
        """Delete a file by ID."""
        pass

    @abstractmethod
    async def create_folder(
        self, folder_name: str, parent_folder_id: Optional[str] = None
    ) -> str:
        """Create a new folder."""
        pass
