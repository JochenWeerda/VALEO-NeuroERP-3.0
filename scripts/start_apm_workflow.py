"""
Startet den LangGraph-basierten APM Workflow
"""
import asyncio
import logging
from pathlib import Path
from linkup_mcp.apm_framework.workflow_manager import APMWorkflowManager

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("apm_workflow.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("apm-workflow")

async def main():
    """Hauptfunktion"""
    try:
        logger.info("Starte APM Workflow...")
        
        # Workflow Manager initialisieren
        workflow = APMWorkflowManager()
        
        # Workflow starten
        result = await workflow.start_workflow()
        
        if result["status"] == "completed":
            logger.info("Workflow erfolgreich abgeschlossen")
            logger.info("Finale Phase: %s", result.get("current_phase"))
            logger.info("Handover Dateien: %s", result.get("handover_files", []))
        else:
            logger.error("Workflow fehlgeschlagen: %s", result.get("error"))
            
        return result
        
    except Exception as e:
        logger.error("Fehler im Workflow: %s", str(e))
        raise

if __name__ == "__main__":
    asyncio.run(main()) 