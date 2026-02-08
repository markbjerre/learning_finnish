"""Health check endpoints for Learning Finnish API"""

from fastapi import APIRouter
from datetime import datetime
from app.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Comprehensive health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow()
    )


@router.get("/health/simple")
async def simple_health_check():
    """Lightweight health check endpoint"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
