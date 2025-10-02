***REMOVED***!/usr/bin/env python3
***REMOVED*** -*- coding: utf-8 -*-
"""
GENXAIS Framework - Memory Bank Initialisierung

Dieses Skript initialisiert die Memory Bank und Todo-Listen für das GENXAIS-Framework.
Es erstellt die notwendige Verzeichnisstruktur und Basisdateien.
Optional kann es die Daten in eine MongoDB-Datenbank laden für RAG-Zugriff.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path

***REMOVED*** Pfad zum Projektverzeichnis hinzufügen
sys.path.append(str(Path(__file__).resolve().parent.parent))

***REMOVED*** Logger konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

***REMOVED*** Importiere das GENXAIS SDK
try:
    from genxais_sdk import GENXAISFramework
except ImportError:
    logger.error("GENXAIS SDK konnte nicht importiert werden. Bitte stellen Sie sicher, dass es installiert ist.")
    sys.exit(1)

***REMOVED*** Versuche MongoDB-Unterstützung zu importieren
try:
    import pymongo
    MONGODB_AVAILABLE = True
except ImportError:
    logger.warning("PyMongo nicht installiert. MongoDB-Integration wird deaktiviert.")
    MONGODB_AVAILABLE = False

class MemoryBankInitializer:
    """Klasse zur Initialisierung der Memory Bank"""
    
    def __init__(self, base_dir=None, mongodb_uri=None, db_name=None):
        """Initialisiert den Memory Bank Initializer
        
        Args:
            base_dir: Basisverzeichnis für die Memory Bank
            mongodb_uri: MongoDB URI für RAG-Integration
            db_name: MongoDB Datenbankname
        """
        self.framework = GENXAISFramework()
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.memory_bank_dir = self.base_dir / "memory-bank"
        
        ***REMOVED*** MongoDB-Verbindung einrichten, falls verfügbar
        self.mongodb_client = None
        self.db = None
        if MONGODB_AVAILABLE and mongodb_uri and db_name:
            try:
                self.mongodb_client = pymongo.MongoClient(mongodb_uri)
                self.db = self.mongodb_client[db_name]
                logger.info(f"MongoDB-Verbindung hergestellt: {mongodb_uri}, Datenbank: {db_name}")
            except Exception as e:
                logger.error(f"Fehler bei der MongoDB-Verbindung: {str(e)}")
    
    def create_directory_structure(self):
        """Erstellt die Verzeichnisstruktur für die Memory Bank"""
        logger.info("Erstelle Memory Bank Verzeichnisstruktur...")
        
        ***REMOVED*** Hauptverzeichnisse
        directories = [
            self.memory_bank_dir,
            self.memory_bank_dir / "archive",
            self.memory_bank_dir / "creative",
            self.memory_bank_dir / "handover",
            self.memory_bank_dir / "handover" / "handover-history",
            self.memory_bank_dir / "planning",
            self.memory_bank_dir / "reflection",
            self.memory_bank_dir / "tasks",
            self.memory_bank_dir / "validation",
            self.memory_bank_dir / "van",
            self.memory_bank_dir / "visual-maps"
        ]
        
        ***REMOVED*** Erstelle alle Verzeichnisse
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"Verzeichnis erstellt: {directory}")
        
        logger.info("Memory Bank Verzeichnisstruktur erfolgreich erstellt")
    
    def create_base_files(self):
        """Erstellt die Basisdateien für die Memory Bank"""
        logger.info("Erstelle Memory Bank Basisdateien...")
        
        ***REMOVED*** activeContext.md - Aktiver Kontext
        active_context_content = """***REMOVED*** Aktiver Kontext

***REMOVED******REMOVED*** Aktueller Modus
Der aktuelle Modus ist: ${CURRENT_MODE}

***REMOVED******REMOVED*** Aktuelle Aufgabe
${CURRENT_TASK}

***REMOVED******REMOVED*** Projektkontext
Das GENXAIS-Framework ist ein modulares Framework für KI-gestützte Softwareentwicklung.
Es unterstützt verschiedene Modi für den Entwicklungsprozess:

- VAN-Modus: Verstehen, Analysieren, Nachfragen
- PLAN-Modus: Projektplanung, Lösungskonzeption
- CREATE-Modus: Codegenerierung, Ressourcenbereitstellung
- IMPLEMENT-Modus: Integration, Deployment
- REFLECT-Modus: Reflexion, Dokumentation

***REMOVED******REMOVED*** Letzte Aktivitäten
${RECENT_ACTIVITIES}
"""
        
        ***REMOVED*** current_mode.txt - Aktueller Modus
        current_mode_content = "VAN"
        
        ***REMOVED*** todo.md - Todo-Liste
        todo_content = """***REMOVED*** Todo-Liste

***REMOVED******REMOVED*** Offene Aufgaben

- [ ] Framework-Struktur vervollständigen
- [ ] Dokumentation erweitern
- [ ] Tests implementieren
- [ ] CI/CD-Pipeline einrichten
- [ ] Beispielanwendung erstellen

***REMOVED******REMOVED*** Erledigte Aufgaben

- [x] Grundlegende Framework-Struktur erstellen
- [x] Modus-Kommandos implementieren
- [x] Memory Bank initialisieren
"""
        
        ***REMOVED*** tasks.md - Aufgabenliste
        tasks_content = """***REMOVED*** Aufgabenliste

***REMOVED******REMOVED*** Aktuelle Aufgaben

***REMOVED******REMOVED******REMOVED*** Framework-Entwicklung
- Implementierung der Kernfunktionalität
- Integration mit externen Diensten
- Dokumentation der API

***REMOVED******REMOVED******REMOVED*** Dokumentation
- Benutzerhandbuch erstellen
- API-Dokumentation generieren
- Beispiele dokumentieren

***REMOVED******REMOVED******REMOVED*** Tests
- Unit-Tests schreiben
- Integrationstests implementieren
- Performance-Tests durchführen
"""
        
        ***REMOVED*** Handover-Template
        handover_template_content = """***REMOVED*** Handover-Dokument

***REMOVED******REMOVED*** Datum und Zeit
${DATE_TIME}

***REMOVED******REMOVED*** Von Modus
${FROM_MODE}

***REMOVED******REMOVED*** Zu Modus
${TO_MODE}

***REMOVED******REMOVED*** Zusammenfassung
${SUMMARY}

***REMOVED******REMOVED*** Aktueller Status
${CURRENT_STATUS}

***REMOVED******REMOVED*** Offene Aufgaben
${OPEN_TASKS}

***REMOVED******REMOVED*** Nächste Schritte
${NEXT_STEPS}

***REMOVED******REMOVED*** Hinweise
${NOTES}
"""
        
        ***REMOVED*** Dateien schreiben
        files_to_create = [
            (self.memory_bank_dir / "activeContext.md", active_context_content),
            (self.memory_bank_dir / "current_mode.txt", current_mode_content),
            (self.memory_bank_dir / "todo.md", todo_content),
            (self.memory_bank_dir / "tasks.md", tasks_content),
            (self.memory_bank_dir / "handover" / "handover-template.md", handover_template_content)
        ]
        
        for file_path, content in files_to_create:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.debug(f"Datei erstellt: {file_path}")
        
        logger.info("Memory Bank Basisdateien erfolgreich erstellt")
    
    def load_to_mongodb(self):
        """Lädt die Memory Bank Dateien in MongoDB für RAG-Zugriff"""
        if not self.db:
            logger.warning("MongoDB nicht verfügbar. Überspringe Laden in MongoDB.")
            return
        
        logger.info("Lade Memory Bank Dateien in MongoDB...")
        
        ***REMOVED*** Sammlungen erstellen
        collections = {
            "memory_bank": self.db["memory_bank"],
            "tasks": self.db["tasks"],
            "handover": self.db["handover"]
        }
        
        ***REMOVED*** Dateien in MongoDB laden
        for collection_name, collection in collections.items():
            ***REMOVED*** Bestehende Dokumente löschen
            collection.delete_many({})
        
        ***REMOVED*** Memory Bank Dateien laden
        memory_bank_files = []
        for root, _, files in os.walk(self.memory_bank_dir):
            for file in files:
                if file.endswith(".md"):
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(self.memory_bank_dir)
                    
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        ***REMOVED*** Dokument erstellen
                        document = {
                            "path": str(relative_path),
                            "content": content,
                            "created_at": datetime.now(),
                            "updated_at": datetime.now(),
                            "type": "memory_bank"
                        }
                        
                        ***REMOVED*** In die entsprechende Sammlung einfügen
                        if "tasks" in str(relative_path):
                            collections["tasks"].insert_one(document)
                        elif "handover" in str(relative_path):
                            collections["handover"].insert_one(document)
                        else:
                            collections["memory_bank"].insert_one(document)
                        
                        memory_bank_files.append(str(relative_path))
                    except Exception as e:
                        logger.error(f"Fehler beim Laden von {file_path}: {str(e)}")
        
        logger.info(f"{len(memory_bank_files)} Memory Bank Dateien in MongoDB geladen")
    
    def initialize(self, load_mongodb=False):
        """Führt die vollständige Initialisierung durch"""
        self.create_directory_structure()
        self.create_base_files()
        
        if load_mongodb and self.db:
            self.load_to_mongodb()
        
        logger.info("Memory Bank Initialisierung abgeschlossen")

def main():
    """Hauptfunktion für die Kommandozeilen-Schnittstelle"""
    parser = argparse.ArgumentParser(description="GENXAIS Framework Memory Bank Initialisierung")
    parser.add_argument("--base-dir", help="Basisverzeichnis für die Memory Bank")
    parser.add_argument("--mongodb-uri", help="MongoDB URI für RAG-Integration")
    parser.add_argument("--db-name", help="MongoDB Datenbankname")
    parser.add_argument("--load-mongodb", action="store_true", help="Lade Dateien in MongoDB")
    
    args = parser.parse_args()
    
    initializer = MemoryBankInitializer(
        base_dir=args.base_dir,
        mongodb_uri=args.mongodb_uri,
        db_name=args.db_name
    )
    
    initializer.initialize(load_mongodb=args.load_mongodb)

if __name__ == "__main__":
    main() 