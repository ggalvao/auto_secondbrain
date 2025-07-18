"""Database connection and session management."""

import os
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator, Optional, cast

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from libs.models.base import Base


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self, database_url: Optional[str] = None):
        """Initialize the database manager."""
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/secondbrain"
        )
        self.database_url = cast(str, self.database_url)

        # Create sync engine
        self.engine = create_engine(
            self.database_url,
            pool_pre_ping=True,
            echo=os.getenv("SQL_DEBUG", "false").lower() == "true",
        )

        # Create async engine
        async_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        self.async_engine = create_async_engine(
            async_url,
            pool_pre_ping=True,
            echo=os.getenv("SQL_DEBUG", "false").lower() == "true",
        )

        # Create session factories
        self.SessionLocal = sessionmaker(
            bind=self.engine, autocommit=False, autoflush=False
        )

        self.AsyncSessionLocal = sessionmaker(
            class_=AsyncSession,
            expire_on_commit=False,
        )

    def create_tables(self) -> None:
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)

    async def create_tables_async(self) -> None:
        """Create all database tables asynchronously."""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session."""
        session = self.AsyncSessionLocal()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_db() -> Generator[Session, None, None]:
    """Get database session for FastAPI dependency."""
    db_manager = DatabaseManager()
    session = db_manager.SessionLocal()
    try:
        yield session
    finally:
        session.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Get database session with context manager for general use."""
    db_manager = DatabaseManager()
    with db_manager.get_session() as session:
        yield session


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session for FastAPI dependency."""
    db_manager = DatabaseManager()
    async with db_manager.get_async_session() as session:
        yield session
