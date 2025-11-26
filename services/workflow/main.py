"""
Workflow Microservice
"""

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


