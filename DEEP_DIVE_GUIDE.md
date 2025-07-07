# 🧠 SecondBrain Deep Dive Guide

> **The Complete Developer's Guide to Understanding and Extending SecondBrain**

This comprehensive guide will teach you the inner workings of the SecondBrain codebase, helping you understand how every piece fits together so you can confidently extend and modify the system.

## 📖 Table of Contents

1. [High-Level Architecture Overview](#high-level-architecture-overview)
2. [Monorepo Structure Deep Dive](#monorepo-structure-deep-dive)
3. [Core Applications Explained](#core-applications-explained)
4. [Shared Libraries Deep Dive](#shared-libraries-deep-dive)
5. [Data Flow and Processing Pipeline](#data-flow-and-processing-pipeline)
6. [Database Architecture](#database-architecture)
7. [Configuration and Environment Management](#configuration-and-environment-management)
8. [Inter-Service Communication](#inter-service-communication)
9. [Error Handling and Logging](#error-handling-and-logging)
10. [Testing Architecture](#testing-architecture)
11. [Development Patterns and Conventions](#development-patterns-and-conventions)
12. [Extension Points and Customization](#extension-points-and-customization)

---

## High-Level Architecture Overview

SecondBrain is a **microservices-based AI knowledge management system** built as a Python monorepo. The architecture follows modern patterns for scalability, maintainability, and developer experience.

### System Philosophy

```
┌─────────────────────────────────────────────────────────────┐
│                    SecondBrain Philosophy                  │
├─────────────────────────────────────────────────────────────┤
│ • Async-First: Built for concurrent operations             │
│ • Event-Driven: Background processing via message queues   │
│ • Type-Safe: Full TypeScript-style annotations in Python   │
│ • API-Centric: REST APIs as the primary interface          │
│ • Container-Native: Docker-first development and deployment │
│ • Developer-Friendly: Comprehensive tooling and automation │
└─────────────────────────────────────────────────────────────┘
```

### Service Interaction Map

```
┌─────────────┐    HTTP    ┌─────────────┐    Celery    ┌─────────────┐
│   Frontend  │ ---------> │  API Server │ -----------> │   Workers   │
│ (Streamlit) │            │  (FastAPI)  │              │  (Celery)   │
└─────────────┘            └─────────────┘              └─────────────┘
       │                          │                             │
       │                          │                             │
       v                          v                             v
┌─────────────┐            ┌─────────────┐              ┌─────────────┐
│     CLI     │            │ PostgreSQL  │              │    Redis    │
│   (Typer)   │            │ (Database)  │              │ (Message    │
│             │            │             │              │  Broker)    │
└─────────────┘            └─────────────┘              └─────────────┘
```

### Core Technologies Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Web Framework** | FastAPI + Uvicorn | High-performance async API server |
| **Task Queue** | Celery + Redis | Background processing and job management |
| **Database** | PostgreSQL + SQLAlchemy 2.0 | Persistent data storage with modern ORM |
| **Frontend** | Streamlit | Rapid UI prototyping and admin interface |
| **CLI** | Typer + Rich | Command-line administration tools |
| **Package Management** | uv | Ultra-fast Python package management |
| **Migrations** | Alembic | Database schema versioning |
| **Containerization** | Docker + Docker Compose | Development and deployment |

---

## Monorepo Structure Deep Dive

### Why Monorepo?

The monorepo structure enables:
- **Shared Code Reuse**: Common libraries used across all services
- **Coordinated Development**: Changes across services in single PR
- **Unified Tooling**: Single place for linting, testing, formatting
- **Dependency Management**: uv workspace manages all packages

### Directory Structure Explained

```
auto_secondbrain/
├── 📁 apps/                    # Application services
│   ├── 🌐 api/                 # FastAPI REST API server
│   ├── 🖥️  cli/                # Command-line interface
│   ├── 🎨 frontend/            # Future React app (placeholder)
│   ├── 📊 streamlit_app/       # Streamlit web UI
│   └── 🔄 workers/             # Celery background workers
├── 📚 libs/                    # Shared libraries
│   ├── ☁️  cloud_storage/      # Cloud provider integrations
│   ├── 🗄️  database/           # DB connections and migrations
│   ├── 🤖 llm_clients/         # AI model API wrappers
│   ├── 📊 models/              # Data models and schemas
│   └── 🔍 vector_db/           # Vector database abstractions
├── 🏗️  infra/                  # Infrastructure configurations
│   └── 🐳 docker/              # Dockerfiles for each service
├── 🧪 tests/                   # Test suites
│   ├── 🔧 integration/         # API and database integration tests
│   └── ⚡ unit/                # Isolated component tests
├── 🔧 .devcontainer/           # VS Code development environment
├── 📋 alembic/                 # Database migration files
└── 📄 Configuration Files      # Project-wide settings
```

### Package Dependencies Flow

```
┌─────────────┐     depends on     ┌─────────────┐
│    apps     │ -----------------> │    libs     │
└─────────────┘                    └─────────────┘
      │                                  │
      │ imports                          │ imports
      v                                  v
┌─────────────┐                    ┌─────────────┐
│  External   │                    │  External   │
│ Packages    │                    │ Packages    │
│ (FastAPI,   │                    │ (SQLAlchemy,│
│ Celery, etc)│                    │ Pydantic)   │
└─────────────┘                    └─────────────┘
```

**Key Principle**: Apps depend on libs, but libs never depend on apps. This ensures clean separation and reusability.

---

## Core Applications Explained

### 🌐 API Service (`apps/api/`)

The FastAPI-based REST API server that serves as the system's primary interface.

#### Structure Deep Dive

```
apps/api/
├── 📄 main.py              # FastAPI app initialization and middleware
├── ⚙️  config.py           # Environment-specific configuration
├── 🔌 dependencies.py      # Dependency injection setup
├── 🛣️  routers/            # API endpoint definitions
│   ├── 🏥 health.py        # Health check endpoints
│   └── 📦 vault.py         # Vault management endpoints
└── 🛠️  services/           # Business logic layer
    └── 📦 vault_service.py  # Vault operations business logic
```

#### Key Files Explained

**`main.py` - Application Bootstrap**
```python
# This file sets up the entire FastAPI application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers (endpoint collections)
from .routers import health, vault

# Create FastAPI app instance
app = FastAPI(
    title="SecondBrain API",
    description="AI-powered knowledge management system",
    version="0.1.0"
)

# Add middleware for cross-origin requests
app.add_middleware(CORSMiddleware, ...)

# Include router modules
app.include_router(health.router)
app.include_router(vault.router, prefix="/api/v1")
```

**`dependencies.py` - Dependency Injection**
```python
# FastAPI's dependency injection system
from sqlalchemy.orm import Session
from libs.database.connection import get_db_session

# This function will be injected into route handlers
def get_db() -> Session:
    """Database session dependency for API endpoints."""
    with get_db_session() as session:
        yield session
```

**`services/vault_service.py` - Business Logic**
```python
# Service layer pattern - business logic separated from API endpoints
class VaultService:
    def __init__(self, db: Session):
        self.db = db

    async def create_vault(self, vault_data: VaultCreate) -> Vault:
        """Business logic for vault creation."""
        # 1. Validate input
        # 2. Create database record
        # 3. Trigger background processing
        # 4. Return result
```

#### API Design Patterns

1. **Layered Architecture**: Controllers → Services → Models
2. **Dependency Injection**: Database sessions injected via FastAPI
3. **Async/Await**: All endpoints are async for better concurrency
4. **Pydantic Validation**: Request/response models ensure type safety
5. **Error Handling**: Structured HTTP exceptions with proper status codes

### 🔄 Workers Service (`apps/workers/`)

Celery-based background task processing system.

#### Structure Deep Dive

```
apps/workers/
├── 📄 main.py              # Celery app configuration
├── ⚙️  config.py           # Worker-specific settings
└── 📋 tasks/               # Task definitions
    └── 📦 vault_processing.py # Vault processing tasks
```

#### Celery Configuration Deep Dive

**`main.py` - Celery Setup**
```python
from celery import Celery

# Create Celery app with Redis as broker
celery_app = Celery(
    "secondbrain-workers",
    broker=settings.REDIS_URL,      # Message broker
    backend=settings.REDIS_URL,     # Result backend
    include=[                       # Task modules to discover
        "apps.workers.tasks.vault_processing",
    ],
)

# Configure Celery behavior
celery_app.conf.update(
    task_serializer="json",         # How tasks are serialized
    accept_content=["json"],        # What content types to accept
    result_serializer="json",       # How results are serialized
    timezone="UTC",                 # Timezone for scheduled tasks
    enable_utc=True,                # Use UTC timestamps
    task_track_started=True,        # Track when tasks start
    task_acks_late=True,            # Acknowledge tasks after completion
    worker_prefetch_multiplier=1,   # How many tasks to prefetch
    result_expires=3600,            # How long to keep results (seconds)
)

# Task routing configuration
celery_app.conf.task_routes = {
    "apps.workers.tasks.vault_processing.process_vault": {"queue": "vault_processing"},
}
```

#### Task Pattern Deep Dive

**`tasks/vault_processing.py` - Task Implementation**
```python
@celery_app.task(
    bind=True,                      # Pass task instance as first argument
    autoretry_for=(Exception,),     # Auto-retry on these exceptions
    retry_kwargs={'max_retries': 3, 'countdown': 60},  # Retry configuration
    soft_time_limit=300,            # Soft timeout (sends SIGTERM)
    time_limit=600                  # Hard timeout (sends SIGKILL)
)
def process_vault(self: Task, vault_id: str) -> Dict[str, Any]:
    """
    Process uploaded vault content with AI analysis.

    This task demonstrates several key patterns:
    1. Error handling with structured logging
    2. Database operations within tasks
    3. Progress tracking and status updates
    4. Integration with external AI services
    """
    try:
        logger.info("Starting vault processing", vault_id=vault_id)

        # Update vault status to processing
        update_vault_status(vault_id, VaultStatus.PROCESSING)

        # Extract files from uploaded ZIP
        extracted_files = extract_vault_files(vault_id)

        # Process each file with AI
        for file_path in extracted_files:
            analyze_file_content(file_path)
            # Update progress here

        # Mark as completed
        update_vault_status(vault_id, VaultStatus.COMPLETED)

        return {"status": "completed", "files_processed": len(extracted_files)}

    except Exception as e:
        logger.error("Vault processing failed", vault_id=vault_id, error=str(e))
        update_vault_status(vault_id, VaultStatus.FAILED, error_message=str(e))
        raise  # Re-raise for Celery retry mechanism
```

#### Worker Patterns Explained

1. **Task Binding**: `bind=True` passes task instance for self-inspection
2. **Automatic Retries**: Failed tasks are automatically retried with exponential backoff
3. **Time Limits**: Soft and hard limits prevent runaway tasks
4. **Status Tracking**: Tasks update database with progress information
5. **Error Isolation**: Each task handles its own errors and cleanup

### 📊 Streamlit App (`apps/streamlit_app/`)

Web-based UI for rapid prototyping and vault management.

#### Structure and Patterns

```
apps/streamlit_app/
├── 📄 main.py              # Streamlit app entry point
└── ⚙️  config.py           # UI-specific configuration
```

**`main.py` - Streamlit Application**
```python
import streamlit as st
import requests

def main() -> None:
    """Main Streamlit application."""
    st.set_page_config(
        page_title="SecondBrain",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Sidebar navigation
    page = st.sidebar.selectbox("Choose a page", [
        "Upload Vault", "Vault Management", "Analytics", "Settings"
    ])

    # Route to appropriate page function
    if page == "Upload Vault":
        upload_vault_page()
    elif page == "Vault Management":
        vault_management_page()
    # ... etc

def upload_vault_page() -> None:
    """Handle vault upload UI and API communication."""
    with st.form("vault_upload"):
        name = st.text_input("Vault Name")
        uploaded_file = st.file_uploader("Choose ZIP file", type=["zip"])

        if st.form_submit_button("Upload Vault"):
            # Call API endpoint
            response = requests.post(
                f"{settings.API_BASE_URL}/api/v1/vaults/upload",
                files={"file": uploaded_file},
                data={"name": name},
                timeout=60
            )

            if response.status_code == 200:
                st.success("✅ Vault uploaded successfully!")
            else:
                st.error(f"Upload failed: {response.text}")
```

### 🖥️ CLI Service (`apps/cli/`)

Command-line interface for administration and automation.

#### Structure Deep Dive

```
apps/cli/
├── 📄 main.py              # CLI commands and Typer app
└── ⚙️  config.py           # CLI-specific settings
```

**CLI Command Pattern**
```python
import typer
from rich.console import Console

app = typer.Typer(
    name="secondbrain",
    help="SecondBrain CLI - AI-powered knowledge management system",
    no_args_is_help=True,
)

console = Console()

@app.command()
def status() -> None:
    """Check API status and health."""
    try:
        response = requests.get(f"{settings.API_BASE_URL}/health/detailed", timeout=10)
        health_data = response.json()

        # Create rich table for output
        table = Table(title="SecondBrain Health Status")
        table.add_column("Service", style="cyan")
        table.add_column("Status", justify="center")

        for service, status in health_data.get("checks", {}).items():
            color = "green" if status == "healthy" else "red"
            table.add_row(service.title(), f"[{color}]{status}[/{color}]")

        console.print(table)

    except Exception as e:
        console.print(f"❌ Failed to check status: {str(e)}", style="bold red")
```

---

## Shared Libraries Deep Dive

### 📊 Models Library (`libs/models/`)

Contains all data models, schemas, and type definitions used across the system.

#### Structure Deep Dive

```
libs/models/
├── 📄 __init__.py          # Public exports
├── 🏗️  base.py             # Base classes and mixins
├── 📦 vault.py             # Vault-related models
└── 📋 processing.py        # Processing job models
```

#### Model Pattern Deep Dive

**`base.py` - Foundation Classes**
```python
"""Base model classes that provide common functionality."""

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime
from datetime import datetime
import uuid

class BaseModel(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass

class UUIDMixin:
    """Mixin to add UUID primary key to models."""
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

class TimestampMixin:
    """Mixin to add created_at/updated_at timestamps."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
```

**`vault.py` - Vault Models**
```python
"""Vault models demonstrating the dual-model pattern."""

from enum import Enum
from typing import Optional
from sqlalchemy import String, BigInteger, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from .base import BaseModel as SQLBaseModel, UUIDMixin, TimestampMixin

# Enums for type safety
class VaultStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# SQLAlchemy Model (Database)
class VaultDB(SQLBaseModel, UUIDMixin, TimestampMixin):
    """Database model for vault storage."""

    __tablename__ = "vaults"

    # Required fields
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[VaultStatus] = mapped_column(
        SQLEnum(VaultStatus),
        default=VaultStatus.UPLOADED
    )

    # Optional fields
    file_count: Mapped[Optional[int]] = mapped_column(nullable=True)
    processed_files: Mapped[Optional[int]] = mapped_column(nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

# Pydantic Models (API)
class VaultBase(BaseModel):
    """Base vault schema for API operations."""
    name: str
    original_filename: str

class VaultCreate(VaultBase):
    """Schema for vault creation requests."""
    file_size: int
    storage_path: str

class Vault(VaultBase):
    """Complete vault schema for API responses."""
    id: str
    status: VaultStatus
    file_size: int
    file_count: Optional[int] = None
    processed_files: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allow conversion from SQLAlchemy models
```

#### Model Design Patterns

1. **Dual Model Pattern**: SQLAlchemy for database, Pydantic for API
2. **Mixins**: Reusable functionality (UUIDs, timestamps)
3. **Enums**: Type-safe status and option handling
4. **Optional Fields**: Database nullable fields properly typed
5. **Config Classes**: Pydantic configuration for ORM integration

### 🗄️ Database Library (`libs/database/`)

Database connections, session management, and migration utilities.

#### Structure Deep Dive

```
libs/database/
├── 📄 __init__.py          # Public exports
├── 🔌 connection.py        # Database connection and session management
└── 📋 migrations.py        # Migration utilities and helpers
```

**`connection.py` - Database Connection Pattern**
```python
"""Database connection management with dependency injection support."""

from contextlib import contextmanager
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Iterator

class DatabaseManager:
    """Centralized database connection management."""

    def __init__(self, database_url: str):
        """Initialize database manager with connection URL."""
        self.engine: Engine = create_engine(
            database_url,
            echo=False,                    # Set to True for SQL logging
            pool_pre_ping=True,           # Verify connections before use
            pool_recycle=3600,            # Recycle connections every hour
        )

        self.SessionLocal = sessionmaker(
            autocommit=False,             # Explicit transaction control
            autoflush=False,              # Explicit flush control
            bind=self.engine
        )

    @contextmanager
    def get_session(self) -> Iterator[Session]:
        """Context manager for database sessions."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()              # Auto-commit on success
        except Exception:
            session.rollback()            # Auto-rollback on error
            raise
        finally:
            session.close()               # Always close session

# Global database manager instance
db_manager = DatabaseManager(settings.DATABASE_URL)

# Convenience function for context manager usage
def get_db_session() -> Iterator[Session]:
    """Get database session context manager."""
    with db_manager.get_session() as session:
        yield session

# Dependency injection function for FastAPI
def get_db() -> Iterator[Session]:
    """Database dependency for FastAPI endpoints."""
    with get_db_session() as session:
        yield session
```

#### Database Patterns Explained

1. **Connection Pooling**: SQLAlchemy engine manages connection pools
2. **Session Management**: Context managers ensure proper cleanup
3. **Transaction Control**: Explicit commit/rollback for data integrity
4. **Dependency Injection**: Clean integration with FastAPI
5. **Error Handling**: Automatic rollback on exceptions

### 🤖 LLM Clients Library (`libs/llm_clients/`)

AI model API wrappers and utilities for LLM integration.

#### Structure Deep Dive

```
libs/llm_clients/
├── 📄 __init__.py          # Public exports
├── 🏗️  base.py             # Abstract base client
├── 🔤 openai_client.py     # OpenAI API wrapper
└── 🧠 anthropic_client.py  # Anthropic API wrapper
```

**Abstract Base Pattern**
```python
"""Abstract base class for LLM clients."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from pydantic import BaseModel

class LLMResponse(BaseModel):
    """Standardized response from LLM clients."""
    content: str
    model: str
    usage: Dict[str, Any]
    finish_reason: str

class BaseLLMClient(ABC):
    """Abstract base class for all LLM clients."""

    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """Generate text from a prompt."""
        pass

    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> LLMResponse:
        """Chat with the model using message history."""
        pass

    @abstractmethod
    async def summarize(self, text: str, **kwargs: Any) -> LLMResponse:
        """Summarize the given text."""
        pass
```

**Concrete Implementation Pattern**
```python
"""OpenAI client implementation."""

import openai
from tenacity import retry, stop_after_attempt, wait_exponential
from .base import BaseLLMClient, LLMResponse

class OpenAIClient(BaseLLMClient):
    """OpenAI client for text generation."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """Initialize OpenAI client."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = openai.AsyncOpenAI(api_key=self.api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_text(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """Generate text with automatic retry logic."""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages, **kwargs)

    async def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> LLMResponse:
        """Chat implementation with error handling."""
        try:
            response = await self.client.chat.completions.create(
                model=kwargs.get("model", self.model),
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1000),
            )

            return LLMResponse(
                content=response.choices[0].message.content or "",
                model=response.model,
                usage=response.usage.model_dump() if response.usage else {},
                finish_reason=response.choices[0].finish_reason or "",
            )
        except Exception as e:
            logger.error("OpenAI API call failed", error=str(e))
            raise
```

#### LLM Client Patterns

1. **Abstract Base Classes**: Common interface for all LLM providers
2. **Retry Logic**: Automatic retries with exponential backoff
3. **Standardized Responses**: Consistent return types across providers
4. **Error Handling**: Structured logging and exception handling
5. **Configuration**: Environment-based API key management

---

## Data Flow and Processing Pipeline

Understanding how data flows through the system is crucial for extending functionality.

### Complete Vault Processing Flow

```
┌─────────────┐    1. Upload     ┌─────────────┐    2. Validate    ┌─────────────┐
│   User/UI   │ ──────────────> │ API Server  │ ──────────────> │ Validation  │
└─────────────┘                 └─────────────┘                 └─────────────┘
                                       │                               │
                                       │ 3. Store                      │ ✓/✗
                                       v                               │
┌─────────────┐    8. Status     ┌─────────────┐    4. Create DB    │
│  Database   │ <──────────────  │  Storage    │ <──────────────────┘
└─────────────┘                 └─────────────┘
       │                               │
       │ 9. Update                     │ 5. Trigger
       v                               v
┌─────────────┐    7. Complete   ┌─────────────┐    6. Process     ┌─────────────┐
│   Status    │ <──────────────  │ Celery Task │ ──────────────> │ AI Analysis │
│   Updates   │                 └─────────────┘                 └─────────────┘
└─────────────┘
```

### Step-by-Step Flow Analysis

#### 1. Upload Request Processing

**API Endpoint**: `POST /api/v1/vaults/upload`

```python
@router.post("/upload", response_model=Vault, status_code=status.HTTP_201_CREATED)
async def upload_vault(
    name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Vault:
    """Upload vault endpoint with detailed flow."""

    # Step 1: Validate input
    if not file.filename.endswith('.zip'):
        raise HTTPException(400, "Only ZIP files are supported")

    # Step 2: Create temporary storage
    upload_path = f"/tmp/uploads/{uuid.uuid4()}/{file.filename}"
    os.makedirs(os.path.dirname(upload_path), exist_ok=True)

    # Step 3: Save uploaded file
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Step 4: Create database record
    vault_service = VaultService(db)
    vault = await vault_service.create_vault(VaultCreate(
        name=name,
        original_filename=file.filename,
        file_size=file.size,
        storage_path=upload_path
    ))

    # Step 5: Trigger background processing
    from apps.workers.tasks.vault_processing import process_vault
    process_vault.delay(vault.id)

    return vault
```

#### 2. Background Processing Deep Dive

**Task**: `process_vault(vault_id: str)`

```python
@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def process_vault(self: Task, vault_id: str) -> Dict[str, Any]:
    """Complete vault processing pipeline."""

    # Phase 1: Setup and validation
    logger.info("Starting vault processing", vault_id=vault_id, task_id=self.request.id)

    try:
        # Update status to processing
        update_vault_status(vault_id, VaultStatus.PROCESSING)

        # Phase 2: File extraction
        extracted_files = extract_vault_files.delay(vault_id).get()

        # Phase 3: Content analysis
        analysis_results = []
        for file_path in extracted_files:
            result = analyze_file_content.delay(file_path).get()
            analysis_results.append(result)

        # Phase 4: AI processing
        ai_analysis = analyze_vault_content.delay(vault_id, analysis_results).get()

        # Phase 5: Finalization
        update_vault_status(vault_id, VaultStatus.COMPLETED,
                          processed_files=len(extracted_files))

        return {
            "status": "completed",
            "vault_id": vault_id,
            "files_processed": len(extracted_files),
            "ai_analysis": ai_analysis
        }

    except Exception as e:
        logger.error("Vault processing failed", vault_id=vault_id, error=str(e))
        update_vault_status(vault_id, VaultStatus.FAILED, error_message=str(e))
        raise
```

#### 3. Status Tracking System

```python
def update_vault_status(
    vault_id: str,
    status: VaultStatus,
    error_message: Optional[str] = None,
    processed_files: Optional[int] = None
) -> None:
    """Centralized status update system."""

    with get_db_session() as db:
        vault = db.query(VaultDB).filter(VaultDB.id == vault_id).first()
        if not vault:
            logger.error("Vault not found for status update", vault_id=vault_id)
            return

        # Update fields
        vault.status = status
        vault.updated_at = datetime.utcnow()

        if error_message:
            vault.error_message = error_message

        if processed_files is not None:
            vault.processed_files = processed_files

        db.commit()

        # Log status change for monitoring
        logger.info(
            "Vault status updated",
            vault_id=vault_id,
            old_status=vault.status,
            new_status=status,
            processed_files=processed_files
        )
```

### Error Handling and Recovery

#### Retry Logic in Tasks

```python
# Task-level retry configuration
@celery_app.task(
    bind=True,
    autoretry_for=(ConnectionError, TimeoutError),  # Specific exceptions
    retry_kwargs={
        'max_retries': 3,
        'countdown': 60,      # Wait 60 seconds between retries
        'backoff': True,      # Exponential backoff
        'jitter': True        # Add random jitter
    }
)
def resilient_task(self: Task, data: Any) -> Any:
    """Task with comprehensive retry logic."""
    try:
        return process_data(data)
    except (ConnectionError, TimeoutError) as e:
        logger.warning(f"Retryable error in task {self.request.id}: {e}")
        raise  # Let Celery handle the retry
    except Exception as e:
        logger.error(f"Non-retryable error in task {self.request.id}: {e}")
        # Don't retry for these errors
        raise self.retry(countdown=0, max_retries=0)
```

#### Dead Letter Queue Pattern

```python
# Configure dead letter queue for failed tasks
celery_app.conf.task_routes = {
    "apps.workers.tasks.*": {
        "queue": "default",
        "routing_key": "default",
        "options": {
            "priority": 0,
            "retry_policy": {
                "max_retries": 3,
                "interval_start": 0,
                "interval_step": 0.2,
                "interval_max": 0.2,
            },
        },
    },
    # Failed tasks go to DLQ
    "*.failed": {"queue": "failed_tasks"},
}
```

---

## Database Architecture

### Schema Design Philosophy

The database schema follows these principles:

1. **Normalization**: Proper table relationships and minimal redundancy
2. **Audit Trail**: Created/updated timestamps on all entities
3. **Soft Deletes**: Mark records as deleted rather than removing them
4. **Indexing Strategy**: Performance-optimized indexes on query columns
5. **Constraint Enforcement**: Database-level constraints for data integrity

### Current Schema Deep Dive

#### Core Tables

```sql
-- Vaults table (primary entity)
CREATE TABLE vaults (
    id VARCHAR(36) PRIMARY KEY,           -- UUID as string
    name VARCHAR(255) NOT NULL,           -- User-friendly name
    original_filename VARCHAR(255) NOT NULL,  -- Original file name
    file_size BIGINT NOT NULL,            -- File size in bytes
    storage_path TEXT NOT NULL,           -- Path to stored file
    status VARCHAR(20) NOT NULL DEFAULT 'uploaded',  -- Processing status
    file_count INTEGER,                   -- Number of files in vault
    processed_files INTEGER,              -- Number of processed files
    error_message TEXT,                   -- Error details if failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Indexes for performance
    INDEX idx_vaults_status (status),
    INDEX idx_vaults_created_at (created_at),
    INDEX idx_vaults_name (name)
);

-- Processing jobs table (audit trail)
CREATE TABLE processing_jobs (
    id VARCHAR(36) PRIMARY KEY,
    vault_id VARCHAR(36) NOT NULL,
    job_type VARCHAR(50) NOT NULL,       -- Type of processing job
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    input_data JSON,                     -- Job input parameters
    output_data JSON,                    -- Job results
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key relationship
    FOREIGN KEY (vault_id) REFERENCES vaults(id) ON DELETE CASCADE,

    -- Indexes
    INDEX idx_processing_jobs_vault_id (vault_id),
    INDEX idx_processing_jobs_status (status),
    INDEX idx_processing_jobs_type (job_type)
);
```

### Migration Strategy

#### Alembic Configuration

**`alembic.ini` - Migration Configuration**
```ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/secondbrain

[post_write_hooks]
hooks = black
black.type = console_scripts
black.entrypoint = black
```

**Migration File Pattern**
```python
"""Add vault processing status fields

Revision ID: abc123def456
Revises: previous_revision
Create Date: 2024-01-01 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'abc123def456'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Add new columns for vault processing status."""
    # Add new columns
    op.add_column('vaults', sa.Column('file_count', sa.Integer(), nullable=True))
    op.add_column('vaults', sa.Column('processed_files', sa.Integer(), nullable=True))

    # Add new indexes
    op.create_index('ix_vaults_status', 'vaults', ['status'])

    # Add check constraints
    op.create_check_constraint(
        'check_processed_files_not_greater_than_total',
        'vaults',
        'processed_files <= file_count OR processed_files IS NULL OR file_count IS NULL'
    )

def downgrade() -> None:
    """Remove vault processing status fields."""
    op.drop_constraint('check_processed_files_not_greater_than_total', 'vaults')
    op.drop_index('ix_vaults_status')
    op.drop_column('vaults', 'processed_files')
    op.drop_column('vaults', 'file_count')
```

### Database Access Patterns

#### Repository Pattern Implementation

```python
"""Repository pattern for data access abstraction."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from libs.models.vault import VaultDB, VaultStatus

class VaultRepository:
    """Repository for vault data access operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, vault_data: VaultDB) -> VaultDB:
        """Create a new vault record."""
        self.db.add(vault_data)
        self.db.commit()
        self.db.refresh(vault_data)
        return vault_data

    def get_by_id(self, vault_id: str) -> Optional[VaultDB]:
        """Get vault by ID with error handling."""
        try:
            return self.db.query(VaultDB).filter(VaultDB.id == vault_id).first()
        except Exception as e:
            logger.error("Database query failed", vault_id=vault_id, error=str(e))
            raise

    def get_all(self, skip: int = 0, limit: int = 100) -> List[VaultDB]:
        """Get paginated list of vaults."""
        return (
            self.db.query(VaultDB)
            .order_by(desc(VaultDB.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(self, status: VaultStatus) -> List[VaultDB]:
        """Get vaults by processing status."""
        return self.db.query(VaultDB).filter(VaultDB.status == status).all()

    def get_processing_stats(self) -> Dict[str, int]:
        """Get aggregated processing statistics."""
        stats = (
            self.db.query(
                VaultDB.status,
                func.count(VaultDB.id).label('count')
            )
            .group_by(VaultDB.status)
            .all()
        )

        return {status: count for status, count in stats}

    def update_status(
        self,
        vault_id: str,
        status: VaultStatus,
        **kwargs
    ) -> Optional[VaultDB]:
        """Update vault status with additional fields."""
        vault = self.get_by_id(vault_id)
        if not vault:
            return None

        vault.status = status
        for key, value in kwargs.items():
            if hasattr(vault, key) and value is not None:
                setattr(vault, key, value)

        self.db.commit()
        self.db.refresh(vault)
        return vault

    def delete(self, vault_id: str) -> bool:
        """Soft delete vault (mark as deleted)."""
        vault = self.get_by_id(vault_id)
        if not vault:
            return False

        # Soft delete - just mark as deleted
        vault.status = VaultStatus.DELETED
        vault.deleted_at = datetime.utcnow()
        self.db.commit()
        return True
```

---

## Configuration and Environment Management

### Configuration Architecture

The system uses a layered configuration approach:

1. **Default Values**: Hardcoded sensible defaults
2. **Environment Variables**: Override defaults via ENV vars
3. **Configuration Files**: Optional `.env` files for development
4. **Runtime Configuration**: Dynamic configuration via API

### Configuration Pattern Deep Dive

**Base Configuration Class**
```python
"""Base configuration with Pydantic BaseSettings."""

from pydantic import BaseSettings, Field
from typing import Optional

class BaseConfig(BaseSettings):
    """Base configuration class with common settings."""

    # Environment
    ENVIRONMENT: str = Field(default="development", description="Runtime environment")
    DEBUG: bool = Field(default=False, description="Enable debug mode")

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/secondbrain",
        description="PostgreSQL connection string"
    )

    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string"
    )

    # API
    API_BASE_URL: str = Field(
        default="http://localhost:8000",
        description="Base URL for API server"
    )

    # AI Services
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    ANTHROPIC_API_KEY: Optional[str] = Field(
        default=None,
        description="Anthropic API key"
    )

    class Config:
        env_file = ".env"                    # Load from .env file
        env_file_encoding = "utf-8"         # File encoding
        case_sensitive = True               # Environment variables are case-sensitive

        # Environment variable parsing
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
            """Custom environment variable parsing."""
            if field_name.endswith('_URL'):
                # URL validation
                return raw_val.strip()
            elif field_name.endswith('_KEY'):
                # API key validation
                return raw_val.strip() if raw_val.strip() else None
            return raw_val
```

**Service-Specific Configuration**
```python
"""API service configuration."""

class APIConfig(BaseConfig):
    """Configuration specific to API service."""

    # FastAPI settings
    TITLE: str = "SecondBrain API"
    DESCRIPTION: str = "AI-powered knowledge management system"
    VERSION: str = "0.1.0"

    # CORS settings
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8501"],
        description="Allowed CORS origins"
    )

    # File upload settings
    MAX_UPLOAD_SIZE: int = Field(
        default=100 * 1024 * 1024,  # 100MB
        description="Maximum upload file size in bytes"
    )
    UPLOAD_DIR: str = Field(
        default="/tmp/uploads",
        description="Directory for uploaded files"
    )

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60,
        description="API rate limit per minute"
    )

    class Config:
        env_prefix = "API_"  # Environment variables prefixed with API_

# Global settings instance
settings = APIConfig()
```

### Environment-Specific Configurations

**Development Environment (`.env.development`)**
```bash
# Development environment settings
ENVIRONMENT=development
DEBUG=true

# Database (local PostgreSQL)
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/secondbrain

# Redis (local Redis)
REDIS_URL=redis://redis:6379/0

# API
API_BASE_URL=http://localhost:8000
CORS_ORIGINS=["http://localhost:3000","http://localhost:8501"]

# File uploads
MAX_UPLOAD_SIZE=100000000
UPLOAD_DIR=/tmp/uploads

# AI Services (development keys)
OPENAI_API_KEY=sk-development-key-here
ANTHROPIC_API_KEY=development-key-here

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=development
```

**Production Environment (`.env.production`)**
```bash
# Production environment settings
ENVIRONMENT=production
DEBUG=false

# Database (production PostgreSQL)
DATABASE_URL=postgresql://user:password@prod-db:5432/secondbrain

# Redis (production Redis cluster)
REDIS_URL=redis://prod-redis:6379/0

# API
API_BASE_URL=https://api.secondbrain.ai
CORS_ORIGINS=["https://secondbrain.ai"]

# File uploads
MAX_UPLOAD_SIZE=500000000
UPLOAD_DIR=/var/uploads

# AI Services (production keys)
OPENAI_API_KEY=${OPENAI_API_KEY}  # Injected by container orchestrator
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

## Inter-Service Communication

### Communication Patterns

The system uses multiple communication patterns based on the use case:

1. **Synchronous HTTP**: API requests between services
2. **Asynchronous Messages**: Background task processing
3. **Database Sharing**: Shared data store for state
4. **Event Streaming**: Real-time updates (future)

### HTTP Communication Pattern

**Service-to-Service HTTP Calls**
```python
"""HTTP client for inter-service communication."""

import httpx
from typing import Optional, Dict, Any
from urllib.parse import urljoin

class ServiceClient:
    """Base class for HTTP service communication."""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers={
                "User-Agent": "SecondBrain-ServiceClient/1.0",
                "Content-Type": "application/json"
            }
        )

    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """GET request with error handling."""
        try:
            response = await self.client.get(endpoint, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("HTTP request failed", endpoint=endpoint, error=str(e))
            raise
        except Exception as e:
            logger.error("Unexpected error in HTTP request", error=str(e))
            raise

    async def post(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """POST request with error handling."""
        try:
            response = await self.client.post(endpoint, json=data, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("HTTP POST failed", endpoint=endpoint, error=str(e))
            raise

class APIServiceClient(ServiceClient):
    """Client for communicating with API service."""

    async def get_vault(self, vault_id: str) -> Optional[Dict[str, Any]]:
        """Get vault details from API service."""
        try:
            return await self.get(f"/api/v1/vaults/{vault_id}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    async def update_vault_status(
        self,
        vault_id: str,
        status: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Update vault status via API."""
        data = {"status": status, **kwargs}
        return await self.post(f"/api/v1/vaults/{vault_id}/status", data)

# Usage in worker tasks
async def communicate_with_api():
    """Example of service communication in worker."""
    api_client = APIServiceClient(settings.API_BASE_URL)

    # Get vault details
    vault = await api_client.get_vault("vault-123")
    if not vault:
        logger.error("Vault not found", vault_id="vault-123")
        return

    # Update status
    await api_client.update_vault_status(
        "vault-123",
        "processing",
        progress=50
    )
```

### Message Queue Communication

**Celery Task Communication Pattern**
```python
"""Advanced Celery task patterns for service communication."""

from celery import group, chain, chord
from apps.workers.main import celery_app

# Sequential processing with chain
@celery_app.task
def extract_files(vault_id: str) -> List[str]:
    """Extract files from vault."""
    # Implementation here
    return ["file1.md", "file2.md", "file3.md"]

@celery_app.task
def analyze_file(file_path: str) -> Dict[str, Any]:
    """Analyze individual file."""
    # Implementation here
    return {"file": file_path, "analysis": "..."}

@celery_app.task
def combine_analysis(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Combine individual file analyses."""
    # Implementation here
    return {"combined_analysis": "..."}

# Complex workflow with chord (parallel + callback)
def process_vault_workflow(vault_id: str):
    """Complex processing workflow."""

    # Step 1: Extract files (sequential)
    extract_task = extract_files.s(vault_id)

    # Step 2: Analyze files in parallel
    def create_analysis_tasks(file_list):
        return group(analyze_file.s(file_path) for file_path in file_list)

    # Step 3: Combine results (after all analysis complete)
    combine_task = combine_analysis.s()

    # Create workflow: extract -> analyze (parallel) -> combine
    workflow = chain(
        extract_task,
        lambda result: chord(
            create_analysis_tasks(result),
            combine_task
        )
    )

    return workflow.apply_async()

# Usage
result = process_vault_workflow("vault-123")
final_result = result.get()  # Wait for completion
```

### Event-Driven Communication (Future)

**Event Bus Pattern (Planned)**
```python
"""Event-driven communication pattern for future implementation."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable
from datetime import datetime
import json

class Event:
    """Base event class."""

    def __init__(self, event_type: str, data: Dict[str, Any], source: str):
        self.event_type = event_type
        self.data = data
        self.source = source
        self.timestamp = datetime.utcnow()
        self.event_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Serialize event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "data": self.data,
            "source": self.source,
            "timestamp": self.timestamp.isoformat()
        }

class EventBus:
    """Simple event bus for service communication."""

    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to events of a specific type."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    async def publish(self, event: Event):
        """Publish event to all subscribers."""
        handlers = self.handlers.get(event.event_type, [])

        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(
                    "Event handler failed",
                    event_type=event.event_type,
                    handler=handler.__name__,
                    error=str(e)
                )

# Example usage
event_bus = EventBus()

# Subscribe to vault events
@event_bus.subscribe("vault.status_changed")
async def handle_vault_status_change(event: Event):
    """Handle vault status change events."""
    vault_id = event.data["vault_id"]
    new_status = event.data["status"]

    logger.info("Vault status changed", vault_id=vault_id, status=new_status)

    # Trigger additional processing based on status
    if new_status == "completed":
        await trigger_post_processing(vault_id)

# Publish event
await event_bus.publish(Event(
    "vault.status_changed",
    {"vault_id": "123", "status": "completed"},
    "api-service"
))
```

---

## Error Handling and Logging

### Logging Architecture

The system uses **structured logging** with `structlog` for consistent, searchable, and analyzable logs across all services.

#### Logging Configuration Deep Dive

**`libs/logging/config.py` (Planned)**
```python
"""Centralized logging configuration."""

import structlog
import logging
from typing import Any, Dict
from datetime import datetime

class CustomFormatter:
    """Custom log formatter for structured logging."""

    def __call__(self, _: Any, __: str, event_dict: Dict[str, Any]) -> str:
        """Format log entry with timestamp and structure."""
        # Add timestamp
        event_dict["timestamp"] = datetime.utcnow().isoformat()

        # Add service context
        event_dict["service"] = getattr(settings, "SERVICE_NAME", "unknown")

        # Format as JSON for production, pretty for development
        if settings.ENVIRONMENT == "production":
            return json.dumps(event_dict, sort_keys=True)
        else:
            return self._pretty_format(event_dict)

    def _pretty_format(self, event_dict: Dict[str, Any]) -> str:
        """Pretty format for development."""
        timestamp = event_dict.pop("timestamp", "")
        level = event_dict.pop("level", "INFO")
        message = event_dict.pop("event", "")

        extras = " ".join(f"{k}={v}" for k, v in event_dict.items() if k not in ["service"])

        return f"{timestamp} [{level}] {message} {extras}"

def configure_logging():
    """Configure structured logging for the application."""

    # Configure standard library logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format="%(message)s"
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            CustomFormatter(),
        ],
        logger_factory=structlog.WriteLoggerFactory(),
        wrapper_class=structlog.BoundLogger,
        cache_logger_on_first_use=True,
    )

# Global logger instance
logger = structlog.get_logger()
```

#### Structured Logging Patterns

**Service-Level Logging**
```python
"""Logging patterns for different scenarios."""

import structlog
from typing import Any, Dict, Optional

logger = structlog.get_logger()

class VaultService:
    """Service with comprehensive logging."""

    def __init__(self, db: Session):
        self.db = db
        # Create service-specific logger with context
        self.logger = logger.bind(service="vault_service")

    async def create_vault(self, vault_data: VaultCreate) -> Vault:
        """Create vault with detailed logging."""

        # Log operation start
        self.logger.info(
            "Starting vault creation",
            vault_name=vault_data.name,
            file_size=vault_data.file_size,
            operation="create_vault"
        )

        try:
            # Business logic
            db_vault = VaultDB(**vault_data.dict())
            self.db.add(db_vault)
            self.db.commit()

            # Log success
            self.logger.info(
                "Vault created successfully",
                vault_id=db_vault.id,
                vault_name=db_vault.name,
                operation="create_vault",
                duration_ms=123  # Add timing
            )

            return Vault.from_orm(db_vault)

        except Exception as e:
            # Log error with context
            self.logger.error(
                "Vault creation failed",
                vault_name=vault_data.name,
                error=str(e),
                error_type=type(e).__name__,
                operation="create_vault"
            )
            raise

# Request-level logging (FastAPI middleware)
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all HTTP requests and responses."""

    # Generate request ID for tracing
    request_id = str(uuid.uuid4())

    # Add request context to logger
    with structlog.contextvars.bound_contextvars(request_id=request_id):
        logger.info(
            "HTTP request started",
            method=request.method,
            url=str(request.url),
            user_agent=request.headers.get("user-agent"),
            request_id=request_id
        )

        start_time = time.time()

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            logger.info(
                "HTTP request completed",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                duration_ms=int(duration * 1000),
                request_id=request_id
            )

            return response

        except Exception as e:
            duration = time.time() - start_time

            logger.error(
                "HTTP request failed",
                method=request.method,
                url=str(request.url),
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=int(duration * 1000),
                request_id=request_id
            )
            raise

# Celery task logging
@celery_app.task(bind=True)
def logged_task(self: Task, data: Any) -> Any:
    """Task with comprehensive logging."""

    task_id = self.request.id

    with structlog.contextvars.bound_contextvars(task_id=task_id):
        logger.info(
            "Task started",
            task_name=self.name,
            task_id=task_id,
            data_size=len(str(data))
        )

        try:
            result = process_data(data)

            logger.info(
                "Task completed successfully",
                task_name=self.name,
                task_id=task_id,
                result_size=len(str(result))
            )

            return result

        except Exception as e:
            logger.error(
                "Task failed",
                task_name=self.name,
                task_id=task_id,
                error=str(e),
                error_type=type(e).__name__
            )
            raise
```

### Error Handling Strategies

#### Layered Error Handling

```python
"""Layered error handling from database to API."""

# Custom exception hierarchy
class SecondBrainException(Exception):
    """Base exception for all SecondBrain errors."""

    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}

class VaultNotFoundError(SecondBrainException):
    """Vault not found in database."""
    pass

class VaultProcessingError(SecondBrainException):
    """Error during vault processing."""
    pass

class InvalidVaultFormatError(SecondBrainException):
    """Invalid vault file format."""
    pass

# Repository layer error handling
class VaultRepository:
    """Repository with error handling."""

    def get_by_id(self, vault_id: str) -> VaultDB:
        """Get vault with proper error handling."""
        try:
            vault = self.db.query(VaultDB).filter(VaultDB.id == vault_id).first()
            if not vault:
                raise VaultNotFoundError(
                    f"Vault not found: {vault_id}",
                    error_code="VAULT_NOT_FOUND",
                    details={"vault_id": vault_id}
                )
            return vault

        except SQLAlchemyError as e:
            logger.error("Database query failed", vault_id=vault_id, error=str(e))
            raise SecondBrainException(
                "Database operation failed",
                error_code="DATABASE_ERROR",
                details={"original_error": str(e)}
            ) from e

# Service layer error handling
class VaultService:
    """Service with error handling and retry logic."""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(SQLAlchemyError)
    )
    async def create_vault(self, vault_data: VaultCreate) -> Vault:
        """Create vault with retry logic."""
        try:
            # Validate input
            if not vault_data.name.strip():
                raise InvalidVaultFormatError(
                    "Vault name cannot be empty",
                    error_code="INVALID_VAULT_NAME"
                )

            # Repository operation
            repo = VaultRepository(self.db)
            db_vault = repo.create(VaultDB(**vault_data.dict()))

            return Vault.from_orm(db_vault)

        except VaultNotFoundError:
            # Don't retry for business logic errors
            raise
        except SQLAlchemyError as e:
            # Log and let retry decorator handle it
            logger.warning("Database error in vault creation, will retry", error=str(e))
            raise

# API layer error handling
@app.exception_handler(SecondBrainException)
async def secondbrain_exception_handler(request: Request, exc: SecondBrainException):
    """Convert SecondBrain exceptions to HTTP responses."""

    status_code_map = {
        "VaultNotFoundError": 404,
        "InvalidVaultFormatError": 400,
        "VaultProcessingError": 422,
        "DatabaseError": 500,
    }

    status_code = status_code_map.get(type(exc).__name__, 500)

    # Log error with context
    logger.error(
        "API error occurred",
        error_type=type(exc).__name__,
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        status_code=status_code,
        path=request.url.path
    )

    # Return structured error response
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )

# Endpoint with error handling
@router.get("/{vault_id}", response_model=Vault)
async def get_vault(vault_id: str, db: Session = Depends(get_db)) -> Vault:
    """Get vault with comprehensive error handling."""
    try:
        service = VaultService(db)
        return await service.get_vault(vault_id)

    except VaultNotFoundError:
        # Let exception handler deal with it
        raise
    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(
            "Unexpected error in get_vault",
            vault_id=vault_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise SecondBrainException(
            "Internal server error",
            error_code="INTERNAL_ERROR"
        ) from e
```

---

## Testing Architecture

### Testing Philosophy

The testing strategy follows the testing pyramid:

1. **Unit Tests (70%)**: Fast, isolated tests for individual components
2. **Integration Tests (20%)**: Test component interactions
3. **End-to-End Tests (10%)**: Full system workflow tests

### Test Structure Deep Dive

```
tests/
├── 📁 unit/                    # Isolated component tests
│   ├── 🧪 test_vault_service.py
│   ├── 🧪 test_llm_clients.py
│   └── 🧪 test_models.py
├── 📁 integration/             # Component interaction tests
│   ├── 🧪 test_api_endpoints.py
│   ├── 🧪 test_database.py
│   └── 🧪 test_worker_tasks.py
├── 📁 e2e/                     # End-to-end workflow tests
│   └── 🧪 test_vault_workflow.py
├── 📁 fixtures/                # Test data and utilities
│   ├── 📄 sample_vaults/
│   └── 📄 test_data.py
└── 📄 conftest.py              # Shared test configuration
```

#### Test Configuration and Fixtures

**`conftest.py` - Shared Test Setup**
```python
"""Shared test configuration and fixtures."""

import pytest
import tempfile
import shutil
from typing import Iterator, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from httpx import AsyncClient

from libs.database.connection import BaseModel
from libs.models.vault import VaultDB, VaultStatus
from apps.api.main import app
from apps.api.dependencies import get_db

# Test database setup
@pytest.fixture(scope="session")
def test_database_url() -> str:
    """Test database URL."""
    return "sqlite:///./test.db"

@pytest.fixture(scope="session")
def test_engine(test_database_url: str):
    """Create test database engine."""
    engine = create_engine(test_database_url, connect_args={"check_same_thread": False})

    # Create all tables
    BaseModel.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    BaseModel.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(test_engine) -> Iterator[Session]:
    """Create isolated database session for each test."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def override_get_db(db_session: Session):
    """Override database dependency for testing."""
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def client(override_get_db) -> TestClient:
    """FastAPI test client."""
    return TestClient(app)

@pytest.fixture
async def async_client(override_get_db) -> AsyncClient:
    """Async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# Sample data fixtures
@pytest.fixture
def sample_vault_data() -> Dict[str, Any]:
    """Sample vault data for testing."""
    return {
        "name": "Test Vault",
        "original_filename": "test_vault.zip",
        "file_size": 1024,
        "storage_path": "/tmp/test_vault.zip"
    }

@pytest.fixture
def sample_vault_db(db_session: Session, sample_vault_data: Dict[str, Any]) -> VaultDB:
    """Create sample vault in database."""
    vault = VaultDB(**sample_vault_data)
    db_session.add(vault)
    db_session.commit()
    db_session.refresh(vault)
    return vault

@pytest.fixture
def sample_vault_file() -> Iterator[str]:
    """Create temporary vault file for testing."""
    import zipfile

    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    vault_dir = os.path.join(temp_dir, "test_vault")
    os.makedirs(vault_dir)

    # Create sample markdown files
    with open(os.path.join(vault_dir, "note1.md"), "w") as f:
        f.write("# Test Note 1\n\nThis is a test note.")

    with open(os.path.join(vault_dir, "note2.md"), "w") as f:
        f.write("# Test Note 2\n\nThis is another test note.")

    # Create ZIP file
    zip_path = os.path.join(temp_dir, "test_vault.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, dirs, files in os.walk(vault_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, vault_dir)
                zipf.write(file_path, arcname)

    yield zip_path

    # Cleanup
    shutil.rmtree(temp_dir)

# Celery testing fixtures
@pytest.fixture
def celery_config():
    """Celery configuration for testing."""
    return {
        'broker_url': 'memory://',
        'result_backend': 'cache+memory://',
        'task_always_eager': True,  # Execute tasks synchronously
        'task_eager_propagates': True,  # Propagate exceptions
    }

@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing."""
    from unittest.mock import Mock
    from libs.llm_clients.base import LLMResponse

    mock_client = Mock()
    mock_client.generate_text.return_value = LLMResponse(
        content="Mocked LLM response",
        model="mock-model",
        usage={"tokens": 10},
        finish_reason="stop"
    )

    return mock_client
```

#### Unit Test Patterns

**`test_vault_service.py` - Service Layer Tests**
```python
"""Unit tests for VaultService."""

import pytest
from unittest.mock import Mock, patch
from apps.api.services.vault_service import VaultService
from libs.models.vault import VaultCreate, VaultStatus, VaultDB

@pytest.mark.unit
class TestVaultService:
    """Unit tests for VaultService."""

    async def test_create_vault_success(self, db_session, sample_vault_data):
        """Test successful vault creation."""
        # Arrange
        service = VaultService(db_session)
        vault_data = VaultCreate(**sample_vault_data)

        # Act
        result = await service.create_vault(vault_data)

        # Assert
        assert result.name == vault_data.name
        assert result.status == VaultStatus.UPLOADED
        assert result.id is not None

        # Verify database record
        db_vault = db_session.query(VaultDB).filter(VaultDB.id == result.id).first()
        assert db_vault is not None
        assert db_vault.name == vault_data.name

    async def test_get_vault_not_found(self, db_session):
        """Test getting non-existent vault."""
        # Arrange
        service = VaultService(db_session)
        non_existent_id = "non-existent-id"

        # Act
        result = await service.get_vault(non_existent_id)

        # Assert
        assert result is None

    async def test_get_vaults_empty(self, db_session):
        """Test getting vaults when none exist."""
        # Arrange
        service = VaultService(db_session)

        # Act
        result = await service.get_vaults()

        # Assert
        assert len(result) == 0

    async def test_update_vault_status(self, db_session, sample_vault_db):
        """Test updating vault status."""
        # Arrange
        service = VaultService(db_session)

        # Act
        updated_vault = await service.update_vault_status(
            sample_vault_db.id,
            VaultStatus.PROCESSING,
            file_count=10,
            processed_files=0
        )

        # Assert
        assert updated_vault is not None
        assert updated_vault.status == VaultStatus.PROCESSING
        assert updated_vault.file_count == 10
        assert updated_vault.processed_files == 0

    @patch('apps.workers.tasks.vault_processing.process_vault.delay')
    async def test_create_vault_triggers_processing(self, mock_task, db_session, sample_vault_data):
        """Test that vault creation triggers background processing."""
        # Arrange
        service = VaultService(db_session)
        vault_data = VaultCreate(**sample_vault_data)

        # Act
        vault = await service.create_vault(vault_data)

        # Assert
        mock_task.assert_called_once_with(vault.id)
```

#### Integration Test Patterns

**`test_api_endpoints.py` - API Integration Tests**
```python
"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient
from libs.models.vault import VaultStatus

@pytest.mark.integration
class TestVaultAPI:
    """Integration tests for vault API endpoints."""

    async def test_health_check(self, async_client: AsyncClient):
        """Test health check endpoint."""
        # Act
        response = await async_client.get("/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "secondbrain-api"

    async def test_upload_vault_success(self, async_client: AsyncClient, sample_vault_file):
        """Test successful vault upload."""
        # Arrange
        with open(sample_vault_file, "rb") as f:
            files = {"file": ("test_vault.zip", f, "application/zip")}
            data = {"name": "Test Vault"}

            # Act
            response = await async_client.post("/api/v1/vaults/upload", files=files, data=data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Vault"
        assert data["status"] == "uploaded"
        assert "id" in data

    async def test_upload_invalid_file_type(self, async_client: AsyncClient):
        """Test upload with invalid file type."""
        # Arrange
        files = {"file": ("test.txt", b"not a zip file", "text/plain")}
        data = {"name": "Test Vault"}

        # Act
        response = await async_client.post("/api/v1/vaults/upload", files=files, data=data)

        # Assert
        assert response.status_code == 400
        assert "Only ZIP files are supported" in response.json()["detail"]

    async def test_list_vaults_empty(self, async_client: AsyncClient):
        """Test listing vaults when none exist."""
        # Act
        response = await async_client.get("/api/v1/vaults/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    async def test_get_vault_not_found(self, async_client: AsyncClient):
        """Test getting non-existent vault."""
        # Act
        response = await async_client.get("/api/v1/vaults/non-existent-id")

        # Assert
        assert response.status_code == 404

    async def test_delete_vault_not_found(self, async_client: AsyncClient):
        """Test deleting non-existent vault."""
        # Act
        response = await async_client.delete("/api/v1/vaults/non-existent-id")

        # Assert
        assert response.status_code == 404
```

#### End-to-End Test Patterns

**`test_vault_workflow.py` - Complete Workflow Tests**
```python
"""End-to-end tests for complete vault processing workflow."""

import pytest
import time
from httpx import AsyncClient
from apps.workers.tasks.vault_processing import process_vault

@pytest.mark.e2e
class TestVaultWorkflow:
    """End-to-end tests for vault processing."""

    async def test_complete_vault_processing_workflow(
        self,
        async_client: AsyncClient,
        sample_vault_file,
        celery_worker
    ):
        """Test complete vault upload and processing workflow."""

        # Step 1: Upload vault
        with open(sample_vault_file, "rb") as f:
            files = {"file": ("test_vault.zip", f, "application/zip")}
            data = {"name": "E2E Test Vault"}

            upload_response = await async_client.post(
                "/api/v1/vaults/upload",
                files=files,
                data=data
            )

        assert upload_response.status_code == 201
        vault_data = upload_response.json()
        vault_id = vault_data["id"]

        # Step 2: Verify initial status
        status_response = await async_client.get(f"/api/v1/vaults/{vault_id}")
        assert status_response.status_code == 200
        assert status_response.json()["status"] == "uploaded"

        # Step 3: Wait for processing to complete (with timeout)
        max_wait_time = 30  # seconds
        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            status_response = await async_client.get(f"/api/v1/vaults/{vault_id}")
            status_data = status_response.json()

            if status_data["status"] in ["completed", "failed"]:
                break

            time.sleep(1)

        # Step 4: Verify final status
        final_response = await async_client.get(f"/api/v1/vaults/{vault_id}")
        final_data = final_response.json()

        assert final_data["status"] == "completed"
        assert final_data["file_count"] > 0
        assert final_data["processed_files"] == final_data["file_count"]

        # Step 5: Verify vault can be deleted
        delete_response = await async_client.delete(f"/api/v1/vaults/{vault_id}")
        assert delete_response.status_code == 200

        # Step 6: Verify vault is deleted
        get_response = await async_client.get(f"/api/v1/vaults/{vault_id}")
        assert get_response.status_code == 404

    @pytest.mark.slow
    async def test_vault_processing_with_ai_analysis(
        self,
        async_client: AsyncClient,
        sample_vault_file,
        mock_llm_client
    ):
        """Test vault processing including AI analysis."""

        # Mock AI client
        with patch('libs.llm_clients.openai_client.OpenAIClient') as mock_client_class:
            mock_client_class.return_value = mock_llm_client

            # Upload and process vault
            with open(sample_vault_file, "rb") as f:
                files = {"file": ("ai_test_vault.zip", f, "application/zip")}
                data = {"name": "AI Test Vault"}

                response = await async_client.post(
                    "/api/v1/vaults/upload",
                    files=files,
                    data=data
                )

            vault_id = response.json()["id"]

            # Wait for processing
            # ... (similar to previous test)

            # Verify AI client was called
            assert mock_llm_client.generate_text.called
            assert mock_llm_client.summarize.called
```

### Testing Best Practices

#### Test Data Management

```python
"""Test data factories for consistent test data."""

import factory
from libs.models.vault import VaultDB, VaultStatus

class VaultDBFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating VaultDB instances."""

    class Meta:
        model = VaultDB
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"Test Vault {n}")
    original_filename = factory.LazyAttribute(lambda obj: f"{obj.name.lower().replace(' ', '_')}.zip")
    file_size = factory.Faker('random_int', min=1024, max=1024*1024)  # 1KB to 1MB
    storage_path = factory.LazyAttribute(lambda obj: f"/tmp/{obj.id}/{obj.original_filename}")
    status = VaultStatus.UPLOADED

# Usage in tests
def test_with_factory_data(db_session):
    """Test using factory-generated data."""
    vault = VaultDBFactory.create(session=db_session, name="Factory Test Vault")

    assert vault.name == "Factory Test Vault"
    assert vault.status == VaultStatus.UPLOADED
    assert vault.id is not None
```

#### Performance Testing

```python
"""Performance and load testing utilities."""

import asyncio
import time
from typing import List
import pytest
from httpx import AsyncClient

@pytest.mark.performance
class TestPerformance:
    """Performance tests for API endpoints."""

    async def test_concurrent_vault_uploads(self, async_client: AsyncClient, sample_vault_file):
        """Test concurrent vault uploads."""

        async def upload_vault(client: AsyncClient, vault_name: str) -> float:
            """Upload single vault and return duration."""
            start_time = time.time()

            with open(sample_vault_file, "rb") as f:
                files = {"file": ("test_vault.zip", f, "application/zip")}
                data = {"name": vault_name}

                response = await client.post("/api/v1/vaults/upload", files=files, data=data)

            duration = time.time() - start_time
            assert response.status_code == 201
            return duration

        # Test concurrent uploads
        tasks = [
            upload_vault(async_client, f"Concurrent Vault {i}")
            for i in range(10)
        ]

        durations = await asyncio.gather(*tasks)

        # Verify performance
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)

        assert avg_duration < 5.0  # Average under 5 seconds
        assert max_duration < 10.0  # No request takes more than 10 seconds

    async def test_api_response_times(self, async_client: AsyncClient):
        """Test API response times for various endpoints."""

        endpoints = [
            ("GET", "/health"),
            ("GET", "/api/v1/vaults/"),
            ("GET", "/health/detailed"),
        ]

        for method, endpoint in endpoints:
            start_time = time.time()

            if method == "GET":
                response = await async_client.get(endpoint)
            # Add other methods as needed

            duration = time.time() - start_time

            assert response.status_code in [200, 404]  # Valid response
            assert duration < 1.0  # Response under 1 second
```

---

## Development Patterns and Conventions

### Code Organization Patterns

#### Service Layer Pattern

The service layer pattern separates business logic from presentation and data access layers.

```python
"""Service layer implementation pattern."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

# Abstract service interface
class BaseService(ABC):
    """Abstract base service for common functionality."""

    def __init__(self, db: Session):
        self.db = db
        self.logger = structlog.get_logger().bind(service=self.__class__.__name__)

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[Any]:
        """Get entity by ID."""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Any]:
        """Get all entities with pagination."""
        pass

    @abstractmethod
    async def create(self, entity_data: Any) -> Any:
        """Create new entity."""
        pass

    @abstractmethod
    async def update(self, entity_id: str, entity_data: Any) -> Optional[Any]:
        """Update existing entity."""
        pass

    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Delete entity."""
        pass

# Concrete service implementation
class VaultService(BaseService):
    """Vault service with business logic."""

    async def get_by_id(self, vault_id: str) -> Optional[Vault]:
        """Get vault by ID with logging."""
        self.logger.info("Getting vault by ID", vault_id=vault_id)

        try:
            db_vault = self.db.query(VaultDB).filter(VaultDB.id == vault_id).first()
            if not db_vault:
                self.logger.warning("Vault not found", vault_id=vault_id)
                return None

            self.logger.info("Vault retrieved successfully", vault_id=vault_id)
            return Vault.from_orm(db_vault)

        except Exception as e:
            self.logger.error("Failed to get vault", vault_id=vault_id, error=str(e))
            raise

    async def create(self, vault_data: VaultCreate) -> Vault:
        """Create vault with validation and processing trigger."""
        self.logger.info("Creating vault", vault_name=vault_data.name)

        # Validation
        await self._validate_vault_data(vault_data)

        # Database operation
        db_vault = VaultDB(**vault_data.dict())
        self.db.add(db_vault)
        self.db.commit()
        self.db.refresh(db_vault)

        # Convert to API model
        vault = Vault.from_orm(db_vault)

        # Trigger processing
        await self._trigger_processing(vault.id)

        self.logger.info("Vault created successfully", vault_id=vault.id)
        return vault

    async def _validate_vault_data(self, vault_data: VaultCreate) -> None:
        """Validate vault data before creation."""
        if not vault_data.name.strip():
            raise ValueError("Vault name cannot be empty")

        if vault_data.file_size <= 0:
            raise ValueError("File size must be positive")

        if not vault_data.storage_path:
            raise ValueError("Storage path is required")

    async def _trigger_processing(self, vault_id: str) -> None:
        """Trigger background processing for vault."""
        from apps.workers.tasks.vault_processing import process_vault

        try:
            task = process_vault.delay(vault_id)
            self.logger.info("Processing task triggered", vault_id=vault_id, task_id=task.id)
        except Exception as e:
            self.logger.error("Failed to trigger processing", vault_id=vault_id, error=str(e))
            # Don't raise - vault is created, processing can be retried
```

#### Repository Pattern

The repository pattern provides an abstraction layer over data access.

```python
"""Repository pattern for data access."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Type, TypeVar
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

T = TypeVar('T')

class BaseRepository(ABC):
    """Abstract base repository."""

    def __init__(self, db: Session, model_class: Type[T]):
        self.db = db
        self.model_class = model_class

    def create(self, **kwargs) -> T:
        """Create new record."""
        instance = self.model_class(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def get_by_id(self, entity_id: str) -> Optional[T]:
        """Get record by ID."""
        return self.db.query(self.model_class).filter(
            self.model_class.id == entity_id
        ).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination."""
        return (
            self.db.query(self.model_class)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, entity_id: str, **kwargs) -> Optional[T]:
        """Update record by ID."""
        instance = self.get_by_id(entity_id)
        if not instance:
            return None

        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, entity_id: str) -> bool:
        """Delete record by ID."""
        instance = self.get_by_id(entity_id)
        if not instance:
            return False

        self.db.delete(instance)
        self.db.commit()
        return True

class VaultRepository(BaseRepository):
    """Vault-specific repository operations."""

    def __init__(self, db: Session):
        super().__init__(db, VaultDB)

    def get_by_status(self, status: VaultStatus) -> List[VaultDB]:
        """Get vaults by processing status."""
        return self.db.query(VaultDB).filter(VaultDB.status == status).all()

    def get_recent(self, limit: int = 10) -> List[VaultDB]:
        """Get recently created vaults."""
        return (
            self.db.query(VaultDB)
            .order_by(desc(VaultDB.created_at))
            .limit(limit)
            .all()
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get vault statistics."""
        total_count = self.db.query(func.count(VaultDB.id)).scalar()

        status_counts = (
            self.db.query(VaultDB.status, func.count(VaultDB.id))
            .group_by(VaultDB.status)
            .all()
        )

        avg_file_size = self.db.query(func.avg(VaultDB.file_size)).scalar()

        return {
            "total_vaults": total_count,
            "status_distribution": dict(status_counts),
            "average_file_size": avg_file_size or 0,
        }
```

#### Dependency Injection Pattern

FastAPI's dependency injection system enables clean separation of concerns.

```python
"""Dependency injection patterns."""

from typing import Iterator, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from libs.database.connection import get_db_session
from apps.api.services.vault_service import VaultService
from apps.api.repositories.vault_repository import VaultRepository

# Database dependency
def get_db() -> Iterator[Session]:
    """Database session dependency."""
    with get_db_session() as session:
        yield session

# Repository dependencies
def get_vault_repository(db: Session = Depends(get_db)) -> VaultRepository:
    """Vault repository dependency."""
    return VaultRepository(db)

# Service dependencies
def get_vault_service(db: Session = Depends(get_db)) -> VaultService:
    """Vault service dependency."""
    return VaultService(db)

# Authentication dependency (future)
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current authenticated user."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = get_user(username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user

# Permission dependency (future)
def require_permission(permission: str):
    """Dependency factory for permission checking."""

    def check_permission(user: User = Depends(get_current_user)) -> User:
        if not user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission}"
            )
        return user

    return check_permission

# Usage in endpoints
@router.post("/", response_model=Vault)
async def create_vault(
    vault_data: VaultCreate,
    vault_service: VaultService = Depends(get_vault_service),
    current_user: User = Depends(require_permission("vault:create"))
) -> Vault:
    """Create vault with injected dependencies."""
    return await vault_service.create(vault_data)
```

### Error Handling Patterns

#### Custom Exception Hierarchy

```python
"""Custom exception hierarchy for domain-specific errors."""

from typing import Dict, Any, Optional

class SecondBrainError(Exception):
    """Base exception for all SecondBrain errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.status_code = status_code

# Domain-specific exceptions
class VaultError(SecondBrainError):
    """Base class for vault-related errors."""
    pass

class VaultNotFoundError(VaultError):
    """Vault not found."""

    def __init__(self, vault_id: str):
        super().__init__(
            f"Vault not found: {vault_id}",
            error_code="VAULT_NOT_FOUND",
            details={"vault_id": vault_id},
            status_code=404
        )

class VaultValidationError(VaultError):
    """Vault validation failed."""

    def __init__(self, field: str, message: str):
        super().__init__(
            f"Validation failed for {field}: {message}",
            error_code="VAULT_VALIDATION_ERROR",
            details={"field": field, "validation_message": message},
            status_code=400
        )

class VaultProcessingError(VaultError):
    """Vault processing failed."""

    def __init__(self, vault_id: str, reason: str):
        super().__init__(
            f"Processing failed for vault {vault_id}: {reason}",
            error_code="VAULT_PROCESSING_ERROR",
            details={"vault_id": vault_id, "reason": reason},
            status_code=422
        )

# Infrastructure exceptions
class DatabaseError(SecondBrainError):
    """Database operation failed."""

    def __init__(self, operation: str, original_error: Exception):
        super().__init__(
            f"Database {operation} failed: {str(original_error)}",
            error_code="DATABASE_ERROR",
            details={"operation": operation, "original_error": str(original_error)},
            status_code=500
        )

class ExternalServiceError(SecondBrainError):
    """External service call failed."""

    def __init__(self, service: str, operation: str, status_code: int):
        super().__init__(
            f"{service} {operation} failed with status {status_code}",
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service, "operation": operation, "status_code": status_code},
            status_code=502
        )

# Error handling decorator
def handle_errors(logger):
    """Decorator for consistent error handling."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except SecondBrainError:
                # Re-raise domain errors
                raise
            except Exception as e:
                # Convert unexpected errors
                logger.error(
                    "Unexpected error in function",
                    function=func.__name__,
                    error=str(e),
                    error_type=type(e).__name__
                )
                raise SecondBrainError(
                    "Internal server error",
                    error_code="INTERNAL_ERROR",
                    details={"function": func.__name__}
                ) from e

        return wrapper
    return decorator

# Usage
@handle_errors(logger)
async def risky_operation(data: Any) -> Any:
    """Function with error handling."""
    # Implementation that might raise exceptions
    pass
```

### Async/Await Patterns

#### Database Operations

```python
"""Async patterns for database operations."""

import asyncio
from typing import List, Optional
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

class AsyncVaultService:
    """Async vault service with proper concurrency handling."""

    def __init__(self, db: Session):
        self.db = db
        self.logger = structlog.get_logger().bind(service="AsyncVaultService")

    async def get_vault_with_details(self, vault_id: str) -> Optional[Dict[str, Any]]:
        """Get vault with related data using concurrent queries."""

        async def get_vault():
            """Get basic vault data."""
            return await asyncio.to_thread(
                lambda: self.db.query(VaultDB).filter(VaultDB.id == vault_id).first()
            )

        async def get_processing_jobs():
            """Get processing jobs for vault."""
            return await asyncio.to_thread(
                lambda: self.db.query(ProcessingJobDB)
                .filter(ProcessingJobDB.vault_id == vault_id)
                .all()
            )

        async def get_file_analysis():
            """Get file analysis results."""
            # Simulate async external service call
            await asyncio.sleep(0.1)
            return {"analysis": "mock data"}

        # Execute queries concurrently
        try:
            vault, jobs, analysis = await asyncio.gather(
                get_vault(),
                get_processing_jobs(),
                get_file_analysis(),
                return_exceptions=True
            )

            # Handle any exceptions
            for result in [vault, jobs, analysis]:
                if isinstance(result, Exception):
                    self.logger.error("Concurrent query failed", error=str(result))
                    raise result

            if not vault:
                return None

            return {
                "vault": Vault.from_orm(vault).dict(),
                "processing_jobs": [ProcessingJob.from_orm(job).dict() for job in jobs],
                "analysis": analysis
            }

        except Exception as e:
            self.logger.error("Failed to get vault details", vault_id=vault_id, error=str(e))
            raise

    async def bulk_update_status(
        self,
        vault_ids: List[str],
        status: VaultStatus
    ) -> List[str]:
        """Update multiple vaults concurrently."""

        async def update_single_vault(vault_id: str) -> str:
            """Update single vault status."""
            return await asyncio.to_thread(
                self._update_vault_status_sync, vault_id, status
            )

        # Update vaults concurrently (with semaphore to limit concurrency)
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent updates

        async def update_with_semaphore(vault_id: str):
            async with semaphore:
                return await update_single_vault(vault_id)

        tasks = [update_with_semaphore(vault_id) for vault_id in vault_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter successful updates
        successful_updates = []
        for vault_id, result in zip(vault_ids, results):
            if isinstance(result, Exception):
                self.logger.error("Failed to update vault", vault_id=vault_id, error=str(result))
            else:
                successful_updates.append(vault_id)

        return successful_updates

    def _update_vault_status_sync(self, vault_id: str, status: VaultStatus) -> str:
        """Synchronous vault status update."""
        vault = self.db.query(VaultDB).filter(VaultDB.id == vault_id).first()
        if not vault:
            raise VaultNotFoundError(vault_id)

        vault.status = status
        self.db.commit()
        return vault_id

# Context manager for async operations
@asynccontextmanager
async def async_vault_operation(vault_id: str):
    """Context manager for vault operations with cleanup."""

    logger = structlog.get_logger().bind(vault_id=vault_id)
    logger.info("Starting vault operation")

    start_time = asyncio.get_event_loop().time()

    try:
        yield vault_id
    except Exception as e:
        logger.error("Vault operation failed", error=str(e))
        raise
    finally:
        duration = asyncio.get_event_loop().time() - start_time
        logger.info("Vault operation completed", duration_seconds=duration)

# Usage
async def example_async_operations():
    """Example of async patterns."""

    async with async_vault_operation("vault-123") as vault_id:
        service = AsyncVaultService(db)

        # Concurrent operations
        details = await service.get_vault_with_details(vault_id)

        # Bulk operations
        updated_vaults = await service.bulk_update_status(
            ["vault-1", "vault-2", "vault-3"],
            VaultStatus.PROCESSING
        )

        return details, updated_vaults
```

---

## Extension Points and Customization

### Plugin Architecture (Future)

The system is designed to support future plugin extensions:

```python
"""Plugin architecture for extending functionality."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

@dataclass
class PluginMetadata:
    """Plugin metadata."""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str]

class Plugin(ABC):
    """Base plugin class."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = structlog.get_logger().bind(plugin=self.__class__.__name__)

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Plugin metadata."""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize plugin."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup plugin resources."""
        pass

class VaultProcessorPlugin(Plugin):
    """Plugin interface for vault processing."""

    @abstractmethod
    async def process_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Process individual file."""
        pass

    @abstractmethod
    async def post_process(self, vault_id: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Post-process vault results."""
        pass

class LLMProviderPlugin(Plugin):
    """Plugin interface for LLM providers."""

    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using LLM."""
        pass

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generate text embeddings."""
        pass

# Example plugin implementation
class OpenAIVaultProcessor(VaultProcessorPlugin):
    """OpenAI-based vault processor."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="openai-processor",
            version="1.0.0",
            description="OpenAI-based content analysis",
            author="SecondBrain Team",
            dependencies=["openai>=1.0.0"]
        )

    async def initialize(self) -> None:
        """Initialize OpenAI client."""
        from libs.llm_clients.openai_client import OpenAIClient
        self.client = OpenAIClient(api_key=self.config["api_key"])
        self.logger.info("OpenAI processor initialized")

    async def process_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Process file with OpenAI."""
        try:
            summary = await self.client.summarize(content)
            keywords = await self.client.extract_keywords(content)

            return {
                "file_path": file_path,
                "summary": summary.content,
                "keywords": keywords,
                "model": summary.model,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error("File processing failed", file_path=file_path, error=str(e))
            raise

    async def post_process(self, vault_id: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine file results into vault summary."""
        all_summaries = [r["summary"] for r in results]
        combined_content = "\n\n".join(all_summaries)

        vault_summary = await self.client.summarize(combined_content)

        return {
            "vault_id": vault_id,
            "overall_summary": vault_summary.content,
            "total_files": len(results),
            "processing_timestamp": datetime.utcnow().isoformat()
        }

    async def cleanup(self) -> None:
        """Cleanup resources."""
        self.logger.info("OpenAI processor cleaned up")

# Plugin manager
class PluginManager:
    """Manages plugin lifecycle."""

    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.logger = structlog.get_logger().bind(component="PluginManager")

    async def register_plugin(self, plugin: Plugin) -> None:
        """Register a plugin."""
        try:
            await plugin.initialize()
            self.plugins[plugin.metadata.name] = plugin
            self.logger.info("Plugin registered", plugin_name=plugin.metadata.name)
        except Exception as e:
            self.logger.error("Plugin registration failed", plugin_name=plugin.metadata.name, error=str(e))
            raise

    async def unregister_plugin(self, plugin_name: str) -> None:
        """Unregister a plugin."""
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            try:
                await plugin.cleanup()
                del self.plugins[plugin_name]
                self.logger.info("Plugin unregistered", plugin_name=plugin_name)
            except Exception as e:
                self.logger.error("Plugin cleanup failed", plugin_name=plugin_name, error=str(e))

    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get plugin by name."""
        return self.plugins.get(plugin_name)

    def list_plugins(self) -> List[PluginMetadata]:
        """List all registered plugins."""
        return [plugin.metadata for plugin in self.plugins.values()]

# Usage
plugin_manager = PluginManager()

async def setup_plugins():
    """Setup default plugins."""
    openai_processor = OpenAIVaultProcessor({"api_key": "your-api-key"})
    await plugin_manager.register_plugin(openai_processor)
```

### Configuration Extension Points

```python
"""Configuration extension points for customization."""

from typing import Dict, Any, Callable, Optional
from pydantic import BaseSettings, Field

class ExtensibleConfig(BaseSettings):
    """Configuration with extension points."""

    # Core settings
    DATABASE_URL: str = "postgresql://localhost/secondbrain"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Extension points
    VAULT_PROCESSORS: List[str] = Field(
        default=["openai", "anthropic"],
        description="List of enabled vault processors"
    )

    STORAGE_BACKENDS: Dict[str, Dict[str, Any]] = Field(
        default={
            "local": {"type": "filesystem", "base_path": "/tmp/uploads"},
            "cloud": {"type": "google_drive", "credentials_path": "/etc/gcp-creds.json"}
        },
        description="Available storage backends"
    )

    LLM_PROVIDERS: Dict[str, Dict[str, Any]] = Field(
        default={
            "openai": {"api_key": "", "model": "gpt-3.5-turbo"},
            "anthropic": {"api_key": "", "model": "claude-3-sonnet"}
        },
        description="LLM provider configurations"
    )

    # Feature flags
    ENABLE_AI_ANALYSIS: bool = Field(default=True, description="Enable AI content analysis")
    ENABLE_VECTOR_SEARCH: bool = Field(default=False, description="Enable vector search")
    ENABLE_REAL_TIME_UPDATES: bool = Field(default=False, description="Enable real-time status updates")

    # Customization hooks
    CUSTOM_PROCESSORS: Dict[str, str] = Field(
        default={},
        description="Custom processor class paths"
    )

# Extension registry
class ExtensionRegistry:
    """Registry for custom extensions."""

    def __init__(self):
        self._processors: Dict[str, Callable] = {}
        self._storage_backends: Dict[str, Callable] = {}
        self._llm_providers: Dict[str, Callable] = {}

    def register_processor(self, name: str, processor_class: Callable):
        """Register custom vault processor."""
        self._processors[name] = processor_class

    def register_storage_backend(self, name: str, backend_class: Callable):
        """Register custom storage backend."""
        self._storage_backends[name] = backend_class

    def register_llm_provider(self, name: str, provider_class: Callable):
        """Register custom LLM provider."""
        self._llm_providers[name] = provider_class

    def get_processor(self, name: str) -> Optional[Callable]:
        """Get processor by name."""
        return self._processors.get(name)

    def get_storage_backend(self, name: str) -> Optional[Callable]:
        """Get storage backend by name."""
        return self._storage_backends.get(name)

    def get_llm_provider(self, name: str) -> Optional[Callable]:
        """Get LLM provider by name."""
        return self._llm_providers.get(name)

# Global extension registry
extension_registry = ExtensionRegistry()

# Custom processor example
class CustomMarkdownProcessor:
    """Custom processor for specialized markdown handling."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    async def process(self, content: str) -> Dict[str, Any]:
        """Custom processing logic."""
        # Your custom implementation
        return {"processed": True, "content_length": len(content)}

# Register custom processor
extension_registry.register_processor("custom_markdown", CustomMarkdownProcessor)
```

---

This comprehensive deep-dive guide covers the inner workings of the SecondBrain codebase from architecture to implementation details. You now have a thorough understanding of:

1. **System Architecture**: How all components fit together
2. **Code Organization**: Monorepo structure and service patterns
3. **Data Flow**: How requests move through the system
4. **Database Design**: Schema and access patterns
5. **Configuration**: Environment and service setup
6. **Error Handling**: Robust error management strategies
7. **Testing**: Comprehensive testing approaches
8. **Development Patterns**: Established coding conventions
9. **Extension Points**: How to customize and extend the system

With this knowledge, you should be able to confidently navigate, understand, and extend the SecondBrain codebase for your specific needs.

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"id": "1", "content": "Create comprehensive deep-dive architectural guide for SecondBrain codebase", "status": "completed", "priority": "high"}]
