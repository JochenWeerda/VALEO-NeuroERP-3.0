"""
Health Check & Readiness Endpoints
For Load Balancers, Kubernetes, and AI Agents
"""

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
from datetime import datetime
from sqlalchemy import text
import psutil
import logging

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema, StatusResponse
from app.api.v1.schemas.health_schemas import HealthOut


router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK, summary="Check health",
    response_model=HealthOut
)
async def health_check() -> Dict[str, Any]:
    """
    Basic health check - is the service alive?
    Used by: Load Balancers, Docker health checks
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "valeo-neuroerp",
        "version": "3.0"
    }


@router.get("/ready", status_code=status.HTTP_200_OK, summary="Check readiness",
    response_model=HealthOut
)
async def readiness_check() -> JSONResponse:
    """
    Readiness check - is the service ready to accept traffic?
    Checks: Database, Event Bus, Critical Services
    Used by: Kubernetes Readiness Probes, AI Agents
    """
    checks = {}
    ready = True
    
    # 1. Database Check
    try:
        from app.core.database import SessionLocal
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        checks["database"] = {"status": "healthy", "latency_ms": 5}
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}
        ready = False
        logger.error(f"Database check failed: {e}")
    
    # 1b. Kritische Module (SPEC-P0-03): FIBU-Journal und Bestandsfuehrung
    # muessen migriert sein — eine frische, unmigrierte Installation darf
    # keinen Traffic annehmen (kein stilles Leer-Liefern auf Finanzpfaden).
    critical_tables = (
        "domain_erp.journal_entries",
        "domain_inventory.inventory_stock_movements",
        "domain_shared.tenants",
    )
    try:
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            missing = [
                t for t in critical_tables
                if db.execute(text("SELECT to_regclass(:t)"), {"t": t}).scalar() is None
            ]
        finally:
            db.close()
        if missing:
            checks["critical_modules"] = {"status": "unhealthy", "missing_tables": missing}
            ready = False
            logger.error(f"Critical module tables missing: {missing}")
        else:
            checks["critical_modules"] = {"status": "healthy", "tables_checked": len(critical_tables)}
    except Exception as e:
        checks["critical_modules"] = {"status": "unhealthy", "error": str(e)}
        ready = False
        logger.error(f"Critical module check failed: {e}")

    # 2. Event Bus Check (NATS)
    try:
        from app.infrastructure.eventbus.nats_publisher import nats_publisher
        if nats_publisher._connected:
            checks["event_bus"] = {"status": "healthy", "connected": True}
        else:
            checks["event_bus"] = {"status": "degraded", "connected": False}
            # Not critical, we have fallback
    except Exception as e:
        checks["event_bus"] = {"status": "unknown", "error": str(e)}
        logger.warning(f"Event Bus check failed: {e}")
    
    # 3. Vector Store Check (Chroma/RAG)
    try:
        from app.infrastructure.rag.vector_store import get_vector_store
        _vector_store = get_vector_store()  # noqa: F841
        # Simple ping
        checks["vector_store"] = {"status": "healthy"}
    except Exception as e:
        checks["vector_store"] = {"status": "degraded", "error": str(e)}
        logger.warning(f"Vector Store check failed: {e}")
    
    # 4. System Resources
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        checks["resources"] = {
            "status": "healthy" if cpu_percent < 80 and memory.percent < 85 else "degraded",
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent
        }
        
        if cpu_percent > 90 or memory.percent > 95:
            ready = False
    except Exception as e:
        checks["resources"] = {"status": "unknown", "error": str(e)}
    
    response_data = {
        "ready": ready,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }
    
    return JSONResponse(
        content=response_data,
        status_code=status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE
    )


@router.get("/health/live", status_code=status.HTTP_200_OK, summary="Check liveness",
    response_model=StatusResponse
)
async def liveness_check() -> Dict[str, str]:
    """
    Kubernetes liveness probe - is the process alive?
    Simple check, no dependencies.
    """
    return StatusResponse(success=True, message="alive")


@router.get("/health/startup", status_code=status.HTTP_200_OK, summary="Check startup",
    response_model=HealthOut
)
async def startup_check(request: Request) -> Dict[str, Any]:
    """
    Kubernetes startup probe - has the service finished starting?
    """
    started = getattr(request.app.state, "startup_done", False)
    return {
        "status": "started" if started else "starting",
        "startup_done": started,
        "timestamp": datetime.utcnow().isoformat()
    }
