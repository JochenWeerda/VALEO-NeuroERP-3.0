"""
Health & Readiness Checks
"""

import asyncio
from typing import Dict, Any
from sqlalchemy import text
from app.core.database import engine
from app.core.sse import sse_hub


def _check_postgresql_sync() -> tuple[bool, str]:
    """Run a lightweight sync DB ping using the configured SQLAlchemy engine."""
    try:
        with engine.connect() as conn:
            # Check basic connectivity
            conn.execute(text("SELECT 1"))
            
            # Check alembic version table exists and has at least one migration
            result = conn.execute(text("SELECT COUNT(*) FROM alembic_version"))
            version_count = result.scalar()
            
            if version_count == 0:
                return False, "No alembic migrations applied (empty alembic_version table)"
            
            # Get current migration version
            result = conn.execute(text("SELECT version FROM alembic_version LIMIT 1"))
            current_version = result.scalar()
            
        return True, f"ok (migration: {current_version})"
    except Exception as e:
        return False, str(e)


async def check_postgresql() -> tuple[bool, str]:
    """Check PostgreSQL connection from async context."""
    return await asyncio.to_thread(_check_postgresql_sync)


async def check_sse_hub() -> tuple[bool, str]:
    """Check SSE Hub status"""
    try:
        # Check if hub is responsive
        total_connections = sum(
            sse_hub.get_connection_count(ch) 
            for ch in ["workflow", "sales", "inventory", "policy"]
        )
        return True, f"{total_connections} active connections"
    except Exception as e:
        return False, str(e)


async def readiness_check() -> Dict[str, Any]:
    """
    Comprehensive readiness check
    Returns status and dependency states
    """
    checks = {}
    
    # PostgreSQL
    pg_ok, pg_msg = await check_postgresql()
    checks["postgresql"] = {"healthy": pg_ok, "message": pg_msg}
    
    # SSE Hub
    sse_ok, sse_msg = await check_sse_hub()
    checks["sse_hub"] = {"healthy": sse_ok, "message": sse_msg}
    
    # Overall status
    all_healthy = all(c["healthy"] for c in checks.values())
    
    return {
        "ready": all_healthy,
        "checks": checks
    }

