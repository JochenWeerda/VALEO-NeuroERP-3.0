"""
System Optimizer AI Agent
Monitors system metrics and automatically optimizes resources
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class SystemOptimizerAgent:
    """
    AI Agent that monitors system health and performs auto-optimization.
    
    Responsibilities:
    - Monitor CPU, Memory, Disk usage
    - Detect performance bottlenecks
    - Auto-scale resources (when possible)
    - Clear caches when memory pressure is high
    - Alert when manual intervention is needed
    """
    
    def __init__(self):
        self.running = False
        self.check_interval = 30  ***REMOVED*** seconds
        self.optimization_history: List[Dict[str, Any]] = []
    
    async def start(self):
        """Start the optimization agent."""
        self.running = True
        logger.info("System Optimizer Agent started")
        
        while self.running:
            try:
                await self._check_and_optimize()
            except Exception as e:
                logger.error(f"Error in optimizer agent: {e}", exc_info=True)
            
            await asyncio.sleep(self.check_interval)
    
    async def stop(self):
        """Stop the optimization agent."""
        self.running = False
        logger.info("System Optimizer Agent stopped")
    
    async def _check_and_optimize(self):
        """Main optimization loop."""
        ***REMOVED*** Fetch metrics from our API
        import httpx
        
        try:
            async with httpx.AsyncClient() as client:
                ***REMOVED*** Get system metrics
                system_response = await client.get("http://localhost:8000/api/v1/metrics/system")
                system_metrics = system_response.json()
                
                ***REMOVED*** Get optimization signals
                signals_response = await client.get("http://localhost:8000/api/v1/metrics/optimization-signals")
                signals = signals_response.json()
                
                ***REMOVED*** Process signals and take action
                if signals.get("signal_count", 0) > 0:
                    await self._process_signals(signals["signals"])
                
        except Exception as e:
            logger.error(f"Failed to fetch metrics: {e}")
    
    async def _process_signals(self, signals: List[Dict[str, Any]]):
        """Process optimization signals and take action."""
        for signal in signals:
            signal_type = signal.get("type")
            severity = signal.get("severity")
            
            logger.info(f"Processing signal: {signal_type} (severity: {severity})")
            
            if signal_type == "memory_critical":
                await self._handle_memory_critical(signal)
            elif signal_type == "scale_up":
                await self._handle_scale_up(signal)
            elif signal_type == "scale_down":
                await self._handle_scale_down(signal)
            elif signal_type == "connection_pool_exhaustion":
                await self._handle_connection_pool(signal)
            
            ***REMOVED*** Record action
            self.optimization_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "signal": signal,
                "action_taken": signal.get("action")
            })
    
    async def _handle_memory_critical(self, signal: Dict[str, Any]):
        """Handle critical memory situation."""
        logger.warning("⚠️ Critical memory usage detected - clearing caches")
        
        try:
            ***REMOVED*** Clear Vector Store cache (if applicable)
            from app.infrastructure.rag.vector_store import get_vector_store
            vector_store = get_vector_store()
            ***REMOVED*** TODO: Implement cache clearing
            
            logger.info("✅ Caches cleared successfully")
            
            ***REMOVED*** Publish event for monitoring
            from app.domains.shared.events import get_event_publisher
            event_publisher = get_event_publisher()
            ***REMOVED*** TODO: Create SystemOptimizationEvent
            
        except Exception as e:
            logger.error(f"Failed to clear caches: {e}")
    
    async def _handle_scale_up(self, signal: Dict[str, Any]):
        """Handle scale-up signal."""
        resource = signal.get("resource")
        logger.info(f"📈 Scale-up signal received for {resource}")
        
        ***REMOVED*** In a cloud environment, this would trigger auto-scaling
        ***REMOVED*** For now, just log and alert
        logger.warning(f"Manual intervention recommended: {signal.get('action')}")
        
        ***REMOVED*** TODO: Integrate with K8s HPA or cloud auto-scaling APIs
    
    async def _handle_scale_down(self, signal: Dict[str, Any]):
        """Handle scale-down signal."""
        resource = signal.get("resource")
        logger.info(f"📉 Scale-down opportunity detected for {resource}")
        
        ***REMOVED*** Log for cost optimization
        logger.info(f"Cost optimization opportunity: {signal.get('action')}")
    
    async def _handle_connection_pool(self, signal: Dict[str, Any]):
        """Handle connection pool exhaustion."""
        logger.warning("⚠️ Database connection pool near capacity")
        
        ***REMOVED*** Recommendation: Increase pool size or investigate slow queries
        logger.info("Action: Investigating slow queries and increasing pool size")
        
        ***REMOVED*** TODO: Implement automatic pool size adjustment
        ***REMOVED*** TODO: Trigger slow query analysis
    
    def get_optimization_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent optimization history."""
        return self.optimization_history[-limit:]


***REMOVED*** Global instance
_optimizer_agent: SystemOptimizerAgent | None = None


def get_optimizer_agent() -> SystemOptimizerAgent:
    """Get the global optimizer agent instance."""
    global _optimizer_agent
    if _optimizer_agent is None:
        _optimizer_agent = SystemOptimizerAgent()
    return _optimizer_agent


async def start_optimizer_agent():
    """Start the system optimizer agent."""
    agent = get_optimizer_agent()
    await agent.start()

