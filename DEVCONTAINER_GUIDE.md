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

### Starting Services

The DevContainer automatically starts PostgreSQL and Redis. To start the application services:

```bash
# Start API server (in terminal 1)
uv run uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload

# Start Celery workers (in terminal 2)
uv run celery -A apps.workers.main worker --loglevel=info

# Start Streamlit UI (in terminal 3)
uv run streamlit run apps/streamlit_app/main.py --server.port=8501 --server.address=0.0.0.0
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
uv run pytest --cov

# Run specific test types
uv run pytest -m unit
uv run pytest -m integration
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
```

### Port Conflicts

If ports 5432, 6379, 8000, or 8501 are already in use on your host:

1. Stop conflicting services on your host
2. Or modify the port mappings in `.devcontainer/docker-compose.dev.yml`

### Performance Issues

- **Enable Docker Desktop WSL 2** (Windows)
- **Increase Docker memory allocation** to at least 4GB
- **Use volume mounts** instead of bind mounts for better performance

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