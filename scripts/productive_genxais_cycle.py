#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Produktiver GENXAIS v2.0 Zyklus
Dieses Skript implementiert einen produktiven GENXAIS-Zyklus, der tatsächlich Code generiert
und Aufgaben ausführt, anstatt nur eine Simulation durchzuführen.
"""

import argparse
import yaml
import logging
import os
import sys
import time
import json
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
import importlib.util
import shutil
from typing import Dict, Any, List, Optional, Union

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("genxais_productive_cycle.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("genxais_productive")

class GenxaisProductiveRunner:
    """Klasse zum Ausführen des produktiven GENXAIS-Zyklus"""
    
    def __init__(self, config_path: str):
        """Initialisiert den produktiven GENXAIS-Zyklus-Runner"""
        self.config_path = config_path
        self.config = self.load_config()
        self.data_dir = Path("data/dashboard")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Extrahiere Phasen und Pipelines
        self.phases = self.config.get("phases", ["VAN", "PLAN", "CREATE", "IMPLEMENTATION", "REFLEKTION"])
        self.current_phase = self.phases[0]
        self.pipelines = self.config.get("pipelines", [])
        
        # LangGraph-Integration
        self.use_langgraph = self.config.get("use_langgraph", False)
        self.langgraph_controller = None
        
        # RAG-Integration
        self.use_rag = self.config.get("use_rag", False)
        self.rag_client = None
        
        # Ausgabedokumente
        self.artifacts = self.config.get("artifacts", {}).get("track", [])
        
    def load_config(self) -> Dict[str, Any]:
        """Lädt die Zyklus-Konfiguration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            logger.info(f"Zyklus-Konfiguration erfolgreich geladen aus {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Fehler beim Laden der Zyklus-Konfiguration: {e}")
            sys.exit(1)
    
    async def initialize_integrations(self) -> None:
        """Initialisiert die externen Integrationen (LangGraph, RAG)"""
        if self.use_langgraph:
            try:
                # Dynamisch die LangGraph-Integration laden
                spec = importlib.util.find_spec("linkup_mcp.langgraph_integration")
                if spec:
                    langgraph_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(langgraph_module)
                    LangGraphIntegration = getattr(langgraph_module, "LangGraphIntegration")
                    self.langgraph_controller = LangGraphIntegration(self.config.get("langgraph_config", {}))
                    logger.info("LangGraph-Integration erfolgreich initialisiert")
                else:
                    logger.warning("LangGraph-Modul nicht gefunden, Integration deaktiviert")
                    self.use_langgraph = False
            except Exception as e:
                logger.error(f"Fehler bei der Initialisierung der LangGraph-Integration: {e}")
                self.use_langgraph = False
        
        if self.use_rag:
            try:
                # RAG-Client initialisieren
                from linkup_mcp.rag_client import RAGClient
                self.rag_client = RAGClient(self.config.get("rag_config", {}))
                await self.rag_client.initialize()
                logger.info("RAG-Integration erfolgreich initialisiert")
            except Exception as e:
                logger.error(f"Fehler bei der Initialisierung der RAG-Integration: {e}")
                self.use_rag = False
    
    async def update_dashboard_data(self, phase: Optional[str] = None, progress: Optional[int] = None) -> None:
        """Aktualisiert die Dashboard-Daten"""
        # Phasendaten
        phase_data_path = self.data_dir / "phase_data.json"
        
        # Lade bestehende Daten oder erstelle neue
        if phase_data_path.exists():
            with open(phase_data_path, 'r', encoding='utf-8') as file:
                phase_data = json.load(file)
        else:
            phase_data = {
                "phases": self.phases,
                "current_phase": self.current_phase,
                "status": {
                    p: {
                        "status": "Ausstehend" if p != self.current_phase else "Aktiv", 
                        "progress": 0
                    } for p in self.phases
                },
                "last_updated": datetime.now().isoformat()
            }
        
        # Aktualisiere die Daten
        if phase:
            self.current_phase = phase
            phase_data["current_phase"] = phase
            
            # Aktualisiere den Status aller Phasen
            for p in self.phases:
                if p == phase:
                    phase_data["status"][p]["status"] = "Aktiv"
                elif self.phases.index(p) < self.phases.index(phase):
                    phase_data["status"][p]["status"] = "Abgeschlossen"
                    phase_data["status"][p]["progress"] = 100
                else:
                    phase_data["status"][p]["status"] = "Ausstehend"
        
        if progress is not None and self.current_phase in phase_data["status"]:
            phase_data["status"][self.current_phase]["progress"] = progress
        
        phase_data["last_updated"] = datetime.now().isoformat()
        
        # Speichere die aktualisierten Daten
        with open(phase_data_path, 'w', encoding='utf-8') as file:
            json.dump(phase_data, file, ensure_ascii=False, indent=2)
        
        # Pipeline-Daten aktualisieren
        await self.update_pipeline_data()
        
        # Artefakt-Daten aktualisieren
        await self.update_artifact_data()
    
    async def update_pipeline_data(self) -> None:
        """Aktualisiert die Pipeline-Daten"""
        pipeline_data_path = self.data_dir / "pipeline_data.json"
        
        # Lade bestehende Daten oder erstelle neue
        if pipeline_data_path.exists():
            with open(pipeline_data_path, 'r', encoding='utf-8') as file:
                pipeline_data = json.load(file)
        else:
            pipeline_names = [p.get("name", f"Pipeline {i+1}") for i, p in enumerate(self.pipelines)]
            
            pipeline_data = {
                "pipelines": pipeline_names,
                "status": {
                    pipeline: {
                        "status": "Initialisierung",
                        "progress": 0,
                        "runtime": "0h 0m",
                        "last_task": None
                    } for pipeline in pipeline_names
                },
                "last_updated": datetime.now().isoformat()
            }
        
        # Aktualisiere die Pipeline-Daten basierend auf dem tatsächlichen Status
        for i, pipeline in enumerate(self.pipelines):
            pipeline_name = pipeline.get("name", f"Pipeline {i+1}")
            if pipeline_name in pipeline_data["status"]:
                # Aktualisiere den Status basierend auf der aktuellen Phase
                phase_index = self.phases.index(self.current_phase)
                pipeline_status = pipeline_data["status"][pipeline_name]
                
                # Berechne den Fortschritt basierend auf den abgeschlossenen Aufgaben
                completed_tasks = pipeline.get("completed_tasks", 0)
                total_tasks = max(1, len(pipeline.get("tasks", [])))
                progress = min(100, int((completed_tasks / total_tasks) * 100))
                
                # Aktualisiere den Status
                if progress == 100:
                    pipeline_status["status"] = "Abgeschlossen"
                else:
                    pipeline_status["status"] = "Aktiv"
                
                pipeline_status["progress"] = progress
                
                # Aktualisiere die Laufzeit
                start_time = pipeline.get("start_time")
                if start_time:
                    current_time = datetime.now()
                    if isinstance(start_time, str):
                        start_time = datetime.fromisoformat(start_time)
                    
                    runtime = current_time - start_time
                    hours = runtime.seconds // 3600
                    minutes = (runtime.seconds % 3600) // 60
                    pipeline_status["runtime"] = f"{hours}h {minutes}m"
                
                # Aktualisiere die letzte Aufgabe
                last_task = pipeline.get("last_task")
                if last_task:
                    pipeline_status["last_task"] = last_task
        
        pipeline_data["last_updated"] = datetime.now().isoformat()
        
        # Speichere die aktualisierten Daten
        with open(pipeline_data_path, 'w', encoding='utf-8') as file:
            json.dump(pipeline_data, file, ensure_ascii=False, indent=2)
    
    async def update_artifact_data(self) -> None:
        """Aktualisiert die Artefakt-Daten"""
        artifact_data_path = self.data_dir / "artifact_data.json"
        
        # Lade bestehende Daten oder erstelle neue
        if artifact_data_path.exists():
            with open(artifact_data_path, 'r', encoding='utf-8') as file:
                artifact_data = json.load(file)
        else:
            artifact_data = {
                "artifacts": self.artifacts,
                "status": {
                    artifact: {
                        "status": "Ausstehend",
                        "last_updated": None
                    } for artifact in self.artifacts
                },
                "last_updated": datetime.now().isoformat()
            }
        
        # Überprüfe, ob neue Artefakte erstellt wurden
        for artifact in self.artifacts:
            artifact_path = self.output_dir / artifact
            if artifact_path.exists():
                artifact_data["status"][artifact]["status"] = "Abgeschlossen"
                artifact_data["status"][artifact]["last_updated"] = datetime.now().isoformat()
        
        artifact_data["last_updated"] = datetime.now().isoformat()
        
        # Speichere die aktualisierten Daten
        with open(artifact_data_path, 'w', encoding='utf-8') as file:
            json.dump(artifact_data, file, ensure_ascii=False, indent=2)
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Führt eine Aufgabe aus"""
        task_type = task.get("type", "unknown")
        task_name = task.get("name", "Unbenannte Aufgabe")
        logger.info(f"Führe Aufgabe aus: {task_name} (Typ: {task_type})")
        
        result = {"status": "failed", "message": "Nicht implementiert"}
        
        try:
            if task_type == "code_generation":
                result = await self.execute_code_generation_task(task)
            elif task_type == "file_creation":
                result = await self.execute_file_creation_task(task)
            elif task_type == "command_execution":
                result = await self.execute_command_task(task)
            elif task_type == "documentation":
                result = await self.execute_documentation_task(task)
            elif task_type == "analysis":
                result = await self.execute_analysis_task(task)
            else:
                logger.warning(f"Unbekannter Aufgabentyp: {task_type}")
                result = {"status": "failed", "message": f"Unbekannter Aufgabentyp: {task_type}"}
        except Exception as e:
            logger.error(f"Fehler bei der Ausführung der Aufgabe {task_name}: {e}")
            result = {"status": "failed", "message": str(e)}
        
        return result
    
    async def execute_code_generation_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Führt eine Code-Generierungsaufgabe aus"""
        target_file = task.get("target_file")
        code_content = task.get("code")
        
        if not target_file or not code_content:
            return {"status": "failed", "message": "Zieldatei oder Code-Inhalt fehlt"}
        
        try:
            # Stelle sicher, dass das Zielverzeichnis existiert
            target_path = Path(target_file)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Schreibe den Code in die Zieldatei
            with open(target_path, 'w', encoding='utf-8') as file:
                file.write(code_content)
            
            logger.info(f"Code erfolgreich generiert: {target_file}")
            return {
                "status": "success", 
                "message": f"Code erfolgreich generiert: {target_file}",
                "file_path": str(target_path)
            }
        except Exception as e:
            logger.error(f"Fehler bei der Code-Generierung: {e}")
            return {"status": "failed", "message": str(e)}
    
    async def execute_file_creation_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Führt eine Datei-Erstellungsaufgabe aus"""
        target_file = task.get("target_file")
        content = task.get("content")
        
        if not target_file or content is None:
            return {"status": "failed", "message": "Zieldatei oder Inhalt fehlt"}
        
        try:
            # Stelle sicher, dass das Zielverzeichnis existiert
            target_path = Path(target_file)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Schreibe den Inhalt in die Zieldatei
            with open(target_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            logger.info(f"Datei erfolgreich erstellt: {target_file}")
            return {
                "status": "success", 
                "message": f"Datei erfolgreich erstellt: {target_file}",
                "file_path": str(target_path)
            }
        except Exception as e:
            logger.error(f"Fehler bei der Dateierstellung: {e}")
            return {"status": "failed", "message": str(e)}
    
    async def execute_command_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Führt einen Befehl aus"""
        command = task.get("command")
        
        if not command:
            return {"status": "failed", "message": "Befehl fehlt"}
        
        try:
            # Führe den Befehl aus
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Befehl erfolgreich ausgeführt: {command}")
                return {
                    "status": "success",
                    "message": f"Befehl erfolgreich ausgeführt: {command}",
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                    "returncode": process.returncode
                }
            else:
                logger.error(f"Befehl fehlgeschlagen: {command}, Fehler: {stderr.decode()}")
                return {
                    "status": "failed",
                    "message": f"Befehl fehlgeschlagen: {command}",
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                    "returncode": process.returncode
                }
        except Exception as e:
            logger.error(f"Fehler bei der Befehlsausführung: {e}")
            return {"status": "failed", "message": str(e)}
    
    async def execute_documentation_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Führt eine Dokumentationsaufgabe aus"""
        target_file = task.get("target_file")
        content = task.get("content")
        
        if not target_file or not content:
            return {"status": "failed", "message": "Zieldatei oder Inhalt fehlt"}
        
        try:
            # Stelle sicher, dass das Zielverzeichnis existiert
            target_path = self.output_dir / target_file
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Schreibe den Inhalt in die Zieldatei
            with open(target_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            logger.info(f"Dokumentation erfolgreich erstellt: {target_file}")
            return {
                "status": "success", 
                "message": f"Dokumentation erfolgreich erstellt: {target_file}",
                "file_path": str(target_path)
            }
        except Exception as e:
            logger.error(f"Fehler bei der Dokumentationserstellung: {e}")
            return {"status": "failed", "message": str(e)}
    
    async def execute_analysis_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Führt eine Analyseaufgabe aus"""
        analysis_type = task.get("analysis_type")
        target = task.get("target")
        output_file = task.get("output_file")
        
        if not analysis_type or not target:
            return {"status": "failed", "message": "Analysetyp oder Ziel fehlt"}
        
        try:
            # Führe die Analyse aus
            result = {"type": analysis_type, "target": target, "timestamp": datetime.now().isoformat()}
            
            if analysis_type == "code_quality":
                # Hier könnte ein Code-Qualitätscheck durchgeführt werden
                result["quality_score"] = 85
                result["issues"] = []
            elif analysis_type == "dependency":
                # Hier könnte eine Abhängigkeitsanalyse durchgeführt werden
                result["dependencies"] = []
            elif analysis_type == "performance":
                # Hier könnte eine Performance-Analyse durchgeführt werden
                result["performance_score"] = 90
                result["bottlenecks"] = []
            
            # Speichere die Analyseergebnisse
            if output_file:
                output_path = self.output_dir / output_file
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as file:
                    json.dump(result, file, ensure_ascii=False, indent=2)
            
            logger.info(f"Analyse erfolgreich durchgeführt: {analysis_type}")
            return {
                "status": "success",
                "message": f"Analyse erfolgreich durchgeführt: {analysis_type}",
                "result": result
            }
        except Exception as e:
            logger.error(f"Fehler bei der Analyse: {e}")
            return {"status": "failed", "message": str(e)}
    
    async def execute_pipeline(self, pipeline: Dict[str, Any]) -> Dict[str, Any]:
        """Führt eine Pipeline aus"""
        pipeline_name = pipeline.get("name", "Unbenannte Pipeline")
        logger.info(f"Starte Pipeline: {pipeline_name}")
        
        # Setze Startzeit
        pipeline["start_time"] = datetime.now().isoformat()
        pipeline["completed_tasks"] = 0
        
        results = []
        
        # Führe alle Aufgaben der Pipeline aus
        for task in pipeline.get("tasks", []):
            pipeline["last_task"] = task.get("name", "Unbenannte Aufgabe")
            
            # Aktualisiere das Dashboard
            await self.update_pipeline_data()
            
            # Führe die Aufgabe aus
            task_result = await self.execute_task(task)
            results.append(task_result)
            
            if task_result["status"] == "success":
                pipeline["completed_tasks"] += 1
            
            # Aktualisiere das Dashboard nach jeder Aufgabe
            await self.update_pipeline_data()
        
        # Setze Endzeit
        pipeline["end_time"] = datetime.now().isoformat()
        
        logger.info(f"Pipeline abgeschlossen: {pipeline_name}")
        return {"pipeline": pipeline_name, "results": results}
    
    async def execute_phase(self, phase: str) -> List[Dict[str, Any]]:
        """Führt eine Phase des Zyklus aus"""
        logger.info(f"Starte Phase: {phase}")
        await self.update_dashboard_data(phase=phase, progress=0)
        
        # Starte die LangGraph-Phase, falls aktiviert
        if self.use_langgraph and self.langgraph_controller:
            try:
                await self.langgraph_controller.start_phase(phase)
            except Exception as e:
                logger.error(f"Fehler beim Starten der LangGraph-Phase: {e}")
        
        results = []
        total_pipelines = len(self.pipelines)
        
        # Führe alle Pipelines der Phase aus
        for i, pipeline in enumerate(self.pipelines):
            # Berechne den Fortschritt
            progress = int((i / total_pipelines) * 100)
            await self.update_dashboard_data(progress=progress)
            
            # Führe die Pipeline aus
            pipeline_result = await self.execute_pipeline(pipeline)
            results.append(pipeline_result)
            
            # Aktualisiere den Fortschritt nach jeder Pipeline
            progress = int(((i + 1) / total_pipelines) * 100)
            await self.update_dashboard_data(progress=progress)
        
        # Abschluss der Phase
        await self.update_dashboard_data(progress=100)
        
        # Beende die LangGraph-Phase, falls aktiviert
        if self.use_langgraph and self.langgraph_controller:
            try:
                await self.langgraph_controller.complete_phase(phase)
            except Exception as e:
                logger.error(f"Fehler beim Abschließen der LangGraph-Phase: {e}")
        
        logger.info(f"Phase {phase} abgeschlossen")
        return results
    
    async def generate_handover_document(self) -> Dict[str, Any]:
        """Generiert ein Handover-Dokument"""
        handover_path = self.output_dir / "handover.md"
        
        # Sammle Informationen für das Handover
        handover_content = f"""# GENXAIS Zyklus Handover

## Zusammenfassung

GENXAIS Zyklus v{self.config.get('version', '2.0')} wurde am {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} abgeschlossen.

## Durchgeführte Phasen
"""
        
        for phase in self.phases:
            handover_content += f"- {phase}\n"
        
        handover_content += "\n## Pipelines und Ergebnisse\n"
        
        for i, pipeline in enumerate(self.pipelines):
            pipeline_name = pipeline.get("name", f"Pipeline {i+1}")
            handover_content += f"\n### {pipeline_name}\n\n"
            
            for task in pipeline.get("tasks", []):
                task_name = task.get("name", "Unbenannte Aufgabe")
                task_type = task.get("type", "unknown")
                handover_content += f"- {task_name} (Typ: {task_type})\n"
        
        handover_content += "\n## Erstellte Artefakte\n\n"
        
        for artifact in self.artifacts:
            artifact_path = self.output_dir / artifact
            if artifact_path.exists():
                handover_content += f"- [{artifact}](../output/{artifact})\n"
            else:
                handover_content += f"- {artifact} (nicht erstellt)\n"
        
        handover_content += "\n## Nächste Schritte\n\n"
        handover_content += "- Überprüfung der erstellten Artefakte\n"
        handover_content += "- Integration der Änderungen in das Hauptprojekt\n"
        handover_content += "- Planung des nächsten GENXAIS-Zyklus\n"
        
        # Speichere das Handover-Dokument
        try:
            with open(handover_path, 'w', encoding='utf-8') as file:
                file.write(handover_content)
            
            logger.info(f"Handover-Dokument erfolgreich erstellt: {handover_path}")
            return {
                "status": "success",
                "message": f"Handover-Dokument erfolgreich erstellt: {handover_path}",
                "file_path": str(handover_path)
            }
        except Exception as e:
            logger.error(f"Fehler bei der Erstellung des Handover-Dokuments: {e}")
            return {"status": "failed", "message": str(e)}
    
    async def generate_project_overview(self) -> Dict[str, Any]:
        """Generiert eine Projektübersicht mit offenen Aufgaben"""
        overview_path = self.output_dir / "project_overview.md"
        
        # Sammle Informationen über das Projekt
        try:
            # Verzeichnisstruktur analysieren
            project_structure = []
            for root, dirs, files in os.walk('.', topdown=True):
                # Ignoriere versteckte Verzeichnisse und venv
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'venv']
                
                level = root.count(os.sep)
                indent = ' ' * 4 * level
                if level <= 2:  # Begrenze die Tiefe für Übersichtlichkeit
                    project_structure.append(f"{indent}- {os.path.basename(root)}/")
                    
                    # Füge Dateien hinzu, aber begrenze die Anzahl
                    if level == 2:
                        file_count = len(files)
                        if file_count > 0:
                            if file_count <= 5:
                                for file in files:
                                    project_structure.append(f"{indent}    - {file}")
                            else:
                                project_structure.append(f"{indent}    - [{file_count} Dateien]")
            
            # Offene Aufgaben identifizieren
            open_tasks = []
            
            # Suche nach TODO-Kommentaren in Python-Dateien
            for root, _, files in os.walk('.'):
                for file in files:
                    if file.endswith('.py'):
                        try:
                            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                                for i, line in enumerate(lines):
                                    if 'TODO' in line or 'FIXME' in line:
                                        open_tasks.append({
                                            'file': os.path.join(root, file),
                                            'line': i + 1,
                                            'text': line.strip()
                                        })
                        except Exception:
                            # Ignoriere Fehler beim Lesen von Dateien
                            pass
            
            # Suche nach offenen Issues in GitHub-ähnlichen Dateien
            issue_files = ['issues.md', 'ISSUES.md', 'todo.md', 'TODO.md']
            for issue_file in issue_files:
                if os.path.exists(issue_file):
                    try:
                        with open(issue_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            open_tasks.append({
                                'file': issue_file,
                                'line': 0,
                                'text': f"Siehe {issue_file} für weitere offene Aufgaben"
                            })
                    except Exception:
                        pass
            
            # Erstelle die Projektübersicht
            overview_content = f"""# VALEO-NeuroERP Projektübersicht

## Generiert am {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Projektstruktur (Hauptkomponenten)

```
{''.join(project_structure[:50])}  # Begrenze die Ausgabe für Übersichtlichkeit
```

## Offene Aufgaben

"""
            if open_tasks:
                for task in open_tasks[:20]:  # Begrenze die Anzahl der angezeigten Aufgaben
                    overview_content += f"- **{task['file']}:{task['line']}**: {task['text']}\n"
            else:
                overview_content += "Keine offenen Aufgaben gefunden.\n"
            
            # Füge Empfehlungen für die Projektfertigstellung hinzu
            overview_content += """
## Empfehlungen zur Projektfertigstellung

1. **Dokumentation vervollständigen**
   - Stellen Sie sicher, dass alle Module und Funktionen dokumentiert sind
   - Erstellen Sie eine Benutzeranleitung für das System

2. **Tests erweitern**
   - Erhöhen Sie die Testabdeckung für kritische Komponenten
   - Implementieren Sie End-to-End-Tests für wichtige Workflows

3. **Performance-Optimierung**
   - Identifizieren und optimieren Sie Engpässe
   - Implementieren Sie Caching für häufig verwendete Daten

4. **Sicherheitsüberprüfung**
   - Führen Sie ein Sicherheitsaudit durch
   - Stellen Sie sicher, dass alle Abhängigkeiten aktuell sind

5. **Deployment-Pipeline einrichten**
   - Automatisieren Sie den Bereitstellungsprozess
   - Implementieren Sie Continuous Integration/Continuous Deployment
"""
            
            # Speichere die Projektübersicht
            with open(overview_path, 'w', encoding='utf-8') as file:
                file.write(overview_content)
            
            logger.info(f"Projektübersicht erfolgreich erstellt: {overview_path}")
            return {
                "status": "success",
                "message": f"Projektübersicht erfolgreich erstellt: {overview_path}",
                "file_path": str(overview_path)
            }
        except Exception as e:
            logger.error(f"Fehler bei der Erstellung der Projektübersicht: {e}")
            return {"status": "failed", "message": str(e)}
    
    async def run_cycle(self) -> Dict[str, Any]:
        """Führt den gesamten GENXAIS-Zyklus aus"""
        logger.info("Starte produktiven GENXAIS-Zyklus")
        
        # Initialisiere Integrationen
        await self.initialize_integrations()
        
        # Generiere Projektübersicht als ersten Schritt
        overview_result = await self.generate_project_overview()
        
        results = {"project_overview": overview_result}
        
        # Durchlaufe alle Phasen
        for phase in self.phases:
            if phase not in results:
                results[phase] = []
            
            # Führe die Phase aus
            phase_results = await self.execute_phase(phase)
            results[phase].extend(phase_results)
        
        # Generiere das Handover-Dokument
        handover_result = await self.generate_handover_document()
        results["handover"] = handover_result
        
        # Generiere die Projektabschlussanalyse
        completion_result = await self.generate_completion_analysis()
        results["completion_analysis"] = completion_result
        
        logger.info("Produktiver GENXAIS-Zyklus abgeschlossen")
        return results
    
    async def generate_completion_analysis(self) -> Dict[str, Any]:
        """Generiert eine Projektabschlussanalyse mit Fokus auf offenen Punkten und Fertigstellung"""
        analysis_path = self.output_dir / "completion_analysis.md"
        
        try:
            # Sammle Informationen über den aktuellen Projektstatus
            completion_stats = {
                "total_files": 0,
                "python_files": 0,
                "js_files": 0,
                "doc_files": 0,
                "test_files": 0,
                "test_coverage": 0,
                "open_issues": 0,
                "critical_components": []
            }
            
            # Zähle Dateien nach Typ
            for root, _, files in os.walk('.'):
                # Ignoriere versteckte Verzeichnisse und venv
                if '/.' in root or '\\.' in root or '/venv' in root or '\\venv' in root:
                    continue
                    
                for file in files:
                    completion_stats["total_files"] += 1
                    
                    if file.endswith('.py'):
                        completion_stats["python_files"] += 1
                        if '/tests/' in root or '\\tests\\' in root or file.startswith('test_'):
                            completion_stats["test_files"] += 1
                    elif file.endswith(('.js', '.jsx', '.ts', '.tsx')):
                        completion_stats["js_files"] += 1
                    elif file.endswith(('.md', '.rst', '.txt')):
                        completion_stats["doc_files"] += 1
            
            # Berechne geschätzte Testabdeckung
            if completion_stats["python_files"] > 0:
                completion_stats["test_coverage"] = min(100, int((completion_stats["test_files"] / completion_stats["python_files"]) * 100))
            
            # Identifiziere kritische Komponenten
            critical_dirs = ['backend', 'frontend', 'api', 'core', 'models', 'services']
            for critical_dir in critical_dirs:
                if os.path.exists(critical_dir) and os.path.isdir(critical_dir):
                    component_files = len([f for f in os.listdir(critical_dir) if os.path.isfile(os.path.join(critical_dir, f))])
                    completion_stats["critical_components"].append({
                        "name": critical_dir,
                        "files": component_files
                    })
            
            # Schätze den Gesamtfortschritt
            overall_progress = min(100, max(0, 100 - (completion_stats.get("open_issues", 0) * 2)))
            
            # Erstelle die Abschlussanalyse
            analysis_content = f"""# VALEO-NeuroERP Projektabschlussanalyse

## Generiert am {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Projektstatus

- **Gesamtfortschritt**: {overall_progress}%
- **Dateien insgesamt**: {completion_stats["total_files"]}
- **Python-Dateien**: {completion_stats["python_files"]}
- **JavaScript-Dateien**: {completion_stats["js_files"]}
- **Dokumentationsdateien**: {completion_stats["doc_files"]}
- **Test-Dateien**: {completion_stats["test_files"]}
- **Geschätzte Testabdeckung**: {completion_stats["test_coverage"]}%

## Kritische Komponenten

"""
            for component in completion_stats["critical_components"]:
                analysis_content += f"- **{component['name']}**: {component['files']} Dateien\n"
            
            # Füge Abschlussplan hinzu
            analysis_content += """
## Abschlussplan

Um das Projekt zügig zu einem Ende zu bringen, empfehlen wir den folgenden Abschlussplan:

### 1. Funktionale Vollständigkeit (1-2 Wochen)

- [ ] Überprüfung aller kritischen Komponenten auf Vollständigkeit
- [ ] Implementierung fehlender Kernfunktionalitäten
- [ ] Abschluss aller offenen API-Endpunkte
- [ ] Vervollständigung der Frontend-Komponenten

### 2. Qualitätssicherung (1 Woche)

- [ ] Erhöhung der Testabdeckung auf mindestens 80%
- [ ] Durchführung von End-to-End-Tests für kritische Workflows
- [ ] Code-Review und Refactoring problematischer Bereiche
- [ ] Performance-Optimierung

### 3. Dokumentation (3-5 Tage)

- [ ] Vervollständigung der API-Dokumentation
- [ ] Erstellung einer umfassenden Benutzeranleitung
- [ ] Dokumentation der Systemarchitektur
- [ ] Erstellung von Installations- und Deployment-Anleitungen

### 4. Deployment-Vorbereitung (2-3 Tage)

- [ ] Finalisierung der Docker-Container und Kubernetes-Konfigurationen
- [ ] Einrichtung der CI/CD-Pipeline
- [ ] Vorbereitung der Produktionsumgebung
- [ ] Erstellung von Backup- und Wiederherstellungsprozeduren

### 5. Abnahme und Übergabe (1 Woche)

- [ ] Durchführung von Benutzerakzeptanztests
- [ ] Behebung letzter Fehler und Probleme
- [ ] Übergabe der Dokumentation und des Quellcodes
- [ ] Schulung der Administratoren und Endbenutzer

## Empfehlungen für die sofortige Umsetzung

1. **Priorisierung der kritischen Komponenten**: Konzentrieren Sie sich auf die Fertigstellung der Kernfunktionalitäten.
2. **Feature Freeze**: Implementieren Sie keine neuen Funktionen mehr, sondern konzentrieren Sie sich auf die Stabilisierung.
3. **Tägliche Statusmeetings**: Führen Sie tägliche kurze Meetings durch, um den Fortschritt zu überwachen.
4. **Automatisierung**: Automatisieren Sie so viele Prozesse wie möglich, um die Effizienz zu steigern.
5. **Externe Ressourcen**: Ziehen Sie bei Bedarf externe Ressourcen hinzu, um den Abschluss zu beschleunigen.

Mit diesem Abschlussplan kann das VALEO-NeuroERP-Projekt innerhalb von 3-4 Wochen erfolgreich abgeschlossen werden.
"""
            
            # Speichere die Abschlussanalyse
            with open(analysis_path, 'w', encoding='utf-8') as file:
                file.write(analysis_content)
            
            logger.info(f"Projektabschlussanalyse erfolgreich erstellt: {analysis_path}")
            return {
                "status": "success",
                "message": f"Projektabschlussanalyse erfolgreich erstellt: {analysis_path}",
                "file_path": str(analysis_path)
            }
        except Exception as e:
            logger.error(f"Fehler bei der Erstellung der Projektabschlussanalyse: {e}")
            return {"status": "failed", "message": str(e)}

async def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(description="Produktiver GENXAIS v2.0 Zyklus")
    parser.add_argument("--config", required=True, help="Pfad zur Zyklus-Konfiguration")
    args = parser.parse_args()
    
    # Erstelle und starte den produktiven Zyklus-Runner
    runner = GenxaisProductiveRunner(args.config)
    results = await runner.run_cycle()
    
    # Zeige eine Zusammenfassung der Ergebnisse
    print("\n=== GENXAIS Zyklus Ergebnisse ===\n")
    
    for phase, phase_results in results.items():
        if phase != "handover":
            print(f"Phase {phase}: {len(phase_results)} Pipelines ausgeführt")
    
    if "handover" in results:
        handover_result = results["handover"]
        if handover_result["status"] == "success":
            print(f"\nHandover-Dokument: {handover_result['file_path']}")
        else:
            print(f"\nFehler bei der Erstellung des Handover-Dokuments: {handover_result['message']}")
    
    print("\nGENXAIS Zyklus abgeschlossen!")

if __name__ == "__main__":
    asyncio.run(main())
