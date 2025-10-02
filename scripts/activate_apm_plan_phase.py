#!/usr/bin/env python3

import os
import sys
import json
from datetime import datetime

def activate_plan_phase():
    """Aktiviert die PLAN-Phase des APM-Frameworks"""
    
    # Aktuellen Status speichern
    status = {
        "previous_phase": "VAN",
        "current_phase": "PLAN",
        "activation_time": datetime.now().isoformat(),
        "status": "active"
    }
    
    # Status-Datei erstellen/aktualisieren
    os.makedirs('data/apm_status', exist_ok=True)
    with open('data/apm_status/phase_status.json', 'w') as f:
        json.dump(status, f, indent=2)
    
    # Memory Bank Status aktualisieren
    memory_bank_status = {
        "phase": "PLAN",
        "context": "planning",
        "focus": "detailed_planning",
        "last_update": datetime.now().isoformat()
    }
    
    os.makedirs('memory-bank/status', exist_ok=True)
    with open('memory-bank/status/current_phase.json', 'w') as f:
        json.dump(memory_bank_status, f, indent=2)
    
    print("APM-Framework erfolgreich auf PLAN-Phase umgestellt")
    print("Alle notwendigen Status-Updates wurden durchgeführt")
    print("System ist bereit für die Planungsphase")

if __name__ == "__main__":
    activate_plan_phase() 