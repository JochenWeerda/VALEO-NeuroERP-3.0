#!/usr/bin/env python3
"""
Demo für den PLAN-Modus des APM-Frameworks.
Verwendet die Ergebnisse des VAN-Modus als Eingabe.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from bson import ObjectId

# Pfad zum Projektverzeichnis hinzufügen
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.apm_framework.apm_workflow import APMWorkflow
from backend.apm_framework.mongodb_connector import APMMongoDBConnector

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# RAG-Service für Tests
class DummyRAGService:
    async def query(self, prompt, agent_type=None):
        logger.info(f"RAG-Abfrage für {agent_type}: {prompt[:50]}...")
        
        # Simulierte Antworten basierend auf dem Prompt-Inhalt
        if "Projektplan" in prompt:
            return """
            Name: Optimierung der Transaktionsverarbeitung
            
            Beschreibung: Implementierung eines skalierbaren Systems zur Verarbeitung hoher Transaktionsvolumen mit Fokus auf Effizienz und Datenintegrität.
            
            Meilenstein 1: Anforderungsanalyse und Systemdesign
            Beschreibung: Detaillierte Analyse der Anforderungen und Erstellung eines Systemdesigns
            Aufwand: 5 Personentage
            Start: 01.07.2025
            Ende: 07.07.2025
            
            Meilenstein 2: Implementierung des Chunk-basierten Verarbeitungsmodells
            Beschreibung: Entwicklung des Kernmoduls für die Chunk-basierte Transaktionsverarbeitung
            Aufwand: 10 Personentage
            Start: 08.07.2025
            Ende: 21.07.2025
            
            Meilenstein 3: Integration mit bestehenden Systemen
            Beschreibung: Anbindung an die bestehende Datenbankstruktur und ORM-System
            Aufwand: 7 Personentage
            Start: 22.07.2025
            Ende: 30.07.2025
            
            Meilenstein 4: Performance-Tests und Optimierung
            Beschreibung: Durchführung von Lasttests und Optimierung für Hochlast-Szenarien
            Aufwand: 8 Personentage
            Start: 31.07.2025
            Ende: 11.08.2025
            
            Meilenstein 5: Dokumentation und Schulung
            Beschreibung: Erstellung der technischen Dokumentation und Schulung der Entwickler
            Aufwand: 3 Personentage
            Start: 12.08.2025
            Ende: 14.08.2025
            """
        elif "Lösungsdesign" in prompt:
            return """
            Architekturübersicht: Das System verwendet einen Chunk-basierten Ansatz für die Transaktionsverarbeitung mit Savepoints zur Fehlerbehandlung.
            
            Designentscheidung 1: Chunked Processing mit Savepoints
            Begründung: Bietet die beste Balance zwischen Performance und Fehlertoleranz. Durch die Verarbeitung in Chunks können wir die Datenbankzugriffe optimieren und gleichzeitig eine granulare Fehlerbehandlung ermöglichen.
            
            Designentscheidung 2: Asynchrone Audit-Logging
            Begründung: Trennung des Audit-Loggings vom kritischen Pfad der Transaktionsverarbeitung verbessert die Performance, ohne die Compliance-Anforderungen zu beeinträchtigen.
            
            Designentscheidung 3: Optimistisches Locking für Parallelzugriffe
            Begründung: Ermöglicht höheren Durchsatz bei gleichzeitigen Zugriffen im Vergleich zu pessimistischem Locking, mit akzeptablem Risiko von Konflikten.
            
            Alternative 1: Event-basierte asynchrone Verarbeitung
            Vorteile: Höhere Skalierbarkeit, bessere Entkopplung
            Nachteile: Komplexere Implementierung, verzögerte Konsistenz
            
            Alternative 2: Microservice-Architektur für Transaktionsverarbeitung
            Vorteile: Bessere Skalierbarkeit einzelner Komponenten, unabhängige Entwicklung
            Nachteile: Erhöhte Komplexität, zusätzlicher Overhead für Service-Kommunikation
            
            Technologien: PostgreSQL mit Partitionierung, SQLAlchemy für ORM, Redis für Caching, Prometheus für Monitoring
            """
        elif "Aufgaben" in prompt:
            return """
            Aufgabe 1: Detaillierte Anforderungsanalyse
            Beschreibung: Analyse der funktionalen und nicht-funktionalen Anforderungen mit Fokus auf Performance-Kriterien
            Aufwand: 16 Stunden
            Priorität: 1
            Abhängigkeiten: Keine
            
            Aufgabe 2: Technische Spezifikation des Chunk-Verarbeitungsmodells
            Beschreibung: Erstellung einer detaillierten technischen Spezifikation für das Chunk-Verarbeitungsmodell
            Aufwand: 24 Stunden
            Priorität: 1
            Abhängigkeiten: Aufgabe 1
            
            Aufgabe 3: Implementierung der Basis-Transaktionsklassen
            Beschreibung: Entwicklung der grundlegenden Klassen für die Transaktionsverarbeitung
            Aufwand: 32 Stunden
            Priorität: 2
            Abhängigkeiten: Aufgabe 2
            
            Aufgabe 4: Implementierung des Chunk-Managers
            Beschreibung: Entwicklung des Chunk-Managers zur Verwaltung der Transaktions-Chunks
            Aufwand: 40 Stunden
            Priorität: 2
            Abhängigkeiten: Aufgabe 3
            
            Aufgabe 5: Implementierung der Savepoint-Funktionalität
            Beschreibung: Integration von Savepoints in die Transaktionsverarbeitung
            Aufwand: 24 Stunden
            Priorität: 2
            Abhängigkeiten: Aufgabe 4
            
            Aufgabe 6: Entwicklung des asynchronen Audit-Logging
            Beschreibung: Implementierung des Audit-Logging-Systems mit asynchroner Verarbeitung
            Aufwand: 16 Stunden
            Priorität: 3
            Abhängigkeiten: Aufgabe 3
            
            Aufgabe 7: Integration mit bestehender Datenbankstruktur
            Beschreibung: Anpassung des Systems an die bestehende PostgreSQL-Datenbank
            Aufwand: 24 Stunden
            Priorität: 3
            Abhängigkeiten: Aufgabe 5
            
            Aufgabe 8: Implementierung des optimistischen Lockings
            Beschreibung: Integration von optimistischem Locking für parallele Transaktionen
            Aufwand: 16 Stunden
            Priorität: 3
            Abhängigkeiten: Aufgabe 7
            
            Aufgabe 9: Performance-Tests unter Last
            Beschreibung: Durchführung von Lasttests mit simulierten 10.000 Transaktionen pro Stunde
            Aufwand: 24 Stunden
            Priorität: 4
            Abhängigkeiten: Aufgabe 7, Aufgabe 8
            
            Aufgabe 10: Optimierung basierend auf Testergebnissen
            Beschreibung: Durchführung von Performance-Optimierungen basierend auf den Testergebnissen
            Aufwand: 32 Stunden
            Priorität: 4
            Abhängigkeiten: Aufgabe 9
            """
        else:
            return "Simulierte RAG-Antwort für: " + prompt[:30] + "..."

async def main():
    """Hauptfunktion zum Testen des PLAN-Modus"""
    try:
        # MongoDB-Verbindung initialisieren
        mongodb_uri = "mongodb://localhost:27017/"
        db_name = "valeo_neuroerp"
        mongodb = APMMongoDBConnector(connection_string=mongodb_uri, db_name=db_name)
        
        # Die neueste VAN-Analyse finden
        van_analyses = mongodb.find_many(
            "van_analysis",
            {},
            sort=[("created_at", -1)],
            limit=1
        )
        
        if not van_analyses:
            logger.error("Keine VAN-Analyse gefunden. Bitte führen Sie zuerst den VAN-Modus aus.")
            return
        
        van_analysis_id = str(van_analyses[0].get("_id"))
        logger.info(f"Verwende VAN-Analyse mit ID: {van_analysis_id}")
        
        # APM-Workflow initialisieren
        workflow = APMWorkflow(mongodb_uri=mongodb_uri, db_name=db_name)
        
        # RAG-Service setzen
        rag_service = DummyRAGService()
        workflow.set_rag_service(rag_service)
        
        logger.info("Starte PLAN-Mode mit der ausgewählten VAN-Analyse")
        
        # PLAN-Mode ausführen
        plan_result = await workflow.run_plan_mode(van_analysis_id)
        
        # Ergebnis ausgeben
        logger.info(f"PLAN-Mode abgeschlossen mit ID: {plan_result.get('id')}")
        
        # Projektplan ausgeben
        plan_data = plan_result.get('plan', {})
        logger.info(f"Projektplan: {plan_data.get('name')}")
        logger.info(f"Beschreibung: {plan_data.get('description')}")
        logger.info(f"Anzahl der Meilensteine: {len(plan_data.get('milestones', []))}")
        
        # Lösungsdesign ausgeben
        design_data = plan_result.get('design', {})
        logger.info(f"Lösungsdesign: {design_data.get('description')[:100]}...")
        logger.info(f"Anzahl der Designentscheidungen: {len(design_data.get('design_decisions', []))}")
        
        # Aufgaben ausgeben
        tasks = plan_result.get('tasks', [])
        logger.info(f"Anzahl der Aufgaben: {len(tasks)}")
        
        print("\n" + "="*80)
        print("PROJEKTPLAN")
        print("="*80)
        print(f"Name: {plan_data.get('name')}")
        print(f"Beschreibung: {plan_data.get('description')}")
        print("\nMEILENSTEINE:")
        
        for i, milestone in enumerate(plan_data.get('milestones', []), 1):
            print(f"\n{i}. {milestone.get('name')}")
            print(f"   Beschreibung: {milestone.get('description')}")
            print(f"   Aufwand: {milestone.get('effort_days')} Personentage")
            print(f"   Zeitraum: {milestone.get('start_date')} bis {milestone.get('end_date')}")
        
        print("\n" + "="*80)
        print("LÖSUNGSDESIGN")
        print("="*80)
        print(f"Architektur: {design_data.get('description')}")
        
        print("\nDESIGNENTSCHEIDUNGEN:")
        for i, decision in enumerate(design_data.get('design_decisions', []), 1):
            print(f"\n{i}. {decision.get('name')}")
            print(f"   Begründung: {decision.get('rationale')}")
        
        print("\nALTERNATIVEN:")
        for i, alternative in enumerate(design_data.get('alternatives_considered', []), 1):
            print(f"\n{i}. {alternative.get('name')}")
            print(f"   Vorteile: {', '.join(alternative.get('pros', []))}")
            print(f"   Nachteile: {', '.join(alternative.get('cons', []))}")
        
        print("\n" + "="*80)
        print("AUFGABEN")
        print("="*80)
        
        for i, task in enumerate(tasks, 1):
            print(f"\n{i}. {task.get('name')}")
            print(f"   Beschreibung: {task.get('description')}")
            print(f"   Aufwand: {task.get('estimated_hours')} Stunden")
            print(f"   Priorität: {task.get('priority')}")
            if task.get('dependencies'):
                print(f"   Abhängigkeiten: {', '.join(task.get('dependencies'))}")
        
        # Verbindung schließen
        workflow.close()
        
        logger.info("PLAN-Mode-Test erfolgreich abgeschlossen")
        
    except Exception as e:
        logger.error(f"Fehler beim Testen des PLAN-Modus: {str(e)}")
        raise

if __name__ == "__main__":
    print("\n" + "="*80)
    print("DEMO DES PLAN-MODUS")
    print("="*80)
    print("Diese Demo verwendet die Ergebnisse des VAN-Modus als Eingabe")
    print("und generiert einen Projektplan, ein Lösungsdesign und Aufgaben.")
    print("="*80 + "\n")
    
    asyncio.run(main())
