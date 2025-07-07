"""Main application file for the SecondBrain API."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .routers import health, vault

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifecycle."""
    # Startup
    logger.info("Starting SecondBrain API", version="0.1.0")

    yield

    # Shutdown
    logger.info("Shutting down SecondBrain API")


app = FastAPI(
    title="SecondBrain API",
    description="AI-powered knowledge management system",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(vault.router, prefix="/api/v1/vaults", tags=["vaults"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler."""
    logger.error(
        "Unhandled exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=exc,
    )

    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "SecondBrain API", "version": "0.1.0", "docs": "/docs"}
