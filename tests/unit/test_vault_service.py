import pytest
from unittest.mock import Mock, patch
from uuid import uuid4

from libs.models import VaultCreate, VaultStatus
from apps.api.services.vault_service import VaultService


@pytest.mark.unit
class TestVaultService:
    """Test vault service functionality."""
    
    def test_create_vault(self, test_db):
        """Test creating a new vault."""
        service = VaultService(test_db)
        
        vault_data = VaultCreate(
            name="Test Vault",
            original_filename="test.zip",
            file_size=1024,
            storage_path="/tmp/test.zip"
        )
        
        vault = service.create_vault(vault_data)
        
        assert vault.name == "Test Vault"
        assert vault.original_filename == "test.zip"
        assert vault.file_size == 1024
        assert vault.status == VaultStatus.UPLOADED
    
    def test_get_vault_not_found(self, test_db):
        """Test getting a non-existent vault."""
        service = VaultService(test_db)
        
        vault = service.get_vault(str(uuid4()))
        
        assert vault is None
    
    def test_get_vaults_empty(self, test_db):
        """Test getting vaults when none exist."""
        service = VaultService(test_db)
        
        vaults = service.get_vaults()
        
        assert len(vaults) == 0
    
    def test_update_vault_status(self, test_db):
        """Test updating vault status."""
        service = VaultService(test_db)
        
        # Create a vault first
        vault_data = VaultCreate(
            name="Test Vault",
            original_filename="test.zip",
            file_size=1024,
            storage_path="/tmp/test.zip"
        )
        
        vault = service.create_vault(vault_data)
        
        # Update status
        updated_vault = service.update_vault_status(
            str(vault.id),
            VaultStatus.PROCESSING,
            file_count=10
        )
        
        assert updated_vault.status == VaultStatus.PROCESSING
        assert updated_vault.file_count == 10