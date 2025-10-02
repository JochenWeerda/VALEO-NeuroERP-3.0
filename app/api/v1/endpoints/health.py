"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import time
import sqlite3

from app.core.database import get_db

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "VALEO-NeuroERP API",
        "version": "3.0.0",
        "timestamp": time.time()
    }


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check - verifies database connectivity"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {
            "status": "ready",
            "database": "connected",
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "not ready",
            "database": "disconnected",
            "error": str(e),
            "timestamp": time.time()
        }


@router.get("/live")
async def liveness_check():
    """Liveness check - always returns healthy if service is running"""
    return {
        "status": "alive",
        "timestamp": time.time()
    }


@router.get("/database")
async def database_health():
    """Detailed database health check"""
    try:
        conn = sqlite3.connect("valeo_neuro_erp.db")
        cursor = conn.cursor()

        # Get database statistics
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]

        # Get record counts for main tables
        stats = {}
        tables = ['shared_tenants', 'shared_users', 'crm_customers',
                 'erp_chart_of_accounts', 'inventory_articles', 'inventory_warehouses']

        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            except:
                stats[table] = 0

        conn.close()

        return {
            "status": "healthy",
            "database_type": "SQLite",
            "total_tables": table_count,
            "record_counts": stats,
            "timestamp": time.time()
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }