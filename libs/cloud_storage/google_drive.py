"""Google Drive cloud storage provider implementation."""

import io
from typing import Any, BinaryIO, Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

from .base import CloudFile, CloudStorageProvider


class GoogleDriveProvider(CloudStorageProvider):
    """Google Drive implementation of CloudStorageProvider."""

    SCOPES = ["https://www.googleapis.com/auth/drive"]

    def __init__(self) -> None:
        """Initialize the GoogleDriveProvider."""
        self.service = None
        self.credentials: Optional[Credentials] = None

    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with Google Drive."""
        try:
            if "token" in credentials:
                # Use existing token
                self.credentials = Credentials.from_authorized_user_info(credentials)
            else:
                # Perform OAuth flow
                flow = InstalledAppFlow.from_client_config(credentials, self.SCOPES)
                self.credentials = flow.run_local_server(port=0)

            # Refresh token if needed
            if (
                self.credentials
                and self.credentials.expired
                and self.credentials.refresh_token
            ):
                self.credentials.refresh(Request())

            # Build service
            self.service = build("drive", "v3", credentials=self.credentials)
            return True
        except Exception:
            return False

    async def list_files(self, folder_id: Optional[str] = None) -> List[CloudFile]:
        """List files in Google Drive folder."""
        if not self.service:
            raise ValueError("Not authenticated")

        query = "trashed=false"
        if folder_id:
            query += f" and '{folder_id}' in parents"

        results = (
            self.service.files()
            .list(
                q=query,
                pageSize=1000,
                fields=(
                    "nextPageToken, files(id, name, size, mimeType, "
                    "modifiedTime, parents)"
                ),
            )
            .execute()
        )

        files = []
        for item in results.get("files", []):
            files.append(
                CloudFile(
                    id=item["id"],
                    name=item["name"],
                    size=int(item.get("size", 0)),
                    mime_type=item["mimeType"],
                    modified_time=item["modifiedTime"],
                    parent_folder=(
                        item.get("parents")[0] if item.get("parents") else None
                    ),
                )
            )

        return files

    async def download_file(self, file_id: str) -> BinaryIO:
        """Download file from Google Drive."""
        if not self.service:
            raise ValueError("Not authenticated")

        request = self.service.files().get_media(fileId=file_id)
        file_io = io.BytesIO()
        downloader = MediaIoBaseDownload(file_io, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        file_io.seek(0)
        return file_io

    async def upload_file(
        self, file_name: str, file_content: BinaryIO, folder_id: Optional[str] = None
    ) -> CloudFile:
        """Upload file to Google Drive."""
        if not self.service:
            raise ValueError("Not authenticated")

        file_metadata: Dict[str, Any] = {"name": file_name}
        if folder_id:
            file_metadata["parents"] = [folder_id]

        media = MediaIoBaseUpload(
            file_content, mimetype="application/octet-stream", resumable=True
        )

        file = (
            self.service.files()
            .create(
                body=file_metadata,
                media_body=media,
                fields="id, name, size, mimeType, modifiedTime",
            )
            .execute()
        )

        return CloudFile(
            id=file["id"],
            name=file["name"],
            size=int(file.get("size", 0)),
            mime_type=file["mimeType"],
            modified_time=file["modifiedTime"],
            parent_folder=folder_id,
        )

    async def delete_file(self, file_id: str) -> bool:
        """Delete file from Google Drive."""
        if not self.service:
            raise ValueError("Not authenticated")

        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
        except Exception:
            return False

    async def create_folder(
        self, folder_name: str, parent_folder_id: Optional[str] = None
    ) -> str:
        """Create folder in Google Drive."""
        if not self.service:
            raise ValueError("Not authenticated")

        file_metadata: Dict[str, Any] = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
        }

        if parent_folder_id:
            file_metadata["parents"] = [parent_folder_id]

        folder = self.service.files().create(body=file_metadata, fields="id").execute()

        return folder["id"]
