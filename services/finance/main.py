"""
Finance Microservice  
Isolated FastAPI service for Financial Management
"""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from sqlalchemy.orm import Session
import logging

from services.finance.app.core.config import settings
from services.finance.app.core.database import get_db, Base, engine
from services.finance.app.domains.finance.api import router as finance_router
from services.finance.app.middleware.metrics import PrometheusMiddleware
from services.finance.app.middleware.correlation import CorrelationMiddleware
from services.finance.app.core.logging import setup_logging

setup_logging(json_format=True)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Finance Service starting…")
    Base.metadata.create_all(bind=engine)
    try:
        yield
    finally:
        logger.info("Finance Service shutting down…")


app = FastAPI(
    title="VALEO Finance Service",
    description="Financial Management Microservice",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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

app.include_router(finance_router, prefix="/api/v1", tags=["Finance"])

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/health")
async def health():
    return {"service": "finance", "status": "healthy"}

@app.get("/ready")
async def ready(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"service": "finance", "status": "ready", "database": "healthy"}
    except Exception as e:
        return {"service": "finance", "status": "not_ready", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)

