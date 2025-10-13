***REMOVED***!/usr/bin/env python3
"""
VALEO-NeuroERP Service Manager
Zentrale Verwaltung aller Services mit Port-Management und Auto-Cleanup
"""

import sys
import os
import subprocess
import socket
import time
import yaml
import psutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class ServiceManager:
    """Verwaltet alle VALEO-NeuroERP Services"""
    
    def __init__(self):
        self.config_file = project_root / "config" / "services.yml"
        self.services = self.load_config()
        self.running_services = {}
        
    def load_config(self) -> dict:
        """Lädt Service-Konfiguration"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def check_port(self, port: int) -> Optional[int]:
        """Prüft ob Port belegt ist und gibt PID zurück"""
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port == port and conn.status == 'LISTEN':
                return conn.pid
        return None
    
    def kill_process_on_port(self, port: int, service_name: str) -> bool:
        """Stoppt Prozess auf einem Port"""
        pid = self.check_port(port)
        if pid:
            try:
                process = psutil.Process(pid)
                print(f"   🔴 Port {port} belegt von PID {pid} ({process.name()})")
                print(f"      Stoppe Prozess für {service_name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                    print(f"   ✅ Prozess gestoppt")
                    return True
                except psutil.TimeoutExpired:
                    print(f"   ⚠️  Prozess reagiert nicht - Force Kill...")
                    process.kill()
                    print(f"   ✅ Prozess force-killed")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                print(f"   ❌ Fehler beim Stoppen: {e}")
                return False
        else:
            print(f"   🟢 Port {port} ist frei")
            return True
    
    def check_docker_container(self, container_name: str) -> str:
        """Prüft Docker-Container-Status"""
        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            status = result.stdout.strip()
            if not status:
                return "NOT_FOUND"
            elif "Up" in status:
                if "healthy" in status:
                    return "HEALTHY"
                elif "unhealthy" in status:
                    return "UNHEALTHY"
                else:
                    return "RUNNING"
            else:
                return "STOPPED"
        except Exception:
            return "ERROR"
    
    def start_docker_container(self, container_name: str) -> bool:
        """Startet Docker-Container"""
        try:
            subprocess.run(
                ["docker", "start", container_name],
                capture_output=True,
                timeout=10,
                check=True
            )
            return True
        except Exception as e:
            print(f"   ❌ Fehler beim Starten: {e}")
            return False
    
    def stop_docker_container(self, container_name: str) -> bool:
        """Stoppt Docker-Container"""
        try:
            subprocess.run(
                ["docker", "stop", container_name],
                capture_output=True,
                timeout=30,
                check=True
            )
            return True
        except Exception as e:
            print(f"   ❌ Fehler beim Stoppen: {e}")
            return False
    
    def cleanup_all_ports(self):
        """Räumt alle konfigurierten Ports auf"""
        print("\n🧹 PORT-CLEANUP")
        print("=" * 80)
        
        for service_key, service_config in self.services['services'].items():
            port = service_config.get('port')
            if port:
                service_name = service_config['name']
                print(f"\n{service_name} (Port {port}):")
                self.kill_process_on_port(port, service_name)
    
    def status_report(self):
        """Zeigt Status aller Services"""
        print("\n📊 SERVICE-STATUS-REPORT")
        print("=" * 80)
        
        for service_key, service_config in self.services['services'].items():
            port = service_config.get('port')
            service_name = service_config['name']
            service_type = service_config['type']
            required = "✅ REQUIRED" if service_config.get('required', False) else "⚪ OPTIONAL"
            
            print(f"\n{service_name}")
            print(f"   Typ: {service_type}")
            print(f"   Port: {port}")
            print(f"   Status: {required}")
            
            if service_type == "docker":
                container = service_config['container']
                status = self.check_docker_container(container)
                status_icon = {
                    "HEALTHY": "🟢",
                    "RUNNING": "🟡",
                    "UNHEALTHY": "🔴",
                    "STOPPED": "⚪",
                    "NOT_FOUND": "❌",
                    "ERROR": "❌"
                }.get(status, "❓")
                print(f"   Container: {status_icon} {status}")
            else:
                pid = self.check_port(port)
                if pid:
                    try:
                        proc = psutil.Process(pid)
                        print(f"   Prozess: 🟢 RUNNING (PID {pid}, {proc.name()})")
                    except:
                        print(f"   Prozess: 🔴 PID {pid} (Zugriff verweigert)")
                else:
                    print(f"   Prozess: ⚪ NICHT LAUFEND")
    
    def start_minimal_stack(self):
        """Startet minimalen Service-Stack für Testing"""
        print("\n🚀 STARTE MINIMAL-STACK FÜR TESTING")
        print("=" * 80)
        
        testing_config = self.services['testing_services']
        required_services = testing_config['required']
        
        print(f"\nBenötigte Services: {', '.join(required_services)}")
        print("\nStartup-Reihenfolge:")
        
        for phase, services in self.services['startup_order'].items():
            ***REMOVED*** Nur required services starten
            phase_services = [s for s in services if s in required_services]
            if phase_services:
                print(f"\n🔹 Phase {phase}: {', '.join(phase_services)}")
                
                for service_key in phase_services:
                    if service_key not in self.services['services']:
                        continue
                        
                    service_config = self.services['services'][service_key]
                    port = service_config.get('port')
                    service_name = service_config['name']
                    service_type = service_config['type']
                    
                    print(f"\n   {service_name} (Port {port}):")
                    
                    ***REMOVED*** Port cleanup
                    if not self.kill_process_on_port(port, service_name):
                        print(f"   ⚠️  Warnung: Port-Cleanup fehlgeschlagen")
                    
                    ***REMOVED*** Docker-Service
                    if service_type == "docker":
                        container = service_config['container']
                        status = self.check_docker_container(container)
                        
                        if status == "HEALTHY" or status == "RUNNING":
                            print(f"   ℹ️  Container läuft bereits")
                        elif status == "STOPPED":
                            print(f"   🔄 Starte Container...")
                            self.start_docker_container(container)
                            time.sleep(2)
                        elif status == "NOT_FOUND":
                            print(f"   ❌ Container existiert nicht - muss mit docker-compose erstellt werden")
                            print(f"      docker-compose -f docker-compose.production.yml up -d {service_key}")
                    
                    ***REMOVED*** Node/Python-Service (wird separat gestartet)
                    elif service_type in ["node", "python"]:
                        print(f"   ℹ️  Manueller Start erforderlich:")
                        print(f"      {service_config['command']}")
                
                ***REMOVED*** Warte zwischen Phasen
                if int(phase) < len(self.services['startup_order']):
                    wait_time = 5
                    print(f"\n   ⏳ Warte {wait_time}s vor nächster Phase...")
                    time.sleep(wait_time)
    
    def health_check_all(self):
        """Führt Health-Checks für alle Services durch"""
        print("\n🏥 HEALTH-CHECKS")
        print("=" * 80)
        
        results = {}
        for service_key, service_config in self.services['services'].items():
            service_name = service_config['name']
            health_cmd = service_config.get('health_check')
            
            if not health_cmd:
                continue
            
            print(f"\n{service_name}:")
            
            if service_config['type'] == "docker":
                container = service_config['container']
                status = self.check_docker_container(container)
                results[service_key] = status in ["HEALTHY", "RUNNING"]
                print(f"   {status}")
            else:
                ***REMOVED*** HTTP Health-Check
                try:
                    import requests
                    response = requests.get(health_cmd, timeout=5)
                    if response.status_code == 200:
                        print(f"   ✅ HEALTHY (HTTP 200)")
                        results[service_key] = True
                    else:
                        print(f"   ⚠️  HTTP {response.status_code}")
                        results[service_key] = False
                except Exception as e:
                    print(f"   ❌ UNREACHABLE: {e}")
                    results[service_key] = False
        
        return results

def main():
    manager = ServiceManager()
    
    if len(sys.argv) < 2:
        print("Usage: python scripts/service_manager.py [command]")
        print("\nCommands:")
        print("  status    - Zeigt Status aller Services")
        print("  cleanup   - Räumt alle Ports auf (stoppt alte Prozesse)")
        print("  start     - Startet Minimal-Stack für Testing")
        print("  health    - Führt Health-Checks durch")
        print("  stop-all  - Stoppt alle Services")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "status":
        manager.status_report()
    
    elif command == "cleanup":
        manager.cleanup_all_ports()
        print("\n✅ Cleanup abgeschlossen")
    
    elif command == "start":
        manager.cleanup_all_ports()
        manager.start_minimal_stack()
        print("\n\n✅ Minimal-Stack-Setup abgeschlossen")
        print("\nNächste Schritte:")
        print("  1. Starte Backend: python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        print("  2. Starte Frontend: cd packages/frontend-web && pnpm vite")
        print("  3. Öffne Browser: http://localhost:3000")
    
    elif command == "health":
        results = manager.health_check_all()
        healthy = sum(1 for v in results.values() if v)
        total = len(results)
        print(f"\n📊 Ergebnis: {healthy}/{total} Services gesund")
    
    elif command == "stop-all":
        print("\n🛑 STOPPE ALLE SERVICES")
        print("=" * 80)
        manager.cleanup_all_ports()
        
        ***REMOVED*** Stoppe auch alle Docker-Container
        for service_key, service_config in manager.services['services'].items():
            if service_config['type'] == "docker":
                container = service_config['container']
                status = manager.check_docker_container(container)
                if status in ["HEALTHY", "RUNNING", "UNHEALTHY"]:
                    print(f"\n   Stoppe {service_config['name']}...")
                    manager.stop_docker_container(container)
        
        print("\n✅ Alle Services gestoppt")
    
    else:
        print(f"❌ Unbekannter Command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Abgebrochen durch Benutzer")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

