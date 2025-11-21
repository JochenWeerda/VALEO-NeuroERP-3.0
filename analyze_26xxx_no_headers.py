#!/usr/bin/env python3
"""
Analyse der vorgefilerten PLZ 26XXX-Daten ohne Header
LibreOffice hat die CSV mit Kommas und ohne Header exportiert
"""

import csv
import json
from collections import defaultdict
from datetime import datetime

def analyze_filtered_26xxx_no_headers():
    csv_path = r"C:\Users\Jochen\Downloads\impdata2024_PLZ_26XXX.csv"
    output_file = "PLZ_26XXX_no_headers_leads.json"
    
    print("ANALYSE DER VORGEFILERTEN PLZ 26XXX-DATEN (OHNE HEADER)")
    print("=" * 65)
    print("LibreOffice Format: Kommas getrennt, keine Header")
    print(f"Datei: {csv_path}")
    print()
    
    # Flächenprämien-Codes
    area_premium_codes = {
        'I.1': 'Basis-Direktzahlung',
        'I.2': 'Umverteilungsz. für Nachhaltigkeit', 
        'I.3': 'Zahlung für Junglandwirte',
        'I.4': 'Gekoppelte Einkommensstützung', 
        'I.6': 'Kleinerzeugerregelung',
        'V.1': 'Agrarumwelt-Klimamaßnahmen',
    }
    
    print("FOCUS: NUR FLAECHENPRAEMIEN-CODES")
    print("-" * 40)
    for code, description in area_premium_codes.items():
        print(f"  {code}: {description}")
    print()
    
    # Container
    farm_data = defaultdict(lambda: {
        "name": "",
        "plz": "",
        "city": "", 
        "total_area_premiums": 0.0,
        "premium_breakdown": {},
        "estimated_hectares": 0.0,
        "farm_category": "",
        "lead_score": 0,
        "payment_count": 0
    })
    
    plz_distribution = defaultdict(int)
    measure_code_stats = defaultdict(lambda: {"count": 0, "amount": 0.0})
    
    total_rows = 0
    area_premium_rows = 0
    excluded_rows = 0
    total_amount = 0.0
    
    print("Analysiere erste Zeilen zur Struktur-Erkennung...")
    
    # Struktur basierend auf Beispielzeile:
    # 2024,"Dinklage-Hallecker, Gerlind",,,26121,"Oldenburg (Oldenburg), Stadt",DE,I.2,1,,,836.3,2710.31,,,,,,2710.31
    # Index: 0=Jahr, 1=Name, 2-4=Leer/Gruppe, 5=PLZ, 6=Stadt, 7=Land, 8=Measure_Code, 9=Ziel, 10-11=Leer, 12=EGFL_Betrag, 13=Gesamt_Betrag, ... 19=Final_Betrag
    
    encodings_to_try = ['windows-1252', 'utf-8', 'iso-8859-1']
    
    for encoding in encodings_to_try:
        try:
            print(f"Versuche Encoding: {encoding}")
            
            with open(csv_path, 'r', encoding=encoding) as f:
                reader = csv.reader(f, delimiter=',')  # Komma als Delimiter!
                
                print("Erste 3 Zeilen zur Struktur-Analyse:")
                
                for row_num, row in enumerate(reader, 1):
                    total_rows += 1
                    
                    # Erste paar Zeilen zur Analyse ausgeben
                    if row_num <= 3:
                        print(f"Zeile {row_num}: {len(row)} Spalten")
                        for i, cell in enumerate(row):
                            print(f"  [{i:2d}]: '{cell}'")
                        print()
                    
                    if row_num > 3:
                        # Normale Verarbeitung
                        if len(row) >= 20:  # Mindestens 20 Spalten erwartet
                            
                            # Daten extrahieren (basierend auf erkannter Struktur)
                            try:
                                year = row[0].strip()
                                name = row[1].strip().replace('"', '')  # Anführungszeichen entfernen
                                plz = row[5].strip()
                                city = row[6].strip().replace('"', '')  # Anführungszeichen entfernen
                                measure_code = row[8].strip()
                                
                                # Verschiedene Betrag-Spalten probieren
                                gap_amount = 0.0
                                # Spalte 19 (Final), 13 (Gesamt), 12 (EGFL)
                                amount_candidates = [19, 13, 12]
                                
                                for col_idx in amount_candidates:
                                    if col_idx < len(row) and row[col_idx].strip():
                                        try:
                                            gap_amount = float(row[col_idx].replace(',', '.'))
                                            break
                                        except ValueError:
                                            continue
                                
                                # PLZ-Filter: nur 26xxx
                                if plz and plz.startswith('26') and len(plz) == 5:
                                    
                                    # PLZ-Verteilung
                                    plz_distribution[plz] += 1
                                    
                                    # Measure Code Stats
                                    if measure_code:
                                        measure_code_stats[measure_code]["count"] += 1
                                        measure_code_stats[measure_code]["amount"] += gap_amount
                                    
                                    # Nur Flächenprämien
                                    if measure_code in area_premium_codes:
                                        area_premium_rows += 1
                                        total_amount += gap_amount
                                        
                                        # Farm-Key
                                        farm_key = f"{name}_{plz}"
                                        farm = farm_data[farm_key]
                                        
                                        # Basisdaten
                                        if not farm["name"]:
                                            farm["name"] = name[:60]
                                            farm["plz"] = plz
                                            farm["city"] = city
                                            farm["premium_breakdown"] = {}
                                        
                                        # Aggregieren
                                        farm["total_area_premiums"] += gap_amount
                                        farm["payment_count"] += 1
                                        
                                        # Premium-Breakdown
                                        if measure_code not in farm["premium_breakdown"]:
                                            farm["premium_breakdown"][measure_code] = {
                                                "description": area_premium_codes[measure_code],
                                                "amount": 0.0,
                                                "count": 0
                                            }
                                        
                                        farm["premium_breakdown"][measure_code]["amount"] += gap_amount
                                        farm["premium_breakdown"][measure_code]["count"] += 1
                                        
                                        # Erste Treffer zeigen
                                        if area_premium_rows <= 15:
                                            print(f"Lead {area_premium_rows:2d}: {name[:25]}... | PLZ {plz} | {measure_code} | {gap_amount:,.0f} EUR")
                                    
                                    else:
                                        excluded_rows += 1
                            
                            except (IndexError, ValueError) as e:
                                excluded_rows += 1
                                continue
                    
                    # Progress
                    if total_rows % 5000 == 0:
                        print(f"Verarbeitet: {total_rows:,} | PLZ 26XXX Flächenprämien: {area_premium_rows} | Ausgeschlossen: {excluded_rows}")
                
                print(f"Erfolgreich mit Encoding: {encoding}")
                break
                
        except UnicodeDecodeError:
            print(f"Encoding {encoding} fehlgeschlagen")
            continue
        except FileNotFoundError:
            print(f"FEHLER: Datei nicht gefunden: {csv_path}")
            return
        except Exception as e:
            print(f"Fehler mit {encoding}: {e}")
            continue
    
    # Betriebsgrößen-Kategorisierung
    for farm_key, farm in farm_data.items():
        amount = farm["total_area_premiums"]
        farm["estimated_hectares"] = amount / 300  # ~300 EUR/ha
        
        if amount >= 200000:
            farm["farm_category"] = "Mega-Betrieb"
            farm["lead_score"] = 10
        elif amount >= 100000:
            farm["farm_category"] = "Großbetrieb"
            farm["lead_score"] = 9
        elif amount >= 50000:
            farm["farm_category"] = "Mittlerer Betrieb"
            farm["lead_score"] = 7
        elif amount >= 20000:
            farm["farm_category"] = "Kleinbetrieb"
            farm["lead_score"] = 5
        elif amount >= 10000:
            farm["farm_category"] = "Sehr kleiner Betrieb"
            farm["lead_score"] = 3
        else:
            farm["farm_category"] = "Kleinstbetrieb"
            farm["lead_score"] = 1
    
    # Ergebnisse
    print()
    print("FINALE PLZ 26XXX ANALYSE (LibreOffice Format)")
    print("=" * 55)
    print(f"Gesamt Zeilen: {total_rows:,}")
    print(f"PLZ 26XXX Flächenprämien: {area_premium_rows:,} ({area_premium_rows/max(total_rows,1)*100:.1f}%)")
    print(f"Ausgeschlossen: {excluded_rows:,}")
    print(f"Einzigartige Betriebe: {len(farm_data):,}")
    print(f"Gesamt Flächenprämien: {total_amount:,.2f} EUR")
    if len(farm_data) > 0:
        print(f"Durchschnitt/Betrieb: {total_amount/len(farm_data):,.2f} EUR")
    print()
    
    # Top PLZ
    if plz_distribution:
        print("TOP PLZ-VERTEILUNG:")
        print("-" * 22)
        sorted_plz = sorted(plz_distribution.items(), key=lambda x: x[1], reverse=True)
        for plz, count in sorted_plz[:15]:
            print(f"PLZ {plz}: {count:,} Zahlungen")
        print()
    
    # Top Measure Codes
    if measure_code_stats:
        print("MEASURE CODE VERTEILUNG:")
        print("-" * 28)
        sorted_measures = sorted(measure_code_stats.items(), key=lambda x: x[1]["count"], reverse=True)
        for code, stats in sorted_measures[:10]:
            focus = "✓" if code in area_premium_codes else "✗"
            print(f"{focus} {code}: {stats['count']:,} | {stats['amount']:,.0f} EUR")
        print()
    
    # Top Leads
    if farm_data:
        sorted_farms = sorted(farm_data.values(), key=lambda x: x["total_area_premiums"], reverse=True)
        
        print("TOP 20 PLZ 26XXX LEADS:")
        print("-" * 30)
        for i, farm in enumerate(sorted_farms[:20], 1):
            codes = ", ".join(farm["premium_breakdown"].keys())
            
            print(f"{i:2d}. {farm['name'][:35]}...")
            print(f"    PLZ {farm['plz']} {farm['city'][:25]}")
            print(f"    Flächenprämien: {farm['total_area_premiums']:,.0f} EUR")
            print(f"    Fläche: ~{farm['estimated_hectares']:,.0f} ha")
            print(f"    {farm['farm_category']} (Score: {farm['lead_score']}/10)")
            print(f"    Codes: {codes}")
            print()
        
        # Verteilung
        category_stats = defaultdict(int)
        for farm in farm_data.values():
            category_stats[farm["farm_category"]] += 1
        
        print("BETRIEBSGRÖSSEN-VERTEILUNG:")
        print("-" * 30)
        for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
            pct = count / len(farm_data) * 100
            print(f"{category}: {count:,} ({pct:.1f}%)")
    
    # Export
    result_data = {
        "source": "LibreOffice PLZ 26XXX CSV (no headers, comma-delimited)",
        "timestamp": datetime.now().isoformat(),
        "statistics": {
            "total_rows": total_rows,
            "area_premium_payments": area_premium_rows,
            "unique_farms": len(farm_data),
            "total_amount": total_amount
        },
        "top_leads": sorted_farms[:100] if farm_data else []
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)
    
    print()
    print(f"Analyse gespeichert: {output_file}")
    
    if farm_data:
        premium_count = len([f for f in farm_data.values() if f['lead_score'] >= 7])
        print(f"SUCCESS! {premium_count:,} Premium-Leads (Score 7+) identifiziert!")
    else:
        print("INFO: Keine Flächenprämien-Leads in PLZ 26XXX gefunden.")
        print("Möglicherweise anderes CSV-Format oder Filter zu restriktiv.")

if __name__ == "__main__":
    analyze_filtered_26xxx_no_headers()
