"""Vault API routes for upload and management."""

from typing import List

import structlog
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from libs.database import get_db
from libs.models.vault import Vault, VaultUpload

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
    vault_service = VaultService(db, settings.VAULT_STORAGE_PATH)

    try:
        return await vault_service.upload_and_process_vault(
            file=file,
            name=name,
            max_size=settings.MAX_VAULT_SIZE,
        )
    except ValueError as e:
        logger.error("Vault upload validation failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
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
    vault_service = VaultService(db, settings.VAULT_STORAGE_PATH)
    return await vault_service.get_vaults(skip=skip, limit=limit)


@router.get("/{vault_id}", response_model=Vault)
async def get_vault(
    vault_id: str,
    db: Session = Depends(get_db),
) -> Vault:
    """Get vault by ID."""
    vault_service = VaultService(db, settings.VAULT_STORAGE_PATH)
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
    vault_service = VaultService(db, settings.VAULT_STORAGE_PATH)

    deleted = await vault_service.delete_vault(vault_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Vault not found")

    return {"message": "Vault deleted successfully"}
