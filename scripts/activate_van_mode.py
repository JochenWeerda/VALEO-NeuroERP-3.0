#!/usr/bin/env python3
"""
Script zur Aktivierung des VAN-Modus
"""
import asyncio
import logging
from datetime import datetime
from pymongo import MongoClient
from pathlib import Path
import json
import sys

# Logging-Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VANMode:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['valeo_neuroerp']
        self.van_collection = self.db['van_analysis']
        
    async def activate(self):
        """Aktiviert den VAN-Modus"""
        try:
            # Aktuelle VAN-Analyse laden
            van_analysis_path = Path('memory-bank/van/optimization_analysis_2025-07-04.md')
            if not van_analysis_path.exists():
                raise FileNotFoundError(f"VAN-Analyse nicht gefunden: {van_analysis_path}")
                
            with open(van_analysis_path, 'r', encoding='utf-8') as f:
                analysis_content = f.read()
            
            # Analyse in MongoDB speichern
            van_doc = {
                'date': datetime.now(),
                'type': 'system_optimization',
                'content': analysis_content,
                'status': 'active',
                'metadata': {
                    'source': str(van_analysis_path),
                    'version': '1.0'
                }
            }
            
            # Speichere in MongoDB
            result = self.van_collection.insert_one(van_doc)
            logger.info(f"VAN-Analyse in MongoDB gespeichert (ID: {result.inserted_id})")
            
            # Aktualisiere den Modus-Status
            with open('memory-bank/current_mode.txt', 'w') as f:
                f.write('VAN')
            
            # Erstelle Index für schnellere Abfragen
            self.van_collection.create_index('date')
            
            logger.info("VAN-Modus erfolgreich aktiviert")
            return True
            
        except Exception as e:
            logger.error(f"Fehler bei der Aktivierung des VAN-Modus: {e}")
            return False

async def main():
    """Hauptfunktion"""
    try:
        van = VANMode()
        success = await van.activate()
        
        if success:
            logger.info("VAN-Modus-Aktivierung abgeschlossen")
        else:
            logger.error("VAN-Modus-Aktivierung fehlgeschlagen")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Unerwarteter Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 