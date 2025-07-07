"""Vault API routes for upload and management."""

import os
import tempfile
import zipfile
from typing import List
from uuid import uuid4

import structlog
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from libs.database import get_db
from libs.models.vault import Vault, VaultCreate, VaultUpload

from ..config import settings
from ..services.vault_service import VaultService

router = APIRouter()
logger = structlog.get_logger()


@router.post("/upload", response_model=VaultUpload)
async def upload_vault(
    file: UploadFile = File(...),
    name: str = Form(...),
    db: Session = Depends(get_db),
) -> VaultUpload:
    """Upload an Obsidian vault ZIP file."""
    # Validate file
    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only ZIP files are supported")

    if file.size and file.size > settings.MAX_VAULT_SIZE:
        raise HTTPException(
            status_code=400,
            detail=(
                f"File size exceeds maximum limit of "
                f"{settings.MAX_VAULT_SIZE} bytes"
            ),
        )

    # Create vault service
    vault_service = VaultService(db)

    try:
        # Read file content
        content = await file.read()

        # Validate ZIP file
        if not _is_valid_zip(content):
            raise HTTPException(status_code=400, detail="Invalid ZIP file format")

        # Generate unique storage path
        vault_id = str(uuid4())
        storage_path = os.path.join(settings.VAULT_STORAGE_PATH, vault_id)

        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)

        # Save and unzip file
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            with zipfile.ZipFile(tmp_path, "r") as zip_ref:
                zip_ref.extractall(storage_path)
        finally:
            if "tmp_path" in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)

        # Create vault record
        vault_data = VaultCreate(
            name=name,
            original_filename=file.filename,
            file_size=len(content),
            storage_path=storage_path,
        )

        vault = await vault_service.create_vault(vault_data)

        # Trigger processing job
        # process_vault_task.delay(str(vault.id))
        logger.info(
            "Vault uploaded and unzipped successfully",
            vault_id=str(vault.id),
            name=vault.name,
            size=vault.file_size,
        )

        return VaultUpload(
            id=vault.id,
            name=vault.name,
            status=vault.status,
            message="Vault uploaded successfully and queued for processing",
        )

    except Exception as e:
        logger.error("Failed to upload vault", error=str(e), exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to upload vault")


@router.get("/", response_model=List[Vault])
async def list_vaults(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[Vault]:
    """List all vaults."""
    vault_service = VaultService(db)
    return await vault_service.get_vaults(skip=skip, limit=limit)


@router.get("/{vault_id}", response_model=Vault)
async def get_vault(
    vault_id: str,
    db: Session = Depends(get_db),
) -> Vault:
    """Get vault by ID."""
    vault_service = VaultService(db)
    vault = await vault_service.get_vault(vault_id)

    if not vault:
        raise HTTPException(status_code=404, detail="Vault not found")

    return vault


@router.delete("/{vault_id}")
async def delete_vault(
    vault_id: str,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Delete vault by ID."""
    vault_service = VaultService(db)

    deleted = await vault_service.delete_vault(vault_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Vault not found")

    return {"message": "Vault deleted successfully"}


def _is_valid_zip(content: bytes) -> bool:
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
