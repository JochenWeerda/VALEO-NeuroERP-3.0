#!/usr/bin/env python3
"""
Analysiere die gefilterte PLZ 26XXX CSV mit verschiedenen Encodings
"""

import csv
import json
from datetime import datetime
from collections import defaultdict

def try_different_encodings():
    csv_path = r"C:\Users\Jochen\Downloads\impdata2024_PLZ_26XXX.csv"
    
    # Verschiedene Encodings ausprobieren
    encodings_to_try = [
        'utf-8-sig',
        'utf-8', 
        'windows-1252',
        'iso-8859-1',
        'cp1252',
        'latin1'
    ]
    
    print("ENCODING-TEST FÜR GEFILTERTE CSV")
    print("=" * 50)
    
    for encoding in encodings_to_try:
        try:
            print(f"Teste Encoding: {encoding}")
            
            with open(csv_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=';')
                headers = reader.fieldnames
                
                # Erste Zeile lesen
                first_row = next(reader)
                
                print(f"  ✓ ERFOLG mit {encoding}")
                print(f"  Headers: {len(headers)} Spalten")
                print(f"  Erste Zeile PLZ: {first_row.get('PLZ', 'N/A')}")
                
                # Teste deutsche Umlaute
                for header in headers:
                    if 'begünstigten' in header.lower() or 'maßnahme' in header.lower():
                        print(f"  Umlaut-Test OK: {header[:50]}...")
                        break
                
                print(f"  → Verwende {encoding} für Hauptanalyse")
                return encoding
                
        except Exception as e:
            print(f"  ✗ Fehler mit {encoding}: {str(e)[:50]}...")
            continue
    
    print("FEHLER: Kein funktionierendes Encoding gefunden!")
    return None

def analyze_with_correct_encoding():
    csv_path = r"C:\Users\Jochen\Downloads\impdata2024_PLZ_26XXX.csv"
    output_file = "filtered_ostfriesland_analysis.json"
    
    # Korrektes Encoding finden
    correct_encoding = try_different_encodings()
    if not correct_encoding:
        return
    
    print()
    print("HAUPTANALYSE DER GEFILTERTEN DATEN")
    print("=" * 50)
    
    # Flächenprämien-Codes
    area_premium_codes = {
        'I.1': 'Basis-Direktzahlung',
        'I.2': 'Umverteilungsz. für Nachhaltigkeit', 
        'I.3': 'Zahlung für Junglandwirte',
        'I.4': 'Gekoppelte Einkommensstützung', 
        'I.6': 'Kleinerzeugerregelung',
        'V.1': 'Agrarumwelt-Klimamaßnahmen',
    }
    
    # Statistiken
    total_rows = 0
    total_amount = 0.0
    area_premium_amount = 0.0
    area_premium_count = 0
    plz_distribution = defaultdict(int)
    
    # Lead-Container
    farms = defaultdict(lambda: {
        "name": "",
        "plz": "",
        "city": "",
        "total_area_premiums": 0.0,
        "premium_codes": set(),
        "lead_score": 0,
        "estimated_hectares": 0.0
    })
    
    try:
        with open(csv_path, 'r', encoding=correct_encoding) as f:
            reader = csv.DictReader(f, delimiter=';')
            
            headers = reader.fieldnames
            print(f"CSV Headers: {len(headers)} Spalten")
            
            # Header-Mapping
            amount_header = None
            name_header = None
            measure_header = None
            
            print("Suche korrekte Header...")
            for header in headers:
                header_lower = header.lower()
                if 'eu-betrag' in header_lower and ('egfl' in header_lower or 'eler' in header_lower):
                    amount_header = header
                    print(f"  Betrag-Header: {header}")
                elif 'begünstigten' in header_lower and 'rechtsträgers' in header_lower:
                    name_header = header
                    print(f"  Name-Header: {header}")
                elif 'code' in header_lower and ('maßnahme' in header_lower or 'massnahme' in header_lower):
                    measure_header = header
                    print(f"  Measure-Header: {header}")
            
            if not all([amount_header, name_header, measure_header]):
                print("WARNUNG: Nicht alle Header gefunden. Alle verfügbaren Header:")
                for i, h in enumerate(headers, 1):
                    print(f"  {i:2d}. {h}")
                return
            
            print()
            print("Verarbeite Daten...")
            
            for row_num, row in enumerate(reader, 1):
                total_rows += 1
                
                # Daten extrahieren
                plz = row.get('PLZ', '').strip()
                name = row.get(name_header, '').strip()
                city = row.get('Gemeinde', '').strip()
                measure_code = row.get(measure_header, '').strip()
                
                if not measure_code:
                    measure_code = "LEER"
                
                # Betrag
                gap_amount = 0.0
                amount_field = row.get(amount_header, '').strip()
                if amount_field:
                    try:
                        gap_amount = float(amount_field.replace(',', '.'))
                        total_amount += gap_amount
                    except ValueError:
                        pass
                
                # PLZ-Verteilung
                if plz:
                    plz_distribution[plz] += 1
                
                # Farm-Aggregation
                farm_key = f"{name}_{plz}"
                farm = farms[farm_key]
                
                if not farm["name"]:
                    farm["name"] = name[:50]
                    farm["plz"] = plz
                    farm["city"] = city
                
                # Nur Flächenprämien
                if measure_code in area_premium_codes:
                    area_premium_count += 1
                    area_premium_amount += gap_amount
                    farm["total_area_premiums"] += gap_amount
                    farm["premium_codes"].add(measure_code)
                
                if total_rows % 2000 == 0:
                    print(f"  Verarbeitet: {total_rows:,} Zeilen")
    
    except Exception as e:
        print(f"FEHLER bei Hauptanalyse: {e}")
        return
    
    # Betriebsgrößen-Bewertung
    for farm in farms.values():
        if farm["total_area_premiums"] > 0:
            farm["estimated_hectares"] = farm["total_area_premiums"] / 300
            
            if farm["total_area_premiums"] >= 100000:
                farm["lead_score"] = 10
            elif farm["total_area_premiums"] >= 50000:
                farm["lead_score"] = 8
            elif farm["total_area_premiums"] >= 20000:
                farm["lead_score"] = 6
            elif farm["total_area_premiums"] >= 10000:
                farm["lead_score"] = 4
            else:
                farm["lead_score"] = 2
    
    # Ergebnisse
    print()
    print("ERGEBNISSE - GEFILTERTE OSTFRIESLAND-DATEN")
    print("=" * 60)
    print(f"Gesamt Zahlungen: {total_rows:,}")
    print(f"Gesamt GAP-Betrag: {total_amount:,.2f} EUR")
    print(f"Flächenprämien: {area_premium_count:,} ({area_premium_count/total_rows*100:.1f}%)")
    print(f"Flächenprämien-Betrag: {area_premium_amount:,.2f} EUR")
    print(f"Einzigartige Betriebe: {len(farms):,}")
    print(f"Verschiedene PLZ: {len(plz_distribution)}")
    print()
    
    # Top PLZ
    print("TOP PLZ-BEREICHE:")
    print("-" * 25)
    sorted_plz = sorted(plz_distribution.items(), key=lambda x: x[1], reverse=True)
    for i, (plz, count) in enumerate(sorted_plz[:10], 1):
        print(f"{i:2d}. PLZ {plz}: {count:,} Zahlungen")
    
    # Top Leads
    area_farms = [f for f in farms.values() if f["total_area_premiums"] > 0]
    sorted_farms = sorted(area_farms, key=lambda x: x["total_area_premiums"], reverse=True)
    
    print()
    print("TOP 10 QUALIFIZIERTE LEADS:")
    print("-" * 35)
    for i, farm in enumerate(sorted_farms[:10], 1):
        print(f"{i:2d}. {farm['name'][:35]}...")
        print(f"    PLZ {farm['plz']} | {farm['city']}")
        print(f"    Flächenprämien: {farm['total_area_premiums']:,.0f} EUR")
        print(f"    Geschätzt: {farm['estimated_hectares']:,.0f} ha | Score: {farm['lead_score']}/10")
        print()
    
    # JSON Export
    result_data = {
        "timestamp": datetime.now().isoformat(),
        "encoding_used": correct_encoding,
        "total_payments": total_rows,
        "total_amount_eur": total_amount,
        "area_premium_amount_eur": area_premium_amount,
        "unique_farms": len(farms),
        "qualified_leads_count": len(area_farms),
        "top_leads": [{
            "name": f["name"],
            "plz": f["plz"], 
            "city": f["city"],
            "area_premiums_eur": f["total_area_premiums"],
            "estimated_hectares": f["estimated_hectares"],
            "lead_score": f["lead_score"]
        } for f in sorted_farms[:30]]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)
    
    print(f"Analyse gespeichert: {output_file}")
    print()
    print("ERFOLG! Gefilterte Daten analysiert und ready für Pipeline!")

if __name__ == "__main__":
    analyze_with_correct_encoding()

