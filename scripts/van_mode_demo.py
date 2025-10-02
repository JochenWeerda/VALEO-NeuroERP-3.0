#!/usr/bin/env python3
"""
Interaktive Demo für den VAN-Modus des APM-Frameworks.
Ermöglicht die Eingabe von Antworten auf Klärungsfragen.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Pfad zum Projektverzeichnis hinzufügen
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.apm_framework.apm_workflow import APMWorkflow
from backend.apm_framework.mongodb_connector import APMMongoDBConnector
from backend.apm_framework.models import ClarificationItem

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Interaktiver RAG-Service für Demo
class InteractiveRAGService:
    async def query(self, prompt, agent_type=None):
        logger.info(f"RAG-Abfrage für {agent_type}: {prompt[:50]}...")
        
        # Simulierte Antworten basierend auf dem Prompt-Inhalt
        if "Klärungsfragen" in prompt:
            return """
            1. Welche spezifischen Transaktionstypen müssen unterstützt werden?
            2. Wie soll das System bei Netzwerkausfällen während der Transaktionsverarbeitung reagieren?
            3. Gibt es Anforderungen an die Priorisierung bestimmter Transaktionsarten?
            4. Welche Berichterstattung wird für die Transaktionsverarbeitung benötigt?
            5. Wie sollen historische Transaktionsdaten archiviert werden?
            """
        elif "Analysiere folgende Anforderung" in prompt:
            return """
            # Analyse der Transaktionsverarbeitung
            
            ## Funktionale Anforderungen
            - Verarbeitung verschiedener Transaktionstypen (Eingang, Ausgang, Transfer)
            - Aktualisierung des Lagerbestands in Echtzeit
            - Vollständiges Audit-Logging für Compliance
            - Batch-Verarbeitung für Effizienz
            - Rollback-Mechanismus für Fehlerbehandlung
            
            ## Nicht-funktionale Anforderungen
            - Performance: 500ms Antwortzeit pro Transaktion
            - Skalierbarkeit: 10.000 Transaktionen/Stunde
            - Effizienz: Minimale Datenbankzugriffe
            - Konsistenz: Transaktionssicherheit bei Parallelzugriffen
            
            ## Systemgrenzen und Schnittstellen
            - Integration mit PostgreSQL-Datenbank
            - Kompatibilität mit SQLAlchemy ORM
            - Speicherbegrenzung: 512MB pro Worker
            - Einhaltung des bestehenden Datenmodells
            
            ## Herausforderungen
            - Balance zwischen Batch-Größe und Speicherverbrauch
            - Fehlerbehandlung bei teilweise fehlgeschlagenen Batches
            - Optimierung der Datenbankzugriffe ohne Kompromisse bei der Datenintegrität
            - Skalierbarkeit für Spitzenlasten
            """
        else:
            return "Simulierte RAG-Antwort für: " + prompt[:30] + "..."

class InteractiveVANMode:
    """Interaktive Version des VAN-Modus für Demonstrationszwecke"""
    
    def __init__(self, mongodb_uri="mongodb://localhost:27017/", db_name="valeo_neuroerp"):
        self.mongodb_uri = mongodb_uri
        self.db_name = db_name
        self.workflow = None
        
    async def get_answer_from_user(self, question):
        """Holt eine Antwort vom Benutzer über die Konsole."""
        print("\n" + "="*80)
        print(f"FRAGE: {question}")
        print("-"*80)
        answer = input("Ihre Antwort: ")
        print("="*80 + "\n")
        return answer
    
    async def run(self, requirement_text):
        """Führt den interaktiven VAN-Modus aus."""
        try:
            # APM-Workflow initialisieren
            self.workflow = APMWorkflow(mongodb_uri=self.mongodb_uri, db_name=self.db_name)
            
            # Eigenen RAG-Service mit interaktiver Benutzereingabe erstellen
            class CustomRAGService(InteractiveRAGService):
                async def query(self, prompt, agent_type=None):
                    result = await super().query(prompt, agent_type)
                    return result
            
            rag_service = CustomRAGService()
            self.workflow.set_rag_service(rag_service)
            
            # Original VAN-Mode ausführen, aber get_answer_from_user überschreiben
            original_get_answer = self.workflow.van_mode.get_answer_from_user
            self.workflow.van_mode.get_answer_from_user = self.get_answer_from_user
            
            logger.info("Starte interaktiven VAN-Mode")
            
            # VAN-Mode ausführen
            van_result = await self.workflow.run_van_mode(requirement_text)
            
            # Ergebnis ausgeben
            logger.info(f"VAN-Mode abgeschlossen mit ID: {van_result.get('id')}")
            logger.info(f"Analyse: {van_result.get('analysis')[:200]}...")
            
            # Klärungsfragen und Antworten anzeigen
            clarifications = self.workflow.mongodb.find_many(
                "clarifications",
                {"project_id": self.workflow.project_id}
            )
            
            print("\n" + "="*80)
            print("ZUSAMMENFASSUNG DER KLÄRUNGSFRAGEN UND ANTWORTEN:")
            print("="*80)
            
            for i, clarification in enumerate(clarifications, 1):
                print(f"{i}. Frage: {clarification.get('question')}")
                print(f"   Antwort: {clarification.get('answer')}")
                print("-"*80)
            
            # Verbindung schließen
            self.workflow.close()
            
            logger.info("Interaktiver VAN-Mode erfolgreich abgeschlossen")
            
            return van_result
            
        except Exception as e:
            logger.error(f"Fehler im interaktiven VAN-Mode: {str(e)}")
            if self.workflow:
                self.workflow.close()
            raise

async def main():
    """Hauptfunktion zum Testen des interaktiven VAN-Modus"""
    try:
        # Anforderungstext aus Datei lesen
        requirement_file = Path(__file__).resolve().parent.parent / "data" / "transaktionsverarbeitung.txt"
        with open(requirement_file, "r", encoding="utf-8") as f:
            requirement_text = f.read()
        
        # Interaktiven VAN-Modus starten
        interactive_van = InteractiveVANMode()
        await interactive_van.run(requirement_text)
        
    except Exception as e:
        logger.error(f"Fehler beim Ausführen des interaktiven VAN-Modus: {str(e)}")
        raise

if __name__ == "__main__":
    print("\n" + "="*80)
    print("INTERAKTIVE DEMO DES VAN-MODUS (Verstehen, Analysieren, Nachfragen)")
    print("="*80)
    print("Diese Demo ermöglicht es Ihnen, auf Klärungsfragen zu antworten,")
    print("die während der Anforderungsanalyse generiert werden.")
    print("="*80 + "\n")
    
    asyncio.run(main()) 