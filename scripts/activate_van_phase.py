#!/usr/bin/env python3
"""
Skript zum Aktivieren der VAN-Phase für das VALEO-NeuroERP-System.
"""

import os
import sys
import logging
from datetime import datetime

# Pfad zum Projektverzeichnis hinzufügen
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_validation_report():
    """
    Erstellt einen Validierungsbericht für das Berichtsmodul.
    """
    # Pfad zum Validierungsbericht
    report_path = os.path.join("memory-bank", "validation", "reports-validation-report.md")
    
    # Überprüfe, ob der Bericht bereits existiert
    if os.path.exists(report_path):
        logger.info(f"Validierungsbericht existiert bereits: {report_path}")
        return report_path
    
    # Erstelle das Verzeichnis, falls es nicht existiert
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    # Inhalt des Validierungsberichts
    report_content = """# Validierungsbericht: Berichtsmodul für VALEO-NeuroERP

## Übersicht

Dieser Bericht validiert die Implementierung des Berichtsmoduls für das VALEO-NeuroERP-System. Das Modul ermöglicht die Erstellung, Generierung, Verteilung und Planung von Berichten in verschiedenen Formaten.

**Validierungsdatum:** 25.06.2025  
**Validierungsumfang:** Berichtsmodul-Implementierung  
**Status:** Implementiert, bereit für Tests

## Architektur und Komponenten

Die Implementierung folgt einer klaren Schichtenarchitektur:

1. **Datenmodelle**
   - SQLAlchemy-Modelle für Berichte, Berichtsverteilungen und Berichtszeitpläne
   - Korrekte Beziehungen zwischen den Modellen

2. **Services**
   - `EmailService` für die E-Mail-Verteilung
   - `ReportService` für die zentrale Berichtsverwaltung

3. **API-Endpunkte**
   - REST-API für alle Berichtsfunktionen
   - Korrekte Validierung und Fehlerbehandlung

4. **Asynchrone Verarbeitung**
   - Celery-Tasks für Hintergrundverarbeitung
   - Geplante Aufgaben für wiederkehrende Berichte

5. **Bibliotheken**
   - ReportLab für PDF-Generierung
   - OpenPyXL für Excel-Exporte
   - Matplotlib, Seaborn und Plotly für Visualisierungen

## Validierungsergebnisse

### Stärken

1. **Umfassende Funktionalität**
   - Unterstützt verschiedene Berichtsformate (PDF, Excel, Visualisierungen)
   - Flexible Berichtsparameter und Datenquellen
   - Automatisierte Berichtsverteilung per E-Mail

2. **Skalierbarkeit**
   - Asynchrone Verarbeitung für ressourcenintensive Aufgaben
   - Hintergrundgenerierung für große Berichte
   - Effiziente Datenbankabfragen

3. **Wartbarkeit**
   - Klare Trennung der Verantwortlichkeiten
   - Gut dokumentierter Code
   - Modulare Struktur

4. **Erweiterbarkeit**
   - Einfache Integration neuer Berichtstypen
   - Anpassbare Berichtsvorlagen
   - Flexible Datenquellen

### Verbesserungspotenzial

1. **Datenbankintegration**
   - Alembic-Migrationen funktionieren nicht korrekt (Abhängigkeitsprobleme)
   - Manuelle Tabellenerstellung erforderlich

2. **Fehlerbehandlung**
   - Verbesserte Protokollierung von Fehlern bei der Berichtsgenerierung
   - Wiederherstellungsmechanismen bei fehlgeschlagenen Berichtsverteilungen

3. **Benutzeroberfläche**
   - Frontend für die Berichtsverwaltung fehlt noch
   - Vorschaufunktion für Berichte wäre hilfreich

4. **Tests**
   - Umfassende Testabdeckung erforderlich
   - Integrationstests für die E-Mail-Funktionalität

## Empfehlungen

1. **Kurzfristig**
   - Alembic-Migrationsprobleme beheben
   - Unit-Tests für kritische Funktionen hinzufügen
   - Fehlerprotokolle verbessern

2. **Mittelfristig**
   - Frontend-Komponenten für die Berichtsverwaltung entwickeln
   - Berichtsvorlagen-Editor implementieren
   - Erweiterte Visualisierungsoptionen hinzufügen

3. **Langfristig**
   - Integration mit einem Business Intelligence-Tool
   - Erweiterte Datenanalysefunktionen
   - KI-gestützte Berichtsempfehlungen

## Fazit

Das implementierte Berichtsmodul bietet eine solide Grundlage für die Berichterstattung im VALEO-NeuroERP-System. Es erfüllt die grundlegenden Anforderungen für die Erstellung, Generierung, Verteilung und Planung von Berichten. Mit den empfohlenen Verbesserungen kann es zu einem leistungsstarken und benutzerfreundlichen Berichtssystem ausgebaut werden.

Die Integration echter Datenbankabfragen anstelle von Demo-Daten ist ein wichtiger Fortschritt, der die Qualität und Relevanz der generierten Berichte erheblich verbessert. Die Implementierung der E-Mail-Verteilung und der geplanten Berichte ermöglicht eine effiziente Automatisierung der Berichtsprozesse.
"""
    
    # Schreibe den Bericht in die Datei
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    logger.info(f"Validierungsbericht erstellt: {report_path}")
    return report_path

def create_architecture_diagram():
    """
    Erstellt ein Architekturdiagramm für das Berichtsmodul.
    """
    # Pfad zum Architekturdiagramm
    diagram_path = os.path.join("memory-bank", "visual-maps", "reports-architecture.md")
    
    # Überprüfe, ob das Diagramm bereits existiert
    if os.path.exists(diagram_path):
        logger.info(f"Architekturdiagramm existiert bereits: {diagram_path}")
        return diagram_path
    
    # Erstelle das Verzeichnis, falls es nicht existiert
    os.makedirs(os.path.dirname(diagram_path), exist_ok=True)
    
    # Inhalt des Architekturdiagramms
    diagram_content = """# Architekturdiagramm: Berichtsmodul

## Übersicht

```mermaid
graph TD
    subgraph "Benutzeroberfläche"
        UI[Web-Interface]
    end
    
    subgraph "API-Schicht"
        API[API-Endpunkte]
        API --> ReportCreate["/reports/ POST"]
        API --> ReportGet["/reports/{id} GET"]
        API --> ReportGenerate["/reports/{id}/generate POST"]
        API --> ReportDistribute["/reports/{id}/distribute POST"]
        API --> ReportSchedule["/reports/{id}/schedule POST"]
    end
    
    subgraph "Service-Schicht"
        RS[ReportService]
        ES[EmailService]
    end
    
    subgraph "Datenmodelle"
        Report[Report]
        ReportDistribution[ReportDistribution]
        ReportSchedule[ReportSchedule]
    end
    
    subgraph "Asynchrone Verarbeitung"
        Celery[Celery-Worker]
        Tasks[Report-Tasks]
        Tasks --> PDFReports[pdf_reports.py]
        Tasks --> ExcelExports[excel_exports.py]
        Tasks --> DataViz[data_visualization.py]
        Tasks --> ScheduledReports[scheduled_reports.py]
    end
    
    subgraph "Bibliotheken"
        ReportLib[ReportLab]
        OpenPyXL[OpenPyXL]
        MatplotLib[Matplotlib]
        Seaborn[Seaborn]
        Plotly[Plotly]
    end
    
    subgraph "Datenbank"
        DB[(SQLite/PostgreSQL)]
    end
    
    UI --> API
    API --> RS
    RS --> Report
    RS --> ReportDistribution
    RS --> ReportSchedule
    RS --> ES
    RS --> Celery
    Celery --> Tasks
    PDFReports --> ReportLib
    ExcelExports --> OpenPyXL
    DataViz --> MatplotLib
    DataViz --> Seaborn
    DataViz --> Plotly
    Report --> DB
    ReportDistribution --> DB
    ReportSchedule --> DB
```

## Datenfluss

```mermaid
sequenceDiagram
    actor User
    participant API
    participant ReportService
    participant DB
    participant Celery
    participant EmailService
    
    User->>API: Erstellt Bericht (POST /reports/)
    API->>ReportService: create_report()
    ReportService->>DB: Speichert Berichtskonfiguration
    DB-->>ReportService: Bestätigung
    ReportService-->>API: Berichts-ID
    API-->>User: Berichts-ID
    
    User->>API: Generiert Bericht (POST /reports/{id}/generate)
    API->>ReportService: generate_report()
    ReportService->>Celery: Startet asynchrone Aufgabe
    Celery-->>ReportService: Task-ID
    ReportService-->>API: Status "pending"
    API-->>User: Status "pending"
    
    Celery->>DB: Lädt Berichtsdaten
    Celery->>Celery: Generiert Bericht
    Celery->>DB: Aktualisiert Berichtsstatus
    
    User->>API: Verteilt Bericht (POST /reports/{id}/distribute)
    API->>ReportService: distribute_report()
    ReportService->>EmailService: send_report_email()
    EmailService-->>ReportService: Versandstatus
    ReportService->>DB: Speichert Verteilungsinformationen
    ReportService-->>API: Status "sent"
    API-->>User: Status "sent"
```

## Komponentenbeziehungen

```mermaid
graph LR
    subgraph "Frontend"
        UI[Web-Interface]
    end
    
    subgraph "Backend"
        API[API-Endpunkte]
        Services[Services]
        Models[Datenmodelle]
        Tasks[Asynchrone Tasks]
    end
    
    subgraph "Externe Systeme"
        SMTP[E-Mail-Server]
        DB[(Datenbank)]
    end
    
    UI <--> API
    API <--> Services
    Services <--> Models
    Services <--> Tasks
    Models <--> DB
    Tasks --> SMTP
```
"""
    
    # Schreibe das Diagramm in die Datei
    with open(diagram_path, "w", encoding="utf-8") as f:
        f.write(diagram_content)
    
    logger.info(f"Architekturdiagramm erstellt: {diagram_path}")
    return diagram_path

def create_clarification_questions():
    """
    Erstellt Klärungsfragen für das Berichtsmodul.
    """
    # Pfad zur Klärungsfragen-Datei
    questions_path = os.path.join("memory-bank", "van", "reports-clarification-questions.md")
    
    # Überprüfe, ob die Datei bereits existiert
    if os.path.exists(questions_path):
        logger.info(f"Klärungsfragen existieren bereits: {questions_path}")
        return questions_path
    
    # Erstelle das Verzeichnis, falls es nicht existiert
    os.makedirs(os.path.dirname(questions_path), exist_ok=True)
    
    # Inhalt der Klärungsfragen
    questions_content = """# Klärungsfragen: Berichtsmodul

## Funktionalität

1. **Welche spezifischen Berichtstypen müssen unterstützt werden?**
   - Finanzberichte, Projektstatusberichte, Inventarberichte, etc.
   - Sind bestimmte Branchen- oder regulatorische Berichtsformate erforderlich?

2. **Welche Anforderungen gibt es an die Berichtsformatierung?**
   - Gibt es Corporate-Design-Vorgaben für Berichte?
   - Werden mehrsprachige Berichte benötigt?

3. **Wie komplex sind die Datenvisualisierungen?**
   - Werden nur Standarddiagramme benötigt oder auch komplexe, interaktive Visualisierungen?
   - Gibt es spezielle Anforderungen an die Barrierefreiheit der Visualisierungen?

## Integration

4. **Wie soll die Integration mit externen Systemen erfolgen?**
   - Welche externen Datenquellen müssen angebunden werden?
   - Sollen Berichte in externe Systeme exportiert werden können?

5. **Welche Anforderungen gibt es an die E-Mail-Verteilung?**
   - Werden spezielle E-Mail-Templates benötigt?
   - Gibt es Anforderungen an die Sicherheit der E-Mail-Verteilung (Verschlüsselung, etc.)?

## Performance

6. **Welche Performance-Anforderungen gibt es für die Berichtsgenerierung?**
   - Wie groß können die Datenmengen werden?
   - Gibt es Zeitlimits für die Berichtsgenerierung?

7. **Wie soll mit ressourcenintensiven Berichten umgegangen werden?**
   - Sollen Benutzer über den Fortschritt informiert werden?
   - Gibt es Prioritäten für verschiedene Berichtstypen?

## Sicherheit und Berechtigungen

8. **Welche Berechtigungskonzepte sind für Berichte erforderlich?**
   - Wer darf welche Berichte erstellen, ansehen, verteilen?
   - Gibt es vertrauliche Daten, die besonders geschützt werden müssen?

9. **Welche Anforderungen gibt es an die Nachvollziehbarkeit?**
   - Müssen Berichtszugriffe protokolliert werden?
   - Gibt es regulatorische Anforderungen an die Aufbewahrung von Berichten?

## Zukunftsfähigkeit

10. **Welche Erweiterungen sind für die Zukunft geplant?**
    - Sind weitere Berichtsformate geplant?
    - Gibt es Pläne für KI-gestützte Berichtsanalysen oder -empfehlungen?
"""
    
    # Schreibe die Klärungsfragen in die Datei
    with open(questions_path, "w", encoding="utf-8") as f:
        f.write(questions_content)
    
    logger.info(f"Klärungsfragen erstellt: {questions_path}")
    return questions_path

def main():
    """
    Hauptfunktion zum Aktivieren der VAN-Phase.
    """
    logger.info("Starte VAN-Phase für das Berichtsmodul")
    
    try:
        # Erstelle den Validierungsbericht
        validation_report = create_validation_report()
        
        # Erstelle das Architekturdiagramm
        architecture_diagram = create_architecture_diagram()
        
        # Erstelle die Klärungsfragen
        clarification_questions = create_clarification_questions()
        
        logger.info("VAN-Phase erfolgreich abgeschlossen")
        logger.info(f"Validierungsbericht: {validation_report}")
        logger.info(f"Architekturdiagramm: {architecture_diagram}")
        logger.info(f"Klärungsfragen: {clarification_questions}")
        
        # Aktualisiere die current_mode.txt-Datei
        mode_file = os.path.join("memory-bank", "current_mode.txt")
        with open(mode_file, "w", encoding="utf-8") as f:
            f.write("VAN")
        
        logger.info("Modus auf VAN gesetzt")
        
    except Exception as e:
        logger.error(f"Fehler bei der Ausführung der VAN-Phase: {str(e)}")
        raise

if __name__ == "__main__":
    main() 