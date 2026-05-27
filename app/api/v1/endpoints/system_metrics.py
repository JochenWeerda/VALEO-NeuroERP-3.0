"""
System Metrics API for AI Agents
Provides real-time metrics for Auto-Scaling and Optimization
"""

from datetime import datetime, timedelta
import logging
import time
from typing import Any, Dict, List

from fastapi import APIRouter, Depends
import psutil
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id

logger = logging.getLogger(__name__)

router = APIRouter()

_metrics_cache: dict = {}
_CACHE_TTL = 30  # seconds


@router.get("/system", summary="System metrics abrufen",
    response_model=dict
)
async def get_system_metrics(
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
) -> Dict[str, Any]:
    """
    Real-time system metrics for AI-based optimization.
    
    Used by: AI Agents for Auto-Scaling decisions
    Returns: CPU, Memory, Disk, Network metrics
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network I/O (if available)
        try:
            net_io = psutil.net_io_counters()
            network = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
        except Exception:
            network = None
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": tenant_id,
            "user_id": current_user.get("sub", ""),
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count,
                "load_per_core": cpu_percent / cpu_count if cpu_count > 0 else 0
            },
            "memory": {
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "used_gb": memory.used / (1024**3),
                "percent": memory.percent
            },
            "disk": {
                "total_gb": disk.total / (1024**3),
                "free_gb": disk.free / (1024**3),
                "used_gb": disk.used / (1024**3),
                "percent": disk.percent
            },
            "network": network,
            "status": {
                "cpu_overload": cpu_percent > 80,
                "memory_pressure": memory.percent > 85,
                "disk_critical": disk.percent > 90
            }
        }
    except Exception as e:
        logger.error(f"Failed to collect system metrics: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": tenant_id,
            "user_id": current_user.get("sub", ""),
        }


@router.get("/business", summary="Business metrics abrufen",
    response_model=dict
)
async def get_business_metrics(
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Business KPIs for AI-driven process optimization.
    
    Used by: AI Agents to optimize workflows, detect bottlenecks
    Returns: Queue lengths, processing times, error rates
    """
    try:
        cache_key = f"business_metrics:{tenant_id}"
        now = time.time()
        if cache_key in _metrics_cache and (now - _metrics_cache[cache_key]["ts"]) < _CACHE_TTL:
            return _metrics_cache[cache_key]["data"]

        # 1. Database Connection Pool Status
        from app.core.database import engine
        pool_status = engine.pool.status()
        
        # 2. Event Bus Metrics (from Outbox table)
        from app.infrastructure.eventbus.outbox import OutboxEvent

        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Pending events (not yet published)
        pending_count = db.query(OutboxEvent).filter(  # noqa: E712
            OutboxEvent.published == False,
            OutboxEvent.tenant_id == tenant_id,
        ).count()
        
        # Published today
        published_today = db.query(OutboxEvent).filter(  # noqa: E712
            OutboxEvent.published == True,
            OutboxEvent.published_at >= today_start,
            OutboxEvent.tenant_id == tenant_id,
        ).count()
        
        # Failed events (retries exceeded or stuck for > 24h)
        failed_count = db.query(OutboxEvent).filter(
            OutboxEvent.tenant_id == tenant_id,
            (OutboxEvent.retry_count >= 3)
            | ((OutboxEvent.published == False) & (OutboxEvent.timestamp < now - timedelta(hours=24)))  # noqa: E712
        ).count()
        
        # Oldest pending event
        oldest_pending = db.query(OutboxEvent).filter(
            OutboxEvent.published == False,  # noqa: E712
            OutboxEvent.tenant_id == tenant_id,
        ).order_by(OutboxEvent.timestamp.asc()).first()
        
        # Events by type (for analysis)
        event_types = db.query(
            OutboxEvent.event_type,
            db.func.count(OutboxEvent.id).label('count')
        ).filter(
            OutboxEvent.published == False,  # noqa: E712
            OutboxEvent.tenant_id == tenant_id,
        ).group_by(OutboxEvent.event_type).all()
        
        event_bus_metrics = {
            "pending_events": pending_count,
            "published_today": published_today,
            "failed_events": failed_count,
            "oldest_pending_minutes": int((now - oldest_pending.timestamp).total_seconds() / 60) if oldest_pending else 0,
            "pending_by_type": {et.event_type: et.count for et in event_types}
        }
        
        # 3. Workflow Metrics (AP Approval Workflow)
        workflow_metrics = {"active_workflows": 0, "pending_approvals": 0, "completed_today": 0}
        try:
            pending = db.execute(
                text(
                    "SELECT COUNT(*) FROM domain_erp.ap_approval_requests "
                    "WHERE status = 'pending' AND tenant_id = :tenant_id"
                ),
                {"tenant_id": tenant_id},
            ).scalar()
            workflow_metrics["pending_approvals"] = pending or 0
            workflow_metrics["active_workflows"] = pending or 0
            completed_today = db.execute(
                text(
                    "SELECT COUNT(*) FROM domain_erp.ap_approvals "
                    "WHERE approved_at >= :today AND tenant_id = :tenant_id"
                ),
                {"today": today_start, "tenant_id": tenant_id},
            ).scalar()
            workflow_metrics["completed_today"] = completed_today or 0
        except Exception:  # noqa: BLE001 — Workflow-Metrik nicht verfügbar; Standardwert bleibt
            pass
        
        # 4. Document Processing Queue
        document_metrics = {
            "pending_documents": 0,
            "processing_documents": 0,
            "avg_processing_time_seconds": 0
        }
        
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": tenant_id,
            "user_id": current_user.get("sub", ""),
            "database": {
                "pool_size": engine.pool.size(),
                "connections_in_use": engine.pool.checkedin() + engine.pool.checkedout(),
                "pool_status": pool_status
            },
            "event_bus": event_bus_metrics,
            "workflows": workflow_metrics,
            "documents": document_metrics,
            "recommendations": _generate_recommendations(event_bus_metrics, workflow_metrics)
        }
        _metrics_cache[cache_key] = {"data": result, "ts": time.time()}
        return result
    except Exception as e:
        logger.error(f"Failed to collect business metrics: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": tenant_id,
            "user_id": current_user.get("sub", ""),
        }


@router.get("/optimization-signals", summary="Optimization signals abrufen",
    response_model=dict
)
async def get_optimization_signals(
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
) -> Dict[str, Any]:
    """
    Optimization signals for AI Agents.
    
    Returns actionable signals for:
    - Auto-scaling (up/down)
    - Resource allocation
    - Process optimization
    - Cache warming
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        
        signals = []
        
        # CPU Signals
        if cpu_percent > 85:
            signals.append({
                "type": "scale_up",
                "severity": "high",
                "resource": "cpu",
                "current_value": cpu_percent,
                "threshold": 85,
                "action": "Increase worker processes or scale horizontally"
            })
        elif cpu_percent < 20:
            signals.append({
                "type": "scale_down",
                "severity": "low",
                "resource": "cpu",
                "current_value": cpu_percent,
                "threshold": 20,
                "action": "Reduce worker processes to save resources"
            })
        
        # Memory Signals
        if memory.percent > 90:
            signals.append({
                "type": "memory_critical",
                "severity": "critical",
                "resource": "memory",
                "current_value": memory.percent,
                "threshold": 90,
                "action": "Clear caches, restart services, or scale up memory"
            })
        
        # Database Connection Pool
        from app.core.database import engine
        pool_size = engine.pool.size()
        connections_used = engine.pool.checkedin() + engine.pool.checkedout()
        
        if connections_used > pool_size * 0.9:
            signals.append({
                "type": "connection_pool_exhaustion",
                "severity": "high",
                "resource": "database",
                "current_value": connections_used,
                "threshold": pool_size * 0.9,
                "action": "Increase database connection pool size"
            })
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": tenant_id,
            "user_id": current_user.get("sub", ""),
            "signals": signals,
            "signal_count": len(signals),
            "overall_health": "critical" if any(s["severity"] == "critical" for s in signals) else "warning" if signals else "healthy"
        }
    except Exception as e:
        logger.error(f"Failed to generate optimization signals: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": tenant_id,
            "user_id": current_user.get("sub", ""),
        }


def _generate_recommendations(event_metrics: Dict, workflow_metrics: Dict) -> List[str]:
    """Generate AI-actionable recommendations based on metrics."""
    recommendations = []
    
    if event_metrics.get("pending_events", 0) > 100:
        recommendations.append("High event backlog detected - consider scaling event processors")
    
    if workflow_metrics.get("pending_approvals", 0) > 50:
        recommendations.append("Many workflows awaiting approval - notify approvers or increase timeout")
    
    if event_metrics.get("failed_events", 0) > 10:
        recommendations.append("High event failure rate - investigate event processing errors")
    
    return recommendations

