#!/usr/bin/env python3
"""
Erstellt ein Lösungsdesign mit Komponenten für den CREATE-Modus.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from bson import ObjectId

# Pfad zum Projekt-Root hinzufügen
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.apm_framework.mongodb_connector import APMMongoDBConnector

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def create_solution_design():
    """
    Erstellt ein Lösungsdesign mit Komponenten für den CREATE-Modus.
    """
    try:
        # MongoDB-Verbindung herstellen
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        mongodb_db = os.getenv("MONGODB_DB", "valeo_neuroerp")
        
        logger.info(f"Stelle Verbindung zu MongoDB her: {mongodb_uri}, DB: {mongodb_db}")
        mongodb = APMMongoDBConnector(mongodb_uri, mongodb_db)
        await mongodb.connect()
        
        # Projekt-ID festlegen
        project_id = os.getenv("PROJECT_ID", "valeo_neuroerp_project")
        
        # Neuestes PLAN-Ergebnis abrufen
        plan_results = await mongodb.find_many("plan_results", {"project_id": project_id}, 
                                              sort_field="timestamp", sort_order=-1, limit=1)
        
        if not plan_results:
            logger.error("Kein PLAN-Ergebnis gefunden")
            print("\nFehler: Kein PLAN-Ergebnis gefunden.")
            print("Führen Sie zuerst den PLAN-Modus aus: python scripts/activate_plan_mode.py")
            return
        
        plan_result = plan_results[0]
        plan_result_id = plan_result.get("_id")
        design_id = plan_result.get("design_id")
        
        logger.info(f"PLAN-Ergebnis gefunden: {plan_result_id}")
        logger.info(f"Design-ID: {design_id}")
        
        # Komponenten für das Lösungsdesign erstellen
        components = [
            {
                "name": "UserAuthenticationComponent",
                "type": "Authentication",
                "description": "Komponente für die Benutzerauthentifizierung und -autorisierung",
                "language": "Python",
                "dependencies": ["backend.models.user", "backend.services.auth_service"],
                "interfaces": ["login", "logout", "register", "verify_token"]
            },
            {
                "name": "TransactionProcessingComponent",
                "type": "Core",
                "description": "Komponente für die Verarbeitung von Transaktionen im ERP-System",
                "language": "Python",
                "dependencies": ["backend.models.transaction", "backend.services.transaction_service"],
                "interfaces": ["create_transaction", "process_transaction", "validate_transaction"]
            },
            {
                "name": "ReportGenerationComponent",
                "type": "Reporting",
                "description": "Komponente für die Generierung von Berichten und Auswertungen",
                "language": "Python",
                "dependencies": ["backend.models.report", "backend.services.report_service"],
                "interfaces": ["generate_report", "export_report", "schedule_report"]
            },
            {
                "name": "InventoryManagementComponent",
                "type": "Inventory",
                "description": "Komponente für die Verwaltung des Inventars und der Lagerhaltung",
                "language": "Python",
                "dependencies": ["backend.models.inventory", "backend.services.inventory_service"],
                "interfaces": ["add_item", "remove_item", "update_stock", "check_availability"]
            },
            {
                "name": "DocumentManagementComponent",
                "type": "Document",
                "description": "Komponente für die Verwaltung von Dokumenten und Belegen",
                "language": "Python",
                "dependencies": ["backend.models.document", "backend.services.document_service"],
                "interfaces": ["create_document", "update_document", "archive_document", "search_documents"]
            },
            {
                "name": "UserInterfaceComponent",
                "type": "UI",
                "description": "Frontend-Komponente für die Benutzeroberfläche",
                "language": "TypeScript",
                "dependencies": ["react", "axios", "material-ui"],
                "interfaces": ["render", "handle_events", "update_view"]
            },
            {
                "name": "DataAnalysisComponent",
                "type": "Analytics",
                "description": "Komponente für die Datenanalyse und Business Intelligence",
                "language": "Python",
                "dependencies": ["pandas", "numpy", "backend.services.analytics_service"],
                "interfaces": ["analyze_data", "create_visualization", "export_analysis"]
            },
            {
                "name": "NotificationComponent",
                "type": "Notification",
                "description": "Komponente für die Benachrichtigung von Benutzern",
                "language": "Python",
                "dependencies": ["backend.models.notification", "backend.services.notification_service"],
                "interfaces": ["send_notification", "schedule_notification", "mark_as_read"]
            }
        ]
        
        # Entwurfsmuster für das Lösungsdesign erstellen
        design_patterns = [
            {
                "name": "Repository Pattern",
                "category": "Data Access",
                "description": "Trennung von Datenzugriff und Geschäftslogik",
                "use_case": "Datenbankzugriff für alle Entitäten",
                "rationale": "Verbessert die Testbarkeit und Wartbarkeit des Codes"
            },
            {
                "name": "Factory Pattern",
                "category": "Creational",
                "description": "Erstellung von Objekten ohne direkte Instanziierung",
                "use_case": "Erstellung von Service-Instanzen",
                "rationale": "Vereinfacht die Objekterstellung und verbessert die Erweiterbarkeit"
            },
            {
                "name": "Observer Pattern",
                "category": "Behavioral",
                "description": "Benachrichtigung von Objekten über Änderungen",
                "use_case": "Ereignisbenachrichtigungen im System",
                "rationale": "Ermöglicht lose Kopplung zwischen Komponenten"
            },
            {
                "name": "Dependency Injection",
                "category": "Architectural",
                "description": "Injektion von Abhängigkeiten statt direkter Instanziierung",
                "use_case": "Service-Abhängigkeiten in allen Komponenten",
                "rationale": "Verbessert die Testbarkeit und Wartbarkeit des Codes"
            }
        ]
        
        # Ressourcen für das Lösungsdesign erstellen
        resources = [
            {
                "name": "PostgreSQL-Datenbank",
                "type": "Database",
                "description": "Relationale Datenbank für persistente Speicherung",
                "quantity": 1,
                "configuration": {
                    "version": "14.0",
                    "memory": "4GB",
                    "storage": "100GB"
                }
            },
            {
                "name": "MongoDB-Datenbank",
                "type": "Database",
                "description": "NoSQL-Datenbank für flexible Dokumentenspeicherung",
                "quantity": 1,
                "configuration": {
                    "version": "5.0",
                    "memory": "4GB",
                    "storage": "50GB"
                }
            },
            {
                "name": "Redis-Cache",
                "type": "Cache",
                "description": "In-Memory-Cache für schnellen Datenzugriff",
                "quantity": 1,
                "configuration": {
                    "version": "6.2",
                    "memory": "2GB"
                }
            },
            {
                "name": "API-Server",
                "type": "Server",
                "description": "Server für die API-Bereitstellung",
                "quantity": 2,
                "configuration": {
                    "cpu": "4 Cores",
                    "memory": "8GB",
                    "os": "Linux"
                }
            },
            {
                "name": "Frontend-Server",
                "type": "Server",
                "description": "Server für die Bereitstellung der Benutzeroberfläche",
                "quantity": 2,
                "configuration": {
                    "cpu": "2 Cores",
                    "memory": "4GB",
                    "os": "Linux"
                }
            }
        ]
        
        # Lösungsdesign aktualisieren
        update_dict = {
            "$set": {
                "name": "VALEO-NeuroERP Lösungsdesign",
                "description": "Lösungsdesign für das VALEO-NeuroERP-System",
                "project_id": project_id,
                "requirement_id": plan_result.get("van_analysis_id"),
                "components": components,
                "design_patterns": design_patterns,
                "resources": resources,
                "architecture_style": "Microservices",
                "technology_stack": {
                    "backend": ["Python", "FastAPI", "SQLAlchemy", "Celery"],
                    "frontend": ["TypeScript", "React", "Material-UI"],
                    "database": ["PostgreSQL", "MongoDB"],
                    "cache": ["Redis"],
                    "messaging": ["RabbitMQ"],
                    "deployment": ["Docker", "Kubernetes"]
                },
                "timestamp": datetime.now()
            }
        }
        
        # Lösungsdesign in der Datenbank aktualisieren
        await mongodb.update_one("solution_designs", {"_id": design_id}, update_dict)
        
        logger.info(f"Lösungsdesign mit ID {design_id} aktualisiert")
        
        print("\n" + "=" * 80)
        print("Lösungsdesign erfolgreich aktualisiert")
        print(f"Design-ID: {design_id}")
        print(f"Komponenten: {len(components)}")
        print(f"Entwurfsmuster: {len(design_patterns)}")
        print(f"Ressourcen: {len(resources)}")
        print("=" * 80 + "\n")
        
        print("Sie können jetzt den CREATE-Modus ausführen mit: python scripts/run_create_mode.py")
    
    except Exception as e:
        logger.error(f"Fehler bei der Erstellung des Lösungsdesigns: {str(e)}")
        print(f"\nFehler: {str(e)}")
    
    finally:
        # MongoDB-Verbindung trennen
        if 'mongodb' in locals():
            await mongodb.disconnect()


if __name__ == "__main__":
    # Asynchrone Funktion ausführen
    asyncio.run(create_solution_design()) 