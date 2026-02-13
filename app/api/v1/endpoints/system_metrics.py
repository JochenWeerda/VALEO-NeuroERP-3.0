"""
System Metrics API for AI Agents
Provides real-time metrics for Auto-Scaling and Optimization
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any, List
from datetime import datetime
import psutil
import logging
from sqlalchemy.orm import Session

from app.core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/system")
async def get_system_metrics() -> Dict[str, Any]:
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
        return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}


@router.get("/business")
async def get_business_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Business KPIs for AI-driven process optimization.
    
    Used by: AI Agents to optimize workflows, detect bottlenecks
    Returns: Queue lengths, processing times, error rates
    """
    try:
        # 1. Database Connection Pool Status
        from app.core.database import engine
        pool_status = engine.pool.status()
        
        # 2. Event Bus Metrics
        event_bus_metrics = {
            "pending_events": 0,  # TODO: Query outbox table
            "published_today": 0,  # TODO: Query outbox table
            "failed_events": 0     # TODO: Query outbox table
        }
        
        # 3. Workflow Metrics (from Phase 3)
        # TODO: Query workflow status from database
        workflow_metrics = {
            "active_workflows": 0,
            "pending_approvals": 0,
            "completed_today": 0
        }
        
        # 4. Document Processing Queue
        document_metrics = {
            "pending_documents": 0,
            "processing_documents": 0,
            "avg_processing_time_seconds": 0
        }
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
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
    except Exception as e:
        logger.error(f"Failed to collect business metrics: {e}")
        return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}


@router.get("/optimization-signals")
async def get_optimization_signals() -> Dict[str, Any]:
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
            "signals": signals,
            "signal_count": len(signals),
            "overall_health": "critical" if any(s["severity"] == "critical" for s in signals) else "warning" if signals else "healthy"
        }
    except Exception as e:
        logger.error(f"Failed to generate optimization signals: {e}")
        return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}


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

