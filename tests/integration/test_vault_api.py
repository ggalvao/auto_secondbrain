import pytest
import io


@pytest.mark.integration
class TestVaultAPI:
    """Test vault API endpoints."""

    def test_health_check(self, api_client):
        """Test health check endpoint."""
        response = api_client.get("/health/")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "secondbrain-api"

    def test_upload_vault_success(self, api_client, sample_vault_zip):
        """Test successful vault upload."""
        with open(sample_vault_zip, "rb") as f:
            files = {"file": ("test.zip", f, "application/zip")}
            data = {"name": "Test Vault"}

            response = api_client.post("/api/v1/vaults/upload", files=files, data=data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Vault"
        assert data["status"] == "uploaded"
        assert "id" in data

    def test_upload_vault_invalid_file(self, api_client):
        """Test upload with invalid file type."""
        fake_file = io.BytesIO(b"not a zip file")
        files = {"file": ("test.txt", fake_file, "text/plain")}
        data = {"name": "Test Vault"}

        response = api_client.post("/api/v1/vaults/upload", files=files, data=data)

        assert response.status_code == 400
        assert "Only ZIP files are supported" in response.json()["detail"]

    def test_list_vaults_empty(self, api_client):
        """Test listing vaults when none exist."""
        response = api_client.get("/api/v1/vaults/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_get_vault_not_found(self, api_client):
        """Test getting a non-existent vault."""
        from uuid import uuid4

        response = api_client.get(f"/api/v1/vaults/{uuid4()}")

        assert response.status_code == 404

    def test_delete_vault_not_found(self, api_client):
        """Test deleting a non-existent vault."""
        from uuid import uuid4

        response = api_client.delete(f"/api/v1/vaults/{uuid4()}")

        assert response.status_code == 404
