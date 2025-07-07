"""Test configuration and fixtures for the SecondBrain project."""

# mypy: ignore-errors
import shutil
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apps.api.main import app, settings
from libs.database.connection import get_db

# Import DB models to register them with SQLAlchemy
from libs.models.base import Base


@pytest.fixture
def temp_dir() -> Path:
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="function")
def test_engine(request):
    """Create a test database engine."""
    # Ensure models are imported and registered
    from libs.models.processing import ProcessingJobDB  # noqa
    from libs.models.vault import VaultDB  # noqa

    # Use a named in-memory database that can be shared across connections
    db_name = f"test_{id(request)}"
    engine = create_engine(
        f"sqlite:///{db_name}?mode=memory&cache=shared&uri=true",
        connect_args={"check_same_thread": False, "uri": True},
    )

    Base.metadata.create_all(bind=engine)

    def finalizer():
        Base.metadata.drop_all(bind=engine)
        engine.dispose()

    request.addfinalizer(finalizer)
    return engine


@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def api_client(test_engine, monkeypatch) -> TestClient:  # type: ignore
    """Create FastAPI test client."""
    storage_path = tempfile.mkdtemp()
    monkeypatch.setattr(settings, "VAULT_STORAGE_PATH", storage_path)

    def override_get_db():
        TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=test_engine
        )
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
    shutil.rmtree(storage_path)


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
