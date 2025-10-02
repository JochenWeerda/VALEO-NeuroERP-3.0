#!/usr/bin/env python3
"""
Demo-Skript für den APM-Workflow mit integriertem HandoverManager.
Zeigt den vollständigen Workflow von VAN bis REFLECT mit Handover-Dokumenten.
"""

import os
import sys
import asyncio
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Pfad zum Projektverzeichnis hinzufügen
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.apm_framework.workflow import APMWorkflow
from backend.apm_framework.handover_manager import HandoverManager

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_demo(mode: str = None, requirement_text: str = None):
    """
    Führt die Demo des APM-Workflows aus.
    
    Args:
        mode: Spezifischer Modus, der ausgeführt werden soll (optional)
        requirement_text: Text der Anforderung (optional)
    """
    try:
        # APM-Workflow initialisieren
        workflow = APMWorkflow()
        
        # Standardanforderungstext verwenden, falls keiner angegeben wurde
        if not requirement_text:
            requirement_text = "Implementierung einer Transaktionsverarbeitung mit Chunked Processing und Savepoints"
        
        # Wenn ein spezifischer Modus angegeben wurde, nur diesen ausführen
        if mode:
            if mode == HandoverManager.PHASE_VAN:
                logger.info(f"Führe nur den {mode}-Modus aus")
                result = await workflow.execute_van_mode(requirement_text)
                print(f"\nVAN-Modus-Ergebnis:\n{result}")
                
            elif mode == HandoverManager.PHASE_PLAN:
                logger.info(f"Führe nur den {mode}-Modus aus")
                # Zuerst VAN-Modus ausführen, um eine VAN-Analyse-ID zu erhalten
                van_result = await workflow.execute_van_mode(requirement_text)
                # Dann PLAN-Modus ausführen
                plan_result = await workflow.execute_plan_mode(van_result["_id"])
                print(f"\nPLAN-Modus-Ergebnis:\n{plan_result}")
                
            elif mode == HandoverManager.PHASE_CREATE:
                logger.info(f"Führe nur den {mode}-Modus aus")
                # Zuerst VAN-Modus ausführen
                van_result = await workflow.execute_van_mode(requirement_text)
                # Dann PLAN-Modus ausführen
                plan_result = await workflow.execute_plan_mode(van_result["_id"])
                # Dann CREATE-Modus ausführen
                create_result = await workflow.execute_create_mode(plan_result["_id"])
                print(f"\nCREATE-Modus-Ergebnis:\n{create_result}")
                
            elif mode == HandoverManager.PHASE_IMPLEMENT:
                logger.info(f"Führe nur den {mode}-Modus aus")
                # Zuerst VAN-Modus ausführen
                van_result = await workflow.execute_van_mode(requirement_text)
                # Dann PLAN-Modus ausführen
                plan_result = await workflow.execute_plan_mode(van_result["_id"])
                # Dann CREATE-Modus ausführen
                create_result = await workflow.execute_create_mode(plan_result["_id"])
                # Dann IMPLEMENT-Modus ausführen
                implement_result = await workflow.execute_implement_mode(create_result["_id"])
                print(f"\nIMPLEMENT-Modus-Ergebnis:\n{implement_result}")
                
            elif mode == HandoverManager.PHASE_REFLECT:
                logger.info(f"Führe nur den {mode}-Modus aus")
                # Zuerst VAN-Modus ausführen
                van_result = await workflow.execute_van_mode(requirement_text)
                # Dann PLAN-Modus ausführen
                plan_result = await workflow.execute_plan_mode(van_result["_id"])
                # Dann CREATE-Modus ausführen
                create_result = await workflow.execute_create_mode(plan_result["_id"])
                # Dann IMPLEMENT-Modus ausführen
                implement_result = await workflow.execute_implement_mode(create_result["_id"])
                # Dann REFLECT-Modus ausführen
                reflect_result = await workflow.execute_reflect_mode(implement_result["_id"])
                print(f"\nREFLECT-Modus-Ergebnis:\n{reflect_result}")
                
            else:
                logger.error(f"Ungültiger Modus: {mode}")
                return
        
        # Sonst den gesamten Workflow ausführen
        else:
            logger.info("Führe den gesamten APM-Workflow aus")
            
            # VAN-Modus ausführen
            logger.info("Starte VAN-Modus")
            van_result = await workflow.execute_van_mode(requirement_text)
            print(f"\nVAN-Modus abgeschlossen. Ergebnis-ID: {van_result['_id']}")
            
            # PLAN-Modus ausführen
            logger.info("Starte PLAN-Modus")
            plan_result = await workflow.execute_plan_mode(van_result["_id"])
            print(f"\nPLAN-Modus abgeschlossen. Ergebnis-ID: {plan_result['_id']}")
            
            # CREATE-Modus ausführen
            logger.info("Starte CREATE-Modus")
            create_result = await workflow.execute_create_mode(plan_result["_id"])
            print(f"\nCREATE-Modus abgeschlossen. Ergebnis-ID: {create_result['_id']}")
            
            # IMPLEMENT-Modus ausführen
            logger.info("Starte IMPLEMENT-Modus")
            implement_result = await workflow.execute_implement_mode(create_result["_id"])
            print(f"\nIMPLEMENT-Modus abgeschlossen. Ergebnis-ID: {implement_result['_id']}")
            
            # REFLECT-Modus ausführen
            logger.info("Starte REFLECT-Modus")
            reflect_result = await workflow.execute_reflect_mode(implement_result["_id"])
            print(f"\nREFLECT-Modus abgeschlossen. Ergebnis-ID: {reflect_result['_id']}")
            
            print("\nGesamter APM-Workflow erfolgreich abgeschlossen!")
        
        # Workflow schließen
        workflow.close()
        
    except Exception as e:
        logger.error(f"Fehler in der APM-Workflow-Demo: {str(e)}")
        raise

def main():
    """Hauptfunktion für die Kommandozeile."""
    parser = argparse.ArgumentParser(description="Demo für den APM-Workflow mit integriertem HandoverManager")
    parser.add_argument("--mode", "-m", type=str, 
                        choices=[HandoverManager.PHASE_VAN, HandoverManager.PHASE_PLAN, 
                                HandoverManager.PHASE_CREATE, HandoverManager.PHASE_IMPLEMENT, 
                                HandoverManager.PHASE_REFLECT],
                        help="Spezifischer Modus, der ausgeführt werden soll")
    parser.add_argument("--requirement", "-r", type=str, 
                        help="Text der Anforderung")
    
    args = parser.parse_args()
    
    # Demo ausführen
    asyncio.run(run_demo(args.mode, args.requirement))

if __name__ == "__main__":
    main()
