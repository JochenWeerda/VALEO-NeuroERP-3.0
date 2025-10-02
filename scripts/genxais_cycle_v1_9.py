***REMOVED***!/usr/bin/env python
***REMOVED*** -*- coding: utf-8 -*-

"""
GENXAIS Zyklus v1.9 - LangGraph Integration
Dieses Skript startet den GENXAIS-Zyklus v1.9 in der PLAN-Phase
und nutzt LangGraph zur Steuerung der Workflows.
"""

import os
import sys
import json
import yaml
import asyncio
import logging
from datetime import datetime
from pathlib import Path

***REMOVED*** Importiere notwendige Module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.genxais_version import get_version, get_previous_version
from linkup_mcp.apm_workflow_controller import APMWorkflowController

***REMOVED*** Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/genxais_cycle_v1_9.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GENXAIS.Cycle.v1.9")

***REMOVED*** Konstanten
VERSION = "v1.9"
PREVIOUS_VERSION = "v1.8.1"
DATA_DIR = Path("data/dashboard")
MEMORY_BANK = Path("memory-bank")
OUTPUT_DIR = Path("output")

class GenxaisCycleGraph:
    """
    LangGraph-basierte Steuerung für den GENXAIS-Zyklus.
    """
    
    @classmethod
    def load(cls, project_name):
        """
        Lädt die Konfiguration für ein Projekt.
        
        Args:
            project_name: Name des Projekts
            
        Returns:
            Eine Instanz von GenxaisCycleGraph
        """
        logger.info(f"Lade GENXAIS-Zyklus für Projekt: {project_name}")
        return cls(project_name)
    
    def __init__(self, project_name):
        """
        Initialisiert den GENXAIS-Zyklus.
        
        Args:
            project_name: Name des Projekts
        """
        self.project_name = project_name
        self.controller = APMWorkflowController()
        self.current_phase = None
        self.current_version = VERSION
        self.previous_version = PREVIOUS_VERSION
        self.memory_sources = []
        
        logger.info(f"GENXAIS-Zyklus für {project_name} initialisiert")
        
    async def initialize(self):
        """
        Initialisiert die notwendigen Komponenten.
        """
        await self.controller.initialize()
        logger.info("APM Workflow Controller initialisiert")
        
    async def start_cycle(self, phase="PLAN", version=VERSION, strategy="auto", memory_sources=None):
        """
        Startet einen neuen GENXAIS-Zyklus.
        
        Args:
            phase: Startphase (VAN, PLAN, CREATE, IMPLEMENT, REFLECT)
            version: Version des Zyklus
            strategy: Strategie für die Ausführung
            memory_sources: Quellen für das Gedächtnis
            
        Returns:
            Ergebnis der Initialisierung
        """
        self.current_phase = phase
        self.current_version = version
        self.memory_sources = memory_sources or []
        
        logger.info(f"Starte GENXAIS-Zyklus {version} in Phase {phase}")
        
        ***REMOVED*** Lade Gedächtnis aus den angegebenen Quellen
        memory_data = await self._load_memory_sources()
        
        ***REMOVED*** Starte den Zyklus basierend auf der Phase
        if phase == "VAN":
            return await self._start_van_phase(memory_data)
        elif phase == "PLAN":
            return await self._start_plan_phase(memory_data)
        elif phase == "CREATE":
            return await self._start_create_phase(memory_data)
        elif phase == "IMPLEMENT":
            return await self._start_implement_phase(memory_data)
        elif phase == "REFLECT":
            return await self._start_reflect_phase(memory_data)
        else:
            logger.error(f"Ungültige Phase: {phase}")
            raise ValueError(f"Ungültige Phase: {phase}")
    
    async def transition_phase(self, target_phase, version=VERSION, handover=True, memory_sources=None):
        """
        Führt einen Phasenübergang durch.
        
        Args:
            target_phase: Zielphase (VAN, PLAN, CREATE, IMPLEMENT, REFLECT)
            version: Version des Zyklus
            handover: Ob ein Handover-Dokument erstellt werden soll
            memory_sources: Zusätzliche Gedächtnisquellen
            
        Returns:
            Ergebnis des Phasenübergangs
        """
        logger.info(f"Führe Phasenübergang nach {target_phase} für GENXAIS-Zyklus {version} durch")
        
        ***REMOVED*** Setze Versionen und Phase
        self.current_version = version
        prev_phase = self.current_phase or "PLAN"  ***REMOVED*** Standardmäßig PLAN, wenn keine Phase gesetzt ist
        self.current_phase = target_phase
        
        ***REMOVED*** Lade Gedächtnis aus den angegebenen Quellen
        self.memory_sources = memory_sources or self.memory_sources
        memory_data = await self._load_memory_sources()
        
        ***REMOVED*** Führe Phasenübergang durch
        if prev_phase == "PLAN" and target_phase == "CREATE":
            ***REMOVED*** Schließe PLAN ab
            plan_result = await self.controller.plan_mode.complete()
            
            ***REMOVED*** Wechsle zu CREATE
            from linkup_mcp.apm_framework.mode_manager import APMMode
            await self.controller.mode_manager.transition_to(APMMode.CREATE, plan_result)
            
            ***REMOVED*** Starte CREATE
            create_result = await self._start_create_phase(memory_data)
            
            ***REMOVED*** Erstelle Handover-Dokument
            if handover:
                await self._create_handover_document(prev_phase, target_phase, create_result)
            
            return create_result
        elif prev_phase == "CREATE" and target_phase == "IMPLEMENT":
            ***REMOVED*** Schließe CREATE ab
            create_result = await self.controller.create_mode.complete()
            
            ***REMOVED*** Wechsle zu IMPLEMENT
            from linkup_mcp.apm_framework.mode_manager import APMMode
            await self.controller.mode_manager.transition_to(APMMode.IMPLEMENT, create_result)
            
            ***REMOVED*** Starte IMPLEMENT
            implement_result = await self._start_implement_phase(memory_data)
            
            ***REMOVED*** Erstelle Handover-Dokument
            if handover:
                await self._create_handover_document(prev_phase, target_phase, implement_result)
            
            return implement_result
        elif prev_phase == "IMPLEMENT" and target_phase == "REFLECT":
            ***REMOVED*** Schließe IMPLEMENT ab
            implement_result = await self.controller.implement_mode.complete()
            
            ***REMOVED*** Wechsle zu REFLECT
            from linkup_mcp.apm_framework.mode_manager import APMMode
            await self.controller.mode_manager.transition_to(APMMode.REFLECT, implement_result)
            
            ***REMOVED*** Starte REFLECT
            reflect_result = await self._start_reflect_phase(memory_data)
            
            ***REMOVED*** Erstelle Handover-Dokument
            if handover:
                await self._create_handover_document(prev_phase, target_phase, reflect_result)
            
            return reflect_result
        else:
            logger.error(f"Ungültiger Phasenübergang von {prev_phase} nach {target_phase}")
            raise ValueError(f"Ungültiger Phasenübergang von {prev_phase} nach {target_phase}")
    
    async def _create_handover_document(self, from_phase, to_phase, result):
        """
        Erstellt ein Handover-Dokument für den Phasenübergang.
        
        Args:
            from_phase: Ausgangsphase
            to_phase: Zielphase
            result: Ergebnis des Phasenübergangs
        """
        logger.info(f"Erstelle Handover-Dokument für Übergang von {from_phase} nach {to_phase}")
        
        ***REMOVED*** Erstelle Handover-Datei
        handover_path = OUTPUT_DIR / "handover.md"
        with open(handover_path, "w", encoding="utf-8") as f:
            f.write(f"""***REMOVED*** GENXAIS-Zyklus {self.current_version} - Handover

***REMOVED******REMOVED*** Übersicht
- **Version:** {self.current_version}
- **Phase:** {to_phase}
- **Übergang:** {from_phase} → {to_phase}
- **Datum:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Projekt:** {self.project_name}

***REMOVED******REMOVED*** Status
Der GENXAIS-Zyklus {self.current_version} ist von der {from_phase}-Phase in die {to_phase}-Phase übergegangen.

***REMOVED******REMOVED*** Ergebnisse der {from_phase}-Phase
""")
            
            ***REMOVED*** Füge phasenspezifische Informationen hinzu
            if from_phase == "PLAN":
                with open(MEMORY_BANK / "plan_phase_v1_9.md", "r", encoding="utf-8") as plan_file:
                    plan_content = plan_file.read()
                    
                    ***REMOVED*** Extrahiere die Arbeitspakete
                    import re
                    wp_sections = re.findall(r"***REMOVED******REMOVED******REMOVED*** WP\d+: (.*?)(?=\n***REMOVED******REMOVED******REMOVED*** WP|$)", plan_content, re.DOTALL)
                    
                    f.write("\n***REMOVED******REMOVED******REMOVED*** Arbeitspakete\n\n")
                    for i, wp in enumerate(wp_sections, 1):
                        wp_title = wp.split("\n")[0].strip()
                        f.write(f"{i}. **WP{i}: {wp_title}**\n")
                    
                    f.write("\n***REMOVED******REMOVED******REMOVED*** Ressourcenzuweisung\n\n")
                    if "***REMOVED******REMOVED*** Ressourcenzuweisung" in plan_content:
                        resource_section = plan_content.split("***REMOVED******REMOVED*** Ressourcenzuweisung")[1].split("***REMOVED******REMOVED***")[0]
                        f.write(resource_section)
            
            ***REMOVED*** Füge Informationen zur neuen Phase hinzu
            f.write(f"\n***REMOVED******REMOVED*** Ziele der {to_phase}-Phase\n\n")
            
            if to_phase == "CREATE":
                f.write("""1. **Architekturentwürfe**
   - Detaillierte Architektur für alle Arbeitspakete
   - Technische Spezifikationen
   - Schnittstellen-Definitionen

2. **Prototypentwicklung**
   - Funktionale Prototypen für kritische Komponenten
   - Proof-of-Concept für komplexe Funktionen
   - Validierung der technischen Machbarkeit

3. **Lösungsentwicklung**
   - Implementierung der Kernfunktionalitäten
   - Integration mit bestehenden Systemen
   - Optimierung für Leistung und Skalierbarkeit

4. **Validierung**
   - Unit- und Integrationstests
   - Leistungstests
   - Sicherheitsüberprüfungen

5. **Dokumentation**
   - API-Dokumentation
   - Entwicklerdokumentation
   - Benutzerhandbücher
""")
            
            ***REMOVED*** Füge nächste Schritte hinzu
            f.write("\n***REMOVED******REMOVED*** Nächste Schritte\n\n")
            
            if to_phase == "CREATE":
                f.write("""1. Kick-off-Meeting für die CREATE-Phase organisieren
2. Architekturentwürfe für alle Arbeitspakete erstellen
3. Entwicklungsumgebungen einrichten
4. Prototypen für kritische Komponenten entwickeln
5. Regelmäßige Fortschrittsberichte einrichten
""")
        
        logger.info(f"Handover-Dokument erstellt: {handover_path}")
    
    async def _load_memory_sources(self):
        """
        Lädt die Gedächtnisquellen.
        
        Returns:
            Kombinierte Gedächtnisdaten
        """
        logger.info(f"Lade Gedächtnisquellen: {self.memory_sources}")
        
        memory_data = {
            "previous_version": self.previous_version,
            "current_version": self.current_version,
            "timestamp": datetime.now().isoformat(),
            "sources": {}
        }
        
        ***REMOVED*** Lade Daten aus den angegebenen Quellen
        for source in self.memory_sources:
            source_path = Path(source)
            if source_path.exists():
                try:
                    if source_path.is_dir():
                        ***REMOVED*** Lade alle Markdown-Dateien im Verzeichnis
                        for file_path in source_path.glob("*.md"):
                            with open(file_path, "r", encoding="utf-8") as f:
                                memory_data["sources"][file_path.name] = f.read()
                    else:
                        ***REMOVED*** Lade einzelne Datei
                        with open(source_path, "r", encoding="utf-8") as f:
                            if source_path.suffix == ".json":
                                memory_data["sources"][source_path.name] = json.load(f)
                            elif source_path.suffix in [".yaml", ".yml"]:
                                memory_data["sources"][source_path.name] = yaml.safe_load(f)
                            else:
                                memory_data["sources"][source_path.name] = f.read()
                except Exception as e:
                    logger.error(f"Fehler beim Laden von {source}: {e}")
        
        return memory_data
    
    async def _start_plan_phase(self, memory_data):
        """
        Startet die PLAN-Phase.
        
        Args:
            memory_data: Gedächtnisdaten
            
        Returns:
            Ergebnis der PLAN-Phase
        """
        logger.info("Starte PLAN-Phase")
        
        ***REMOVED*** Erstelle Projekt-ID
        project_id = f"neuroerp_{self.current_version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        ***REMOVED*** Extrahiere Verbesserungsvorschläge aus dem Backlog
        improvement_backlog = memory_data["sources"].get("improvement_backlog_v1_8_1.md", "")
        
        ***REMOVED*** Extrahiere Analyseergebnisse aus VAN-Phase
        van_analysis = memory_data["sources"].get("van_analysis_v1.8.1.md", "")
        edge_validation = memory_data["sources"].get("edge_validation_report.md", "")
        conflict_resolution = memory_data["sources"].get("conflict_resolution_strategy.md", "")
        metrics_framework = memory_data["sources"].get("metrics_framework.md", "")
        mutation_aggregator = memory_data["sources"].get("mutation_aggregator_design.md", "")
        
        ***REMOVED*** Erstelle Input für PLAN-Phase
        plan_input = {
            "project_id": project_id,
            "version": self.current_version,
            "previous_version": self.previous_version,
            "improvement_areas": [
                {
                    "id": "edge_network_resilience",
                    "description": "Verbesserung der Netzwerkrobustheit für Edge-Geräte",
                    "priority": "high",
                    "source": "edge_validation_report"
                },
                {
                    "id": "conflict_resolution",
                    "description": "Implementierung der Konfliktlösungsstrategie",
                    "priority": "high",
                    "source": "conflict_resolution_strategy"
                },
                {
                    "id": "metrics_implementation",
                    "description": "Implementierung des Metrik-Frameworks",
                    "priority": "medium",
                    "source": "metrics_framework"
                },
                {
                    "id": "mutation_aggregator",
                    "description": "Entwicklung des Mutation-Aggregators",
                    "priority": "medium",
                    "source": "mutation_aggregator_design"
                }
            ],
            "constraints": [
                {
                    "type": "technical",
                    "description": "Kompatibilität mit bestehender Edge-Integration"
                },
                {
                    "type": "performance",
                    "description": "Minimale Latenz bei Synchronisationsvorgängen"
                },
                {
                    "type": "reliability",
                    "description": "Robustheit bei instabilen Netzwerkverbindungen"
                }
            ]
        }
        
        ***REMOVED*** Starte PLAN-Modus
        from linkup_mcp.apm_framework.mode_manager import APMMode
        await self.controller.mode_manager.transition_to(APMMode.PLAN, {"project_started": True})
        
        ***REMOVED*** Starte PLAN mit Input
        plan_result = await self.controller.plan_mode.start(plan_input)
        
        return plan_result

    async def _start_van_phase(self, memory_data):
        """Placeholder für VAN-Phase"""
        logger.info("VAN-Phase nicht implementiert")
        return {"status": "not_implemented"}

    async def _start_create_phase(self, memory_data):
        """
        Startet die CREATE-Phase.
        
        Args:
            memory_data: Gedächtnisdaten
            
        Returns:
            Ergebnis der CREATE-Phase
        """
        logger.info("Starte CREATE-Phase")
        
        ***REMOVED*** Extrahiere Arbeitspakete aus der PLAN-Phase
        plan_phase_doc = memory_data["sources"].get("plan_phase_v1_9.md", "")
        
        ***REMOVED*** Erstelle Input für CREATE-Phase
        create_input = {
            "version": self.current_version,
            "previous_phase": "PLAN",
            "workpackages": [
                {
                    "id": "wp1",
                    "name": "Edge Network Resilience Framework",
                    "priority": "high",
                    "team": "Edge-Integration"
                },
                {
                    "id": "wp2",
                    "name": "Conflict Resolution System",
                    "priority": "high",
                    "team": "Datenbank"
                },
                {
                    "id": "wp3",
                    "name": "Edge Metrics Framework",
                    "priority": "medium",
                    "team": "Monitoring"
                },
                {
                    "id": "wp4",
                    "name": "Mutation Aggregator Service",
                    "priority": "medium",
                    "team": "Backend"
                },
                {
                    "id": "wp5",
                    "name": "GraphQL Optimization",
                    "priority": "low",
                    "team": "GraphQL"
                }
            ],
            "goals": [
                "Architekturentwürfe für alle Arbeitspakete",
                "Funktionale Prototypen für kritische Komponenten",
                "Implementierung der Kernfunktionalitäten",
                "Integration mit bestehenden Systemen",
                "Umfassende Tests und Validierung"
            ]
        }
        
        ***REMOVED*** Starte CREATE-Modus
        create_result = await self.controller.create_mode.start(create_input)
        
        return create_result

    async def _start_implement_phase(self, memory_data):
        """Placeholder für IMPLEMENT-Phase"""
        logger.info("IMPLEMENT-Phase nicht implementiert")
        return {"status": "not_implemented"}

    async def _start_reflect_phase(self, memory_data):
        """Placeholder für REFLECT-Phase"""
        logger.info("REFLECT-Phase nicht implementiert")
        return {"status": "not_implemented"}

async def main():
    """Hauptfunktion"""
    logger.info(f"Starte GENXAIS-Zyklus {VERSION}")
    
    ***REMOVED*** Initialisiere LangGraph
    graph = GenxaisCycleGraph.load("VALEO-NeuroERP")
    await graph.initialize()
    
    ***REMOVED*** Prüfe Kommandozeilenargumente
    import argparse
    parser = argparse.ArgumentParser(description="GENXAIS-Zyklus v1.9")
    parser.add_argument("--phase", choices=["VAN", "PLAN", "CREATE", "IMPLEMENT", "REFLECT"], default="PLAN",
                        help="Phase des GENXAIS-Zyklus")
    parser.add_argument("--transition", action="store_true", help="Führt einen Phasenübergang durch")
    parser.add_argument("--to", choices=["VAN", "PLAN", "CREATE", "IMPLEMENT", "REFLECT"],
                        help="Zielphase für den Übergang")
    args = parser.parse_args()
    
    if args.transition and args.to:
        ***REMOVED*** Führe Phasenübergang durch
        result = await graph.transition_phase(
            target_phase=args.to,
            version=VERSION,
            handover=True,
            memory_sources=[
                "memory-bank",
                "output/handover.md",
                "memory-bank/plan_phase_v1_9.md"
            ]
        )
        logger.info(f"Phasenübergang zu {args.to} abgeschlossen: {result}")
    else:
        ***REMOVED*** Starte Zyklus in der angegebenen Phase
        result = await graph.start_cycle(
            phase=args.phase,
            version=VERSION,
            strategy="auto",
            memory_sources=[
                "memory-bank",
                "output/handover.md",
                "memory-bank/improvement_backlog_v1_8_1.md",
                "memory-bank/van_analysis_v1.8.1.md",
                "memory-bank/edge_validation_report.md",
                "memory-bank/conflict_resolution_strategy.md",
                "memory-bank/metrics_framework.md",
                "memory-bank/mutation_aggregator_design.md"
            ]
        )
        logger.info(f"GENXAIS-Zyklus {VERSION} gestartet: {result}")
        
        ***REMOVED*** Erstelle Handover-Datei
        handover_path = OUTPUT_DIR / "handover.md"
        with open(handover_path, "w", encoding="utf-8") as f:
            f.write(f"""***REMOVED*** GENXAIS-Zyklus {VERSION} - Handover

***REMOVED******REMOVED*** Übersicht
- **Version:** {VERSION}
- **Phase:** {args.phase}
- **Gestartet:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Projekt:** VALEO-NeuroERP

***REMOVED******REMOVED*** Status
Der GENXAIS-Zyklus {VERSION} wurde in der {args.phase}-Phase gestartet und wird durch LangGraph gesteuert.
Die Verbesserungsvorschläge aus der VAN-Phase v1.8.1 wurden als Grundlage verwendet.

***REMOVED******REMOVED*** Nächste Schritte
1. Workpackage-Erstellung für die identifizierten Verbesserungsbereiche
2. Ressourcenzuweisung für die Implementierung
3. Risikobewertung und Zeitplanung
4. Übergang zur CREATE-Phase
""")
        
        logger.info(f"Handover-Datei erstellt: {handover_path}")
    
    return result

if __name__ == "__main__":
    asyncio.run(main()) 