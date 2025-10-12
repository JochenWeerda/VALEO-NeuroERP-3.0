"""
Inventory Microservice
Isolated FastAPI service for Inventory & Warehouse Management
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from sqlalchemy.orm import Session
import logging

from app.core.config import settings
from app.core.database import get_db, Base, engine
from app.domains.inventory.api import router as inventory_router
from app.middleware.metrics import PrometheusMiddleware
from app.middleware.correlation import CorrelationMiddleware
from app.core.logging import setup_logging

setup_logging(json_format=True)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="VALEO Inventory Service",
    description="Inventory & Warehouse Management Microservice",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(PrometheusMiddleware)
app.add_middleware(CorrelationMiddleware)

app.include_router(inventory_router, prefix="/api/v1/inventory", tags=["Inventory"])

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/health")
async def health():
    return {"service": "inventory", "status": "healthy"}

@app.get("/ready")
async def ready(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"service": "inventory", "status": "ready", "database": "healthy"}
    except Exception as e:
        return {"service": "inventory", "status": "not_ready", "error": str(e)}

@app.on_event("startup")
async def startup():
    logger.info("Inventory Service starting...")
    Base.metadata.create_all(bind=engine)
    logger.info("Inventory Service ready on port 8002")

@app.on_event("shutdown")
async def shutdown():
    logger.info("Inventory Service shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

