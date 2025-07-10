# 🐳 DevContainer Setup Guide

This guide explains how to use Visual Studio Code DevContainers with the SecondBrain project for a consistent development environment.

## 🔧 Prerequisites

- **Visual Studio Code** with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- **Docker Desktop** or Docker Engine running on your machine
- **Git** for cloning the repository

## 🚀 Quick Start

### 1. Clone and Open the Repository

```bash
git clone <your-repository-url>
cd auto_secondbrain
code .
```

### 2. Open in DevContainer

When VS Code opens the project, you should see a notification:
> "Folder contains a Dev Container configuration file. Reopen folder to develop in a container?"

Click **"Reopen in Container"**

**Alternative methods:**
- Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
- Type "Dev Containers: Reopen in Container"
- Press Enter

### 3. Wait for Container Build

The first time will take 5-10 minutes as it:
- Builds the development container
- Installs Python dependencies with `uv`
- Sets up PostgreSQL and Redis services
- Installs VS Code extensions
- Configures the development environment

## 📁 DevContainer Configuration

The DevContainer setup consists of several files:

### `.devcontainer/devcontainer.json`
Main configuration file that defines:
- Container settings and workspace folder
- VS Code extensions to install
- Port forwarding configuration
- Post-creation commands

### `.devcontainer/docker-compose.dev.yml`
Development-specific Docker Compose override that:
- Creates the development container
- Mounts your workspace with file watching
- Connects to PostgreSQL and Redis services
- Enables Docker-in-Docker for container operations

### `infra/docker/Dockerfile.dev`
Development container definition that:
- Uses Python 3.11 as base image
- Installs system dependencies (build tools, git, PostgreSQL client)
- Installs `uv` package manager
- Sets up a non-root `vscode` user
- Installs project dependencies

## 🔌 Available Services

When the DevContainer starts, you get access to:

| Service | Port | Description |
|---------|------|-------------|
| **API Server** | 8000 | FastAPI backend (auto-starts) |
| **Streamlit UI** | 8501 | Web interface (manual start) |
| **PostgreSQL** | 5432 | Database server |
| **Redis** | 6379 | Cache and message broker |

## 🛠️ Development Workflow

### Understanding the Application Stack

SecondBrain uses a multi-service architecture:

- **Uvicorn + FastAPI**: High-performance ASGI web server running the API
- **Celery Workers**: Background task processing for vault analysis
- **Streamlit**: Interactive web UI for vault management
- **PostgreSQL**: Primary database for application data
- **Redis**: Message broker for Celery and caching

#### What is Uvicorn?

**Uvicorn** is a lightning-fast ASGI (Asynchronous Server Gateway Interface) web server implementation for Python. It's the recommended server for running FastAPI applications.

**Key Features:**
- **High Performance**: Built on uvloop and httptools for maximum speed
- **ASGI Support**: Handles async/await Python code natively
- **Hot Reloading**: Automatically restarts when code changes (development)
- **HTTP/1.1 and WebSocket**: Full protocol support
- **Production Ready**: Used by major companies in production

**Why Uvicorn for SecondBrain?**
- Handles concurrent vault uploads efficiently
- Supports async database operations
- Integrates seamlessly with FastAPI's async features
- Provides excellent development experience with hot reload

### Starting Services

The DevContainer automatically starts PostgreSQL and Redis. To start the application services:

```bash
# Terminal 1: Start API server with Uvicorn
uv run uvicorn apps.api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload \
  --reload-dir apps/api \
  --reload-dir libs

# Terminal 2: Start Celery workers for background processing
uv run celery -A apps.workers.main worker \
  --loglevel=info \
  --concurrency=2 \
  --pool=solo

# Terminal 3: Start Streamlit UI
uv run streamlit run apps/streamlit_app/main.py \
  --server.port=8501 \
  --server.address=0.0.0.0 \
  --server.runOnSave=true

# Terminal 4: Monitor Celery tasks (optional)
uv run celery -A apps.workers.main flower --port=5555
```

### Service Startup Options

#### Uvicorn Configuration Options
```bash
# Development (hot reload)
uv run uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

# Production-like (no reload)
uv run uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Debug mode (verbose logging)
uv run uvicorn apps.api.main:app --reload --log-level debug

# Custom reload directories
uv run uvicorn apps.api.main:app --reload --reload-dir apps --reload-dir libs
```

#### Celery Worker Options
```bash
# Single worker (debugging)
uv run celery -A apps.workers.main worker --loglevel=debug --concurrency=1

# Multiple workers (performance)
uv run celery -A apps.workers.main worker --loglevel=info --concurrency=4

# Specific queue processing
uv run celery -A apps.workers.main worker -Q vault_processing --loglevel=info
```

### Database Setup

```bash
# Run migrations
uv run alembic upgrade head

# Create a new migration (if needed)
uv run alembic revision --autogenerate -m "description"
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=apps --cov=libs --cov-report=html

# Run specific test types
uv run pytest -m unit          # Unit tests only
uv run pytest -m integration   # Integration tests only
uv run pytest -k "vault"       # Tests matching "vault"

# Verbose output with real-time logging
uv run pytest -v -s

# Run specific test file
uv run pytest tests/unit/test_vault_service.py

# Parallel test execution (faster)
uv run pytest -n auto
```

### Comprehensive API Testing

#### 1. Health Check and Service Status

```bash
# Test API health
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/health/detailed

# Using HTTPie (if available)
http GET localhost:8000/health

# Test with CLI tool
uv run secondbrain status
```

#### 2. Vault Upload Testing

```bash
# Create a test vault ZIP file
mkdir -p /tmp/test_vault
echo "# Test Note 1" > /tmp/test_vault/note1.md
echo "# Test Note 2" > /tmp/test_vault/note2.md
cd /tmp && zip -r test_vault.zip test_vault/

# Upload vault via API
curl -X POST "http://localhost:8000/api/v1/vaults/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/tmp/test_vault.zip" \
  -F "name=DevContainer Test Vault"

# Upload via CLI
uv run secondbrain upload /tmp/test_vault.zip --name "CLI Test Vault"
```

#### 3. Vault Management Testing

```bash
# List all vaults
curl http://localhost:8000/api/v1/vaults/

# Get specific vault (replace {vault_id} with actual ID)
curl http://localhost:8000/api/v1/vaults/{vault_id}

# Delete vault
curl -X DELETE http://localhost:8000/api/v1/vaults/{vault_id}

# Using CLI commands
uv run secondbrain list                    # List vaults
uv run secondbrain info {vault_id}         # Get vault details
uv run secondbrain delete {vault_id}       # Delete vault
```

#### 4. Interactive API Testing

Access the automatic API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### 5. Streamlit UI Testing

1. **Start Streamlit**: `uv run streamlit run apps/streamlit_app/main.py --server.port=8501 --server.address=0.0.0.0`
2. **Access UI**: http://localhost:8501
3. **Test workflows**:
   - Upload vaults through the web interface
   - Monitor processing status
   - View vault analytics
   - Test vault deletion

### Advanced Testing Scenarios

#### Database Testing

```bash
# Test database connection
uv run python -c "
from libs.database.connection import get_db_session
with get_db_session() as db:
    result = db.execute('SELECT version();').fetchone()
    print(f'PostgreSQL version: {result[0]}')
"

# Run database migrations
uv run alembic upgrade head

# Check migration status
uv run alembic current

# Create test data
uv run python -c "
from libs.database.connection import get_db_session
from libs.models.vault import VaultDB, VaultStatus
import uuid

with get_db_session() as db:
    vault = VaultDB(
        id=str(uuid.uuid4()),
        name='Test Vault',
        original_filename='test.zip',
        file_size=1024,
        storage_path='/tmp/test.zip',
        status=VaultStatus.UPLOADED
    )
    db.add(vault)
    db.commit()
    print(f'Created test vault: {vault.id}')
"
```

#### Celery Task Testing

```bash
# Check Celery worker status
uv run celery -A apps.workers.main inspect active

# Monitor task queue
uv run celery -A apps.workers.main inspect reserved

# Test task execution (if vault exists)
uv run python -c "
from apps.workers.tasks.vault_processing import process_vault
result = process_vault.delay('vault-id-here')
print(f'Task ID: {result.id}')
print(f'Task status: {result.status}')
"

# View task results
uv run celery -A apps.workers.main inspect stats

# Purge all tasks (reset queue)
uv run celery -A apps.workers.main purge
```

#### Load Testing

```bash
# Install load testing tools (if needed)
pip install httpx

# Simple load test script
uv run python -c "
import asyncio
import httpx
import time

async def test_health_endpoint():
    async with httpx.AsyncClient() as client:
        start = time.time()
        tasks = [client.get('http://localhost:8000/health') for _ in range(100)]
        responses = await asyncio.gather(*tasks)
        duration = time.time() - start

        success_count = sum(1 for r in responses if r.status_code == 200)
        print(f'Completed 100 requests in {duration:.2f}s')
        print(f'Success rate: {success_count}/100')
        print(f'Average response time: {duration/100*1000:.2f}ms')

asyncio.run(test_health_endpoint())
"
```

### Environment Testing

#### Service Integration Testing

```bash
# Test complete workflow
uv run python -c "
import requests
import time
import json

# 1. Check API health
health = requests.get('http://localhost:8000/health')
print(f'API Health: {health.json()}')

# 2. Upload a vault (requires test file)
# files = {'file': open('/tmp/test_vault.zip', 'rb')}
# data = {'name': 'Integration Test Vault'}
# upload = requests.post('http://localhost:8000/api/v1/vaults/upload', files=files, data=data)
# print(f'Upload result: {upload.status_code}')

# 3. List vaults
vaults = requests.get('http://localhost:8000/api/v1/vaults/')
print(f'Vaults count: {len(vaults.json())}')
print('Integration test completed successfully!')
"
```

#### Performance Monitoring

```bash
# Monitor resource usage
docker stats

# View application logs
docker compose logs -f api
docker compose logs -f workers

# Monitor database connections
uv run python -c "
import psycopg2
conn = psycopg2.connect('postgresql://postgres:postgres@postgres:5432/secondbrain')
cursor = conn.cursor()
cursor.execute('SELECT count(*) FROM pg_stat_activity;')
print(f'Active connections: {cursor.fetchone()[0]}')
conn.close()
"
```

### Code Quality

```bash
# Format code
uv run black .
uv run isort .

# Lint code
uv run flake8
uv run mypy .

# Run pre-commit hooks
uv run pre-commit run --all-files
```

## 📦 Installed VS Code Extensions

The DevContainer automatically installs these extensions:

- **Python** - Full Python language support
- **Black Formatter** - Code formatting
- **isort** - Import sorting
- **Flake8** - Linting
- **MyPy** - Type checking
- **Ruff** - Fast Python linter
- **YAML** - YAML file support
- **JSON** - Enhanced JSON support
- **Tailwind CSS** - CSS framework support
- **TypeScript** - TypeScript support

## 🔧 Accessing Services from Host

All services are accessible from your host machine:

- **API Documentation**: http://localhost:8000/docs
- **Streamlit UI**: http://localhost:8501
- **PostgreSQL**: `localhost:5432` (username: `postgres`, password: `postgres`)
- **Redis**: `localhost:6379`

## 🐛 Troubleshooting

### Container Won't Start

1. **Check Docker is running**:
   ```bash
   docker --version
   docker ps
   ```

2. **Rebuild container**:
   - Press `Ctrl+Shift+P`
   - Run "Dev Containers: Rebuild Container"

3. **Check logs**:
   - View Docker logs for container issues
   - Check VS Code output panel for detailed errors

### Database Connection Issues

```bash
# Test PostgreSQL connection
uv run python -c "
import psycopg2
conn = psycopg2.connect('postgresql://postgres:postgres@postgres:5432/secondbrain')
print('Database connection successful!')
conn.close()
"

# Test Redis connection
uv run python -c "
import redis
r = redis.Redis(host='redis', port=6379, db=0)
r.ping()
print('Redis connection successful!')
"

# Check database tables
uv run python -c "
from libs.database.connection import get_db_session
with get_db_session() as db:
    result = db.execute('SELECT tablename FROM pg_tables WHERE schemaname = \'public\';').fetchall()
    print('Available tables:', [r[0] for r in result])
"
```

### Service Connection Issues

```bash
# Check if services are running
docker compose ps

# View service logs
docker compose logs postgres
docker compose logs redis
docker compose logs -f api      # Follow API logs

# Restart specific service
docker compose restart postgres
docker compose restart redis

# Check service health from inside container
curl http://postgres:5432 || echo "PostgreSQL not accessible"
redis-cli -h redis ping || echo "Redis not accessible"
```

### API Server Issues

```bash
# Check if API is responding
curl -f http://localhost:8000/health || echo "API not responding"

# Debug API startup
uv run uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

# Check for port conflicts
netstat -tulpn | grep 8000
lsof -i :8000

# Test API with verbose output
curl -v http://localhost:8000/health
```

### Celery Worker Issues

```bash
# Check worker status
uv run celery -A apps.workers.main inspect ping

# Debug worker startup
uv run celery -A apps.workers.main worker --loglevel=debug

# Check Redis connection (Celery broker)
uv run python -c "
from apps.workers.main import celery_app
inspector = celery_app.control.inspect()
print('Active workers:', inspector.active())
print('Registered tasks:', inspector.registered())
"

# Restart workers
uv run celery -A apps.workers.main control shutdown
# Then restart with: uv run celery -A apps.workers.main worker --loglevel=info
```

### Development Environment Issues

```bash
# Check Python environment
which python
python --version
uv --version

# Verify project dependencies
uv tree
uv sync --dev

# Check environment variables
env | grep -E "(DATABASE_URL|REDIS_URL|ENVIRONMENT)"

# Verify file permissions
ls -la /workspace
ls -la /workspace/.venv

# Test import paths
uv run python -c "
import sys
print('Python path:')
for p in sys.path:
    print(f'  {p}')

try:
    from apps.api.main import app
    print('✓ API import successful')
except ImportError as e:
    print(f'✗ API import failed: {e}')

try:
    from libs.models.vault import VaultDB
    print('✓ Models import successful')
except ImportError as e:
    print(f'✗ Models import failed: {e}')
"
```

### Port Conflicts

If ports 5432, 6379, 8000, or 8501 are already in use on your host:

1. Stop conflicting services on your host
2. Or modify the port mappings in `.devcontainer/docker-compose.dev.yml`

### Performance Issues

- **Enable Docker Desktop WSL 2** (Windows)
- **Increase Docker memory allocation** to at least 4GB
- **Use volume mounts** instead of bind mounts for better performance

## 🚀 Quick Reference

### Essential Commands Cheat Sheet

```bash
# Start the development environment
code .                                    # Open in VS Code
# Ctrl+Shift+P → "Dev Containers: Reopen in Container"

# Service startup (run in separate terminals)
uv run uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
uv run celery -A apps.workers.main worker --loglevel=info
uv run streamlit run apps/streamlit_app/main.py --server.port=8501 --server.address=0.0.0.0

# Database operations
uv run alembic upgrade head               # Apply migrations
uv run alembic current                    # Check migration status

# Testing
uv run pytest                            # Run all tests
uv run pytest -m unit                    # Unit tests only
uv run pytest -m integration             # Integration tests only

# Code quality
uv run black . && uv run isort .         # Format code
uv run flake8 && uv run mypy .           # Lint and type check
uv run pre-commit run --all-files        # Run all hooks

# API testing
curl http://localhost:8000/health        # Health check
curl http://localhost:8000/api/v1/vaults/ # List vaults

# CLI testing
uv run secondbrain status                 # Check system status
uv run secondbrain list                   # List vaults
```

### Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **API ReDoc** | http://localhost:8000/redoc | Alternative API documentation |
| **Health Check** | http://localhost:8000/health | Service health status |
| **Streamlit UI** | http://localhost:8501 | Web interface |
| **Flower (Celery)** | http://localhost:5555 | Task monitoring (if started) |

### Common Development Tasks

#### 1. Test Vault Upload Workflow
```bash
# Create test vault
mkdir -p /tmp/test_vault && echo "# Test" > /tmp/test_vault/test.md
cd /tmp && zip -r test_vault.zip test_vault/

# Upload via API
curl -X POST "http://localhost:8000/api/v1/vaults/upload" \
  -F "file=@/tmp/test_vault.zip" -F "name=Test Vault"

# Upload via CLI
uv run secondbrain upload /tmp/test_vault.zip --name "Test Vault"
```

#### 2. Monitor Background Processing
```bash
# Start Celery monitoring
uv run celery -A apps.workers.main flower --port=5555

# Check task status
uv run celery -A apps.workers.main inspect active
uv run celery -A apps.workers.main inspect stats
```

#### 3. Database Inspection
```bash
# Connect to database
uv run python -c "
from libs.database.connection import get_db_session
from libs.models.vault import VaultDB

with get_db_session() as db:
    vaults = db.query(VaultDB).all()
    print(f'Total vaults: {len(vaults)}')
    for vault in vaults:
        print(f'- {vault.name}: {vault.status}')
"
```

#### 4. Reset Development Environment
```bash
# Reset database
docker compose down postgres && docker compose up -d postgres
uv run alembic upgrade head

# Clear Celery tasks
uv run celery -A apps.workers.main purge

# Clear Redis cache
docker compose exec redis redis-cli FLUSHALL
```

## 🔄 Container Lifecycle

### Rebuilding the Container

When you modify dependency files (`pyproject.toml`, `uv.lock`), rebuild:

1. Press `Ctrl+Shift+P`
2. Run "Dev Containers: Rebuild Container"

### Stopping the Container

- Close VS Code to stop the container
- Or press `Ctrl+Shift+P` and run "Dev Containers: Reopen Folder Locally"

### Container Data Persistence

- **Source code**: Persisted (mounted from host)
- **Database data**: Persisted via Docker volumes
- **VS Code extensions**: Persisted via Docker volumes
- **Python virtual environment**: Rebuilt on container rebuild

## 💡 Tips and Best Practices

### 1. Terminal Usage
- Use the integrated terminal (`Ctrl+` `)
- All commands should be run inside the container
- Environment variables are pre-configured

### 2. Debugging
- Python debugger is pre-configured
- Set breakpoints and use F5 to start debugging
- Works with FastAPI, Celery workers, and Streamlit

### 3. Git Operations
- Git is available inside the container
- Your host's Git credentials are automatically forwarded
- Use GitHub CLI (`gh`) for advanced operations

### 4. Package Management
- Use `uv add <package>` to add dependencies
- Changes to `pyproject.toml` require container rebuild
- Lock file (`uv.lock`) is automatically updated

### 5. Environment Variables
- Development environment variables are pre-configured
- Add custom variables to `.devcontainer/docker-compose.dev.yml`
- Use `.env` files for local overrides (ignored by Git)

## 🤝 Sharing DevContainers

To share this setup with your team:

1. **Commit DevContainer files** to your repository
2. **Update README** with DevContainer instructions
3. **Document any required environment variables**
4. **Test the setup** on a fresh checkout

The entire team will have an identical development environment! 🎉

---

For more information about DevContainers, visit the [official documentation](https://containers.dev/).
