"""Zoll- & Exportkontrollservice."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.api.v1.api import api_router
from app.config import settings
from app.db.models import Base
from app.db.session import engine
from app.dependencies import (
    configure_event_bus,
    configure_sanctions_provider,
    refresh_sanctions_data,
    shutdown_event_bus,
)
from app.workflows import register_export_workflow

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
)
logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


async def _refresh_sanctions() -> None:
    refreshed = await refresh_sanctions_data()
    if not refreshed:
        logger.debug("Sanktionsrefresh wurde übersprungen oder befindet sich im Backoff.")


@asynccontextmanager
async def lifespan(_: FastAPI):
    global _scheduler
    logger.info("Zoll-Service startet ...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await configure_event_bus()
    await configure_sanctions_provider()
    await register_export_workflow()

    _scheduler = AsyncIOScheduler()
    trigger = IntervalTrigger(minutes=settings.SANCTIONS_REFRESH_INTERVAL_MINUTES)
    _scheduler.add_job(lambda: asyncio.create_task(_refresh_sanctions()), trigger)
    _scheduler.start()

    try:
        yield
    finally:
        if _scheduler:
            _scheduler.shutdown(wait=False)
            _scheduler = None
        await shutdown_event_bus()
        await engine.dispose()
        logger.info("Zoll-Service heruntergefahren.")


app = FastAPI(
    title="VALEO Zoll Service",
    description="Sanktionslistenscreening, Exportgenehmigungen, Präferenzkalkulation",
    version="0.1.0",
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

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"service": "zoll", "status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
