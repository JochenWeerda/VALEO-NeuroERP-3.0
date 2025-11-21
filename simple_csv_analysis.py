#!/usr/bin/env python3
"""
Einfache Analyse der gefilterten CSV ohne Unicode-Probleme
"""

import csv
import json
from collections import defaultdict

def analyze_filtered_csv():
    csv_path = r"C:\Users\Jochen\Downloads\impdata2024_PLZ_26XXX.csv"
    
    print("ANALYSE DER GEFILTERTEN PLZ 26XXX CSV")
    print("=" * 50)
    
    # Verschiedene Encodings testen
    encodings = ['windows-1252', 'iso-8859-1', 'latin1', 'cp1252', 'utf-8']
    
    working_encoding = None
    
    for encoding in encodings:
        try:
            print(f"Teste Encoding: {encoding}")
            with open(csv_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=';')
                headers = reader.fieldnames
                first_row = next(reader)
                
                print(f"  ERFOLG! Headers: {len(headers)} Spalten")
                print(f"  Erste PLZ: {first_row.get('PLZ', 'N/A')}")
                working_encoding = encoding
                break
                
        except Exception as e:
            print(f"  Fehler mit {encoding}")
            continue
    
    if not working_encoding:
        print("FEHLER: Kein funktionierendes Encoding gefunden!")
        return
    
    print(f"\nVerwende {working_encoding} fuer Hauptanalyse")
    print()
    
    # Hauptanalyse
    flaechenpraemien_codes = ['I.1', 'I.2', 'I.3', 'I.4', 'I.6', 'V.1']
    
    total_rows = 0
    total_amount = 0.0
    flaechenpraemien_count = 0
    flaechenpraemien_amount = 0.0
    plz_count = defaultdict(int)
    measure_count = defaultdict(int)
    
    # Betriebe (aggregiert)
    farms = defaultdict(lambda: {
        "name": "",
        "plz": "",
        "city": "",
        "flaechenpraemien": 0.0,
        "codes": set()
    })
    
    try:
        with open(csv_path, 'r', encoding=working_encoding) as f:
            reader = csv.DictReader(f, delimiter=';')
            headers = reader.fieldnames
            
            # Header finden
            amount_header = None
            name_header = None
            measure_header = None
            
            for header in headers:
                if 'EU-Betrag' in header and 'EGFL' in header:
                    amount_header = header
                elif 'beguenstigten' in header and 'Rechtstraeger' in header:
                    name_header = header
                elif 'Code der' in header and 'Massnahme' in header:
                    measure_header = header
            
            print("Header gefunden:")
            print(f"  Betrag: {amount_header}")
            print(f"  Name: {name_header}")
            print(f"  Measure: {measure_header}")
            print()
            
            if not all([amount_header, name_header, measure_header]):
                print("WARNUNG: Header nicht vollstaendig gefunden")
                print("Alle Header:")
                for i, h in enumerate(headers, 1):
                    print(f"  {i:2d}. {h}")
            
            print("Verarbeite Daten...")
            
            for row in reader:
                total_rows += 1
                
                plz = row.get('PLZ', '').strip()
                name = row.get(name_header, '').strip() if name_header else ''
                city = row.get('Gemeinde', '').strip()
                measure = row.get(measure_header, '').strip() if measure_header else ''
                
                # Betrag
                amount = 0.0
                amount_str = row.get(amount_header, '').strip() if amount_header else ''
                if amount_str:
                    try:
                        amount = float(amount_str.replace(',', '.'))
                        total_amount += amount
                    except:
                        pass
                
                # Statistiken
                if plz:
                    plz_count[plz] += 1
                if measure:
                    measure_count[measure] += 1
                
                # Flaechenpraemien pruefen
                if measure in flaechenpraemien_codes:
                    flaechenpraemien_count += 1
                    flaechenpraemien_amount += amount
                    
                    # Farm aggregieren
                    farm_key = f"{name}_{plz}"
                    farm = farms[farm_key]
                    if not farm["name"]:
                        farm["name"] = name[:50]
                        farm["plz"] = plz
                        farm["city"] = city
                    farm["flaechenpraemien"] += amount
                    farm["codes"].add(measure)
                
                if total_rows % 3000 == 0:
                    print(f"  Zeile {total_rows:,}")
    
    except Exception as e:
        print(f"FEHLER: {e}")
        return
    
    print()
    print("ERGEBNISSE")
    print("=" * 30)
    print(f"Gesamt Zahlungen: {total_rows:,}")
    print(f"Gesamt Betrag: {total_amount:,.2f} EUR")
    print(f"Flaechenpraemien: {flaechenpraemien_count:,} ({flaechenpraemien_count/total_rows*100:.1f}%)")
    print(f"Flaechenpraemien Betrag: {flaechenpraemien_amount:,.2f} EUR")
    print(f"Qualifizierte Betriebe: {len(farms):,}")
    print(f"Verschiedene PLZ: {len(plz_count)}")
    print()
    
    # Top PLZ
    print("TOP 10 PLZ:")
    sorted_plz = sorted(plz_count.items(), key=lambda x: x[1], reverse=True)
    for i, (plz, count) in enumerate(sorted_plz[:10], 1):
        print(f"{i:2d}. PLZ {plz}: {count:,}")
    
    print()
    
    # Top Measure Codes
    print("TOP MEASURE CODES:")
    sorted_measures = sorted(measure_count.items(), key=lambda x: x[1], reverse=True)
    for i, (code, count) in enumerate(sorted_measures[:10], 1):
        is_area = "JA" if code in flaechenpraemien_codes else "  "
        print(f"{i:2d}. [{is_area}] {code}: {count:,}")
    
    print()
    
    # Top Betriebe
    sorted_farms = sorted(farms.values(), key=lambda x: x["flaechenpraemien"], reverse=True)
    
    print("TOP 15 QUALIFIZIERTE LEADS:")
    print("-" * 40)
    for i, farm in enumerate(sorted_farms[:15], 1):
        hectares = farm["flaechenpraemien"] / 300
        score = 10 if farm["flaechenpraemien"] >= 100000 else (8 if farm["flaechenpraemien"] >= 50000 else 6)
        
        print(f"{i:2d}. {farm['name'][:35]}...")
        print(f"    PLZ {farm['plz']} | {farm['city']}")
        print(f"    Flaechenpraemien: {farm['flaechenpraemien']:,.0f} EUR")
        print(f"    Geschaetzt: {hectares:,.0f} ha | Score: {score}/10")
        print()
    
    # JSON Export
    result = {
        "total_payments": total_rows,
        "total_amount": total_amount,
        "area_premium_payments": flaechenpraemien_count,
        "area_premium_amount": flaechenpraemien_amount,
        "qualified_farms": len(farms),
        "top_leads": [{
            "name": f["name"],
            "plz": f["plz"],
            "city": f["city"],
            "area_premiums": f["flaechenpraemien"],
            "estimated_hectares": f["flaechenpraemien"] / 300,
            "codes": list(f["codes"])
        } for f in sorted_farms[:25]]
    }
    
    with open("filtered_analysis_simple.json", 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print("Analyse gespeichert: filtered_analysis_simple.json")
    print()
    print("ERFOLG! Gefilterte Ostfriesland-Daten analysiert!")

if __name__ == "__main__":
    analyze_filtered_csv()

