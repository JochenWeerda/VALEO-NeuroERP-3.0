"""
CRM Microservice
Isolated FastAPI service for Customer Relationship Management
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from sqlalchemy.orm import Session
import os
import logging

from app.core.config import settings
from app.core.database import get_db, Base, engine
from app.domains.crm.api import router as crm_router
from app.middleware.metrics import PrometheusMiddleware
from app.middleware.correlation import CorrelationMiddleware
from app.core.logging import setup_logging

try:
    from auth_shared import AuthMiddleware
except ImportError as _auth_import_error:  # pragma: no cover - haengt am Image
    # Frueher wurde hier stillschweigend auf None gesetzt und die Middleware
    # unten einfach weggelassen - protokolliert wurde nur der Erfolgsfall. Der
    # Dienst lief dann ohne Authentifizierung und schwieg darueber. Der Grund
    # wird jetzt festgehalten und unten ausgewertet.
    AuthMiddleware = None  # type: ignore[assignment,misc]
    AUTH_IMPORT_ERROR: Exception | None = _auth_import_error
else:
    AUTH_IMPORT_ERROR = None

# Setup logging
setup_logging(json_format=True)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("CRM Service starting...")
    Base.metadata.create_all(bind=engine)
    logger.info("CRM Service ready on port 8001")
    yield
    logger.info("CRM Service shutting down...")


# Create FastAPI app
app = FastAPI(
    title="VALEO CRM Service",
    description="Customer Relationship Management Microservice",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth middleware
if AuthMiddleware is not None:
    app.add_middleware(AuthMiddleware)
    logger.info("Auth middleware enabled")
elif os.getenv("ALLOW_UNAUTHENTICATED_SERVICE", "").strip().lower() in {"1", "true", "yes"}:
    logger.critical(
        "Auth-Middleware NICHT aktiv: auth_shared ist nicht importierbar (%s). "
        "Fortgesetzt, weil ALLOW_UNAUTHENTICATED_SERVICE gesetzt ist - dieser "
        "Dienst beantwortet Anfragen ohne Authentifizierung.",
        AUTH_IMPORT_ERROR,
    )
else:
    raise RuntimeError(
        "auth_shared ist nicht importierbar (%s). Der Dienst wuerde ohne "
        "Authentifizierung laufen und startet deshalb nicht. Entweder "
        "packages/auth-shared ins Image aufnehmen oder den Betrieb ohne "
        "Authentifizierung ausdruecklich mit ALLOW_UNAUTHENTICATED_SERVICE=true "
        "erlauben." % (AUTH_IMPORT_ERROR,)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
