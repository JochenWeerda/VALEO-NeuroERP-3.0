#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Skript zur Aktivierung und Konfiguration der Pipeline-Integration für VALEO-NeuroERP.

Dieses Skript ermöglicht die Aktivierung/Deaktivierung und Konfiguration der
Pipeline-Integration mit dem APM-Framework.
"""

import argparse
import json
import os
import sys
from typing import Dict, Any, List, Optional

# Füge das Hauptverzeichnis zum Pythonpfad hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'apm_pipeline_integration.json')

def load_config() -> Dict[str, Any]:
    """
    Lädt die Konfiguration aus der Datei.
    
    Returns:
        Die geladene Konfiguration
    """
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Fehler: Konfigurationsdatei {CONFIG_FILE} nicht gefunden.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Fehler: Konfigurationsdatei {CONFIG_FILE} enthält ungültiges JSON.")
        sys.exit(1)

def save_config(config: Dict[str, Any]) -> None:
    """
    Speichert die Konfiguration in der Datei.
    
    Args:
        config: Die zu speichernde Konfiguration
    """
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def activate_pipeline_integration(activate: bool) -> None:
    """
    Aktiviert oder deaktiviert die Pipeline-Integration.
    
    Args:
        activate: True, um die Pipeline-Integration zu aktivieren, False, um sie zu deaktivieren
    """
    config = load_config()
    config['pipeline_integration']['enabled'] = activate
    save_config(config)
    
    status = "aktiviert" if activate else "deaktiviert"
    print(f"Pipeline-Integration wurde {status}.")

def configure_pipeline(pipeline_id: str, enabled: bool, integration_points: List[str], priority: str) -> None:
    """
    Konfiguriert eine Pipeline.
    
    Args:
        pipeline_id: Die ID der Pipeline
        enabled: True, um die Pipeline zu aktivieren, False, um sie zu deaktivieren
        integration_points: Die Integrationspunkte der Pipeline
        priority: Die Priorität der Pipeline
    """
    config = load_config()
    
    if pipeline_id not in config['pipelines']:
        print(f"Fehler: Pipeline {pipeline_id} nicht gefunden.")
        sys.exit(1)
    
    config['pipelines'][pipeline_id]['enabled'] = enabled
    config['pipelines'][pipeline_id]['integration_points'] = integration_points
    config['pipelines'][pipeline_id]['priority'] = priority
    
    save_config(config)
    
    status = "aktiviert" if enabled else "deaktiviert"
    print(f"Pipeline {pipeline_id} wurde {status} mit Integrationspunkten {integration_points} und Priorität {priority}.")

def show_status() -> None:
    """
    Zeigt den aktuellen Status der Pipeline-Integration an.
    """
    config = load_config()
    
    print("Status der Pipeline-Integration:")
    print(f"  Aktiviert: {config['pipeline_integration']['enabled']}")
    print(f"  Version: {config['pipeline_integration']['version']}")
    print(f"  Beschreibung: {config['pipeline_integration']['description']}")
    print()
    
    print("Konfigurierte Pipelines:")
    for pipeline_id, pipeline_config in config['pipelines'].items():
        status = "aktiviert" if pipeline_config['enabled'] else "deaktiviert"
        print(f"  {pipeline_id}:")
        print(f"    Status: {status}")
        print(f"    Integrationspunkte: {pipeline_config['integration_points']}")
        print(f"    Priorität: {pipeline_config['priority']}")
        print(f"    Beschreibung: {pipeline_config['description']}")
        print()
    
    print("APM-Phasen und zugeordnete Pipelines:")
    for phase, phase_config in config['apm_phases'].items():
        print(f"  {phase} ({phase_config['description']}):")
        print(f"    Pipelines: {phase_config['post_phase_pipelines']}")
        print()

def main() -> None:
    """
    Hauptfunktion des Skripts.
    """
    parser = argparse.ArgumentParser(description='Aktivierung und Konfiguration der Pipeline-Integration für VALEO-NeuroERP')
    
    subparsers = parser.add_subparsers(dest='command', help='Befehle')
    
    # Aktivieren/Deaktivieren
    activate_parser = subparsers.add_parser('activate', help='Aktiviert oder deaktiviert die Pipeline-Integration')
    activate_parser.add_argument('--enable', action='store_true', help='Aktiviert die Pipeline-Integration')
    activate_parser.add_argument('--disable', action='store_true', help='Deaktiviert die Pipeline-Integration')
    
    # Pipeline konfigurieren
    configure_parser = subparsers.add_parser('configure', help='Konfiguriert eine Pipeline')
    configure_parser.add_argument('--pipeline', required=True, help='Die ID der Pipeline')
    configure_parser.add_argument('--enable', action='store_true', help='Aktiviert die Pipeline')
    configure_parser.add_argument('--disable', action='store_true', help='Deaktiviert die Pipeline')
    configure_parser.add_argument('--integration-points', nargs='+', help='Die Integrationspunkte der Pipeline')
    configure_parser.add_argument('--priority', choices=['high', 'medium', 'low'], help='Die Priorität der Pipeline')
    
    # Status anzeigen
    status_parser = subparsers.add_parser('status', help='Zeigt den aktuellen Status der Pipeline-Integration an')
    
    args = parser.parse_args()
    
    if args.command == 'activate':
        if args.enable and args.disable:
            print("Fehler: --enable und --disable können nicht gleichzeitig verwendet werden.")
            sys.exit(1)
        elif args.enable:
            activate_pipeline_integration(True)
        elif args.disable:
            activate_pipeline_integration(False)
        else:
            print("Fehler: Entweder --enable oder --disable muss angegeben werden.")
            sys.exit(1)
    elif args.command == 'configure':
        if args.enable and args.disable:
            print("Fehler: --enable und --disable können nicht gleichzeitig verwendet werden.")
            sys.exit(1)
        
        enabled = args.enable if args.enable else not args.disable
        
        config = load_config()
        pipeline_config = config['pipelines'].get(args.pipeline, {})
        
        integration_points = args.integration_points if args.integration_points else pipeline_config.get('integration_points', [])
        priority = args.priority if args.priority else pipeline_config.get('priority', 'medium')
        
        configure_pipeline(args.pipeline, enabled, integration_points, priority)
    elif args.command == 'status':
        show_status()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
