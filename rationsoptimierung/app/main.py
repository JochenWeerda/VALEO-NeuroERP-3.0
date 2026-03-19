"""
Main FastAPI application for the rations optimization tool
"""
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import feeds, requirements, optimization
from .schemas.common import BaseResponse
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Key security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Get API key from environment (in production, use proper secrets management)
API_KEY = os.getenv("RATIONS_OPTIMIZATION_API_KEY", "dev-api-key-change-in-production")

async def get_api_key(api_key_header: str = Security(api_key_header)):
    """Validate API key"""
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
        )

# Create FastAPI app (API key is applied per-router, not globally, so /health stays public)
app = FastAPI(
    title="VALEO Rations Optimization Tool",
    description="A tool for optimizing dairy cow rations using linear programming",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (API routers require authentication)
# Note: /health is defined below, not via router
app.include_router(
    feeds.router, prefix="/api/v1", tags=["feeds"],
    dependencies=[Depends(get_api_key)]
)
app.include_router(
    requirements.router, prefix="/api/v1", tags=["requirements"],
    dependencies=[Depends(get_api_key)]
)
app.include_router(
    optimization.router, prefix="/api/v1", tags=["optimization"],
    dependencies=[Depends(get_api_key)]
)

@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint with basic information
    """
    return {
        "message": "VALEO Rations Optimization Tool",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Health endpoint that doesn't require authentication (for load balancers, etc.)
@app.get("/health", response_model=BaseResponse, include_in_schema=False)
async def health_check_no_auth():
    """
    Health check endpoint without authentication (for internal monitoring)
    """
    logger.debug("Health check requested")
    return BaseResponse(
        success=True,
        message="Service is healthy"
    )

logger.info("VALEO Rations Optimization Tool application started with API key authentication")