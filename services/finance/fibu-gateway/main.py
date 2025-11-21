"""Entry point for FiBu-Gateway."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.config import settings
from app.middleware.tenant import tenant_middleware
from app.dependencies import get_event_publisher

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

