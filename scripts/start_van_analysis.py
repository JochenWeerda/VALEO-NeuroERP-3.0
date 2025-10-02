"""
Startet die reale ERP-Systemanalyse mit dem VAN Mode
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
    """Führt die reale Systemanalyse durch"""
    try:
        logger.info("Starte reale ERP-Systemanalyse...")
        
        # VAN Mode initialisieren
        van_mode = OptimizedVANMode()
        logger.info("VAN Mode initialisiert")
        
        # Systemanalyse starten
        analysis_result = await van_mode.start({})
        logger.info("Systemanalyse abgeschlossen")
        
        # Vision Phase mit realen Daten
        vision_result = await van_mode.process({
            "phase": "vision",
            "system_analysis": analysis_result["result"]
        })
        logger.info("Vision Phase abgeschlossen")
        
        # Ergebnisse speichern
        output_dir = Path("analysis_results")
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / "system_analysis.json", "w", encoding="utf-8") as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False)
            
        with open(output_dir / "vision_analysis.json", "w", encoding="utf-8") as f:
            json.dump(vision_result, f, indent=2, ensure_ascii=False)
            
        logger.info("Analyseergebnisse gespeichert in: %s", output_dir)
        
        # Ergebnisse ausgeben
        print("\n=== Systemanalyse Ergebnisse ===")
        print(f"Komplexitätsscore: {vision_result['complexity_score']}")
        print("\nIdentifizierte Verbesserungspotenziale:")
        for area in vision_result["improvement_areas"]:
            print(f"- {area['area']}: {area['issue']} (Priorität: {area['priority']})")
        print(f"\nVision Statement:\n{vision_result['vision_statement']}")
        
        return {
            "status": "success",
            "analysis_result": analysis_result,
            "vision_result": vision_result
        }
        
    except Exception as e:
        logger.error("Fehler bei der Systemanalyse: %s", str(e))
        raise

if __name__ == "__main__":
    asyncio.run(main()) 