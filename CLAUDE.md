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
- `docker-compose up -d postgres redis` - Start required services

### Service Management
- `docker-compose up -d` - Start all services in development mode
- `uv run uvicorn apps.api.main:app --reload --port 8000` - Start API server
- `uv run celery -A apps.workers.main worker --loglevel=info` - Start Celery workers
- `uv run streamlit run apps/streamlit_app/main.py --port 8501` - Start Streamlit UI

### CLI Tools
- `uv run secondbrain status` - Check system health
- `uv run secondbrain upload <path> --name "name"` - Upload vault
- `uv run secondbrain list` - List all vaults

## Architecture Overview

SecondBrain is a Python monorepo using uv for dependency management with the following structure:

### Core Services
- **API Service** (`apps/api/`) - FastAPI backend with vault ingestion endpoints
- **Workers** (`apps/workers/`) - Celery workers for background vault processing
- **Streamlit App** (`apps/streamlit_app/`) - Web UI for vault management
- **CLI** (`apps/cli/`) - Command-line administration tools

### Shared Libraries
- **Models** (`libs/models/`) - SQLAlchemy and Pydantic models for vaults and processing jobs
- **Database** (`libs/database/`) - Database connections, migrations, and session management
- **Cloud Storage** (`libs/cloud_storage/`) - Google Drive integration with abstract interface
- **Vector DB** (`libs/vector_db/`) - Vector database abstraction (in-memory implementation)
- **LLM Clients** (`libs/llm_clients/`) - OpenAI and Anthropic API wrappers

### Development Infrastructure
- **Docker Compose** - Local development environment with PostgreSQL and Redis
- **Devcontainer** - VSCode development container configuration
- **Alembic** - Database migration management
- **Pre-commit hooks** - Code quality enforcement

## Key Patterns

### Vault Processing Flow
1. Upload via `/api/v1/vaults/upload` endpoint in `apps/api/routers/vault.py`
2. File validation and storage in `apps/api/services/vault_service.py`
3. Background processing triggered via Celery tasks in `apps/workers/tasks/vault_processing.py`
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
- Celery task retries with exponential backoff

## Testing Strategy

- **Unit tests** in `tests/unit/` for isolated component testing
- **Integration tests** in `tests/integration/` for API and database testing
- Test fixtures in `tests/conftest.py` for database and file setup
- Use pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`

## Important Notes

- All Python code uses absolute imports from root level
- Database sessions managed via FastAPI dependencies
- Celery tasks are atomic and handle their own database connections
- Vector database currently uses in-memory implementation for development
- Frontend placeholder exists but requires full implementation
