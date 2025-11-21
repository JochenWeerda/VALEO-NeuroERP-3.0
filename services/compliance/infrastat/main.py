"""InfraStat Compliance Microservice."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.api.v1.api import api_router
from app.config import settings
from app.db.models import Base
from app.db.session import SessionLocal, engine
from app.dependencies import configure_event_bus, get_event_bus, shutdown_event_bus
from app.services.scheduler_tasks import ensure_periodic_batches, trigger_workflow_for_ready_batches
from app.workflow import register_intrastat_workflow

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
)
logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


async def _run_scheduler_cycle() -> None:
    async with SessionLocal() as session:
        async with session.begin():
            await ensure_periodic_batches(session)
        async with session.begin():
            await trigger_workflow_for_ready_batches(session, get_event_bus())


@asynccontextmanager
async def lifespan(_: FastAPI):
    global _scheduler
    logger.info("InfraStat Service startet...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await configure_event_bus()
    await register_intrastat_workflow()

    if settings.SCHEDULER_ENABLED:
        trigger = CronTrigger.from_crontab(settings.SCHEDULER_CRON)
        _scheduler = AsyncIOScheduler()
        _scheduler.add_job(lambda: asyncio.create_task(_run_scheduler_cycle()), trigger)
        _scheduler.start()
        await _run_scheduler_cycle()

    try:
        yield
    finally:
        if _scheduler:
            _scheduler.shutdown(wait=False)
            _scheduler = None
        await shutdown_event_bus()
        await engine.dispose()
        logger.info("InfraStat Service heruntergefahren.")


app = FastAPI(
    title="VALEO InfraStat Service",
    description="Automatisierte Intrastat/InfraStat Meldungen",
    version="0.2.0",
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
    return {"service": "infrastat", "status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )

