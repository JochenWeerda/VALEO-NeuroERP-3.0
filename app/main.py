from __future__ import annotations

from fastapi import FastAPI

from app.api.v1.api import api_router

app = FastAPI(title="VALEO-NeuroERP Test App")
app.include_router(api_router, prefix="/api/v1")

__all__ = ["app"]
