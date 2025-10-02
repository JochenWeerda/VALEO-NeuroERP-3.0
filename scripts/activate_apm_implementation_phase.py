"""
Script zur Aktivierung des IMPLEMENTATION Mode
"""
import os
import json
import shutil
from datetime import datetime

def create_implementation_structure():
    """Implementation Verzeichnisstruktur erstellen"""
    dirs = [
        "memory-bank/implementation",
        "memory-bank/implementation/tests",
        "memory-bank/implementation/ci_cd",
        "memory-bank/implementation/monitoring",
        "memory-bank/implementation/docs"
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        
def save_phase_status():
    """Phase Status speichern"""
    status = {
        "phase": "IMPLEMENTATION",
        "activated_at": datetime.now().isoformat(),
        "previous_phase": "CREATE",
        "status": "active"
    }
    
    with open("memory-bank/status/phase_status.json", "w") as f:
        json.dump(status, f, indent=2)
        
def copy_rules():
    """APM Rules kopieren"""
    rules_dir = ".cursor/rules/implementation"
    os.makedirs(rules_dir, exist_ok=True)
    
    # Basis Rules kopieren
    shutil.copy(
        "rules/implementation/base_rules.json",
        f"{rules_dir}/base_rules.json"
    )
    
    # Test Rules kopieren
    shutil.copy(
        "rules/implementation/test_rules.json",
        f"{rules_dir}/test_rules.json"
    )
    
    # CI/CD Rules kopieren
    shutil.copy(
        "rules/implementation/ci_cd_rules.json",
        f"{rules_dir}/ci_cd_rules.json"
    )
    
def main():
    """Hauptfunktion"""
    try:
        print("Aktiviere IMPLEMENTATION Mode...")
        
        # Verzeichnisse erstellen
        create_implementation_structure()
        print("✓ Verzeichnisstruktur erstellt")
        
        # Status speichern
        save_phase_status()
        print("✓ Phase Status gespeichert")
        
        # Rules kopieren
        copy_rules()
        print("✓ APM Rules kopiert")
        
        print("\nIMPLEMENTATION Mode erfolgreich aktiviert!")
        print("\nNächste Schritte:")
        print("1. Unit Tests implementieren")
        print("2. CI/CD Pipeline aufsetzen")
        print("3. Monitoring einrichten")
        print("4. Dokumentation vervollständigen")
        
    except Exception as e:
        print(f"\nFehler bei der Aktivierung: {str(e)}")
        return 1
        
    return 0
    
if __name__ == "__main__":
    exit(main()) 