"""
Finance Microservice  
Isolated FastAPI service for Financial Management
"""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from sqlalchemy.orm import Session
import os
import logging

from services.finance.app.core.config import settings
from services.finance.app.core.database import get_db, Base, engine
from services.finance.app.domains.finance.api import router as finance_router
from services.finance.app.middleware.metrics import PrometheusMiddleware
from services.finance.app.middleware.correlation import CorrelationMiddleware
from services.finance.app.core.logging import setup_logging

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

# Auth middleware (must be before other middleware)
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
    uvicorn.run(app, host="127.0.0.1", port=8003)

