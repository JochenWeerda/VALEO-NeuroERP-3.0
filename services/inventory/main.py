"""Inventory Microservice."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.api.v1.api import api_router
from app.config import settings
from app.db.models import Base
from app.db.session import dispose_engine, get_engine
from app.dependencies import init_event_bus, shutdown_event_bus
from app.workflows import register_inventory_workflow

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Inventory Service startet…")
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await init_event_bus()
    await register_inventory_workflow()
    try:
        yield
    finally:
        await shutdown_event_bus()
        await dispose_engine()
        logger.info("Inventory Service wird heruntergefahren…")


app = FastAPI(
    title="VALEO Inventory Service",
    description="Mehrlager- und Chargenverwaltung",
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

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"service": "inventory", "status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )

