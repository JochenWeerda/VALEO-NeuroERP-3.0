#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Einfacher GENXAIS v1.9 LangGraph Zyklus
--------------------------------------
Dieses Skript führt einen vereinfachten LangGraph-Zyklus für GENXAIS v1.9 aus.
"""

import os
import sys
import json
import datetime
from pathlib import Path
import openai

# Pfade konfigurieren
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
PROMPTS_DIR = BASE_DIR / "prompts"

# API-Schlüssel laden
API_KEYS_PATH = BASE_DIR / "config" / "api_keys.local.json"

def load_api_keys():
    """
    Lädt die API-Schlüssel aus der Konfigurationsdatei.
    
    Returns:
        Dict mit den API-Schlüsseln
    """
    if not API_KEYS_PATH.exists():
        print(f"[FEHLER] API-Schlüssel-Datei nicht gefunden: {API_KEYS_PATH}")
        return {}
    
    try:
        with open(API_KEYS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[FEHLER] Fehler beim Laden der API-Schlüssel: {str(e)}")
        return {}

# API-Schlüssel laden und in Umgebungsvariablen setzen
api_keys = load_api_keys()
if "openai" in api_keys:
    os.environ["OPENAI_API_KEY"] = api_keys["openai"]
    openai.api_key = api_keys["openai"]

def load_prompt():
    """
    Lädt den Prompt aus der Datei.
    
    Returns:
        String mit dem Prompt
    """
    prompt_path = PROMPTS_DIR / "genxais_prompt_v1.9.md"
    if prompt_path.exists():
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"[FEHLER] Fehler beim Laden des Prompts: {str(e)}")
            return ""
    else:
        print(f"[FEHLER] Prompt-Datei nicht gefunden: {prompt_path}")
        return ""

def save_result(phase, result):
    """
    Speichert das Ergebnis einer Phase.
    
    Args:
        phase: Die Phase
        result: Das Ergebnis
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    result_path = OUTPUT_DIR / f"{phase.lower()}_result.md"
    try:
        with open(result_path, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"[INFO] {phase}-Phase abgeschlossen. Ergebnis gespeichert unter {result_path}")
    except Exception as e:
        print(f"[FEHLER] Fehler beim Speichern des Ergebnisses: {str(e)}")

def run_van_phase():
    """
    Führt die VAN-Phase aus.
    
    Returns:
        String mit dem Ergebnis
    """
    print("[INFO] Führe VAN-Phase aus...")
    
    prompt = load_prompt()
    if not prompt:
        return "Fehler: Kein Prompt geladen."
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Du bist ein leistungsstarker KI-Agent im GENXAIS-Framework, der die VAN-Phase (Vision, Analyse, Navigation) durchführt. Deine Aufgabe ist es, den aktuellen Zustand des Projekts zu analysieren, Verbesserungspotentiale zu identifizieren und einen Plan für die nächsten Schritte zu erstellen."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"[FEHLER] Fehler in der VAN-Phase: {str(e)}")
        return f"Fehler in der VAN-Phase: {str(e)}"

def run_plan_phase(van_result):
    """
    Führt die PLAN-Phase aus.
    
    Args:
        van_result: Das Ergebnis der VAN-Phase
        
    Returns:
        String mit dem Ergebnis
    """
    print("[INFO] Führe PLAN-Phase aus...")
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Du bist ein leistungsstarker KI-Agent im GENXAIS-Framework, der die PLAN-Phase durchführt. Deine Aufgabe ist es, basierend auf der Analyse aus der VAN-Phase einen detaillierten Plan für die Implementierung zu erstellen. Berücksichtige dabei die identifizierten Verbesserungspotentiale und priorisiere die Aufgaben."},
                {"role": "user", "content": f"Hier ist die Analyse aus der VAN-Phase:\n\n{van_result}\n\nErstelle einen detaillierten Plan für die Implementierung der identifizierten Verbesserungspotentiale."}
            ],
            temperature=0.2
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"[FEHLER] Fehler in der PLAN-Phase: {str(e)}")
        return f"Fehler in der PLAN-Phase: {str(e)}"

def run_create_phase(plan_result):
    """
    Führt die CREATE-Phase aus.
    
    Args:
        plan_result: Das Ergebnis der PLAN-Phase
        
    Returns:
        String mit dem Ergebnis
    """
    print("[INFO] Führe CREATE-Phase aus...")
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Du bist ein leistungsstarker KI-Agent im GENXAIS-Framework, der die CREATE-Phase durchführt. Deine Aufgabe ist es, basierend auf dem Plan aus der PLAN-Phase konkrete Implementierungen zu entwickeln. Erstelle Prototypen, entwickle neue Funktionen und implementiere neue Technologien."},
                {"role": "user", "content": f"Hier ist der Plan aus der PLAN-Phase:\n\n{plan_result}\n\nEntwickle konkrete Implementierungen für die geplanten Funktionen."}
            ],
            temperature=0.2
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"[FEHLER] Fehler in der CREATE-Phase: {str(e)}")
        return f"Fehler in der CREATE-Phase: {str(e)}"

def run_implementation_phase(create_result):
    """
    Führt die IMPLEMENTATION-Phase aus.
    
    Args:
        create_result: Das Ergebnis der CREATE-Phase
        
    Returns:
        String mit dem Ergebnis
    """
    print("[INFO] Führe IMPLEMENTATION-Phase aus...")
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Du bist ein leistungsstarker KI-Agent im GENXAIS-Framework, der die IMPLEMENTATION-Phase durchführt. Deine Aufgabe ist es, die entwickelten Funktionen vollständig zu implementieren, in das bestehende System zu integrieren und Tests durchzuführen."},
                {"role": "user", "content": f"Hier sind die entwickelten Funktionen aus der CREATE-Phase:\n\n{create_result}\n\nImplementiere diese Funktionen vollständig und integriere sie in das bestehende System."}
            ],
            temperature=0.2
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"[FEHLER] Fehler in der IMPLEMENTATION-Phase: {str(e)}")
        return f"Fehler in der IMPLEMENTATION-Phase: {str(e)}"

def run_reflektion_phase(implementation_result):
    """
    Führt die REFLEKTION-Phase aus.
    
    Args:
        implementation_result: Das Ergebnis der IMPLEMENTATION-Phase
        
    Returns:
        String mit dem Ergebnis
    """
    print("[INFO] Führe REFLEKTION-Phase aus...")
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Du bist ein leistungsstarker KI-Agent im GENXAIS-Framework, der die REFLEKTION-Phase durchführt. Deine Aufgabe ist es, den Projekterfolg zu bewerten, Verbesserungspotentiale zu identifizieren und den nächsten Zyklus zu planen."},
                {"role": "user", "content": f"Hier ist die Implementierung aus der IMPLEMENTATION-Phase:\n\n{implementation_result}\n\nBewerte den Projekterfolg, identifiziere Verbesserungspotentiale und plane den nächsten Zyklus."}
            ],
            temperature=0.2
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"[FEHLER] Fehler in der REFLEKTION-Phase: {str(e)}")
        return f"Fehler in der REFLEKTION-Phase: {str(e)}"

def create_handover(phases_results):
    """
    Erstellt ein Handover-Dokument.
    
    Args:
        phases_results: Die Ergebnisse der Phasen
    """
    handover_path = OUTPUT_DIR / "handover.md"
    
    try:
        with open(handover_path, "w", encoding="utf-8") as f:
            f.write(f"""# GENXAIS Zyklus Handover

## Zusammenfassung

GENXAIS Zyklus v1.9 wurde am {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} abgeschlossen.

## Durchgeführte Phasen
- VAN
- PLAN
- CREATE
- IMPLEMENTATION
- REFLEKTION

## Reflektionsergebnisse

{phases_results.get("REFLEKTION", "Keine Reflektionsergebnisse verfügbar.")}

## Nächste Schritte
1. Überprüfung der erstellten Artefakte
2. Integration der Änderungen in das Hauptprojekt
3. Planung des nächsten GENXAIS-Zyklus (v2.0)
""")
        
        print(f"[INFO] Handover-Dokument erstellt: {handover_path}")
    except Exception as e:
        print(f"[FEHLER] Fehler beim Erstellen des Handover-Dokuments: {str(e)}")

def main():
    """
    Hauptfunktion zum Starten des LangGraph-Zyklus.
    """
    print("=" * 80)
    print("GENXAIS v1.9 LangGraph Zyklus (Vereinfacht)")
    print("=" * 80)
    print(f"Startzeit: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Projektverzeichnis: {BASE_DIR}")
    print("-" * 80)
    
    # Prüfe, ob der API-Schlüssel vorhanden ist
    if not os.environ.get("OPENAI_API_KEY"):
        print("[FEHLER] Kein OpenAI-API-Schlüssel gefunden.")
        print("Bitte stelle sicher, dass die Datei config/api_keys.local.json existiert und einen gültigen API-Schlüssel enthält.")
        return 1
    
    # Führe die Phasen aus
    phases_results = {}
    
    # VAN-Phase
    van_result = run_van_phase()
    save_result("VAN", van_result)
    phases_results["VAN"] = van_result
    
    # PLAN-Phase
    plan_result = run_plan_phase(van_result)
    save_result("PLAN", plan_result)
    phases_results["PLAN"] = plan_result
    
    # CREATE-Phase
    create_result = run_create_phase(plan_result)
    save_result("CREATE", create_result)
    phases_results["CREATE"] = create_result
    
    # IMPLEMENTATION-Phase
    implementation_result = run_implementation_phase(create_result)
    save_result("IMPLEMENTATION", implementation_result)
    phases_results["IMPLEMENTATION"] = implementation_result
    
    # REFLEKTION-Phase
    reflektion_result = run_reflektion_phase(implementation_result)
    save_result("REFLEKTION", reflektion_result)
    phases_results["REFLEKTION"] = reflektion_result
    
    # Erstelle Handover-Dokument
    create_handover(phases_results)
    
    print("-" * 80)
    print(f"Endzeit: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 