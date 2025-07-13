# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Essential Commands
- `uv sync --dev` - Install all dependencies for development
- `uv run pytest` - Run test suite with coverage
- `uv run black . && uv run isort .` - Format code
- `uv run flake8 && uv run mypy .` - Lint and type check
- `uv run pre-commit run --all-files` - Run all pre-commit hooks

### Database Operations
- `uv run alembic upgrade head` - Apply database migrations
- `uv run alembic revision --autogenerate -m "description"` - Create new migration
- `docker compose up -d postgres` - Start required services

### Service Management
- `docker compose up -d` - Start all services in development mode
- `uv run uvicorn apps.api.main:app --reload --port 8000` - Start API server
- `uv run uvicorn apps.api.main:app --reload --port 8000` - Start API server
- `uv run streamlit run apps/streamlit_app/main.py --port 8501` - Start Streamlit UI

### CLI Tools
- `uv run secondbrain status` - Check system health
- `uv run secondbrain upload <path> --name "name"` - Upload vault
- `uv run secondbrain list` - List all vaults

## Architecture Overview

SecondBrain is a Python monorepo using uv for dependency management with the following structure:

### Core Services
- **API Service** (`apps/api/`) - FastAPI backend with vault ingestion endpoints
- **Streamlit App** (`apps/streamlit_app/`) - Web UI for vault management
- **CLI** (`apps/cli/`) - Command-line administration tools

### Shared Libraries
- **Models** (`libs/models/`) - SQLAlchemy and Pydantic models for vaults and processing jobs
- **Database** (`libs/database/`) - Database connections, migrations, and session management
- **Cloud Storage** (`libs/cloud_storage/`) - Google Drive integration with abstract interface
- **Vector DB** (`libs/vector_db/`) - Vector database abstraction (in-memory implementation)
- **LLM Clients** (`libs/llm_clients/`) - OpenAI and Anthropic API wrappers

### Development Infrastructure
- **Docker Compose** - Local development environment with PostgreSQL
- **Devcontainer** - VSCode development container configuration
- **Alembic** - Database migration management
- **Pre-commit hooks** - Code quality enforcement

## Key Patterns

### Vault Processing Flow
1. Upload via `/api/v1/vaults/upload` endpoint in `apps/api/routers/vault.py`
2. File validation and storage in `apps/api/services/vault_service.py`
3. Synchronous processing in `apps/api/services/vault_service.py`
4. Status tracking through `VaultStatus` and `ProcessingStatus` enums

### Database Models
- Use `libs/models/base.py` for common mixins (`TimestampMixin`, `UUIDMixin`)
- SQLAlchemy models in `*DB` classes, Pydantic models for API serialization
- All models inherit from shared base classes for consistency

### Configuration Management
- Environment-specific settings in each app's `config.py`
- Shared environment variables via `.env` file
- Pydantic BaseSettings for type-safe configuration

### Error Handling
- Structured logging with `structlog` throughout all services
- HTTP exceptions in API layer with appropriate status codes
- Robust error handling with proper HTTP status codes

## Testing Strategy

- **Unit tests** in `tests/unit/` for isolated component testing
- **Integration tests** in `tests/integration/` for API and database testing
- Test fixtures in `tests/conftest.py` for database and file setup
- Use pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`

## Code Style and Formatting Guidelines

### Python Code Standards
- **Line length**: 88 characters (Black default)
- **Import organization**: Use isort with Black profile
- **Type annotations**: Required for all functions and methods
- **Docstrings**: Required for all modules, classes, and public methods

### Formatting Tools Configuration
```toml
[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["apps", "libs"]

[tool.mypy]
python_version = "3.11"
disallow_untyped_defs = true
disallow_incomplete_defs = true
```

### Code Generation Guidelines

#### When Creating New Modules
1. Always start with a module docstring explaining purpose
2. Import structure should follow this order:
   - Standard library imports
   - Third-party imports
   - Local imports (apps.*, libs.*)
3. Use absolute imports from project root
4. Follow existing naming conventions in similar modules

#### When Creating New Classes
```python
"""Module docstring explaining the purpose."""

from typing import Optional, List
from sqlalchemy.orm import Session
from libs.models.base import BaseModel

class ExampleService:
    """Service for managing example resources."""

    def __init__(self, db: Session) -> None:
        """Initialize the service with database session."""
        self.db = db

    async def create_example(self, data: ExampleCreate) -> Example:
        """Create a new example resource."""
        # Implementation here
        pass
```

#### Database Models Pattern
```python
# SQLAlchemy DB Model
class ExampleDB(BaseModel, TimestampMixin, UUIDMixin):
    """Database model for examples."""

    __tablename__ = "examples"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ExampleStatus] = mapped_column(Enum(ExampleStatus))

# Pydantic API Models
class ExampleBase(BaseModel):
    """Base example model."""
    name: str

class ExampleCreate(ExampleBase):
    """Model for creating examples."""
    pass

class Example(ExampleBase):
    """Complete example model with ID."""
    id: str
    status: ExampleStatus
    created_at: datetime
```

#### API Endpoint Pattern
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from apps.api.dependencies import get_db

router = APIRouter(prefix="/examples", tags=["examples"])

@router.post("/", response_model=Example, status_code=status.HTTP_201_CREATED)
async def create_example(
    example_data: ExampleCreate,
    db: Session = Depends(get_db)
) -> Example:
    """Create a new example."""
    service = ExampleService(db)
    return await service.create_example(example_data)
```

#### Service Method Pattern
```python
import structlog
from libs.models.vault import VaultStatus

logger = structlog.get_logger()

class ExampleService:
    async def process_example(self, example_id: str) -> dict[str, Any]:
        """Process an example resource."""
        try:
            logger.info("Processing example", example_id=example_id)
            # Implementation here
            return {"status": "completed", "example_id": example_id}
        except Exception as e:
            logger.error("Example processing failed", example_id=example_id, error=str(e))
            # Update status to failed
            await self.update_example_status(example_id, ExampleStatus.FAILED, str(e))
            raise
```

### Error Handling Patterns
```python
# Service layer
async def get_example(self, example_id: str) -> Optional[Example]:
    """Get example by ID."""
    db_example = self.db.query(ExampleDB).filter(ExampleDB.id == UUID(example_id)).first()
    if not db_example:
        return None
    return Example.from_orm(db_example)

# API layer
@router.get("/{example_id}", response_model=Example)
async def get_example(example_id: str, db: Session = Depends(get_db)) -> Example:
    """Get example by ID."""
    service = ExampleService(db)
    example = await service.get_example(example_id)
    if not example:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Example {example_id} not found"
        )
    return example
```

### Testing Patterns
```python
import pytest
from httpx import AsyncClient
from libs.models.vault import VaultDB, VaultStatus

@pytest.mark.integration
async def test_create_example(client: AsyncClient, db_session):
    """Test creating a new example."""
    response = await client.post(
        "/api/v1/examples/",
        json={"name": "Test Example"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Example"
    assert data["status"] == "created"
    assert "id" in data
```

## Important Notes

- All Python code uses absolute imports from root level
- Database sessions managed via FastAPI dependencies
- Service methods handle processing synchronously within API requests
- Vector database currently uses in-memory implementation for development
- Frontend placeholder exists but requires full implementation
- All HTTP requests must include timeout parameters for security
- Use structured logging with `structlog` for all services
- Follow the existing patterns for configuration management
- Never commit secrets or API keys to the repository

## Security Guidelines

- Always use timeout parameters in HTTP requests (10s for quick operations, 60s for uploads)
- Validate all input data using Pydantic models
- Use parameterized queries for database operations
- Log security-relevant events using structured logging
- Never expose internal error details in API responses
- Use environment variables for all configuration secrets

## Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:
- **trailing-whitespace** - Remove trailing whitespace
- **end-of-file-fixer** - Ensure files end with newline
- **check-yaml** - Validate YAML files
- **black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting with docstring checks
- **mypy** - Type checking
- **bandit** - Security scanning

Run `uv run pre-commit install` to set up hooks locally.

## Git Commit Guidelines

When creating commits, follow these guidelines:

- Write clear, descriptive commit messages that explain what was changed and why
- Use conventional commit format when appropriate (e.g., "feat:", "fix:", "docs:")
- Keep the first line under 72 characters
- **NEVER include references to Claude Code or AI assistance in commit messages**
- Do not use phrases like "made by Claude Code", "Co-Authored-By: Claude", or similar AI attributions
- Focus on the technical changes and their purpose rather than who or what created them
