"""
Health & Readiness Checks
"""

import asyncio
from typing import Dict, Any
from sqlalchemy import text
from app.core.database_pg import engine
from app.core.sse import sse_hub


async def check_postgresql() -> tuple[bool, str]:
    """Check PostgreSQL connection"""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True, "ok"
    except Exception as e:
        return False, str(e)


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

