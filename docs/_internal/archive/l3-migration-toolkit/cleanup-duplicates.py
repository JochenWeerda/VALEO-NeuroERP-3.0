#!/usr/bin/env python3
"""
Räumt Dubletten auf und behält nur die beste Versionen
"""

from pathlib import Path
import shutil

print("=" * 80)
print("CLEANUP: Dubletten löschen")
print("=" * 80)

# Dateien die BEHALTEN werden sollen
keep_files = [
    "mask-builder-framework/kundenstamm-complete-framework.json",  # Neueste Version
    "mask-builder-framework/generated/subtables/",  # Alle Untertabellen
    "schemas/sql/kundenstamm_complete.sql",  # SQL-Tabellen
    "schemas/mappings/l3-to-valeo-kundenstamm-extended.json",  # Mappings
    "schemas/mappings/subtable-mappings.json",  # Untertabellen-Mappings
    "schemas/kundenstamm_chatgpt.json",  # ChatGPT-Analyse
    "schemas/mask-builder/comparison-report.json",  # Vergleichs-Report
]

# Dateien die GELÖSCHT werden
delete_files = [
    "kundenstamm-final-complete-modern.json",  # Ältere Version
    "schemas/mask-builder/kundenstamm.json",  # Ältere Version
    "schemas/mask-builder/kundenstamm_complete.json",  # Nicht Framework-basiert
    "screenshots/l3-masks/kundenstamm.ocr.json",  # Alt
]

print("\n🗑️  Lösche Dubletten:")
for file_path in delete_files:
    full_path = Path(file_path)
    if full_path.exists():
        if full_path.is_dir():
            shutil.rmtree(full_path)
            print(f"   ❌ Gelöscht (Dir): {file_path}")
        else:
            full_path.unlink()
            print(f"   ❌ Gelöscht (File): {file_path}")
    else:
        print(f"   ⚠️  Nicht gefunden: {file_path}")

print("\n✅ Behalte:")
for file_path in keep_files:
    full_path = Path(file_path)
    if full_path.exists():
        print(f"   ✅ {file_path}")
    else:
        print(f"   ⚠️  Nicht gefunden: {file_path}")

print("\n" + "=" * 80)
print("✅ CLEANUP ABGESCHLOSSEN")
print("=" * 80)


