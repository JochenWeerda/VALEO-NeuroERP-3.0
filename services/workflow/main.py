"""
Workflow Microservice
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from pydantic import ValidationError

from app.config import settings
from app.api.v1.api import api_router
from app.dependencies import configure_dependencies, get_engine
from app.integration.event_bus import EventBus
from app.schemas.workflow import EventPayload
from app.storage.repository import WorkflowRepository

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


logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Workflow Service startet...")

    repository = WorkflowRepository()
    await repository.create_schema()

    event_bus = None
    if settings.EVENT_BUS_ENABLED:
        event_bus = EventBus(settings.EVENT_BUS_URL, settings.EVENT_BUS_SUBJECT_PREFIX)

    configure_dependencies(repository, event_bus)
    engine = get_engine()
    await engine.bootstrap_from_repository()

    async def _handle_event(message: dict) -> None:
        try:
            payload = EventPayload.model_validate(message)
        except ValidationError as exc:
            logger.warning("Ungültiges Event vom Event-Bus: %s", exc)
            return
        await engine.handle_event(payload.event_type, payload.tenant, payload.data)

    if event_bus:
        try:
            await event_bus.connect(_handle_event)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Event-Bus konnte nicht verbunden werden: %s", exc)
            event_bus = None

    try:
        yield
    finally:
        if event_bus:
            await event_bus.close()
    logger.info("Workflow Service wird heruntergefahren...")


app = FastAPI(
    title="VALEO Workflow Service",
    description="Workflow- und Saga-Orchestrierung für NeuroERP",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
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

app.include_router(api_router, prefix="/api/v1")

if settings.METRICS_ENABLED:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


@app.get("/health")
async def health() -> dict:
    return {"service": "workflow", "status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
