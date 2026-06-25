#!/usr/bin/env python3
"""
VALEO-NeuroERP FastAPI Application
Main entry point for the ERP system API
"""

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
import logging
import time
import asyncio
import contextlib
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import create_tables, engine
from app.api.v1.api import api_router
from app.api.v1.endpoints import policies as policies_v1
from app.core.logging import setup_logging
from app.core.security import require_bearer_token
from app.core.container_config import configure_container  # Import container configuration
from app.core.tenant_context import reset_current_tenant_id, set_current_tenant_id
from app.domains.shared.events import startup_event_publisher, shutdown_event_publisher
from app.workers.outbox_publisher import start_outbox_worker, stop_outbox_worker
from modules.bootstrap import initialize_module_registry

# Logger muss vor der Verwendung definiert werden
logger = logging.getLogger(__name__)

from app.policy.router import router as policy_router  # Policy Manager
from app.auth.router import router as auth_router  # Authentication
from app.documents.router import router as documents_router  # Documents & Flows
from app.forms.router import router as forms_router  # Form Specs
from app.lookup.router import router as lookup_router  # Lookup/Autocomplete
from app.routers.print_router import router as print_router  # Print & Archive
from app.routers.export_router import router as export_router  # Export CSV/XLSX
from app.routers.workflow_router import router as workflow_router  # Workflow & Approval
from app.routers.sse_router import router as sse_router  # SSE Streams
from app.routers.verify_router import router as verify_router  # Document Verification
# Legacy GDPR router removed — consolidated into app.api.v1.endpoints.gdpr
from app.routers.numbering_router import router as numbering_router  # Numbering Service
from app.routers.admin_dms_router import router as admin_dms_router  # Admin DMS Integration
from app.routers.dms_webhook_router import router as dms_webhook_router  # DMS Webhooks & Inbox
from app.routers.fibu_router import router as fibu_router  # Finanzbuchhaltung (130 Masken)
from app.routers.translations_router import router as translations_router  # Übersetzungen (/api/translations)
from app.routers.vies_router import router as vies_router  # VIES USt-IdNr.-Prüfung (/api/vies)
from app.routers.contracts_router import router as contracts_router  # Verträge (contracts-v2 Maske)
from app.api.v1.endpoints.kontrakte import router as kontrakte_router  # Valeo Kontraktmodul
from app.api.v1.endpoints import opportunities as opportunities_endpoints  # CRM-Sales (Frontend /api/crm-sales)

# Import domain-specific routers with error handling
try:
    from app.crm.router import router as crm_router  # CRM
except ImportError:
    crm_router = None
    logger.debug("CRM router not available (optional module)")

try:
    from app.finance.router import router as finance_router  # Finance (DATEV, SEPA)
except ImportError:
    finance_router = None
    logger.debug("Finance router not available (optional module)")

try:
    from app.einkauf.router import router as einkauf_router  # Einkauf/Beschaffung
except ImportError:
    einkauf_router = None
    logger.debug("Einkauf router not available (optional module)")

try:
    from app.api.v1.endpoints.purchase_workflow import router as purchase_workflow_router
except ImportError:
    purchase_workflow_router = None
    logger.debug("Purchase workflow router not available (optional module)")

# Setup logging
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    outbox_task = None

    # SC-AUTH-002: API_DEV_TOKEN darf in Produktion nicht gesetzt sein
    if settings.APP_ENV == "production" and settings.API_DEV_TOKEN is not None:
        raise RuntimeError(
            "SECURITY: API_DEV_TOKEN must not be set in production. "
            "Remove API_DEV_TOKEN from your environment or set APP_ENV != 'production'."
        )

    # SC-SECRETS-001: SECRET_KEY und ENCRYPTION_KEY müssen in Produktion aus Env kommen
    if settings.APP_ENV == "production":
        if not settings.SECRET_KEY:
            raise RuntimeError(
                "SECURITY: SECRET_KEY must be set via environment variable in production."
            )
        if not settings.ENCRYPTION_KEY:
            raise RuntimeError(
                "SECURITY: ENCRYPTION_KEY must be set via environment variable in production."
            )
    else:
        # Dev-Modus: generiere ephemere Keys mit Warnung (werden bei Restart neu erzeugt)
        import secrets as _secrets
        if not settings.SECRET_KEY:
            settings.SECRET_KEY = _secrets.token_urlsafe(32)
            logger.warning(
                "WARNING: SECRET_KEY nicht gesetzt - ephemerer Dev-Key generiert. "
                "Tokens werden nach Restart ungueltig."
            )
        if not settings.ENCRYPTION_KEY:
            settings.ENCRYPTION_KEY = _secrets.token_urlsafe(32)
            logger.warning(
                "WARNING: ENCRYPTION_KEY nicht gesetzt - ephemerer Dev-Key generiert."
            )
        # Dev-Modus: API_DEV_TOKEN auf 'dev-token' setzen falls nicht konfiguriert
        if not settings.API_DEV_TOKEN:
            settings.API_DEV_TOKEN = "dev-token"
            logger.warning(
                "WARNING: API_DEV_TOKEN nicht gesetzt - Dev-Token 'dev-token' aktiv. "
                "In Produktion APP_ENV=production setzen!"
            )

    # Startup
    logger.info("Starting VALEO-NeuroERP API server...")

    # Dispose pre-fork connections so each worker opens fresh ones (multi-worker safety)
    engine.dispose()

    # Increase default threadpool limit for sync route handlers under high concurrency
    # Default is min(32, cpu_count+4)=16; at 500 users / 8 workers = 62 users/worker
    import anyio.to_thread
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = 200

    # Configure dependency injection container
    try:
        configure_container()
        logger.info("Dependency injection container configured successfully")
    except Exception as e:
        logger.error(f"Failed to configure dependency container: {e}")
        raise

    try:
        initialize_module_registry()
        logger.info("Module registry initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize module registry: {e}")
        raise

    # XRechnung: optional drafthorse (ZUGFeRD) als Generator registrieren (Open Source, kostenlos)
    try:
        from modules.agrar.services.xrechnung_drafthorse import register_as_xrechnung_generator
        if register_as_xrechnung_generator():
            logger.info("XRechnung generator: drafthorse (ZUGFeRD) registered")
    except Exception as e:
        logger.debug("XRechnung drafthorse not used: %s", e)

    # Create database tables
    try:
        create_tables()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    try:
        await startup_event_publisher()
        logger.info("Event publisher initialized")
    except Exception as e:
        logger.error(f"Failed to initialize event publisher: {e}")
        raise

    if settings.OUTBOX_WORKER_ENABLED:
        outbox_task = asyncio.create_task(start_outbox_worker())
        logger.info("Outbox worker started")

    app.state.startup_done = True
    yield

    # Shutdown
    if settings.OUTBOX_WORKER_ENABLED:
        try:
            await stop_outbox_worker()
        finally:
            if outbox_task:
                outbox_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await outbox_task

    await shutdown_event_publisher()
    logger.info("Shutting down VALEO-NeuroERP API server...")

# SlowAPI Rate Limiter (Export 10/min, Restore 5/min pro SECURITY-FOUNDATION-AUDIT)
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.middleware.rate_limit import limiter

# Create FastAPI application
app = FastAPI(
    title="VALEO-NeuroERP API",
    description="Enterprise Resource Planning System with Clean Architecture",
    version="3.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Set up CORS (open in debug, permissive fallback otherwise to avoid local dev blocks)
cors_kwargs = dict(
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
if settings.DEBUG:
    cors_kwargs.update(allow_origins=["*"], allow_origin_regex=".*")
elif settings.BACKEND_CORS_ORIGINS:
    cors_kwargs.update(
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    )
else:
    cors_kwargs.update(allow_origins=["*"], allow_origin_regex=".*")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# RFC 7807 Problem Details for DomainError, HTTPException, RequestValidationError.
# Registered before the generic Exception handler so specific types take precedence.
from app.core.exceptions import register_domain_exception_handlers
register_domain_exception_handlers(app)

app.add_middleware(CORSMiddleware, **cors_kwargs)

app.add_middleware(GZipMiddleware, minimum_size=500)

# Add trusted host middleware
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

# Add Prometheus metrics middleware
from app.middleware.metrics import PrometheusMiddleware
app.add_middleware(PrometheusMiddleware)

# Add Correlation ID middleware
from app.middleware.correlation import CorrelationMiddleware
app.add_middleware(CorrelationMiddleware)

# Add Security Headers middleware (Gap 049, SC-HDR-001)
from app.middleware.security_headers import SecurityHeadersMiddleware
app.add_middleware(SecurityHeadersMiddleware)

# Add Audit middleware — auto-captures all mutating API calls (Gap 049, SC-AUDIT-001)
from app.middleware.audit_middleware import AuditMiddleware
app.add_middleware(AuditMiddleware)

# ── PERF-MULTIUSER-001 ────────────────────────────────────────────────────
# Authentication + Request-Logging als reine ASGI-Middleware (vorher
# BaseHTTPMiddleware via @app.middleware("http")). BaseHTTPMiddleware verursacht
# unter Multi-User-Last erheblichen anyio-Stream-Overhead (~80ms/Request bei 32
# parallelen Requests gemessen); pure ASGI-Middleware vermeidet das.
from starlette.datastructures import MutableHeaders


def _apply_cors_headers(response: JSONResponse, request: Request) -> None:
    """CORS-Header auf eine früh erzeugte Fehler-/Preflight-Antwort setzen."""
    origin = request.headers.get("origin")
    allow_all = settings.DEBUG or not settings.BACKEND_CORS_ORIGINS
    if origin and (allow_all or origin in [str(o) for o in settings.BACKEND_CORS_ORIGINS]):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"


class BearerAuthMiddleware:
    """Erzwingt Bearer-Token-Auth und setzt den Tenant-Kontext (pure ASGI)."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        # OPTIONS (CORS-Preflight) ohne Auth beantworten
        if request.method == "OPTIONS":
            response = JSONResponse(status_code=200, content={})
            _apply_cors_headers(response, request)
            await response(scope, receive, send)
            return

        try:
            await require_bearer_token(request)
        except HTTPException as exc:
            response = JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
            _apply_cors_headers(response, request)
            await response(scope, receive, send)
            return

        header_tenant = (request.headers.get("X-Tenant-ID") or "").strip()
        claims = getattr(request.state, "token_claims", {}) or {}
        token_tenant = str(claims.get("tenant_id") or claims.get("tid") or "").strip()
        resolved_tenant = header_tenant or token_tenant or settings.DEFAULT_TENANT_ID

        token = set_current_tenant_id(resolved_tenant)
        request.state.tenant_id = resolved_tenant

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message)["X-Tenant-ID"] = resolved_tenant
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            reset_current_tenant_id(token)


class RequestLoggingMiddleware:
    """Loggt nur langsame Requests (> Schwelle) und Fehler (pure ASGI).

    Pro-Request-Volllogging entfällt — Prometheus erfasst Durchsatz/Latenz
    bereits. Das vermeidet unter Multi-User-Last Log-Flut + PII-Redaction-CPU.
    """

    def __init__(self, app, slow_threshold_s: float = 1.0):
        self.app = app
        self.slow_threshold_s = slow_threshold_s

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        method = scope["method"]
        path = scope["path"]
        status_code = 500

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as exc:
            process_time = time.time() - start_time
            logger.error("%s %s failed in %.2fs: %s", method, path, process_time, exc)
            raise

        process_time = time.time() - start_time
        if process_time >= self.slow_threshold_s or status_code >= 500:
            logger.warning(
                "%s %s -> %s in %.2fs",
                method,
                path,
                status_code,
                process_time,
            )


# Reihenfolge wie zuvor: Bearer-Auth innen, Request-Logging außen
app.add_middleware(BearerAuthMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Catch-all for truly unhandled exceptions — RFC 7807 format.
# Specific handlers (HTTPException, RequestValidationError, DomainError) are
# registered earlier via register_domain_exception_handlers() and take precedence.
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    body = {
        "type": "https://valeo-erp.de/errors/internal-server-error",
        "title": "Interner Serverfehler",
        "status": 500,
        "detail": "Interner Serverfehler",
        "instance": str(request.url.path),
        "error": "INTERNAL_SERVER_ERROR",
    }
    if getattr(settings, "DEBUG", False):
        body["detail"] = str(exc)
        body["exception_type"] = type(exc).__name__
    return JSONResponse(status_code=500, content=body, media_type="application/problem+json")

# Health check endpoint (liveness)
@app.get("/healthz")
async def health_check():
    """Liveness probe - basic health check"""
    return {
        "status": "healthy",
        "service": "VALEO-NeuroERP API",
        "version": "3.0.0",
        "timestamp": time.time()
    }

# Readiness check endpoint
@app.get("/readyz")
async def readiness_check():
    """Readiness probe - checks dependencies"""
    from app.core.health import readiness_check as do_readiness_check
    result = await do_readiness_check()
    
    if not result["ready"]:
        return JSONResponse(
            status_code=503,
            content=result
        )
    
    return result

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "VALEO-NeuroERP API",
        "version": "3.0.0",
        "docs": "/docs",
        "health": "/health",
        "api_v1": settings.API_V1_STR
    }

# Include API routers
app.include_router(api_router, prefix=settings.API_V1_STR)

# KI-Usability (Sprachsteuerung, Action Registry) — integriert für Single-Process-Dev
# Frontend /api/ki-usability → Proxy sendet /api/v1/actions (Rewrite)
try:
    from app.api.v1.endpoints.ki_usability import router as ki_usability_router
    app.include_router(ki_usability_router, prefix="/api/v1", tags=["ki-usability"])
except ImportError as e:
    logger.debug("KI-Usability router not available: %s", e)
app.include_router(policies_v1.router, prefix='/api/mcp')

# GoBD Compliance (/api/gobd/status, /api/gobd/hash-chain, …)
try:
    from app.finance.gobd import router as gobd_router
    app.include_router(gobd_router, prefix="/api", tags=["GoBD"])
except ImportError:
    logger.debug("GoBD router not available (optional module)")

# Include Domain routers (Phase 1 - Service-Kernel)
# CRM
if crm_router:
    app.include_router(crm_router, prefix="/api/v1", tags=["CRM"])

# Finance (DATEV, SEPA) – canonical mount at /api/v1/finance
if finance_router:
    app.include_router(finance_router, prefix="/api/v1", tags=["Finance"])

# Einkauf/Beschaffung – canonical mount at /api/v1/einkauf
if einkauf_router:
    app.include_router(einkauf_router, prefix="/api/v1", tags=["Einkauf"])

# Purchase Workflow (Wareneingang, Abgleich, PO-Storno)
if purchase_workflow_router:
    app.include_router(purchase_workflow_router, prefix="/api/purchase-workflow", tags=["Procurement", "Workflow"])

# Legacy domain routers
try:
    from app.domains.inventory.api import router as inventory_router
    app.include_router(inventory_router, prefix="/api/v1/inventory", tags=["Inventory"])
except ImportError:
    logger.debug("Inventory router not available (optional module)")

try:
    from app.domains.agrar.api import router as agrar_router
    app.include_router(agrar_router, prefix="/api/v1/agrar", tags=["Agrar"])
except ImportError:
    logger.debug("Agrar router not available (optional module)")

# Lightweight stubs for missing MCP/stream endpoints to avoid frontend 404s during development
@app.post("/api/mcp/analytics/kpis")
async def mcp_kpis_stub():
    return {"ok": True, "data": []}


@app.post("/api/mcp/analytics/trends")
async def mcp_trends_stub():
    return {"ok": True, "data": []}


@app.post("/api/mcp/copilot/forecast")
async def mcp_copilot_forecast_stub():
    return {"ok": True, "data": {"forecast": None}}


@app.get("/api/stream/workflow")
async def stream_workflow_stub():
    return {"status": "ok", "events": []}

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include Agents API (Phase 3 - Agentik) - TEMPORARILY DISABLED for CRM testing
# from app.api.v1.endpoints.agents import router as agents_router
# app.include_router(agents_router, prefix="/api/v1/agents", tags=["Agents"])

# Include Health & System Metrics API (Phase 4 - Observability for AI)
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.system_metrics import router as system_metrics_router
app.include_router(health_router, tags=["Health"])
app.include_router(system_metrics_router, prefix="/api/v1/metrics", tags=["System Metrics"])

# Include Audit API (Compliance)
from app.api.v1.endpoints.audit import router as audit_router
app.include_router(audit_router, prefix="/api/v1/audit", tags=["Audit"])

# Include GDPR API (Compliance)
from app.api.v1.endpoints.gdpr import router as gdpr_router
app.include_router(gdpr_router, prefix="/api/v1/gdpr", tags=["GDPR"])

# Include RAG API (Phase 3 - Semantic Search) - TEMPORARILY DISABLED for CRM testing
# from app.api.v1.endpoints.rag import router as rag_router
# app.include_router(rag_router, prefix="/api/v1/rag", tags=["RAG"])

# Include WebSocket API (Phase 3 - Realtime)
from app.api.v1.endpoints.websocket import router as websocket_router
app.include_router(websocket_router, prefix="/api/v1", tags=["WebSocket"])
from app.api.v1.endpoints.copilot_ws import router as copilot_ws_router
app.include_router(copilot_ws_router, prefix="/api/v1", tags=["WebSocket", "copilot"])

# Include Authentication Router (⚠️ NUR FÜR ENTWICKLUNG!)
app.include_router(auth_router)

# Include Policy Manager (direkt, ohne prefix - hat eigenen prefix)
app.include_router(policy_router)

# Include Documents & Forms (Phase O - Belegfluss)
app.include_router(documents_router)
app.include_router(forms_router)
app.include_router(lookup_router)

# Include Print & Export (Phase P - Dokumenten-Druck)
app.include_router(print_router)
app.include_router(export_router)
app.include_router(translations_router)
app.include_router(vies_router)

# Include Workflow & Approval (Phase Q - Workflow-Management)
app.include_router(workflow_router)

# Include SSE Streams (Phase P - Realtime Events)
app.include_router(sse_router)

# Include Document Verification (Phase Q - Document Integrity)
app.include_router(verify_router)

# Legacy GDPR duplicate mount removed (already at /api/v1/gdpr above)

# Include Numbering Service (PostgreSQL)
app.include_router(numbering_router)

# Include Admin DMS Integration
app.include_router(admin_dms_router)

# Verträge-API für Frontend contracts-v2 (GET /api/contracts → { items: [] })
app.include_router(contracts_router)
app.include_router(kontrakte_router, prefix="/api/v1")

# CRM Opportunities unter /api/crm-sales/opportunities (Frontend createApiClient('/api/crm-sales/opportunities'))
app.include_router(opportunities_endpoints.router, prefix="/api/crm-sales/opportunities", tags=["crm-sales"])

# Include DMS Webhooks & Inbox
app.include_router(dms_webhook_router)

# Include Finanzbuchhaltung (130 Masken Integration)
app.include_router(fibu_router, prefix="/api/v1")

# Gap 039: OpenTelemetry (optional, siehe OTEL_EXPORTER_OTLP_ENDPOINT / ENABLE_TRACING)
try:
    from app.core.otel_setup import instrument_app_if_configured

    if instrument_app_if_configured(app, engine):
        logger.info("OpenTelemetry: Instrumentierung aktiv")
except Exception as _otel_exc:
    logger.debug("OpenTelemetry-Setup übersprungen: %s", _otel_exc)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

