# mypy: ignore-errors
import pytest
import tempfile
import shutil
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from libs.models.base import Base
from apps.api.main import app
from libs.database.connection import get_db


@pytest.fixture
def temp_dir() -> Path:
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_db() -> sessionmaker:  # type: ignore
    """Create a test database."""
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def api_client(test_db) -> TestClient:  # type: ignore
    """Create FastAPI test client."""

    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_vault_zip(temp_dir) -> Path:  # type: ignore
    """Create a sample vault ZIP file for testing."""
    import zipfile

    # Create sample vault structure
    vault_dir = temp_dir / "sample_vault"
    vault_dir.mkdir()

    # Create some markdown files
    (vault_dir / "note1.md").write_text("# Note 1\n\nThis is the first note.")
    (vault_dir / "note2.md").write_text("# Note 2\n\nThis is the second note.")

    # Create .obsidian directory
    obsidian_dir = vault_dir / ".obsidian"
    obsidian_dir.mkdir()
    (obsidian_dir / "config").write_text("{}")

    # Create ZIP file
    zip_path = temp_dir / "sample_vault.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for file_path in vault_dir.rglob("*"):
            if file_path.is_file():
                zf.write(file_path, file_path.relative_to(vault_dir))

    yield zip_path
