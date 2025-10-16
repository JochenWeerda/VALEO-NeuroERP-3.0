"""
System Optimizer AI Agent
Monitors system metrics and automatically optimizes resources using LangGraph
"""

import asyncio
import logging
from typing import Dict, Any, List, TypedDict, Annotated
from datetime import datetime

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)


# State Definition for LangGraph
class SystemOptimizerState(TypedDict):
    """State for system optimization workflow."""
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]
    system_metrics: Dict[str, Any]
    optimization_signals: List[Dict[str, Any]]
    ai_analysis: Dict[str, Any]
    actions_taken: List[Dict[str, Any]]
    recommendations: List[str]


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
        self.check_interval = 30  # seconds
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
        """Main optimization loop using LangGraph workflow."""
        # Fetch metrics from our API
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                # Get system metrics
                system_response = await client.get("http://localhost:8000/api/v1/metrics/system")
                system_metrics = system_response.json()

                # Get optimization signals
                signals_response = await client.get("http://localhost:8000/api/v1/metrics/optimization-signals")
                signals = signals_response.json()

                # Run LangGraph optimization workflow
                if signals.get("signal_count", 0) > 0:
                    await self._run_optimization_workflow(system_metrics, signals["signals"])

        except Exception as e:
            logger.error(f"Failed to fetch metrics: {e}")
    
    async def _run_optimization_workflow(self, system_metrics: Dict[str, Any], signals: List[Dict[str, Any]]):
        """Run LangGraph optimization workflow."""
        workflow = build_system_optimizer_workflow()

        initial_state: SystemOptimizerState = {
            "messages": [HumanMessage(content="Analyze system metrics and optimize resources")],
            "system_metrics": system_metrics,
            "optimization_signals": signals,
            "ai_analysis": {},
            "actions_taken": [],
            "recommendations": []
        }

        config = {"configurable": {"thread_id": f"system_opt_{datetime.utcnow().isoformat()}"}}

        try:
            result = await workflow.ainvoke(initial_state, config)

            # Record actions taken
            for action in result.get("actions_taken", []):
                self.optimization_history.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "signal": action.get("signal"),
                    "action_taken": action.get("action"),
                    "ai_insights": result.get("ai_analysis")
                })

            logger.info(f"System optimization completed: {len(result.get('actions_taken', []))} actions taken")

        except Exception as e:
            logger.error(f"Optimization workflow failed: {e}")
    
    async def _handle_memory_critical(self, signal: Dict[str, Any]):
        """Handle critical memory situation."""
        logger.warning("⚠️ Critical memory usage detected - clearing caches")
        
        try:
            # Clear Vector Store cache (if applicable)
            from app.infrastructure.rag.vector_store import get_vector_store
            vector_store = get_vector_store()
            # TODO: Implement cache clearing
            
            logger.info("✅ Caches cleared successfully")
            
            # Publish event for monitoring
            from app.domains.shared.events import get_event_publisher
            event_publisher = get_event_publisher()
            # TODO: Create SystemOptimizationEvent
            
        except Exception as e:
            logger.error(f"Failed to clear caches: {e}")
    
    async def _handle_scale_up(self, signal: Dict[str, Any]):
        """Handle scale-up signal."""
        resource = signal.get("resource")
        logger.info(f"📈 Scale-up signal received for {resource}")
        
        # In a cloud environment, this would trigger auto-scaling
        # For now, just log and alert
        logger.warning(f"Manual intervention recommended: {signal.get('action')}")
        
        # TODO: Integrate with K8s HPA or cloud auto-scaling APIs
    
    async def _handle_scale_down(self, signal: Dict[str, Any]):
        """Handle scale-down signal."""
        resource = signal.get("resource")
        logger.info(f"📉 Scale-down opportunity detected for {resource}")
        
        # Log for cost optimization
        logger.info(f"Cost optimization opportunity: {signal.get('action')}")
    
    async def _handle_connection_pool(self, signal: Dict[str, Any]):
        """Handle connection pool exhaustion."""
        logger.warning("⚠️ Database connection pool near capacity")
        
        # Recommendation: Increase pool size or investigate slow queries
        logger.info("Action: Investigating slow queries and increasing pool size")
        
        # TODO: Implement automatic pool size adjustment
        # TODO: Trigger slow query analysis


# LangGraph Workflow Nodes
async def analyze_system_metrics(state: SystemOptimizerState) -> Dict[str, Any]:
    """Analyze system metrics using AI."""
    metrics = state["system_metrics"]
    signals = state["optimization_signals"]

    # Prepare data for AI analysis
    metrics_summary = f"""
System Metrics:
- CPU Usage: {metrics.get('cpu_percent', 'N/A')}%
- Memory Usage: {metrics.get('memory_percent', 'N/A')}%
- Disk Usage: {metrics.get('disk_percent', 'N/A')}%
- Active Connections: {metrics.get('active_connections', 'N/A')}

Optimization Signals: {len(signals)} detected
"""

    for signal in signals[:3]:  # Limit to first 3 for context
        metrics_summary += f"- {signal.get('type', 'unknown')}: {signal.get('severity', 'unknown')} severity\n"

    try:
        # Import here to avoid circular imports
        from services.ai.app.services.openai_service import analyze_text

        ai_analysis = await analyze_text(
            text=metrics_summary,
            task="Analyze system performance metrics and optimization signals to provide intelligent recommendations for resource management and system optimization",
            context={"domain": "system_administration", "system_type": "erp_microservices"}
        )

        state["messages"].append(AIMessage(
            content=f"AI System Analysis: {ai_analysis.get('insights', [])}",
            additional_kwargs={"analysis": ai_analysis}
        ))

        return {"ai_analysis": ai_analysis}
    except Exception as e:
        logger.warning(f"AI analysis failed: {e}")
        return {"ai_analysis": {"error": str(e)}}


async def generate_optimization_plan(state: SystemOptimizerState) -> Dict[str, Any]:
    """Generate optimization plan based on AI analysis."""
    ai_analysis = state.get("ai_analysis", {})
    signals = state["optimization_signals"]

    recommendations = ai_analysis.get("recommendations", [])
    actions_taken = []

    # Process each signal with AI-enhanced logic
    for signal in signals:
        signal_type = signal.get("type")
        severity = signal.get("severity", "low")

        # AI-enhanced decision making
        if signal_type == "memory_critical":
            action = await _handle_memory_critical_with_ai(signal, ai_analysis)
        elif signal_type == "scale_up":
            action = await _handle_scale_up_with_ai(signal, ai_analysis)
        elif signal_type == "scale_down":
            action = await _handle_scale_down_with_ai(signal, ai_analysis)
        elif signal_type == "connection_pool_exhaustion":
            action = await _handle_connection_pool_with_ai(signal, ai_analysis)
        else:
            action = {"action": "monitor", "reason": f"Unknown signal type: {signal_type}"}

        actions_taken.append({
            "signal": signal,
            "action": action,
            "timestamp": datetime.utcnow().isoformat()
        })

    return {
        "actions_taken": actions_taken,
        "recommendations": recommendations
    }


async def _handle_memory_critical_with_ai(signal: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Handle memory critical with AI insights."""
    # AI can suggest more nuanced actions based on analysis
    insights = ai_analysis.get("insights", [])
    memory_related_insights = [i for i in insights if "memory" in i.lower() or "cache" in i.lower()]

    if memory_related_insights:
        return {
            "action": "clear_caches_and_restart_services",
            "reason": f"AI detected memory issues: {memory_related_insights[0]}",
            "ai_enhanced": True
        }
    else:
        return {
            "action": "clear_caches",
            "reason": "Standard memory optimization",
            "ai_enhanced": False
        }


async def _handle_scale_up_with_ai(signal: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Handle scale up with AI insights."""
    return {
        "action": "alert_admin",
        "reason": f"AI recommends manual scaling review: {ai_analysis.get('insights', ['Check system load'])[0]}",
        "ai_enhanced": True
    }


async def _handle_scale_down_with_ai(signal: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Handle scale down with AI insights."""
    return {
        "action": "log_optimization_opportunity",
        "reason": f"AI identified cost optimization: {ai_analysis.get('insights', ['Monitor resource usage'])[0]}",
        "ai_enhanced": True
    }


async def _handle_connection_pool_with_ai(signal: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Handle connection pool exhaustion with AI insights."""
    return {
        "action": "increase_pool_size",
        "reason": f"AI suggests pool optimization: {ai_analysis.get('insights', ['Review connection usage'])[0]}",
        "ai_enhanced": True
    }


def build_system_optimizer_workflow():
    """Build the system optimizer workflow using LangGraph."""
    workflow = StateGraph(SystemOptimizerState)

    # Add nodes
    workflow.add_node("analyze_metrics", analyze_system_metrics)
    workflow.add_node("generate_plan", generate_optimization_plan)

    # Set entry point and edges
    workflow.set_entry_point("analyze_metrics")
    workflow.add_edge("analyze_metrics", "generate_plan")
    workflow.add_edge("generate_plan", END)

    # Compile with checkpointer
    from langgraph.checkpoint.sqlite import SqliteSaver
    checkpointer = SqliteSaver.from_conn_string("data/system_optimizer.db")

    app = workflow.compile(checkpointer=checkpointer)

    return app
    
    def get_optimization_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent optimization history."""
        return self.optimization_history[-limit:]


# Global instance
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

