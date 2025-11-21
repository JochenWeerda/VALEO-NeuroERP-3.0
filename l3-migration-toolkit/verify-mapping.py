***REMOVED***!/usr/bin/env python3
"""
Prüft und vervollständigt das L3 → VALEO Mapping
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set

***REMOVED*** Lade Daten
with open('schemas/mappings/l3-to-valeo-kundenstamm.json', 'r', encoding='utf-8') as f:
    existing_mapping = json.load(f)

with open('schemas/kundenstamm_chatgpt.json', 'r', encoding='utf-8') as f:
    chatgpt_data = json.load(f)

***REMOVED*** Extrahiere alle ChatGPT-Felder
all_chatgpt_fields = set()
for category, fields in chatgpt_data.items():
    for field in fields:
        all_chatgpt_fields.add(field.lower())

***REMOVED*** Extrahiere gemappte Felder
mapped_fields = set()
for field_mapping in existing_mapping['masks'][0]['fields']:
    mapped_fields.add(field_mapping['l3_field'].lower())

***REMOVED*** Berechne fehlende Felder
missing_fields = all_chatgpt_fields - mapped_fields

print("=" * 80)
print("MAPPING-ANALYSE")
print("=" * 80)
print(f"\n📊 ChatGPT-Felder gesamt: {len(all_chatgpt_fields)}")
print(f"📊 Bereits gemappt: {len(mapped_fields)}")
print(f"⚠️  Fehlende Mappings: {len(missing_fields)}")

if missing_fields:
    print("\n🔍 Fehlende Felder:")
    for field in sorted(missing_fields):
        print(f"   - {field}")

***REMOVED*** Funktion: Erstelle Valeo-Feldname aus L3-Feldname
def create_valeo_fieldname(l3_field: str) -> str:
    """Konvertiert L3-Feldname zu Valeo-Feldname (snake_case)"""
    
    ***REMOVED*** Entferne Doppelpunkte und Sonderzeichen
    field = l3_field.lower().replace(':', '').replace('-', '_').replace('/', '_')
    
    ***REMOVED*** Ersetze Umlaute
    replacements = {
        'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
        '(': '', ')': '', '.': '', ',': '', ' ': '_'
    }
    for old, new in replacements.items():
        field = field.replace(old, new)
    
    ***REMOVED*** Entferne mehrfache Unterstriche
    field = re.sub(r'_+', '_', field)
    
    ***REMOVED*** Entferne führende/abschließende Unterstriche
    field = field.strip('_')
    
    return field

***REMOVED*** Funktion: Erkenne Feldtyp
def detect_field_type(l3_field: str) -> str:
    """Erkennt den Feldtyp basierend auf dem L3-Feldnamen"""
    
    field_lower = l3_field.lower()
    
    ***REMOVED*** Zahlen
    if any(word in field_lower for word in ['anzahl', 'nummer', 'nr.', 'nr', 'tabelle', 'betrag', 'umsatz', 'rabatt', 'skonto', 'prozent', '%']):
        return "number"
    
    ***REMOVED*** Datum
    if any(word in field_lower for word in ['datum', 'datum', 'seit', 'bis', 'kuendigung', 'austritt', 'eintritt']):
        return "date"
    
    ***REMOVED*** Boolean
    if any(word in field_lower for word in ['ja/nein', 'gekuendigt', 'erlaubt', 'sperre', 'berechnen', 'gewuenscht', 'empfaenger', 'automatisch']):
        return "boolean"
    
    ***REMOVED*** Select (Dropdown)
    if any(word in field_lower for word in ['art', 'bedingung', 'status', 'gruppe', 'medium', 'schlüssel', 'währung']):
        return "select"
    
    ***REMOVED*** E-Mail
    if 'e-mail' in field_lower or 'email' in field_lower:
        return "string"
    
    ***REMOVED*** Text (mehrzeilig)
    if any(word in field_lower for word in ['information', 'angaben', 'anweisung', 'langtext', 'freitext', 'bemerkung', 'grund', 'philosophie']):
        return "text"
    
    ***REMOVED*** Standard String
    return "string"

***REMOVED*** Erstelle neue Mappings für fehlende Felder
new_mappings = []
for field in sorted(missing_fields):
    valeo_field = create_valeo_fieldname(field)
    field_type = detect_field_type(field)
    
    mapping = {
        "l3_field": field,
        "valeo_field": valeo_field,
        "type": field_type
    }
    
    ***REMOVED*** Füge Transformationen hinzu
    if field_type == "string":
        if 'name' in field.lower() or 'bezeichnung' in field.lower():
            mapping["transformation"] = "trim"
        elif 'email' in field.lower():
            mapping["transformation"] = "lowercase"
        elif 'nummer' in field.lower() or 'nr' in field.lower():
            mapping["transformation"] = "uppercase"
    
    ***REMOVED*** Füge Constraints hinzu
    if field_type == "number":
        if 'rabatt' in field.lower() or 'skonto' in field.lower() or '%' in field:
            mapping["unit"] = "%"
            mapping["min"] = 0
            mapping["max"] = 100
        elif 'tage' in field.lower():
            mapping["unit"] = "Tage"
            mapping["min"] = 0
            mapping["max"] = 365
    
    if field_type == "boolean":
        mapping["default"] = False
    
    if field_type == "select":
        ***REMOVED*** Versuche Optionen zu erkennen
        if 'einzel' in field.lower() or 'sammel' in field.lower():
            mapping["options"] = ["Einzel", "Sammel"]
        elif 'währung' in field.lower() or 'waehrung' in field.lower():
            mapping["options"] = ["EUR", "USD", "GBP", "CHF"]
            mapping["default"] = "EUR"
    
    new_mappings.append(mapping)

***REMOVED*** Ausgabe
print("\n" + "=" * 80)
print("GENERIERTE NEUE MAPPINGS")
print("=" * 80)
print(f"\n✨ Neue Mappings generiert: {len(new_mappings)}")

if new_mappings:
    print("\n🔧 Neue Feld-Mappings:")
    for mapping in new_mappings[:20]:  ***REMOVED*** Zeige erste 20
        print(f"   {mapping['l3_field']:40} → {mapping['valeo_field']:30} ({mapping['type']})")
    
    if len(new_mappings) > 20:
        print(f"   ... und {len(new_mappings) - 20} weitere")

***REMOVED*** Erstelle erweitertes Mapping
extended_mapping = existing_mapping.copy()
extended_mapping['masks'][0]['fields'].extend(new_mappings)
extended_mapping['version'] = "2.0"
extended_mapping['updated'] = "2025-10-26"
extended_mapping['total_fields'] = len(extended_mapping['masks'][0]['fields'])

***REMOVED*** Speichere erweitertes Mapping
output_file = 'schemas/mappings/l3-to-valeo-kundenstamm-extended.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(extended_mapping, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 80)
print("✅ MAPPING-PRÜFUNG ABGESCHLOSSEN")
print("=" * 80)
print(f"\n📄 Erweitertes Mapping gespeichert: {output_file}")
print(f"📊 Felder gesamt: {extended_mapping['total_fields']}")
print(f"✨ Neue Mappings: {len(new_mappings)}")
print(f"\n🎯 Coverage: {len(mapped_fields)}/{len(all_chatgpt_fields)} = {len(mapped_fields)/len(all_chatgpt_fields)*100:.1f}%")

