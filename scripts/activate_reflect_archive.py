#!/usr/bin/env python
"""
Aktiviert den REFLECT-ARCHIVE-Mode und befÃ¼llt die MongoDB mit Daten aus dem AI_driven_ERP-Verzeichnis.
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path

# FÃ¼ge das Projektverzeichnis zum Pfad hinzu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importiere die benÃ¶tigten Module
try:
    from backend.apm_framework.reflect_archive_data_loader import ReflectArchiveDataLoader
    from backend.mongodb_restart_manager import MongoDBRestartManager
except ImportError as e:
    print(f"Fehler beim Importieren der benÃ¶tigten Module: {e}")
    sys.exit(1)

# Logger konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("activate_reflect_archive.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ActivateReflectArchive")

def check_mongodb_status():
    """
    ÃœberprÃ¼ft den Status von MongoDB und startet den Dienst bei Bedarf.
    
    Returns:
        bool: True, wenn MongoDB lÃ¤uft oder gestartet werden konnte, sonst False
    """
    logger.info("ÃœberprÃ¼fe MongoDB-Status...")
    
    # MongoDB Restart Manager initialisieren
    restart_manager = MongoDBRestartManager(
        connection_string="mongodb://localhost:27017/",
        max_retries=3,
        retry_delay=5
    )
    
    # Verbindung prÃ¼fen
    if restart_manager.connect():
        logger.info("MongoDB lÃ¤uft bereits.")
        restart_manager.close()
        return True
    
    # Versuche MongoDB zu starten
    logger.info("MongoDB lÃ¤uft nicht. Versuche zu starten...")
    if restart_manager.restart_mongodb_service():
        logger.info("MongoDB erfolgreich gestartet.")
        restart_manager.close()
        return True
    
    logger.error("Konnte MongoDB nicht starten.")
    return False

def activate_reflect_archive_mode():
    """
    Aktiviert den REFLECT-ARCHIVE-Mode, indem die entsprechende Datei in memory-bank/current_mode.txt geschrieben wird.
    
    Returns:
        bool: True, wenn der Mode erfolgreich aktiviert wurde, sonst False
    """
    logger.info("Aktiviere REFLECT-ARCHIVE-Mode...")
    
    try:
        # Pfad zur current_mode.txt
        mode_file_path = Path("memory-bank") / "current_mode.txt"
        
        # Verzeichnis erstellen, falls es nicht existiert
        mode_file_path.parent.mkdir(exist_ok=True)
        
        # Mode in Datei schreiben
        with open(mode_file_path, "w", encoding="utf-8") as f:
            f.write("REFLECT-ARCHIVE")
        
        logger.info("REFLECT-ARCHIVE-Mode erfolgreich aktiviert.")
        return True
    except Exception as e:
        logger.error(f"Fehler beim Aktivieren des REFLECT-ARCHIVE-Mode: {e}")
        return False

def load_data_to_mongodb(source_dir):
    """
    LÃ¤dt die Daten aus dem angegebenen Verzeichnis in die MongoDB.
    
    Args:
        source_dir: Pfad zum Quellverzeichnis
        
    Returns:
        bool: True, wenn die Daten erfolgreich geladen wurden, sonst False
    """
    logger.info(f"Lade Daten aus {source_dir} in die MongoDB...")
    
    # ReflectArchiveDataLoader initialisieren
    data_loader = ReflectArchiveDataLoader(
        connection_string="mongodb://localhost:27017/",
        database_name="valeo_neuroerp",
        source_dir=source_dir
    )
    
    # Daten laden
    success = data_loader.load_data()
    
    if success:
        logger.info("Daten erfolgreich in die MongoDB geladen.")
    else:
        logger.error("Fehler beim Laden der Daten in die MongoDB.")
    
    return success

def create_reflection_document():
    """
    Erstellt ein Reflexionsdokument fÃ¼r den REFLECT-ARCHIVE-Mode.
    
    Returns:
        bool: True, wenn das Dokument erfolgreich erstellt wurde, sonst False
    """
    logger.info("Erstelle Reflexionsdokument...")
    
    try:
        # Pfad zum Reflexionsdokument
        reflection_file_path = Path("memory-bank") / "reflection" / f"reflection_ai_driven_erp.md"
        
        # Verzeichnis erstellen, falls es nicht existiert
        reflection_file_path.parent.mkdir(exist_ok=True)
        
        # Inhalt des Reflexionsdokuments
        content = """# Reflexion: AI_driven_ERP-Projekt

## ProjektÃ¼bersicht
Das AI_driven_ERP-Projekt ist ein KI-gestÃ¼tztes ERP-System mit Fokus auf Stammdatenpflege. Es orientiert sich am Design und der FunktionalitÃ¤t von ORB-FMS, einem gemeinnÃ¼tzigen Farm-Management-System.

## Hauptkomponenten
- Backend: FastAPI-basiertes Backend mit Mikroservice-Architektur
- Frontend: React-basiertes Frontend im ORB-FMS-Design
- Datenmodelle: Optimierte Modelle fÃ¼r Partner, Artikel, Lager und Finanzen

## Erkenntnisse
- Die Projektstruktur folgt einer klaren Trennung von Backend und Frontend
- Das Backend nutzt FastAPI fÃ¼r eine performante API-Entwicklung
- Das Frontend basiert auf React und implementiert verschiedene Themes
- Es gibt eine umfangreiche Aufgabenliste mit verschiedenen KomplexitÃ¤tsstufen

## NÃ¤chste Schritte
1. VervollstÃ¤ndigung der Dashboard-Implementierung fÃ¼r VALERO Enterprise Suite
2. Entwicklung der Modelle fÃ¼r die GeschÃ¤ftslogik
3. Integration der Module mit bestehenden Community ERP-Funktionen
4. Testen der Module unter realen Bedingungen

## Archivierte Artefakte
- Projektstruktur
- Code-Dateien
- Dokumentation
- Aufgaben
- Kontext

Datum: {datetime}
"""
        
        # Datum einfÃ¼gen
        import datetime
        content = content.replace("{datetime}", datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))
        
        # Dokument schreiben
        with open(reflection_file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"Reflexionsdokument erfolgreich erstellt: {reflection_file_path}")
        return True
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Reflexionsdokuments: {e}")
        return False

def main():
    """
    Hauptfunktion fÃ¼r die Aktivierung des REFLECT-ARCHIVE-Mode und das BefÃ¼llen der MongoDB.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Aktiviert den REFLECT-ARCHIVE-Mode und befÃ¼llt die MongoDB mit Daten.")
    parser.add_argument("--source-dir", default="C:/AI_driven_ERP",
                        help="Quellverzeichnis fÃ¼r die Daten")
    
    args = parser.parse_args()
    
    # MongoDB-Status prÃ¼fen
    if not check_mongodb_status():
        logger.error("MongoDB ist nicht verfÃ¼gbar. Bitte starten Sie MongoDB und versuchen Sie es erneut.")
        sys.exit(1)
    
    # REFLECT-ARCHIVE-Mode aktivieren
    if not activate_reflect_archive_mode():
        logger.error("Konnte REFLECT-ARCHIVE-Mode nicht aktivieren.")
        sys.exit(1)
    
    # Daten in MongoDB laden
    if not load_data_to_mongodb(args.source_dir):
        logger.error("Konnte Daten nicht in MongoDB laden.")
        sys.exit(1)
    
    # Reflexionsdokument erstellen
    if not create_reflection_document():
        logger.error("Konnte Reflexionsdokument nicht erstellen.")
        sys.exit(1)
    
    logger.info("REFLECT-ARCHIVE-Mode erfolgreich aktiviert und MongoDB mit Daten befÃ¼llt.")
    sys.exit(0)


if __name__ == "__main__":
    main() 

