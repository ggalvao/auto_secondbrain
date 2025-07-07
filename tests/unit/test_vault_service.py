# pyright: ignore
import pytest
from uuid import uuid4

from libs.models.vault import VaultCreate, VaultStatus
from apps.api.services.vault_service import VaultService


@pytest.mark.unit
class TestVaultService:
    """Test vault service functionality."""

    @pytest.mark.asyncio
    async def test_create_vault(self, test_db) -> None:
        """Test creating a new vault."""
        service = VaultService(test_db)

        vault_data = VaultCreate(
            name="Test Vault",
            original_filename="test.zip",
            file_size=1024,
            storage_path="/tmp/test.zip",
        )

        vault = await service.create_vault(vault_data)

        assert vault.name == "Test Vault"
        assert vault.original_filename == "test.zip"
        assert vault.file_size == 1024
        assert vault.status == VaultStatus.UPLOADED

    @pytest.mark.asyncio
    async def test_get_vault_not_found(self, test_db) -> None:
        """Test getting a non-existent vault."""
        service = VaultService(test_db)

        vault = await service.get_vault(str(uuid4()))

        assert vault is None

    @pytest.mark.asyncio
    async def test_get_vaults_empty(self, test_db) -> None:
        """Test getting vaults when none exist."""
        service = VaultService(test_db)

        vaults = await service.get_vaults()

        assert len(vaults) == 0

    @pytest.mark.asyncio
    async def test_update_vault_status(self, test_db) -> None:
        """Test updating vault status."""
        service = VaultService(test_db)

        # Create a vault first
        vault_data = VaultCreate(
            name="Test Vault",
            original_filename="test.zip",
            file_size=1024,
            storage_path="/tmp/test.zip",
        )

        vault = await service.create_vault(vault_data)

        # Update status
        updated_vault = await service.update_vault_status(
            str(vault.id), VaultStatus.PROCESSING, file_count=10
        )

        assert updated_vault is not None
        assert updated_vault.status == VaultStatus.PROCESSING  # type: ignore
        assert updated_vault.file_count == 10  # type: ignore
