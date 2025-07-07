"""Integration tests for database operations."""

import pytest
from sqlalchemy import create_engine, inspect

# Import DB models to register them with SQLAlchemy
from libs.models.base import Base


@pytest.mark.integration
def test_database_creation() -> None:
    """Test that the database and tables are created correctly."""
    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(bind=engine)

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        assert "vaults" in tables
        assert "processing_jobs" in tables
    finally:
        engine.dispose()
