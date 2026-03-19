from fastapi import APIRouter, Depends
from ...schemas.common import HealthCheckResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint
    """
    logger.debug("Health check requested")
    return HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        services={
            "api": "running",
            "optimizer": "available"
        }
    )