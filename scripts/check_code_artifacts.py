#!/usr/bin/env python3
"""
Ruft alle Code-Artefakte aus der MongoDB ab und zeigt sie an.
"""

import os
import sys
import asyncio
import logging
import json
from datetime import datetime
from bson import ObjectId

# Pfad zum Projekt-Root hinzufügen
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.apm_framework.mongodb_connector import APMMongoDBConnector

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MongoJSONEncoder(json.JSONEncoder):
    """JSON-Encoder für MongoDB-Objekte."""
    
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(MongoJSONEncoder, self).default(obj)


async def check_code_artifacts():
    """
    Ruft alle Code-Artefakte aus der MongoDB ab und zeigt sie an.
    """
    try:
        # MongoDB-Verbindung herstellen
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        mongodb_db = os.getenv("MONGODB_DB", "valeo_neuroerp")
        
        logger.info(f"Stelle Verbindung zu MongoDB her: {mongodb_uri}, DB: {mongodb_db}")
        mongodb = APMMongoDBConnector(mongodb_uri, mongodb_db)
        await mongodb.connect()
        
        # Code-Artefakte abrufen
        code_artifacts = await mongodb.find_many("code_artifacts", {})
        
        if code_artifacts:
            print(f"\nGefundene Code-Artefakte: {len(code_artifacts)}")
            
            for i, artifact in enumerate(code_artifacts):
                print(f"\n{'-' * 80}")
                print(f"Code-Artefakt {i+1}: {artifact.get('name')}")
                print(f"Typ: {artifact.get('type')}")
                print(f"Sprache: {artifact.get('language')}")
                print(f"Beschreibung: {artifact.get('description')}")
                print(f"Abhängigkeiten: {', '.join(artifact.get('dependencies', []))}")
                print(f"ID: {artifact.get('_id')}")
                print(f"Timestamp: {artifact.get('timestamp')}")
                
                # Code anzeigen
                print(f"\nCode:")
                print(f"{'-' * 40}")
                print(artifact.get('code', 'Kein Code vorhanden'))
                print(f"{'-' * 40}")
                
                # Frage, ob Code in Datei gespeichert werden soll
                save = input(f"Möchten Sie den Code für {artifact.get('name')} in einer Datei speichern? (j/n): ")
                if save.lower() == 'j':
                    # Pfad für die Datei festlegen
                    if artifact.get('language') == 'Python':
                        file_ext = '.py'
                        folder = 'backend/components'
                    elif artifact.get('language') == 'TypeScript':
                        file_ext = '.tsx'
                        folder = 'frontend/src/components'
                    else:
                        file_ext = '.js'
                        folder = 'frontend/src/components'
                    
                    # Ordner erstellen, falls nicht vorhanden
                    os.makedirs(folder, exist_ok=True)
                    
                    # Datei speichern
                    file_path = os.path.join(folder, f"{artifact.get('name')}{file_ext}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(artifact.get('code', ''))
                    
                    print(f"Code gespeichert in: {file_path}")
        else:
            print("\nKeine Code-Artefakte gefunden.")
        
        # Ressourcenanforderungen abrufen
        resource_requirements = await mongodb.find_many("resource_requirements", {})
        
        if resource_requirements:
            print(f"\n{'-' * 80}")
            print(f"\nGefundene Ressourcenanforderungen: {len(resource_requirements)}")
            
            for i, resource in enumerate(resource_requirements):
                print(f"\n{'-' * 40}")
                print(f"Ressource {i+1}: {resource.get('name')}")
                print(f"Typ: {resource.get('type')}")
                print(f"Beschreibung: {resource.get('description')}")
                print(f"Anzahl: {resource.get('quantity')}")
                print(f"Konfiguration: {json.dumps(resource.get('configuration', {}), indent=2)}")
                print(f"ID: {resource.get('_id')}")
                print(f"Timestamp: {resource.get('timestamp')}")
        else:
            print("\nKeine Ressourcenanforderungen gefunden.")
        
        # Entwurfsmuster abrufen
        design_patterns = await mongodb.find_many("design_patterns", {})
        
        if design_patterns:
            print(f"\n{'-' * 80}")
            print(f"\nGefundene Entwurfsmuster: {len(design_patterns)}")
            
            for i, pattern in enumerate(design_patterns):
                print(f"\n{'-' * 40}")
                print(f"Entwurfsmuster {i+1}: {pattern.get('name')}")
                print(f"Kategorie: {pattern.get('category')}")
                print(f"Beschreibung: {pattern.get('description')}")
                print(f"Anwendungsfall: {pattern.get('use_case')}")
                print(f"Begründung: {pattern.get('rationale')}")
                print(f"ID: {pattern.get('_id')}")
                print(f"Timestamp: {pattern.get('timestamp')}")
        else:
            print("\nKeine Entwurfsmuster gefunden.")
        
        # Testfälle abrufen
        test_cases = await mongodb.find_many("test_cases", {})
        
        if test_cases:
            print(f"\n{'-' * 80}")
            print(f"\nGefundene Testfälle: {len(test_cases)}")
            
            for i, test in enumerate(test_cases):
                print(f"\n{'-' * 40}")
                print(f"Testfall {i+1}: {test.get('name')}")
                print(f"Beschreibung: {test.get('description')}")
                print(f"Typ: {test.get('type')}")
                print(f"Erwartetes Ergebnis: {test.get('expected_result')}")
                print(f"ID: {test.get('_id')}")
                print(f"Timestamp: {test.get('timestamp')}")
                
                # Frage, ob Testcode in Datei gespeichert werden soll
                save = input(f"Möchten Sie den Testcode für {test.get('name')} in einer Datei speichern? (j/n): ")
                if save.lower() == 'j':
                    # Pfad für die Datei festlegen
                    component_name = test.get('name').replace('Test für ', '')
                    if 'UserInterface' in component_name:
                        file_ext = '.test.tsx'
                        folder = 'frontend/src/tests'
                    else:
                        file_ext = '_test.py'
                        folder = 'backend/tests'
                    
                    # Ordner erstellen, falls nicht vorhanden
                    os.makedirs(folder, exist_ok=True)
                    
                    # Datei speichern
                    file_path = os.path.join(folder, f"{component_name}{file_ext}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(test.get('test_code', ''))
                    
                    print(f"Testcode gespeichert in: {file_path}")
    
    except Exception as e:
        logger.error(f"Fehler bei der Überprüfung der Code-Artefakte: {str(e)}")
        print(f"\nFehler: {str(e)}")
    
    finally:
        # MongoDB-Verbindung trennen
        if 'mongodb' in locals():
            await mongodb.disconnect()


if __name__ == "__main__":
    # Asynchrone Funktion ausführen
    asyncio.run(check_code_artifacts()) 