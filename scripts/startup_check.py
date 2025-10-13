#!/usr/bin/env python3
"""
VALEO-NeuroERP Startup-Check & Installation-Routine
Prüft ob System in Installation oder Produktiv-Phase ist
"""

import sys
import os
import socket
import subprocess
from pathlib import Path
from datetime import datetime
import json

# Füge Projekt-Root zu sys.path hinzu
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class StartupChecker:
    """Prüft System-Status und führt ggf. Installation durch"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.fixes = []
        self.installation_marker = project_root / ".installation_complete"
        self.port_conflicts = []
        
    def check_port_availability(self, port: int, service_name: str) -> bool:
        """Prüft ob Port verfügbar ist"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            # Port ist belegt
            self.port_conflicts.append({
                "port": port,
                "service": service_name,
                "status": "BELEGT"
            })
            return False
        return True
    
    def check_all_ports(self):
        """Prüfe alle kritischen Ports"""
        print("\n🔍 Port-Check...")
        print("=" * 80)
        
        ports_to_check = {
            8000: "Backend (FastAPI/Uvicorn)",
            3000: "Frontend (Vite - Primary)",
            3001: "Frontend (Vite - Fallback)",
            5432: "PostgreSQL",
            6379: "Redis",
            4222: "NATS",
            8080: "Keycloak",
            9090: "Prometheus",
            3100: "Loki",
        }
        
        all_free = True
        for port, service in ports_to_check.items():
            is_free = self.check_port_availability(port, service)
            status = "🟢 FREI" if is_free else "🔴 BELEGT"
            print(f"   Port {port:5d} ({service:30s}): {status}")
            if not is_free:
                all_free = False
        
        return all_free
    
    def check_installation_status(self) -> str:
        """Prüft ob System installiert ist"""
        if self.installation_marker.exists():
            with open(self.installation_marker, 'r') as f:
                data = json.load(f)
                install_date = data.get('installed_at', 'Unknown')
                version = data.get('version', 'Unknown')
                print(f"\n✅ System ist INSTALLIERT")
                print(f"   Installationsdatum: {install_date}")
                print(f"   Version: {version}")
                return "PRODUCTION"
        else:
            print(f"\n⚠️  System ist NICHT installiert (Erste Installation)")
            return "INSTALLATION"
    
    def check_database_schemas(self) -> bool:
        """Prüft ob PostgreSQL-Schemas existieren"""
        print("\n🗄️  Datenbank-Schema-Check...")
        print("=" * 80)
        
        try:
            # Prüfe Docker-Container
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=valeo-postgres", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if "valeo-postgres" not in result.stdout:
                self.errors.append("PostgreSQL-Container 'valeo-postgres' läuft nicht")
                print("   ❌ PostgreSQL-Container nicht gefunden")
                return False
            
            print("   ✅ PostgreSQL-Container läuft")
            
            # Prüfe Schemas
            check_schemas = subprocess.run(
                ["docker", "exec", "valeo-postgres", "psql", "-U", "valeo", "-d", "valeo_neuro_erp", "-c", "\\dn"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            required_schemas = ["domain_shared", "domain_crm", "domain_inventory", "domain_erp"]
            schemas_found = []
            
            for schema in required_schemas:
                if schema in check_schemas.stdout:
                    schemas_found.append(schema)
                    print(f"   ✅ Schema '{schema}' existiert")
                else:
                    print(f"   ❌ Schema '{schema}' fehlt")
                    self.errors.append(f"Schema '{schema}' fehlt in PostgreSQL")
            
            return len(schemas_found) == len(required_schemas)
            
        except subprocess.TimeoutExpired:
            self.errors.append("Docker-Command Timeout")
            print("   ❌ Docker-Command Timeout")
            return False
        except FileNotFoundError:
            self.errors.append("Docker nicht installiert oder nicht im PATH")
            print("   ❌ Docker nicht gefunden")
            return False
        except Exception as e:
            self.errors.append(f"DB-Check-Fehler: {e}")
            print(f"   ❌ Fehler: {e}")
            return False
    
    def check_database_tables(self) -> dict:
        """Zählt Tabellen pro Schema"""
        print("\n📋 Tabellen-Check...")
        print("=" * 80)
        
        table_count = {}
        schemas = ["domain_shared", "domain_crm", "domain_inventory", "domain_erp"]
        
        for schema in schemas:
            try:
                result = subprocess.run(
                    ["docker", "exec", "valeo-postgres", "psql", "-U", "valeo", "-d", "valeo_neuro_erp",
                     "-c", f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='{schema}'"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                # Parse Ausgabe (Zeile 3 enthält die Zahl)
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 3:
                    count = int(lines[2].strip())
                    table_count[schema] = count
                    status = "✅" if count > 0 else "⚠️ "
                    print(f"   {status} {schema}: {count} Tabellen")
                    
            except Exception as e:
                table_count[schema] = 0
                print(f"   ❌ {schema}: Fehler bei Check ({e})")
        
        return table_count
    
    def create_schemas_if_missing(self):
        """Erstellt fehlende Schemas"""
        print("\n🔧 Erstelle fehlende Schemas...")
        print("=" * 80)
        
        try:
            result = subprocess.run(
                ["docker", "exec", "valeo-postgres", "psql", "-U", "valeo", "-d", "valeo_neuro_erp", "-c",
                 "CREATE SCHEMA IF NOT EXISTS domain_shared; "
                 "CREATE SCHEMA IF NOT EXISTS domain_crm; "
                 "CREATE SCHEMA IF NOT EXISTS domain_inventory; "
                 "CREATE SCHEMA IF NOT EXISTS domain_erp;"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if "CREATE SCHEMA" in result.stdout:
                print("   ✅ Schemas erstellt")
                self.fixes.append("PostgreSQL-Schemas erstellt")
                return True
            else:
                print("   ℹ️  Schemas existierten bereits")
                return True
                
        except Exception as e:
            print(f"   ❌ Fehler beim Schema-Erstellen: {e}")
            self.errors.append(f"Schema-Creation-Fehler: {e}")
            return False
    
    def mark_installation_complete(self):
        """Markiert Installation als abgeschlossen"""
        data = {
            "installed_at": datetime.now().isoformat(),
            "version": "3.0.0",
            "schemas_created": ["domain_shared", "domain_crm", "domain_inventory", "domain_erp"],
            "errors_encountered": self.errors,
            "fixes_applied": self.fixes
        }
        
        with open(self.installation_marker, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n✅ Installation als abgeschlossen markiert: {self.installation_marker}")
    
    def cleanup_stale_processes(self):
        """Räumt vergessene Prozesse auf"""
        print("\n🧹 Process-Cleanup...")
        print("=" * 80)
        
        # Prüfe Python-Prozesse auf kritischen Ports
        try:
            if sys.platform == "win32":
                # Windows: Finde Prozesse auf Port 8000
                result = subprocess.run(
                    ["netstat", "-ano"],
                    capture_output=True,
                    text=True
                )
                
                if ":8000" in result.stdout and "LISTENING" in result.stdout:
                    self.warnings.append("Port 8000 bereits belegt - möglicherweise alter Backend-Prozess")
                    print("   ⚠️  Port 8000 belegt (vermutlich alter Backend-Prozess)")
                    print("   💡 Empfehlung: Stoppe alle Python-Prozesse mit:")
                    print("      Get-Process python | Stop-Process -Force")
                else:
                    print("   ✅ Port 8000 frei")
            
        except Exception as e:
            print(f"   ⚠️  Cleanup-Check fehlgeschlagen: {e}")
    
    def run_full_check(self) -> bool:
        """Führt vollständigen Startup-Check durch"""
        print("=" * 80)
        print("🚀 VALEO-NeuroERP Startup-Check")
        print("=" * 80)
        print(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Projekt-Root: {project_root}")
        
        # 1. Status prüfen
        status = self.check_installation_status()
        
        # 2. Process-Cleanup
        self.cleanup_stale_processes()
        
        # 3. Port-Check
        ports_ok = self.check_all_ports()
        
        if not ports_ok:
            print("\n⚠️  WARNUNG: Einige Ports sind belegt!")
            print("   Mögliche Ursachen:")
            for conflict in self.port_conflicts:
                print(f"   - Port {conflict['port']}: {conflict['service']}")
            print("\n   💡 Lösungsvorschläge:")
            print("   1. Stoppe alte Prozesse: Get-Process python,node | Stop-Process -Force")
            print("   2. Stoppe Docker-Container: docker-compose down")
            print("   3. Prüfe Ports: netstat -ano | findstr \":8000\"")
        
        # 4. Datenbank-Check (nur wenn Installation)
        if status == "INSTALLATION":
            print("\n🔧 INSTALLATIONS-MODUS - Führe Setup durch...")
            
            # 4a. Schema-Check
            schemas_ok = self.check_database_schemas()
            
            if not schemas_ok:
                print("\n   Erstelle fehlende Schemas...")
                if not self.create_schemas_if_missing():
                    print("\n   ❌ Schema-Erstellung fehlgeschlagen")
                    return False
            
            # 4b. Tabellen-Check
            tables = self.check_database_tables()
            total_tables = sum(tables.values())
            
            if total_tables == 0:
                print("\n   ⚠️  Keine Tabellen gefunden - Backend muss sie beim Start erstellen")
                print("   💡 Das passiert automatisch bei `create_tables()` in main.py")
            
            # Markiere Installation als abgeschlossen
            self.mark_installation_complete()
            
        else:
            print("\n✅ PRODUKTIV-MODUS - Überspringe Installation")
            
            # Trotzdem Schema-Check durchführen
            self.check_database_schemas()
            tables = self.check_database_tables()
            total_tables = sum(tables.values())
            print(f"\n   📊 Gesamt: {total_tables} Tabellen in Datenbank")
        
        # 5. Zusammenfassung
        print("\n" + "=" * 80)
        print("📊 Zusammenfassung:")
        print("=" * 80)
        print(f"Status: {status}")
        print(f"Fehler: {len(self.errors)}")
        print(f"Warnungen: {len(self.warnings)}")
        print(f"Angewendete Fixes: {len(self.fixes)}")
        
        if self.errors:
            print("\n❌ Gefundene Fehler:")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
        
        if self.warnings:
            print("\n⚠️  Warnungen:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        if self.fixes:
            print("\n✅ Angewendete Fixes:")
            for i, fix in enumerate(self.fixes, 1):
                print(f"   {i}. {fix}")
        
        print("\n" + "=" * 80)
        
        if self.errors:
            print("❌ STARTUP-CHECK FEHLGESCHLAGEN")
            print("   System ist nicht bereit zum Starten")
            return False
        else:
            print("✅ STARTUP-CHECK ERFOLGREICH")
            print("   System kann gestartet werden")
            return True

def main():
    checker = StartupChecker()
    success = checker.run_full_check()
    
    # Speichere Check-Ergebnis
    log_file = project_root / "logs" / f"startup_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_file.parent.mkdir(exist_ok=True)
    
    check_result = {
        "timestamp": datetime.now().isoformat(),
        "success": success,
        "errors": checker.errors,
        "warnings": checker.warnings,
        "fixes": checker.fixes,
        "port_conflicts": checker.port_conflicts
    }
    
    with open(log_file, 'w') as f:
        json.dump(check_result, f, indent=2)
    
    print(f"\n📝 Check-Log gespeichert: {log_file}")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

