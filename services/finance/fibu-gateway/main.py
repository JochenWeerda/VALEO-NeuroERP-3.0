"""Entry point for FiBu-Gateway."""

from __future__ import annotations

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.config import settings
from app.middleware.tenant import tenant_middleware
from app.dependencies import get_event_publisher

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("FiBu-Gateway startet …")
    publisher = get_event_publisher()
    if settings.EVENT_BUS_ENABLED:
        try:
            await publisher.connect()
            logger.info("Event-Bus verbunden", extra={"url": settings.EVENT_BUS_URL})
        except Exception:
            logger.exception("Event-Bus Verbindung fehlgeschlagen – Events werden geloggt.")
    yield
    await publisher.close()
    logger.info("FiBu-Gateway fährt herunter …")


app = FastAPI(
    title="FiBu Gateway",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
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

app.middleware("http")(tenant_middleware)

app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health() -> dict[str, str]:
    publisher = get_event_publisher()
    bus_status = "connected" if publisher.is_connected else ("disabled" if not settings.EVENT_BUS_ENABLED else "degraded")
    return {"status": "ok", "eventBus": bus_status}


@app.get("/ready")
async def ready() -> dict[str, str]:
    publisher = get_event_publisher()
    bus_ok = (not settings.EVENT_BUS_ENABLED) or publisher.is_connected
    return {"status": "ready", "eventBus": "ready" if bus_ok else "initializing"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
