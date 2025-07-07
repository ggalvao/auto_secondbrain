"""Service layer for managing vaults."""

import os
import shutil
from typing import List, Optional
from uuid import UUID

import structlog
from sqlalchemy import desc
from sqlalchemy.orm import Session

from libs.models.vault import Vault, VaultCreate, VaultDB, VaultStatus

logger = structlog.get_logger()


class VaultService:
    """Service for managing vaults."""

    def __init__(self, db: Session):
        """Initialize the VaultService with a database session."""
        self.db = db

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

        return Vault.from_orm(db_vault)

    async def get_vault(self, vault_id: str) -> Optional[Vault]:
        """Get vault by ID."""
        db_vault = self.db.query(VaultDB).filter(VaultDB.id == UUID(vault_id)).first()

        if not db_vault:
            return None

        return Vault.from_orm(db_vault)

    async def get_vaults(self, skip: int = 0, limit: int = 100) -> List[Vault]:
        """Get list of vaults."""
        db_vaults = (
            self.db.query(VaultDB)
            .order_by(desc(VaultDB.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return [Vault.from_orm(vault) for vault in db_vaults]

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

        return Vault.from_orm(db_vault)

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
