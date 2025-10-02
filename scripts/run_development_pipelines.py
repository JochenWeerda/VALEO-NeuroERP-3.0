# -*- coding: utf-8 -*-
import asyncio
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Füge das Hauptverzeichnis zum Python-Pfad hinzu
sys.path.append(str(Path(__file__).parent.parent))

from linkup_mcp.development_pipeline_manager import DevelopmentPipelineManager

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    try:
        # Pipeline Manager initialisieren
        manager = DevelopmentPipelineManager(
            config_path="config/development_pipelines.json"
        )
        
        # MongoDB-Collections initialisieren
        await manager.initialize()
        
        logger.info("Starte Ausfuehrung der Entwicklungspipelines...")
        
        # Alle Pipelines ausführen
        results = await manager.execute_all_pipelines()
        
        # Ergebnisse ausgeben
        logger.info("Ausfuehrung abgeschlossen. Ergebnisse:")
        for pipeline_name, result in results.items():
            status = result["status"]
            duration = None
            if "start_time" in result and "end_time" in result:
                start = datetime.fromisoformat(result["start_time"])
                end = datetime.fromisoformat(result["end_time"])
                duration = (end - start).total_seconds()
            
            logger.info(f"Pipeline: {pipeline_name}")
            logger.info(f"Status: {status}")
            if duration:
                logger.info(f"Dauer: {duration:.2f} Sekunden")
            if "error" in result:
                error_msg = result["error"]
                logger.error(f"Fehler: {error_msg}")
            logger.info("-" * 50)
            
    except Exception as e:
        logger.error(f"Fehler bei der Ausfuehrung: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
