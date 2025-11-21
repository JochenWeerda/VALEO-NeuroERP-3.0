#!/usr/bin/env python3
"""
Konsolidiert die ChatGPT-Analyse mit dem bestehenden Schema
"""

import json
from pathlib import Path
from typing import Dict, List, Set

# Lade bestehendes Schema
with open('schemas/mask-builder/kundenstamm.json', 'r', encoding='utf-8') as f:
    existing_schema = json.load(f)

# Lade ChatGPT-Analyse
with open('schemas/kundenstamm_chatgpt.json', 'r', encoding='utf-8') as f:
    chatgpt_data = json.load(f)

# Extrahiere Felder aus bestehendem Schema
existing_fields = set()
for field in existing_schema['form']['fields']:
    existing_fields.add(field['l3_original_field'].lower())

# Extrahiere Felder aus ChatGPT-Analyse
chatgpt_fields = set()
for category, fields in chatgpt_data.items():
    for field in fields:
        chatgpt_fields.add(field.lower())

# Vergleich
print("=" * 80)
print("FELD-VERGLEICH: Bestehend vs. ChatGPT")
print("=" * 80)

print(f"\n📊 Bestehende Felder: {len(existing_fields)}")
print(f"📊 ChatGPT Felder: {len(chatgpt_fields)}")

# Felder die neu sind
new_fields = chatgpt_fields - existing_fields
print(f"\n✨ Neue Felder aus ChatGPT: {len(new_fields)}")
if new_fields:
    for field in sorted(new_fields):
        print(f"   + {field}")

# Felder die nur im bestehenden Schema sind
missing_fields = existing_fields - chatgpt_fields
print(f"\n⚠️  Felder nur im bestehenden Schema: {len(missing_fields)}")
if missing_fields:
    for field in sorted(missing_fields):
        print(f"   - {field}")

# Gemeinsame Felder
common_fields = existing_fields & chatgpt_fields
print(f"\n✅ Gemeinsame Felder: {len(common_fields)}")

# Erstelle konsolidierte Tabs-Liste
print("\n" + "=" * 80)
print("TAB-VERGLEICH")
print("=" * 80)

existing_tabs = set(tab['id'] for tab in existing_schema['form']['tabs'])
chatgpt_tabs = set(chatgpt_data.keys())

print(f"\n📋 Bestehende Tabs: {len(existing_tabs)}")
for tab in sorted(existing_tabs):
    print(f"   - {tab}")

print(f"\n📋 ChatGPT Tabs: {len(chatgpt_tabs)}")
for tab in sorted(chatgpt_tabs):
    print(f"   - {tab}")

# Neue Tabs
new_tabs = chatgpt_tabs - existing_tabs
print(f"\n✨ Neue Tabs aus ChatGPT: {len(new_tabs)}")
if new_tabs:
    for tab in sorted(new_tabs):
        print(f"   + {tab}")

# Generiere finalen Bericht
report = {
    "vergleich": {
        "bestehende_felder": len(existing_fields),
        "chatgpt_felder": len(chatgpt_fields),
        "neue_felder": len(new_fields),
        "fehlende_felder": len(missing_fields),
        "gemeinsame_felder": len(common_fields)
    },
    "neue_felder_liste": sorted(list(new_fields)),
    "fehlende_felder_liste": sorted(list(missing_fields)),
    "neue_tabs": sorted(list(new_tabs))
}

# Speichere Bericht
with open('schemas/kundenstamm_vergleich.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 80)
print("✅ Vergleich abgeschlossen!")
print("=" * 80)
print(f"\n📄 Bericht gespeichert: schemas/kundenstamm_vergleich.json")
print(f"\n🎯 Nächste Schritte:")
print(f"   1. Review des Vergleichs-Berichts")
print(f"   2. Konsolidierung des Schemas")
print(f"   3. Erstellung der SQL-Tabellen")

