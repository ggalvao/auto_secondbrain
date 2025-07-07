import os
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine

from libs.models.base import Base


def get_alembic_config() -> Config:
    """Get Alembic configuration."""
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "alembic")
    alembic_cfg.set_main_option(
        "sqlalchemy.url",
        os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/secondbrain")
    )
    return alembic_cfg


def run_migrations():
    """Run database migrations."""
    alembic_cfg = get_alembic_config()
    command.upgrade(alembic_cfg, "head")


def create_migration(message: str):
    """Create a new migration."""
    alembic_cfg = get_alembic_config()
    command.revision(alembic_cfg, message=message, autogenerate=True)


def downgrade_migration(revision: str = "-1"):
    """Downgrade to a specific migration."""
    alembic_cfg = get_alembic_config()
    command.downgrade(alembic_cfg, revision)