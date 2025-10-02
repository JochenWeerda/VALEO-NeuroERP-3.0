#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
VALEO-NeuroERP Abschlusscheckliste

Dieses Skript generiert eine Abschlusscheckliste für das VALEO-NeuroERP-Projekt
und verfolgt den Fortschritt der einzelnen Aufgaben.
"""

import os
import sys
import json
import yaml
import argparse
from datetime import datetime
from pathlib import Path
import logging

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("final_checklist.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("final_checklist")

class ProjectCompletionChecker:
    """Klasse zur Überprüfung des Projektfortschritts und zur Generierung einer Abschlusscheckliste"""
    
    def __init__(self, config_path=None):
        """Initialisiert den ProjectCompletionChecker"""
        self.config_path = config_path
        self.config = self.load_config() if config_path else self.default_config()
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Pfade für Ausgabedateien
        self.checklist_path = self.output_dir / "final_checklist.md"
        self.status_path = self.output_dir / "completion_status.json"
        
    def load_config(self):
        """Lädt die Konfiguration aus einer YAML-Datei"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            logger.info(f"Konfiguration erfolgreich geladen aus {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Fehler beim Laden der Konfiguration: {e}")
            return self.default_config()
    
    def default_config(self):
        """Erstellt eine Standardkonfiguration"""
        return {
            "project_name": "VALEO-NeuroERP",
            "version": "1.0",
            "categories": [
                {
                    "name": "Funktionale Vollständigkeit",
                    "weight": 30,
                    "items": [
                        {"name": "Backend-API vollständig", "weight": 10, "status": "pending"},
                        {"name": "Frontend-Komponenten vollständig", "weight": 10, "status": "pending"},
                        {"name": "Datenmodelle vollständig", "weight": 5, "status": "pending"},
                        {"name": "Business-Logik implementiert", "weight": 5, "status": "pending"}
                    ]
                },
                {
                    "name": "Qualitätssicherung",
                    "weight": 25,
                    "items": [
                        {"name": "Unit-Tests implementiert", "weight": 5, "status": "pending"},
                        {"name": "Integrationstests implementiert", "weight": 5, "status": "pending"},
                        {"name": "End-to-End-Tests implementiert", "weight": 5, "status": "pending"},
                        {"name": "Performance-Tests durchgeführt", "weight": 5, "status": "pending"},
                        {"name": "Sicherheitstests durchgeführt", "weight": 5, "status": "pending"}
                    ]
                },
                {
                    "name": "Dokumentation",
                    "weight": 20,
                    "items": [
                        {"name": "API-Dokumentation", "weight": 5, "status": "pending"},
                        {"name": "Benutzerhandbuch", "weight": 5, "status": "pending"},
                        {"name": "Entwicklerdokumentation", "weight": 5, "status": "pending"},
                        {"name": "Installationsanleitung", "weight": 5, "status": "pending"}
                    ]
                },
                {
                    "name": "Deployment",
                    "weight": 15,
                    "items": [
                        {"name": "Docker-Container konfiguriert", "weight": 5, "status": "pending"},
                        {"name": "Kubernetes-Manifeste erstellt", "weight": 5, "status": "pending"},
                        {"name": "CI/CD-Pipeline eingerichtet", "weight": 5, "status": "pending"}
                    ]
                },
                {
                    "name": "Projektabschluss",
                    "weight": 10,
                    "items": [
                        {"name": "Benutzerakzeptanztests durchgeführt", "weight": 3, "status": "pending"},
                        {"name": "Schulungsmaterialien erstellt", "weight": 3, "status": "pending"},
                        {"name": "Projektdokumentation übergeben", "weight": 2, "status": "pending"},
                        {"name": "Abschlussbericht erstellt", "weight": 2, "status": "pending"}
                    ]
                }
            ]
        }
    
    def save_config(self, path=None):
        """Speichert die aktuelle Konfiguration"""
        save_path = path or self.config_path or "config/final_checklist_config.yaml"
        
        try:
            # Stelle sicher, dass das Verzeichnis existiert
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, sort_keys=False)
            
            logger.info(f"Konfiguration erfolgreich gespeichert unter {save_path}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Konfiguration: {e}")
            return False
    
    def update_item_status(self, category_index, item_index, status):
        """Aktualisiert den Status eines Elements"""
        try:
            valid_statuses = ["pending", "in_progress", "completed", "blocked"]
            if status not in valid_statuses:
                logger.error(f"Ungültiger Status: {status}. Gültige Werte sind: {', '.join(valid_statuses)}")
                return False
            
            self.config["categories"][category_index]["items"][item_index]["status"] = status
            logger.info(f"Status aktualisiert: {self.config['categories'][category_index]['items'][item_index]['name']} -> {status}")
            return True
        except IndexError:
            logger.error(f"Ungültiger Index: Kategorie {category_index}, Element {item_index}")
            return False
    
    def calculate_progress(self):
        """Berechnet den Gesamtfortschritt des Projekts"""
        total_weight = 0
        completed_weight = 0
        
        for category in self.config["categories"]:
            cat_weight = category.get("weight", 0)
            cat_completed = 0
            cat_total = 0
            
            for item in category.get("items", []):
                item_weight = item.get("weight", 0)
                cat_total += item_weight
                
                if item.get("status") == "completed":
                    cat_completed += item_weight
            
            # Normalisiere den Kategoriefortschritt
            if cat_total > 0:
                category_progress = cat_completed / cat_total
            else:
                category_progress = 0
            
            total_weight += cat_weight
            completed_weight += cat_weight * category_progress
        
        # Berechne den Gesamtfortschritt
        if total_weight > 0:
            overall_progress = (completed_weight / total_weight) * 100
        else:
            overall_progress = 0
        
        return round(overall_progress, 2)
    
    def generate_checklist(self):
        """Generiert eine Markdown-Checkliste"""
        progress = self.calculate_progress()
        
        checklist = f"""# {self.config['project_name']} Abschlusscheckliste

## Übersicht

- **Projekt**: {self.config['project_name']}
- **Version**: {self.config['version']}
- **Generiert am**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Gesamtfortschritt**: {progress}%

## Checkliste

"""
        
        for cat_index, category in enumerate(self.config["categories"]):
            cat_name = category.get("name", f"Kategorie {cat_index + 1}")
            cat_weight = category.get("weight", 0)
            
            # Berechne den Kategoriefortschritt
            cat_completed = sum(item.get("weight", 0) for item in category.get("items", []) if item.get("status") == "completed")
            cat_total = sum(item.get("weight", 0) for item in category.get("items", []))
            
            if cat_total > 0:
                cat_progress = (cat_completed / cat_total) * 100
            else:
                cat_progress = 0
            
            checklist += f"### {cat_name} ({cat_progress:.2f}%)\n\n"
            
            for item_index, item in enumerate(category.get("items", [])):
                item_name = item.get("name", f"Element {item_index + 1}")
                item_status = item.get("status", "pending")
                item_weight = item.get("weight", 0)
                
                checkbox = "x" if item_status == "completed" else " "
                status_emoji = {
                    "pending": "⬜",
                    "in_progress": "🟨",
                    "completed": "✅",
                    "blocked": "🚫"
                }.get(item_status, "⬜")
                
                checklist += f"- [{checkbox}] {status_emoji} **{item_name}** (Gewichtung: {item_weight})\n"
            
            checklist += "\n"
        
        # Füge Legende hinzu
        checklist += """## Legende

- ⬜ Ausstehend
- 🟨 In Bearbeitung
- ✅ Abgeschlossen
- 🚫 Blockiert

## Nächste Schritte

1. Aktualisieren Sie den Status der Elemente mit dem Befehl:
   ```
   python scripts/final_checklist.py update --category <index> --item <index> --status <status>
   ```

2. Generieren Sie einen neuen Bericht mit dem Befehl:
   ```
   python scripts/final_checklist.py report
   ```

"""
        
        # Speichere die Checkliste
        try:
            with open(self.checklist_path, 'w', encoding='utf-8') as file:
                file.write(checklist)
            
            logger.info(f"Checkliste erfolgreich generiert: {self.checklist_path}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Generieren der Checkliste: {e}")
            return False
    
    def save_status(self):
        """Speichert den aktuellen Status als JSON"""
        progress = self.calculate_progress()
        
        status_data = {
            "project_name": self.config["project_name"],
            "version": self.config["version"],
            "timestamp": datetime.now().isoformat(),
            "overall_progress": progress,
            "categories": []
        }
        
        for category in self.config["categories"]:
            cat_name = category.get("name", "")
            cat_weight = category.get("weight", 0)
            
            # Berechne den Kategoriefortschritt
            cat_completed = sum(item.get("weight", 0) for item in category.get("items", []) if item.get("status") == "completed")
            cat_total = sum(item.get("weight", 0) for item in category.get("items", []))
            
            if cat_total > 0:
                cat_progress = (cat_completed / cat_total) * 100
            else:
                cat_progress = 0
            
            cat_data = {
                "name": cat_name,
                "weight": cat_weight,
                "progress": round(cat_progress, 2),
                "items": []
            }
            
            for item in category.get("items", []):
                item_data = {
                    "name": item.get("name", ""),
                    "weight": item.get("weight", 0),
                    "status": item.get("status", "pending")
                }
                cat_data["items"].append(item_data)
            
            status_data["categories"].append(cat_data)
        
        # Speichere den Status
        try:
            with open(self.status_path, 'w', encoding='utf-8') as file:
                json.dump(status_data, file, indent=2)
            
            logger.info(f"Status erfolgreich gespeichert: {self.status_path}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Status: {e}")
            return False
    
    def analyze_project(self):
        """Analysiert das Projekt und aktualisiert die Checkliste automatisch"""
        try:
            logger.info("Analysiere Projekt...")
            
            # Zähle Python-Dateien und Tests
            python_files = 0
            test_files = 0
            
            for root, _, files in os.walk('.'):
                # Ignoriere versteckte Verzeichnisse und venv
                if '/.' in root or '\\.' in root or '/venv' in root or '\\venv' in root:
                    continue
                
                for file in files:
                    if file.endswith('.py'):
                        python_files += 1
                        if '/tests/' in root or '\\tests\\' in root or file.startswith('test_'):
                            test_files += 1
            
            # Überprüfe Docker-Dateien
            docker_files = []
            for root, _, files in os.walk('.'):
                for file in files:
                    if file == 'Dockerfile' or file.endswith('.Dockerfile') or file == 'docker-compose.yml' or file == 'docker-compose.yaml':
                        docker_files.append(os.path.join(root, file))
            
            # Überprüfe Kubernetes-Dateien
            k8s_files = []
            try:
                for root, _, files in os.walk('./kubernetes'):
                    for file in files:
                        if file.endswith('.yaml') or file.endswith('.yml'):
                            k8s_files.append(os.path.join(root, file))
            except:
                pass
            
            # Überprüfe Dokumentationsdateien
            api_docs = []
            user_docs = []
            dev_docs = []
            
            try:
                for root, _, files in os.walk('./docs'):
                    for file in files:
                        if file.endswith('.md') or file.endswith('.rst'):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read().lower()
                                    if 'api' in content and ('endpoint' in content or 'route' in content):
                                        api_docs.append(file_path)
                                    if 'user' in content and ('guide' in content or 'manual' in content):
                                        user_docs.append(file_path)
                                    if 'developer' in content or 'architecture' in content:
                                        dev_docs.append(file_path)
                            except:
                                pass
            except:
                pass
            
            # Aktualisiere die Checkliste basierend auf den Ergebnissen
            for cat_index, category in enumerate(self.config["categories"]):
                cat_name = category.get("name", "").lower()
                
                for item_index, item in enumerate(category.get("items", [])):
                    item_name = item.get("name", "").lower()
                    
                    # Aktualisiere den Status basierend auf den Analyseresultaten
                    if "unit-tests" in item_name and test_files > 0:
                        self.update_item_status(cat_index, item_index, "completed")
                    
                    if "docker" in item_name and len(docker_files) > 0:
                        self.update_item_status(cat_index, item_index, "completed")
                    
                    if "kubernetes" in item_name and len(k8s_files) > 0:
                        self.update_item_status(cat_index, item_index, "completed")
                    
                    if "api-dokumentation" in item_name and len(api_docs) > 0:
                        self.update_item_status(cat_index, item_index, "completed")
                    
                    if "benutzerhandbuch" in item_name and len(user_docs) > 0:
                        self.update_item_status(cat_index, item_index, "completed")
                    
                    if "entwicklerdokumentation" in item_name and len(dev_docs) > 0:
                        self.update_item_status(cat_index, item_index, "completed")
            
            logger.info("Projektanalyse abgeschlossen")
            return True
        except Exception as e:
            logger.error(f"Fehler bei der Projektanalyse: {e}")
            return False

def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(description="VALEO-NeuroERP Abschlusscheckliste")
    subparsers = parser.add_subparsers(dest="command", help="Befehle")
    
    # Befehl: init
    init_parser = subparsers.add_parser("init", help="Initialisiert die Abschlusscheckliste")
    init_parser.add_argument("--config", help="Pfad zur Konfigurationsdatei")
    
    # Befehl: update
    update_parser = subparsers.add_parser("update", help="Aktualisiert den Status eines Elements")
    update_parser.add_argument("--config", help="Pfad zur Konfigurationsdatei")
    update_parser.add_argument("--category", type=int, required=True, help="Index der Kategorie (0-basiert)")
    update_parser.add_argument("--item", type=int, required=True, help="Index des Elements (0-basiert)")
    update_parser.add_argument("--status", choices=["pending", "in_progress", "completed", "blocked"], required=True, help="Neuer Status")
    
    # Befehl: report
    report_parser = subparsers.add_parser("report", help="Generiert einen Bericht")
    report_parser.add_argument("--config", help="Pfad zur Konfigurationsdatei")
    
    # Befehl: analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analysiert das Projekt und aktualisiert die Checkliste")
    analyze_parser.add_argument("--config", help="Pfad zur Konfigurationsdatei")
    
    args = parser.parse_args()
    
    # Standardbefehl, wenn keiner angegeben wurde
    if not args.command:
        args.command = "report"
    
    # Erstelle den ProjectCompletionChecker
    checker = ProjectCompletionChecker(args.config if hasattr(args, "config") and args.config else None)
    
    # Führe den entsprechenden Befehl aus
    if args.command == "init":
        checker.save_config("config/final_checklist_config.yaml")
        logger.info("Abschlusscheckliste initialisiert")
    
    elif args.command == "update":
        if checker.update_item_status(args.category, args.item, args.status):
            checker.save_config()
            checker.generate_checklist()
            checker.save_status()
            logger.info(f"Status aktualisiert und Bericht generiert")
        else:
            logger.error("Fehler beim Aktualisieren des Status")
    
    elif args.command == "report":
        checker.generate_checklist()
        checker.save_status()
        logger.info(f"Bericht generiert: {checker.checklist_path}")
    
    elif args.command == "analyze":
        checker.analyze_project()
        checker.save_config()
        checker.generate_checklist()
        checker.save_status()
        logger.info("Projektanalyse durchgeführt und Bericht generiert")

if __name__ == "__main__":
    main() 