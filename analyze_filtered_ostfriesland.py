#!/usr/bin/env python3
"""
Analysiere die bereits gefilterte PLZ 26XXX CSV-Datei
für optimierte Ostfriesland-Lead-Generierung
"""

import csv
import json
from datetime import datetime
from collections import defaultdict

def analyze_filtered_ostfriesland_csv():
    csv_path = r"C:\Users\Jochen\Downloads\impdata2024_PLZ_26XXX.csv"
    output_file = "filtered_ostfriesland_analysis.json"
    
    print("ANALYSE DER VORGEFILTERTEN PLZ 26XXX CSV")
    print("=" * 60)
    print(f"Quelle: {csv_path}")
    print()
    
    # Flächenprämien-Codes (aus vorheriger Analyse)
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
    measure_code_stats = defaultdict(lambda: {"count": 0, "total_amount": 0.0})
    
    # Lead-Container (pro Betrieb aggregiert)
    farms = defaultdict(lambda: {
        "name": "",
        "plz": "",
        "city": "",
        "total_area_premiums": 0.0,
        "total_all_payments": 0.0,
        "premium_codes": set(),
        "all_codes": set(),
        "lead_score": 0,
        "estimated_hectares": 0.0
    })
    
    print("Lade und analysiere gefilterte CSV...")
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            headers = reader.fieldnames
            print(f"CSV Headers: {len(headers)} Spalten")
            
            # Header-Mapping finden
            amount_header = None
            name_header = None
            measure_header = None
            
            for header in headers:
                if 'EU-Betrag' in header and 'EGFL' in header and 'ELER' in header:
                    amount_header = header
                elif 'begünstigten' in header.lower() and 'rechtsträgers' in header.lower():
                    name_header = header
                elif 'code der maßnahme' in header.lower() or 'code der massnahme' in header.lower():
                    measure_header = header
            
            print(f"Betrag-Header: {amount_header}")
            print(f"Name-Header: {name_header}")
            print(f"Measure-Header: {measure_header}")
            print()
            
            for row_num, row in enumerate(reader, 1):
                total_rows += 1
                
                # Daten extrahieren
                plz = row.get('PLZ', '').strip()
                name = row.get(name_header, '').strip()
                city = row.get('Gemeinde', '').strip()
                measure_code = row.get(measure_header, '').strip()
                
                if not measure_code:
                    measure_code = "LEER"
                
                # Betrag extrahieren
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
                
                # Measure Code Statistik
                measure_code_stats[measure_code]["count"] += 1
                measure_code_stats[measure_code]["total_amount"] += gap_amount
                
                # Farm-Aggregation (pro Name+PLZ)
                farm_key = f"{name}_{plz}"
                farm = farms[farm_key]
                
                if not farm["name"]:
                    farm["name"] = name[:50]
                    farm["plz"] = plz
                    farm["city"] = city
                
                farm["total_all_payments"] += gap_amount
                farm["all_codes"].add(measure_code)
                
                # Nur Flächenprämien für Betriebsgröße
                if measure_code in area_premium_codes:
                    area_premium_count += 1
                    area_premium_amount += gap_amount
                    farm["total_area_premiums"] += gap_amount
                    farm["premium_codes"].add(measure_code)
                
                if total_rows % 5000 == 0:
                    print(f"Verarbeitet: {total_rows:,} Zeilen")
    
    except FileNotFoundError:
        print(f"FEHLER: Datei nicht gefunden: {csv_path}")
        print("Bitte prüfen Sie den Dateipfad.")
        return
    except Exception as e:
        print(f"FEHLER: {e}")
        return
    
    # Betriebsgrößen-Schätzung
    for farm in farms.values():
        if farm["total_area_premiums"] > 0:
            # Schätzung: ~300 EUR/ha Direktzahlungen
            farm["estimated_hectares"] = farm["total_area_premiums"] / 300
            
            # Lead-Scoring
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
        else:
            farm["lead_score"] = 1  # Nur andere Zahlungen
    
    # Ergebnisse ausgeben
    print()
    print("ERGEBNISSE DER GEFILTERTEN ANALYSE")
    print("=" * 50)
    print(f"Gesamt Zeilen (Zahlungen): {total_rows:,}")
    print(f"Gesamt GAP-Betrag: {total_amount:,.2f} EUR")
    print(f"Flächenprämien: {area_premium_count:,} ({area_premium_count/total_rows*100:.1f}%)")
    print(f"Flächenprämien-Betrag: {area_premium_amount:,.2f} EUR ({area_premium_amount/total_amount*100:.1f}%)")
    print(f"Einzigartige Betriebe: {len(farms):,}")
    print(f"Verschiedene PLZ: {len(plz_distribution)}")
    print()
    
    # PLZ-Verteilung (Top 15)
    print("TOP PLZ-BEREICHE:")
    print("-" * 25)
    sorted_plz = sorted(plz_distribution.items(), key=lambda x: x[1], reverse=True)
    for i, (plz, count) in enumerate(sorted_plz[:15], 1):
        print(f"{i:2d}. PLZ {plz}: {count:,} Zahlungen")
    
    print()
    
    # Measure Code Statistik (Top 10)
    print("TOP MEASURE CODES:")
    print("-" * 30)
    sorted_codes = sorted(measure_code_stats.items(), key=lambda x: x[1]["count"], reverse=True)
    for i, (code, stats) in enumerate(sorted_codes[:10], 1):
        is_area = "✓" if code in area_premium_codes else " "
        avg_amount = stats["total_amount"] / stats["count"] if stats["count"] > 0 else 0
        print(f"{i:2d}. [{is_area}] {code}: {stats['count']:,} | {stats['total_amount']:,.0f} EUR | Ø {avg_amount:,.0f}")
    
    print()
    
    # Top Leads nach Flächenprämien
    area_farms = [f for f in farms.values() if f["total_area_premiums"] > 0]
    sorted_farms = sorted(area_farms, key=lambda x: x["total_area_premiums"], reverse=True)
    
    print("TOP 15 OSTFRIESLAND-LEADS (FLÄCHENPRÄMIEN):")
    print("-" * 50)
    for i, farm in enumerate(sorted_farms[:15], 1):
        codes_str = ", ".join(sorted(farm["premium_codes"]))
        print(f"{i:2d}. {farm['name'][:40]}...")
        print(f"    PLZ {farm['plz']} | {farm['city']}")
        print(f"    Flächenprämien: {farm['total_area_premiums']:,.0f} EUR")
        print(f"    Geschätzte Größe: {farm['estimated_hectares']:,.0f} ha")
        print(f"    Lead-Score: {farm['lead_score']}/10 | Codes: {codes_str}")
        print()
    
    # Betriebsgrößen-Verteilung
    size_categories = {"Großbetrieb (100k+)": 0, "Mittlerer Betrieb (50-100k)": 0, 
                      "Kleinbetrieb (20-50k)": 0, "Kleinstbetrieb (<20k)": 0, "Nur andere Zahlungen": 0}
    
    for farm in farms.values():
        if farm["total_area_premiums"] >= 100000:
            size_categories["Großbetrieb (100k+)"] += 1
        elif farm["total_area_premiums"] >= 50000:
            size_categories["Mittlerer Betrieb (50-100k)"] += 1
        elif farm["total_area_premiums"] >= 20000:
            size_categories["Kleinbetrieb (20-50k)"] += 1
        elif farm["total_area_premiums"] > 0:
            size_categories["Kleinstbetrieb (<20k)"] += 1
        else:
            size_categories["Nur andere Zahlungen"] += 1
    
    print("BETRIEBSGRÖSSEN-VERTEILUNG:")
    print("-" * 35)
    for category, count in size_categories.items():
        percentage = count / len(farms) * 100 if len(farms) > 0 else 0
        print(f"{category}: {count:,} ({percentage:.1f}%)")
    
    # JSON Export
    result_data = {
        "timestamp": datetime.now().isoformat(),
        "source_file": csv_path,
        "total_payments": total_rows,
        "total_amount_eur": total_amount,
        "area_premium_payments": area_premium_count,
        "area_premium_amount_eur": area_premium_amount,
        "unique_farms": len(farms),
        "plz_distribution": dict(plz_distribution),
        "measure_code_stats": {k: dict(v) for k, v in measure_code_stats.items()},
        "size_distribution": size_categories,
        "top_leads": [{
            "name": f["name"],
            "plz": f["plz"], 
            "city": f["city"],
            "area_premiums_eur": f["total_area_premiums"],
            "estimated_hectares": f["estimated_hectares"],
            "lead_score": f["lead_score"],
            "premium_codes": list(f["premium_codes"])
        } for f in sorted_farms[:50]]  # Top 50
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)
    
    print()
    print(f"Detaillierte Analyse gespeichert: {output_file}")
    print()
    print("ERFOLG! Gefilterte Ostfriesland-Daten analysiert!")
    print("Ready für Pipeline-Integration und Lead Explorer!")

if __name__ == "__main__":
    analyze_filtered_ostfriesland_csv()

