#!/usr/bin/env python3
"""
VALEO-NeuroERP FastAPI Application
Main entry point for the ERP system API
"""

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
import logging
import time
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import create_tables
from app.api.v1.api import api_router
from app.api.v1.endpoints import policies as policies_v1
from app.core.logging import setup_logging
from app.core.security import require_bearer_token
from app.core.container_config import configure_container  # Import container configuration

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
from app.routers.gdpr_router import router as gdpr_router  # GDPR Compliance
from app.routers.numbering_router import router as numbering_router  # Numbering Service
from app.routers.admin_dms_router import router as admin_dms_router  # Admin DMS Integration
from app.routers.dms_webhook_router import router as dms_webhook_router  # DMS Webhooks & Inbox
from app.routers.fibu_router import router as fibu_router  # Finanzbuchhaltung (130 Masken)

# Import domain-specific routers with error handling
try:
    from app.crm.router import router as crm_router  # CRM
except ImportError:
    crm_router = None
    logger.warning("CRM router not available")

try:
    from app.finance.router import router as finance_router  # Finance (DATEV, SEPA)
except ImportError:
    finance_router = None
    logger.warning("Finance router not available")

try:
    from app.einkauf.router import router as einkauf_router  # Einkauf/Beschaffung
except ImportError:
    einkauf_router = None
    logger.warning("Einkauf router not available")

from prometheus_client import make_asgi_app

# Setup logging
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    logger.info("Starting VALEO-NeuroERP API server...")

    # Configure dependency injection container
    try:
        configure_container()
        logger.info("Dependency injection container configured successfully")
    except Exception as e:
        logger.error(f"Failed to configure dependency container: {e}")
        raise

    # Create database tables
    try:
        create_tables()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down VALEO-NeuroERP API server...")

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
        allow_origin_regex=".*",
    )
else:
    cors_kwargs.update(allow_origins=["*"], allow_origin_regex=".*")

app.add_middleware(CORSMiddleware, **cors_kwargs)

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

# Authentication middleware
@app.middleware("http")
async def enforce_bearer_token(request: Request, call_next):
    """
    Enforce bearer-token authentication for protected API routes.
    """
    # Handle OPTIONS requests (CORS preflight) - skip auth and add CORS headers
    if request.method == "OPTIONS":
        response = JSONResponse(status_code=200, content={})
        origin = request.headers.get("origin")
        if origin and origin in [str(o) for o in settings.BACKEND_CORS_ORIGINS]:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
        return response
    
    try:
        await require_bearer_token(request)
    except HTTPException as exc:
        # Return error response with CORS headers
        response = JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
        # Add CORS headers manually for error responses
        origin = request.headers.get("origin")
        if origin and origin in [str(o) for o in settings.BACKEND_CORS_ORIGINS]:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
        return response
    return await call_next(request)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    start_time = time.time()

    # Log request
    logger.info(f"{request.method} {request.url} - {request.client.host if request.client else 'unknown'}")

    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            "%s %s completed in %.2fs with status %s",
            request.method,
            request.url.path,
            process_time,
            response.status_code,
        )
        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            "%s %s failed in %.2fs: %s",
            request.method,
            request.url.path,
            process_time,
            e,
        )
        raise

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "internal_error"}
    )

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
app.include_router(policies_v1.router, prefix='/api/mcp')

# Include Domain routers (Phase 1 - Service-Kernel)
# CRM
if crm_router:
    app.include_router(crm_router, prefix="/api/v1", tags=["CRM"])

# Finance (DATEV, SEPA)
if finance_router:
    app.include_router(finance_router, tags=["Finance"])

# Einkauf/Beschaffung
if einkauf_router:
    app.include_router(einkauf_router, tags=["Einkauf"])

# Legacy domain routers
try:
    from app.domains.inventory.api import router as inventory_router
    app.include_router(inventory_router, prefix="/api/v1/inventory", tags=["Inventory"])
except ImportError:
    logger.warning("Inventory router not available")

try:
    from app.domains.agrar.api import router as agrar_router
    app.include_router(agrar_router, prefix="/api/v1/agrar", tags=["Agrar"])
except ImportError:
    logger.warning("Agrar router not available")

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

# Include Workflow & Approval (Phase Q - Workflow-Management)
app.include_router(workflow_router)

# Include SSE Streams (Phase P - Realtime Events)
app.include_router(sse_router)

# Include Document Verification (Phase Q - Document Integrity)
app.include_router(verify_router)

# Include GDPR Compliance
app.include_router(gdpr_router)

# Include Numbering Service (PostgreSQL)
app.include_router(numbering_router)

# Include Admin DMS Integration
app.include_router(admin_dms_router)

# Include DMS Webhooks & Inbox
app.include_router(dms_webhook_router)

# Include Finanzbuchhaltung (130 Masken Integration)
app.include_router(fibu_router)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

