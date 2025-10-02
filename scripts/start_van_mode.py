"""
VALEO-NeuroERP VAN Mode Starter
"""
import asyncio
import json
import logging
from pathlib import Path
from linkup_mcp.apm_framework.van_mode_optimized import OptimizedVANMode

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Startet den VAN Mode"""
    try:
        # Konfiguration laden
        config_path = Path("config/van_mode_config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            
        logger.info("VAN Mode Konfiguration geladen")
        
        # VAN Mode initialisieren
        van_mode = OptimizedVANMode()
        logger.info("VAN Mode initialisiert")
        
        # VAN Mode starten
        start_result = await van_mode.start(config["input_data"])
        logger.info("VAN Mode gestartet: %s", start_result)
        
        # Vision Phase
        vision_result = await van_mode.process({
            "phase": "vision",
            "phase_data": config["input_data"]
        })
        logger.info("Vision Phase abgeschlossen: %s", vision_result)
        
        # Alignment Phase
        alignment_result = await van_mode.process({
            "phase": "alignment",
            "phase_data": {
                "resources": config["input_data"]["resources"],
                "capabilities": config["input_data"]["capabilities"]
            }
        })
        logger.info("Alignment Phase abgeschlossen: %s", alignment_result)
        
        # Navigation Phase
        navigation_result = await van_mode.process({
            "phase": "navigation",
            "phase_data": {
                "vision_result": vision_result,
                "alignment_result": alignment_result
            }
        })
        logger.info("Navigation Phase abgeschlossen: %s", navigation_result)
        
        # VAN Mode abschließen
        completion_result = await van_mode.complete()
        logger.info("VAN Mode abgeschlossen: %s", completion_result)
        
        return {
            "status": "success",
            "vision_result": vision_result,
            "alignment_result": alignment_result,
            "navigation_result": navigation_result,
            "completion_result": completion_result
        }
        
    except Exception as e:
        logger.error("Fehler beim Ausführen des VAN Mode: %s", str(e))
        raise

if __name__ == "__main__":
    asyncio.run(main()) 