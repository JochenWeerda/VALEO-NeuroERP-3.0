#!/usr/bin/env python3
"""
Review der automatisch generierten Mappings
Identifiziert potenzielle Probleme und Fehler
"""

import json
from pathlib import Path

# Lade erweitertes Mapping
with open('schemas/mappings/l3-to-valeo-kundenstamm-extended.json', 'r', encoding='utf-8') as f:
    mapping = json.load(f)

print("=" * 80)
print("MAPPING-REVIEW")
print("=" * 80)

# 1. Prüfe Feldnamens-Länge
print("\n1️⃣ FELDNAMEN-LÄNGE")
print("-" * 80)

long_fields = []
for field in mapping['masks'][0]['fields']:
    valeo_field = field.get('valeo_field', '')
    if len(valeo_field) > 50:
        long_fields.append({
            'l3': field.get('l3_field', ''),
            'valeo': valeo_field,
            'length': len(valeo_field)
        })

if long_fields:
    print(f"⚠️  {len(long_fields)} Felder mit sehr langen Namen (>50 Zeichen):")
    for field in sorted(long_fields, key=lambda x: x['length'], reverse=True)[:10]:
        print(f"   {field['valeo']:60} ({field['length']} Zeichen)")
else:
    print("✅ Keine überlangen Feldnamen gefunden")

# 2. Prüfe Feldtyp-Einordnung
print("\n2️⃣ FELDTYP-EINORDNUNG")
print("-" * 80)

field_type_issues = {
    'number_as_string': [],
    'string_as_number': [],
    'date_as_string': [],
    'boolean_as_string': []
}

for field in mapping['masks'][0]['fields']:
    l3_field = field.get('l3_field', '').lower()
    field_type = field.get('type', '')
    
    # Zahl-Felder die als String erkannt wurden
    if field_type == 'string' and any(word in l3_field for word in ['nummer', 'nr.', 'nr ', 'anzahl', 'betrag', 'umsatz', 'anteil']):
        field_type_issues['number_as_string'].append(field['l3_field'])
    
    # String-Felder die als Number erkannt wurden
    if field_type == 'number' and any(word in l3_field for word in ['name', 'bezeichnung', 'text', 'angabe']):
        field_type_issues['string_as_number'].append(field['l3_field'])
    
    # Datum-Felder die als String erkannt wurden
    if field_type == 'string' and any(word in l3_field for word in ['datum', 'datum ', 'seit', 'bis ']):
        field_type_issues['date_as_string'].append(field['l3_field'])
    
    # Boolean-Felder die als String erkannt wurden
    if field_type == 'string' and 'ja/nein' in l3_field:
        field_type_issues['boolean_as_string'].append(field['l3_field'])

issues_found = False
for issue_type, fields in field_type_issues.items():
    if fields:
        issues_found = True
        print(f"\n⚠️  {issue_type}: {len(fields)} Felder")
        for field in fields[:5]:
            print(f"   - {field}")
        if len(fields) > 5:
            print(f"   ... und {len(fields) - 5} weitere")

if not issues_found:
    print("✅ Alle Feldtypen korrekt zugeordnet")

# 3. Prüfe fehlende Transformationen
print("\n3️⃣ FEHLENDE TRANSFORMATIONEN")
print("-" * 80)

missing_transformations = []
for field in mapping['masks'][0]['fields']:
    field_type = field.get('type', '')
    has_transformation = 'transformation' in field
    
    if field_type == 'string' and not has_transformation:
        # Prüfe ob Transformation sinnvoll wäre
        l3_field = field.get('l3_field', '').lower()
        if any(word in l3_field for word in ['email', 'nummer', 'name', 'bezeichnung']):
            missing_transformations.append(field['l3_field'])

if missing_transformations:
    print(f"⚠️  {len(missing_transformations)} Felder ohne Transformation:")
    for field in missing_transformations[:10]:
        print(f"   - {field}")
    if len(missing_transformations) > 10:
        print(f"   ... und {len(missing_transformations) - 10} weitere")
else:
    print("✅ Alle Transformationen vorhanden")

# 4. Prüfe Constraints
print("\n4️⃣ CONSTRAINTS")
print("-" * 80)

missing_constraints = []
for field in mapping['masks'][0]['fields']:
    field_type = field.get('type', '')
    has_constraints = any(key in field for key in ['min', 'max', 'unit', 'options'])
    
    if field_type == 'number' and not has_constraints:
        missing_constraints.append(field['l3_field'])

if missing_constraints:
    print(f"⚠️  {len(missing_constraints)} Zahl-Felder ohne Constraints:")
    for field in missing_constraints[:10]:
        print(f"   - {field}")
    if len(missing_constraints) > 10:
        print(f"   ... und {len(missing_constraints) - 10} weitere")
else:
    print("✅ Alle Constraints vorhanden")

# 5. Prüfe spezielle Felder
print("\n5️⃣ SPEZIELLE FELDER")
print("-" * 80)

special_fields = {
    'iban': [],
    'email': [],
    'telefon': [],
    'url': []
}

for field in mapping['masks'][0]['fields']:
    l3_field = field.get('l3_field', '').lower()
    
    if 'iban' in l3_field:
        special_fields['iban'].append(field['l3_field'])
    if 'e-mail' in l3_field or 'email' in l3_field:
        special_fields['email'].append(field['l3_field'])
    if 'telefon' in l3_field or 'mobil' in l3_field:
        special_fields['telefon'].append(field['l3_field'])
    if 'homepage' in l3_field or 'url' in l3_field:
        special_fields['url'].append(field['l3_field'])

for field_type, fields in special_fields.items():
    if fields:
        print(f"\n📍 {field_type}: {len(fields)} Felder")
        for field in fields:
            print(f"   - {field}")

# 6. Zusammenfassung
print("\n" + "=" * 80)
print("ZUSAMMENFASSUNG")
print("=" * 80)

total_fields = len(mapping['masks'][0]['fields'])
issues_count = len(long_fields) + sum(len(v) for v in field_type_issues.values()) + len(missing_transformations) + len(missing_constraints)

print(f"\n📊 Felder gesamt: {total_fields}")
print(f"⚠️  Gefundene Probleme: {issues_count}")
print(f"✅ Qualität: {(1 - issues_count/total_fields)*100:.1f}%")

if issues_count == 0:
    print("\n🎉 Alles perfekt! Keine Probleme gefunden.")
else:
    print(f"\n⚠️  Erfordert manuelle Überprüfung von {issues_count} Feldern")

# Speichere Review-Report
report = {
    "review_date": "2025-10-26",
    "total_fields": total_fields,
    "issues": {
        "long_fieldnames": len(long_fields),
        "type_mismatches": sum(len(v) for v in field_type_issues.values()),
        "missing_transformations": len(missing_transformations),
        "missing_constraints": len(missing_constraints)
    },
    "quality_score": (1 - issues_count/total_fields)*100
}

with open('schemas/mappings/mapping-review-report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\n📄 Review-Report gespeichert: schemas/mappings/mapping-review-report.json")

