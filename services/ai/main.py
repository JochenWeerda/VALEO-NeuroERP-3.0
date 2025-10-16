#!/usr/bin/env python3
"""
VALEO-NeuroERP AI Service
Microservice for AI/ML functionality including RAG, Agents, and Assistants
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.api.v1.api import api_router
from app.config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    logger.info("Starting VALEO-NeuroERP AI Service...")
    
    # Initialize Vector Store
    try:
        from app.services.vector_store import initialize_vector_store
        await initialize_vector_store()
        logger.info("Vector store initialized successfully")
    except Exception as e:
        logger.warning(f"Vector store initialization failed (will retry on first use): {e}")
    
    yield
    
    logger.info("Shutting down VALEO-NeuroERP AI Service...")

# Create FastAPI application
app = FastAPI(
    title="VALEO-NeuroERP AI Service",
    description="AI/ML Microservice for ERP Intelligence",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-service",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

