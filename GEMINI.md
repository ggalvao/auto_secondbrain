# GEMINI.md

This file provides guidance to Google Gemini when working with code in this SecondBrain repository.

## Project Overview

SecondBrain is an AI-powered knowledge management system designed to process, analyze, and organize Obsidian vaults. The system uses a microservices architecture with FastAPI, Celery workers, and a Streamlit frontend, all orchestrated through Docker Compose.

## Quick Start Guide

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- uv package manager

### Setup and Installation
```bash
# Install dependencies
uv sync --dev

# Start infrastructure services
docker compose up -d postgres redis

# Run database migrations
uv run alembic upgrade head

# Install pre-commit hooks
uv run pre-commit install
```

### Running the Application
```bash
# Start all services
docker compose up -d

# Or run services individually:
uv run uvicorn apps.api.main:app --reload --port 8000          # API
uv run celery -A apps.workers.main worker --loglevel=info     # Workers
uv run streamlit run apps/streamlit_app/main.py --port 8501   # UI
```

### Testing and Quality Assurance
```bash
# Run tests
uv run pytest

# Format code
uv run black . && uv run isort .

# Lint and type check
uv run flake8 && uv run mypy .

# Run all pre-commit hooks
uv run pre-commit run --all-files
```

## Architecture and Design Principles

### Monorepo Structure
```
SecondBrain/
├── apps/                    # Application services
│   ├── api/                # FastAPI backend
│   ├── cli/                # Command-line tools
│   ├── streamlit_app/      # Web interface
│   └── workers/            # Celery background tasks
├── libs/                   # Shared libraries
│   ├── cloud_storage/      # Storage providers (Google Drive)
│   ├── database/           # DB connections and migrations
│   ├── llm_clients/        # AI model integrations
│   ├── models/             # Data models and schemas
│   └── vector_db/          # Vector database abstractions
├── tests/                  # Test suites
├── infra/                  # Infrastructure configurations
└── alembic/               # Database migrations
```

### Core Design Patterns

#### Service Layer Pattern
Each application module follows a service layer architecture:
- **Controllers** (FastAPI routers) handle HTTP requests
- **Services** contain business logic and coordinate operations
- **Models** define data structures and database schemas
- **Dependencies** manage database sessions and external services

#### Event-Driven Processing
Vault processing uses an event-driven architecture:
1. File upload triggers immediate validation
2. Background tasks handle resource-intensive operations
3. Status updates propagate through the system
4. Each processing stage is independently retryable

#### Configuration Management
- Environment-specific settings in `config.py` files
- Pydantic BaseSettings for type-safe configuration
- Centralized environment variables in `.env` file
- Docker Compose overrides for development/production

## Code Style and Standards

### Python Code Guidelines

#### Formatting Standards
```python
# Line length: 88 characters (Black default)
# Import organization (isort with Black profile):
import os
from typing import Optional, List, Dict

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from libs.models.vault import Vault, VaultCreate
from apps.api.dependencies import get_db
```

#### Type Annotations
All functions and methods must include complete type annotations:
```python
def process_vault(vault_id: str, options: Dict[str, Any]) -> ProcessingResult:
    """Process a vault with given options."""
    pass

async def get_vault_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[Vault]:
    """Retrieve paginated list of vaults."""
    pass
```

#### Documentation Requirements
- Module docstrings for all Python files
- Class docstrings explaining purpose and usage
- Method docstrings with parameter and return descriptions
- Inline comments for complex business logic

#### Error Handling Strategy
```python
# Service layer - return None or raise specific exceptions
async def get_vault(self, vault_id: str) -> Optional[Vault]:
    """Get vault by ID, returns None if not found."""
    try:
        vault = await self._fetch_vault(vault_id)
        return vault
    except DatabaseError as e:
        logger.error("Database error fetching vault", vault_id=vault_id, error=str(e))
        raise ServiceError(f"Failed to fetch vault: {vault_id}") from e

# API layer - convert to HTTP exceptions
@router.get("/{vault_id}")
async def get_vault(vault_id: str, service: VaultService = Depends()) -> Vault:
    """Get vault by ID."""
    vault = await service.get_vault(vault_id)
    if not vault:
        raise HTTPException(status_code=404, detail="Vault not found")
    return vault
```

### Database Design Patterns

#### Model Definitions
```python
# SQLAlchemy Database Model
class VaultDB(BaseModel, TimestampMixin, UUIDMixin):
    """Database model for vault storage."""

    __tablename__ = "vaults"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[VaultStatus] = mapped_column(Enum(VaultStatus), default=VaultStatus.UPLOADED)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    processing_jobs: Mapped[List["ProcessingJobDB"]] = relationship(
        "ProcessingJobDB", back_populates="vault", cascade="all, delete-orphan"
    )

# Pydantic API Models
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
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

#### Migration Patterns
```python
"""Add vault processing status

Revision ID: abc123
Revises: def456
Create Date: 2024-01-01 12:00:00.000000
"""

def upgrade() -> None:
    """Add processing status columns to vaults table."""
    op.add_column('vaults', sa.Column('file_count', sa.Integer(), nullable=True))
    op.add_column('vaults', sa.Column('processed_files', sa.Integer(), nullable=True))
    op.create_index('ix_vaults_status', 'vaults', ['status'])

def downgrade() -> None:
    """Remove processing status columns."""
    op.drop_index('ix_vaults_status')
    op.drop_column('vaults', 'processed_files')
    op.drop_column('vaults', 'file_count')
```

### API Development Guidelines

#### Endpoint Design
```python
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from typing import List

router = APIRouter(prefix="/api/v1/vaults", tags=["vaults"])

@router.post("/upload", response_model=Vault, status_code=status.HTTP_201_CREATED)
async def upload_vault(
    name: str = Form(..., description="Vault name"),
    file: UploadFile = File(..., description="ZIP file containing vault"),
    db: Session = Depends(get_db)
) -> Vault:
    """Upload and process a new Obsidian vault."""
    # Validate file type
    if not file.filename.endswith('.zip'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only ZIP files are supported"
        )

    # Process upload
    vault_service = VaultService(db)
    return await vault_service.create_vault_from_upload(name, file)

@router.get("/", response_model=List[Vault])
async def list_vaults(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db)
) -> List[Vault]:
    """List all vaults with pagination."""
    vault_service = VaultService(db)
    return await vault_service.get_vaults(skip=skip, limit=limit)
```

#### Request/Response Validation
```python
class VaultUploadRequest(BaseModel):
    """Request model for vault upload."""
    name: str = Field(..., min_length=1, max_length=255, description="Vault display name")
    description: Optional[str] = Field(None, max_length=1000)
    tags: List[str] = Field(default_factory=list, max_items=10)

    @validator('name')
    def validate_name(cls, v):
        """Validate vault name format."""
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()

class VaultResponse(BaseModel):
    """Response model for vault operations."""
    id: str
    name: str
    status: VaultStatus
    progress: float = Field(..., ge=0.0, le=100.0)
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### Background Task Patterns

#### Celery Task Structure
```python
from celery import Task
from celery.exceptions import Retry
from apps.workers.main import celery_app
import structlog

logger = structlog.get_logger()

@celery_app.task(
    bind=True,
    autoretry_for=(ConnectionError, TimeoutError),
    retry_kwargs={'max_retries': 3, 'countdown': 60},
    soft_time_limit=300,
    time_limit=600
)
def process_vault_content(self: Task, vault_id: str, processing_options: Dict[str, Any]) -> Dict[str, Any]:
    """Process vault content with AI analysis."""
    try:
        logger.info("Starting vault processing", vault_id=vault_id, task_id=self.request.id)

        # Update status to processing
        update_vault_status(vault_id, VaultStatus.PROCESSING)

        # Perform processing steps
        result = perform_content_analysis(vault_id, processing_options)

        # Update final status
        update_vault_status(vault_id, VaultStatus.COMPLETED)

        logger.info("Vault processing completed", vault_id=vault_id, result=result)
        return result

    except Exception as e:
        logger.error(
            "Vault processing failed",
            vault_id=vault_id,
            error=str(e),
            task_id=self.request.id
        )
        update_vault_status(vault_id, VaultStatus.FAILED, error_message=str(e))
        raise
```

#### Task Monitoring and Status Updates
```python
def update_vault_status(
    vault_id: str,
    status: VaultStatus,
    progress: Optional[float] = None,
    error_message: Optional[str] = None
) -> None:
    """Update vault processing status in database."""
    with get_db_session() as db:
        vault = db.query(VaultDB).filter(VaultDB.id == vault_id).first()
        if vault:
            vault.status = status
            if progress is not None:
                vault.progress = progress
            if error_message:
                vault.error_message = error_message
            vault.updated_at = datetime.utcnow()
            db.commit()
```

## Testing Strategy and Patterns

### Test Organization
```python
# tests/unit/test_vault_service.py
import pytest
from unittest.mock import Mock, patch
from apps.api.services.vault_service import VaultService

@pytest.mark.unit
class TestVaultService:
    """Unit tests for VaultService."""

    def test_create_vault_success(self, mock_db_session):
        """Test successful vault creation."""
        service = VaultService(mock_db_session)
        vault_data = VaultCreate(name="Test", file_size=1024, storage_path="/tmp/test")

        result = await service.create_vault(vault_data)

        assert result.name == "Test"
        assert result.status == VaultStatus.UPLOADED

# tests/integration/test_vault_api.py
import pytest
from httpx import AsyncClient

@pytest.mark.integration
class TestVaultAPI:
    """Integration tests for vault endpoints."""

    async def test_upload_vault_endpoint(self, client: AsyncClient):
        """Test vault upload through API."""
        with open("test_vault.zip", "rb") as f:
            response = await client.post(
                "/api/v1/vaults/upload",
                files={"file": ("vault.zip", f, "application/zip")},
                data={"name": "Test Vault"}
            )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Vault"
        assert "id" in data
```

### Test Fixtures and Utilities
```python
# tests/conftest.py
@pytest.fixture
async def client():
    """Create test HTTP client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def sample_vault_file():
    """Create a sample vault ZIP file for testing."""
    import tempfile
    import zipfile

    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
        with zipfile.ZipFile(tmp.name, 'w') as zf:
            zf.writestr("note1.md", "# Test Note\nContent here")
            zf.writestr("note2.md", "# Another Note\nMore content")
        yield tmp.name

    os.unlink(tmp.name)
```

## Security and Performance Guidelines

### Security Practices
- Always validate file uploads (size, type, content)
- Use parameterized queries to prevent SQL injection
- Implement rate limiting on API endpoints
- Log security-relevant events with structured logging
- Never expose internal error details in API responses
- Use environment variables for secrets and API keys

### Performance Optimization
```python
# Database query optimization
async def get_vaults_with_stats(self, limit: int = 100) -> List[Dict[str, Any]]:
    """Get vaults with processing statistics."""
    query = (
        select(VaultDB, func.count(ProcessingJobDB.id).label('job_count'))
        .outerjoin(ProcessingJobDB)
        .group_by(VaultDB.id)
        .order_by(VaultDB.created_at.desc())
        .limit(limit)
    )
    result = await self.db.execute(query)
    return [{"vault": vault, "job_count": count} for vault, count in result]

# Async processing patterns
async def process_multiple_files(file_paths: List[str]) -> List[ProcessingResult]:
    """Process multiple files concurrently."""
    tasks = [process_single_file(path) for path in file_paths]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]
```

## Development Workflow

### Adding New Features
1. **Plan the feature** - Define requirements and API design
2. **Create database models** - Add/modify SQLAlchemy models if needed
3. **Implement service layer** - Add business logic in service classes
4. **Create API endpoints** - Add FastAPI routes with proper validation
5. **Add background tasks** - Create Celery tasks for async processing
6. **Write tests** - Add unit and integration tests
7. **Update documentation** - Update API docs and README

### Code Review Checklist
- [ ] All functions have type annotations and docstrings
- [ ] Code follows Black formatting and passes flake8 linting
- [ ] Tests cover new functionality (unit and integration)
- [ ] No secrets or credentials in code
- [ ] Error handling is comprehensive and logs appropriately
- [ ] Database queries are optimized and use proper indexing
- [ ] API endpoints have proper validation and error responses

### Deployment Considerations
- Use Docker for consistent environments
- Environment variables for configuration
- Database migrations run automatically
- Health checks for all services
- Structured logging for monitoring
- Graceful shutdown handling for background tasks

## Troubleshooting Common Issues

### Database Connection Issues
```bash
# Check database status
docker compose ps postgres

# View database logs
docker compose logs postgres

# Reset database
docker compose down postgres && docker compose up -d postgres
uv run alembic upgrade head
```

### Celery Worker Problems
```bash
# Check worker status
uv run celery -A apps.workers.main inspect active

# Monitor task queue
uv run celery -A apps.workers.main monitor

# Restart workers
docker compose restart workers
```

### Development Environment Reset
```bash
# Complete environment reset
docker compose down -v
uv sync --dev
docker compose up -d
uv run alembic upgrade head
```

This guide provides comprehensive information for developing, testing, and maintaining the SecondBrain application while following established patterns and best practices.
