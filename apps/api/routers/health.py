"""Health check endpoints for the API."""

from typing import Any

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from libs.database import get_db

router = APIRouter()
logger = structlog.get_logger()


@router.get("/")
async def health_check() -> dict[str, str]:
    """Perform a basic health check."""
    return {"status": "healthy", "service": "secondbrain-api"}


@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Perform a detailed health check including dependencies."""
    checks = {
        "api": "healthy",
        "database": "unknown",
    }

    # Check database
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        checks["database"] = "unhealthy"

    overall_status = (
        "healthy"
        if all(status == "healthy" for status in checks.values())
        else "unhealthy"
    )

    return {"status": overall_status, "checks": checks, "service": "secondbrain-api"}
