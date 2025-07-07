import os
import zipfile
import tempfile
from pathlib import Path
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import structlog

from libs.database import get_db
from libs.models import VaultDB, VaultCreate, VaultUpload, VaultStatus, Vault
from ..config import settings
from ..services.vault_service import VaultService


router = APIRouter()
logger = structlog.get_logger()


@router.post("/upload", response_model=VaultUpload)
async def upload_vault(
    file: UploadFile = File(...),
    name: str = Form(...),
    db: Session = Depends(get_db),
):
    """Upload an Obsidian vault ZIP file."""
    
    # Validate file
    if not file.filename.endswith('.zip'):
        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are supported"
        )
    
    if file.size > settings.MAX_VAULT_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum limit of {settings.MAX_VAULT_SIZE} bytes"
        )
    
    # Create vault service
    vault_service = VaultService(db)
    
    try:
        # Read file content
        content = await file.read()
        
        # Validate ZIP file
        if not _is_valid_zip(content):
            raise HTTPException(
                status_code=400,
                detail="Invalid ZIP file format"
            )
        
        # Generate unique storage path
        vault_id = str(uuid4())
        storage_path = os.path.join(
            settings.VAULT_STORAGE_PATH,
            vault_id,
            file.filename
        )
        
        # Ensure storage directory exists
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        
        # Save file
        with open(storage_path, 'wb') as f:
            f.write(content)
        
        # Create vault record
        vault_data = VaultCreate(
            name=name,
            original_filename=file.filename,
            file_size=len(content),
            storage_path=storage_path,
        )
        
        vault = await vault_service.create_vault(vault_data)
        
        # TODO: Trigger processing job
        logger.info(
            "Vault uploaded successfully",
            vault_id=vault.id,
            name=vault.name,
            size=vault.file_size,
        )
        
        return VaultUpload(
            id=vault.id,
            name=vault.name,
            status=vault.status,
            message="Vault uploaded successfully and queued for processing"
        )
        
    except Exception as e:
        logger.error("Failed to upload vault", error=str(e), exc_info=e)
        raise HTTPException(
            status_code=500,
            detail="Failed to upload vault"
        )


@router.get("/", response_model=List[Vault])
async def list_vaults(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all vaults."""
    vault_service = VaultService(db)
    return await vault_service.get_vaults(skip=skip, limit=limit)


@router.get("/{vault_id}", response_model=Vault)
async def get_vault(
    vault_id: str,
    db: Session = Depends(get_db),
):
    """Get vault by ID."""
    vault_service = VaultService(db)
    vault = await vault_service.get_vault(vault_id)
    
    if not vault:
        raise HTTPException(
            status_code=404,
            detail="Vault not found"
        )
    
    return vault


@router.delete("/{vault_id}")
async def delete_vault(
    vault_id: str,
    db: Session = Depends(get_db),
):
    """Delete vault by ID."""
    vault_service = VaultService(db)
    
    deleted = await vault_service.delete_vault(vault_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Vault not found"
        )
    
    return {"message": "Vault deleted successfully"}


def _is_valid_zip(content: bytes) -> bool:
    """Validate ZIP file content."""
    try:
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(content)
            tmp.flush()
            
            with zipfile.ZipFile(tmp.name, 'r') as zip_file:
                # Check if it's a valid ZIP
                zip_file.testzip()
                
                # Check for common Obsidian files
                file_list = zip_file.namelist()
                
                # Should contain .md files or .obsidian directory
                has_obsidian_files = any(
                    f.endswith('.md') or '.obsidian' in f 
                    for f in file_list
                )
                
                return has_obsidian_files
                
    except Exception:
        return False