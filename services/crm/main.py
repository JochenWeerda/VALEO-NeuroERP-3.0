"""
CRM Microservice
Isolated FastAPI service for Customer Relationship Management
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from sqlalchemy.orm import Session
import logging

from app.core.config import settings
from app.core.database import get_db, Base, engine
from app.domains.crm.api import router as crm_router
from app.middleware.metrics import PrometheusMiddleware
from app.middleware.correlation import CorrelationMiddleware
from app.core.logging import setup_logging

# Setup logging
setup_logging(json_format=True)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="VALEO CRM Service",
    description="Customer Relationship Management Microservice",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics & Correlation
app.add_middleware(PrometheusMiddleware)
app.add_middleware(CorrelationMiddleware)

# Include routers
app.include_router(crm_router, prefix="/api/v1/crm", tags=["CRM"])

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Health checks
@app.get("/health")
async def health():
    return {"service": "crm", "status": "healthy"}

@app.get("/ready")
async def ready(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"service": "crm", "status": "ready", "database": "healthy"}
    except Exception as e:
        return {"service": "crm", "status": "not_ready", "error": str(e)}

# Startup
@app.on_event("startup")
async def startup():
    logger.info("CRM Service starting...")
    # Create tables if not exist
    Base.metadata.create_all(bind=engine)
    logger.info("CRM Service ready on port 8001")

# Shutdown
@app.on_event("shutdown")
async def shutdown():
    logger.info("CRM Service shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

