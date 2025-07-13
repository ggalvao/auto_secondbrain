"""Service layer for managing vaults."""

import os
import shutil
import tempfile
import zipfile
from typing import List, Optional
from uuid import UUID, uuid4

import structlog
from fastapi import UploadFile
from sqlalchemy import desc
from sqlalchemy.orm import Session

from libs.models.vault import (
    Vault,
    VaultCreate,
    VaultDB,
    VaultFileInfo,
    VaultStatus,
    VaultUpload,
)

logger = structlog.get_logger()


class VaultService:
    """Service for managing vaults."""

    def __init__(self, db: Session, storage_path: str):
        """Initialize the VaultService with a database session and storage path."""
        self.db = db
        self.storage_path = storage_path

    async def create_vault(self, vault_data: VaultCreate) -> Vault:
        """Create a new vault."""
        db_vault = VaultDB(
            name=vault_data.name,
            original_filename=vault_data.original_filename,
            file_size=vault_data.file_size,
            storage_path=vault_data.storage_path,
            status=VaultStatus.UPLOADED,
        )

        self.db.add(db_vault)
        self.db.commit()
        self.db.refresh(db_vault)

        return Vault.model_validate(db_vault)

    async def get_vault(self, vault_id: str) -> Optional[Vault]:
        """Get vault by ID."""
        db_vault = self.db.query(VaultDB).filter(VaultDB.id == UUID(vault_id)).first()

        if not db_vault:
            return None

        return Vault.model_validate(db_vault)

    async def get_vaults(self, skip: int = 0, limit: int = 100) -> List[Vault]:
        """Get list of vaults."""
        db_vaults = (
            self.db.query(VaultDB)
            .order_by(desc(VaultDB.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return [Vault.model_validate(vault) for vault in db_vaults]

    async def update_vault_status(
        self,
        vault_id: str,
        status: VaultStatus,
        error_message: Optional[str] = None,
        file_count: Optional[int] = None,
        processed_files: Optional[int] = None,
    ) -> Optional[Vault]:
        """Update vault status."""
        db_vault = self.db.query(VaultDB).filter(VaultDB.id == UUID(vault_id)).first()

        if not db_vault:
            return None

        db_vault.status = status

        if error_message is not None:
            db_vault.error_message = error_message

        if file_count is not None:
            db_vault.file_count = file_count

        if processed_files is not None:
            db_vault.processed_files = processed_files

        self.db.commit()
        self.db.refresh(db_vault)

        return Vault.model_validate(db_vault)

    async def delete_vault(self, vault_id: str) -> bool:
        """Delete vault and its files."""
        db_vault = self.db.query(VaultDB).filter(VaultDB.id == UUID(vault_id)).first()

        if not db_vault:
            return False

        # Delete files from storage
        try:
            vault_dir = os.path.dirname(db_vault.storage_path)
            if os.path.exists(vault_dir):
                shutil.rmtree(vault_dir)
        except Exception as e:
            logger.error(
                "Failed to delete vault files", vault_id=vault_id, error=str(e)
            )

        # Delete from database
        self.db.delete(db_vault)
        self.db.commit()

        return True

    async def upload_and_process_vault(
        self, file: UploadFile, name: str, max_size: int
    ) -> VaultUpload:
        """Complete vault upload and processing workflow."""
        # Validate file
        filename = self._validate_vault_file(file, max_size)
        logger.info(
            "Starting vault upload and processing", name=name, filename=filename
        )

        # Read file content
        content = await file.read()

        # Validate ZIP content
        if not self._is_valid_zip_content(content):
            raise ValueError("Invalid ZIP file format or missing Obsidian files")

        # Store file
        vault_id = str(uuid4())
        storage_path = self._store_vault_file(vault_id, content)

        # Create vault record
        vault_data = VaultCreate(
            name=name,
            original_filename=filename,
            file_size=len(content),
            storage_path=storage_path,
        )

        vault = await self.create_vault(vault_data)

        # Process vault synchronously
        try:
            logger.info("Processing vault files", vault_id=str(vault.id))
            file_info = self._process_vault_files(storage_path)

            # Update vault with processing results
            await self.update_vault_status(
                str(vault.id),
                VaultStatus.COMPLETED,
                file_count=file_info.file_count,
                processed_files=file_info.file_count,
            )

            logger.info(
                "Vault uploaded and processed successfully",
                vault_id=str(vault.id),
                file_count=file_info.file_count,
            )

            return VaultUpload(
                id=vault.id,
                name=vault.name,
                status=VaultStatus.COMPLETED,
                message="Vault uploaded and processed successfully",
            )

        except Exception as e:
            logger.error(
                "Vault processing failed", vault_id=str(vault.id), error=str(e)
            )
            await self.update_vault_status(
                str(vault.id),
                VaultStatus.FAILED,
                error_message=str(e),
            )
            raise ValueError(f"Failed to process vault: {str(e)}")

    def _validate_vault_file(self, file: UploadFile, max_size: int) -> str:
        """Validate uploaded vault file and return filename."""
        if not file.filename or not file.filename.endswith(".zip"):
            raise ValueError("Only ZIP files are supported")

        if file.size and file.size > max_size:
            raise ValueError(f"File size exceeds maximum limit of {max_size} bytes")

        return file.filename

    def _is_valid_zip_content(self, content: bytes) -> bool:
        """Validate ZIP file content."""
        try:
            with tempfile.NamedTemporaryFile() as tmp:
                tmp.write(content)
                tmp.flush()

                with zipfile.ZipFile(tmp.name, "r") as zip_file:
                    # Check if it's a valid ZIP
                    zip_file.testzip()

                    # Check for common Obsidian files
                    file_list = zip_file.namelist()

                    # Should contain .md files or .obsidian directory
                    has_obsidian_files = any(
                        f.endswith(".md") or ".obsidian" in f for f in file_list
                    )

                    return has_obsidian_files

        except Exception:
            return False

    def _store_vault_file(self, vault_id: str, content: bytes) -> str:
        """Store vault ZIP file to disk."""
        zip_filename = f"{vault_id}.zip"
        storage_path = os.path.join(self.storage_path, zip_filename)

        # Ensure storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)

        # Save ZIP file directly
        with open(storage_path, "wb") as f:
            f.write(content)

        return storage_path

    def _process_vault_files(self, storage_path: str) -> VaultFileInfo:
        """Process vault files and return file information."""
        # Create extraction directory
        vault_dir = os.path.splitext(storage_path)[0]  # Remove .zip extension
        extract_dir = f"{vault_dir}_extracted"
        os.makedirs(extract_dir, exist_ok=True)

        # Extract ZIP file
        with zipfile.ZipFile(storage_path, "r") as zip_file:
            zip_file.extractall(extract_dir)
            file_list = zip_file.namelist()

        # Analyze extracted files
        markdown_files: List[str] = []
        attachment_files: List[str] = []
        config_files: List[str] = []

        for root, _, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, extract_dir)

                if file.endswith(".md"):
                    markdown_files.append(relative_path)
                elif file.startswith(".") or ".obsidian" in relative_path:
                    config_files.append(relative_path)
                else:
                    attachment_files.append(relative_path)

        return VaultFileInfo(
            file_count=len(file_list),
            markdown_files=markdown_files,
            attachment_files=attachment_files,
            config_files=config_files,
            extraction_path=extract_dir,
        )
