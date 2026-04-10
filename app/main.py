from __future__ import annotations

from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import settings
from app.domains.shared.events import (
    startup_event_publisher,
    shutdown_event_publisher,
    startup_event_consumer,
    shutdown_event_consumer,
)
from app.middleware.audit_middleware import AuditMiddleware
from app.middleware.tenant_enforcement import TenantEnforcementMiddleware
from app.services.secrets_vault import validate_startup_secrets

app = FastAPI(title="VALEO-NeuroERP Test App")
# Middleware stack: outermost first → Tenant runs before Audit
app.add_middleware(AuditMiddleware)
app.add_middleware(TenantEnforcementMiddleware)
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def on_startup() -> None:
    validate_startup_secrets()
    app.state.startup_done = False
    app.state.secret_provider = settings.SECRET_PROVIDER
    await startup_event_publisher()
    await startup_event_consumer()
    app.state.startup_done = True


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await shutdown_event_consumer()
    await shutdown_event_publisher()

__all__ = ["app"]
