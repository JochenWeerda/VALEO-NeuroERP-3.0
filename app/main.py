"""Auth-freie Test-Kompatibilitaetsschicht fuer ``api_router``.

Diese App ist **nicht** die Produktionsanwendung. Der Container faehrt
``uvicorn main:app`` aus der Wurzel-``main.py``; dort haengen 251 weitere
Routen und unter anderem ``BearerAuthMiddleware``. Hier fehlt die
Auth-Middleware bewusst, damit Tests ``api_router`` direkt ansprechen koennen
(Prozesskern-Welle 9, Paket A).

Deshalb: **nicht als Quelle fuer Vertraege, Specs oder Laufzeit-Gates
verwenden.** Bis 2026-09-10 erzeugte ``scripts/generate_openapi.py`` die
veroeffentlichte OpenAPI-Spec aus dieser App; sie trug daher den Titel
"VALEO-NeuroERP Test App" und war um 193 Pfade zu klein
(SPEC-SOURCE-REALAPP-20260910). Verbleibender Nutzer ist ``tests/conftest.py``.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api.v1.api import api_router, ws_router
from app.api.numbering import router as numbering_router
from app.routers.sse_router import router as sse_router
from app.core.config import settings
import app.core.container_config  # noqa: F401 — registriert DI-Factories (container.resolve in Endpoints)
from app.core.exceptions import register_domain_exception_handlers
from app.domains.shared.events import (
    startup_event_publisher,
    shutdown_event_publisher,
    startup_event_consumer,
    shutdown_event_consumer,
)
from app.middleware.audit_middleware import AuditMiddleware
from app.middleware.tenant_enforcement import TenantEnforcementMiddleware
from app.services.secrets_vault import validate_startup_secrets


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # startup
    validate_startup_secrets()
    app.state.startup_done = False
    app.state.secret_provider = settings.SECRET_PROVIDER
    await startup_event_publisher()
    await startup_event_consumer()
    app.state.startup_done = True

    yield

    # shutdown
    await shutdown_event_consumer()
    await shutdown_event_publisher()


app = FastAPI(title="VALEO-NeuroERP Test App", lifespan=lifespan)
register_domain_exception_handlers(app)
# Middleware stack: outermost first → Tenant runs before Audit
app.add_middleware(AuditMiddleware)
app.add_middleware(TenantEnforcementMiddleware)
app.include_router(api_router, prefix="/api/v1")
app.include_router(ws_router, prefix="/api/v1")
app.include_router(numbering_router, prefix="/api/numbering")
app.include_router(sse_router)  # absolute paths: /api/events, /api/stream/{channel}

__all__ = ["app"]
