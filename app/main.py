from __future__ import annotations

from fastapi import FastAPI

from app.api.v1.api import api_router
from app.middleware.audit_middleware import AuditMiddleware

app = FastAPI(title="VALEO-NeuroERP Test App")
app.add_middleware(AuditMiddleware)
app.include_router(api_router, prefix="/api/v1")

__all__ = ["app"]
