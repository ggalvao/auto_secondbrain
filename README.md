# 🧠 SecondBrain

An AI-powered knowledge management system designed to process, analyze, and enhance your Obsidian vaults using modern AI capabilities.

## 🏗️ Architecture

SecondBrain is built as a Python monorepo with the following components:

### Applications
- **`apps/api/`** - FastAPI backend service providing REST APIs for vault management
- **`apps/workers/`** - Celery worker services for background processing and AI analysis
- **`apps/streamlit_app/`** - Streamlit UI for rapid prototyping and vault management
- **`apps/frontend/`** - Future TypeScript/React application (placeholder)
- **`apps/cli/`** - Command-line tools for administration and testing

### Shared Libraries
- **`libs/models/`** - Shared data models and Pydantic/SQLAlchemy schemas
- **`libs/database/`** - Database connection, migrations, and ORM setup
- **`libs/cloud_storage/`** - Google Drive integration and cloud storage abstraction
- **`libs/vector_db/`** - Vector database abstraction layer for embeddings
- **`libs/llm_clients/`** - OpenAI/Anthropic API wrappers and utilities

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- [uv](https://github.com/astral-sh/uv) package manager

### Option 1: Development with DevContainers (Recommended)

For a consistent development environment with all dependencies pre-configured:

**Prerequisites:**
- Visual Studio Code with [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- Docker Desktop or Docker Engine

**Setup:**
1. **Clone and open the repository:**
   ```bash
   git clone <repository-url>
   cd auto_secondbrain
   code .
   ```

2. **Open in DevContainer:**
   - VS Code will show a notification about the DevContainer configuration
   - Click "Reopen in Container"
   - Or press `Ctrl+Shift+P` and run "Dev Containers: Reopen in Container"

3. **Wait for container setup** (5-10 minutes first time)

4. **Start the services:**
   ```bash
   # Terminal 1: Start API server
   uv run uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

   # Terminal 2: Start Celery workers
   uv run celery -A apps.workers.main worker --loglevel=info

   # Terminal 3: Start Streamlit UI (optional)
   uv run streamlit run apps/streamlit_app/main.py --server.port=8501 --server.address=0.0.0.0
   ```

**DevContainer Benefits:**
- Pre-configured PostgreSQL and Redis services
- All VS Code extensions and settings installed
- Consistent Python environment with uv
- Pre-run database migrations
- No local dependency conflicts

> 📖 **For comprehensive DevContainer setup, testing, and troubleshooting instructions, see [DEVCONTAINER_GUIDE.md](DEVCONTAINER_GUIDE.md)**

### Option 2: Local Development Setup

For development without DevContainers:

1. **Clone and setup environment:**
   ```bash
   git clone <repository-url>
   cd auto_secondbrain
   cp .env.example .env
   ```

2. **Install dependencies:**
   ```bash
   uv sync --dev
   ```

3. **Start development services:**
   ```bash
   docker-compose up -d postgres redis
   ```

4. **Run database migrations:**
   ```bash
   uv run alembic upgrade head
   ```

5. **Start the API server:**
   ```bash
   uv run uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Start Celery workers (in another terminal):**
   ```bash
   uv run celery -A apps.workers.main worker --loglevel=info
   ```

7. **Start Streamlit UI (optional):**
   ```bash
   uv run streamlit run apps/streamlit_app/main.py --server.port=8501
   ```

### Option 3: Using Docker Compose (All Services)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Accessing the Application

After starting the services, you can access:
- **API Documentation**: http://localhost:8000/docs
- **Streamlit UI**: http://localhost:8501
- **Health Check**: http://localhost:8000/health

## 🔧 Development Commands

### Package Management
```bash
# Install dependencies
uv sync --dev

# Add new dependency
uv add <package>

# Add dev dependency
uv add --dev <package>
```

### Database Operations
```bash
# Create migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

### Testing
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

### CLI Usage
```bash
# Check system status
uv run secondbrain status

# Upload a vault
uv run secondbrain upload path/to/vault.zip --name "My Vault"

# List vaults
uv run secondbrain list

# Get vault details
uv run secondbrain info <vault-id>

# Delete vault
uv run secondbrain delete <vault-id>
```

## 📁 Vault Processing Pipeline

1. **Upload**: ZIP file uploaded via API endpoint
2. **Validation**: File format and content validation
3. **Storage**: File stored in configured storage location
4. **Extraction**: ZIP contents extracted and analyzed
5. **Processing**: Background workers process vault content
6. **Analysis**: AI-powered content analysis and embedding generation

## 🔌 API Endpoints

### Health Check
- `GET /health/` - Basic health check
- `GET /health/detailed` - Detailed health check with dependencies

### Vault Management
- `POST /api/v1/vaults/upload` - Upload vault ZIP file
- `GET /api/v1/vaults/` - List all vaults
- `GET /api/v1/vaults/{id}` - Get vault details
- `DELETE /api/v1/vaults/{id}` - Delete vault

## 🎯 Current Features

- ✅ Vault upload and validation
- ✅ Background processing pipeline
- ✅ Basic content extraction and analysis
- ✅ REST API with comprehensive endpoints
- ✅ Streamlit UI for vault management
- ✅ CLI tools for administration
- ✅ Docker containerization
- ✅ Database migrations and ORM

## 🚧 Planned Features

- [ ] AI-powered content analysis and insights
- [ ] Vector embeddings and semantic search
- [ ] Knowledge graph extraction
- [ ] Advanced analytics and visualizations
- [ ] Google Drive integration
- [ ] React frontend application
- [ ] Real-time processing status updates
- [ ] User authentication and authorization

## 🏢 Production Deployment

This system is currently optimized for local development. For production deployment, consider:

- Container orchestration (Kubernetes)
- Load balancing and scaling
- Production database setup
- Message queue clustering
- SSL/TLS configuration
- Monitoring and observability
- Backup and disaster recovery

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details.
