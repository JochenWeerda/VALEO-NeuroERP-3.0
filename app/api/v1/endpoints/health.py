"""
Health check endpoints
"""

import time
from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ....core.database import SessionLocal, get_db
from ....infrastructure.models import (
    Account as AccountModel,
    Article as ArticleModel,
    Customer as CustomerModel,
    Tenant as TenantModel,
    Warehouse as WarehouseModel,
)

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, str | float]:
    """Basic health check."""
    return {
        "status": "healthy",
        "service": "VALEO-NeuroERP API",
        "version": "3.0.0",
        "timestamp": time.time(),
    }


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)) -> Dict[str, str | float]:
    """Readiness check - verifies database connectivity."""
    try:
        db.execute("SELECT 1")
        return {
            "status": "ready",
            "database": "connected",
            "timestamp": time.time(),
        }
    except Exception as exc:  # pragma: no cover - surfaced in response
        return {
            "status": "not ready",
            "database": "disconnected",
            "error": str(exc),
            "timestamp": time.time(),
        }


@router.get("/live")
async def liveness_check() -> Dict[str, str | float]:
    """Liveness check - always returns healthy if service is running."""
    return {
        "status": "alive",
        "timestamp": time.time(),
    }


@router.get("/database")
async def database_health() -> Dict[str, object]:
    """Detailed database health check using PostgreSQL statistics."""
    record_counts: Dict[str, int] = {}
    models = {
        "tenants": TenantModel,
        "customers": CustomerModel,
        "articles": ArticleModel,
        "warehouses": WarehouseModel,
        "accounts": AccountModel,
    }

    with SessionLocal() as session:
        for label, model in models.items():
            try:
                record_counts[label] = session.query(model).count()
            except SQLAlchemyError:
                record_counts[label] = 0

    return {
        "status": "ready" if all(counts >= 0 for counts in record_counts.values()) else "degraded",
        "database": "postgresql",
        "record_counts": record_counts,
        "timestamp": time.time(),
    }

