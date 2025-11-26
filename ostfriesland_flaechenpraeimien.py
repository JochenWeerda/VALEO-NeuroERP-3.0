#!/usr/bin/env python3
"""
Ostfriesland-Lead-Analyse fokussiert auf Flaechenprämien
zur Bewertung der tatsächlichen Betriebsgröße
"""

import csv
import json
from collections import defaultdict
from datetime import datetime

def analyze_ostfriesland_area_premiums():
    csv_path = "data/gap/impdata2024.csv"
    output_file = "ostfriesland_flaechenprämien_leads.json"
    
    print("OSTFRIESLAND-FLAECHENPRAEMIEN-ANALYSE")
    print("=" * 60)
    print("Fokus: Nur Flächenprämien für Betriebsgrössen-Bewertung")
    print()
    
    # Flächenprämien-Codes (basierend auf typischen GAP-Kategorien)
    area_premium_codes = {
        'I.1': 'Basis-Direktzahlung',
        'I.2': 'Umverteilungsz. für Nachhaltigkeit', 
        'I.3': 'Zahlung für Junglandwirte',
        'I.4': 'Gekoppelte Einkommensstützung', 
        'I.6': 'Kleinerzeugerregelung',
        'V.1': 'Agrarumwelt-Klimamaßnahmen',  # Oft flächenbezogen
    }
    
    print("VERWENDETE FLAECHENPRAEMIEN-CODES:")
    print("-" * 40)
    for code, description in area_premium_codes.items():
        print(f"  {code}: {description}")
    print()
    
    # Container für Analyse 
    farm_data = defaultdict(lambda: {
        "name": "",
        "plz": "",
        "city": "", 
        "total_area_premiums": 0.0,
        "premium_codes": [],
        "lead_score": 0,
        "farm_size_estimate": ""
    })
    
    excluded_leads = 0
    included_leads = 0
    total_premium_amount = 0.0
    
    # Header
    amount_header = "EU-Betrag (EGFL und ELER) und kofinanzierter Betrag insgesamt für diesen Begünstigten*"
    name_header = "Name des Begünstigten/Rechtsträgers/Verdands"
    measure_header = "Code der Maßnahme/der Interventionskategorie/des Sektors gemäß Anhang IX "
    
    print("Analysiere CSV für Flächenprämien...")
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            # Header-Mapping
            headers = reader.fieldnames
            for header in headers:
                if 'EU-Betrag' in header and 'EGFL' in header and 'ELER' in header:
                    amount_header = header
                if 'begünstigten' in header.lower() and 'rechtsträgers' in header.lower():
                    name_header = header
                if 'code der maßnahme' in header.lower() or 'code der massnahme' in header.lower():
                    measure_header = header
            
            for row_num, row in enumerate(reader, 1):
                plz = row.get('PLZ', '').strip()
                
                # Nur PLZ 26400-26999 (Ostfriesland)
                if plz and len(plz) >= 5:
                    try:
                        plz_num = int(plz)
                        if 26400 <= plz_num <= 26999:
                            
                            measure_code = row.get(measure_header, '').strip()
                            
                            # NUR Flächenprämien-Codes berücksichtigen!
                            if measure_code in area_premium_codes:
                                included_leads += 1
                                
                                name = row.get(name_header, '').strip()
                                city = row.get('Gemeinde', '').strip()
                                
                                # Betrag extrahieren
                                gap_amount = 0.0
                                amount_field = row.get(amount_header, '').strip()
                                if amount_field:
                                    try:
                                        gap_amount = float(amount_field.replace(',', '.'))
                                        total_premium_amount += gap_amount
                                    except ValueError:
                                        pass
                                
                                # Farm-Daten aggregieren (pro Name+PLZ)
                                farm_key = f"{name}_{plz}"
                                farm = farm_data[farm_key]
                                
                                if not farm["name"]:
                                    farm["name"] = name[:50]
                                    farm["plz"] = plz
                                    farm["city"] = city
                                
                                farm["total_area_premiums"] += gap_amount
                                
                                if measure_code not in farm["premium_codes"]:
                                    farm["premium_codes"].append({
                                        "code": measure_code,
                                        "description": area_premium_codes[measure_code],
                                        "amount": gap_amount
                                    })
                            else:
                                excluded_leads += 1
                    
                    except ValueError:
                        continue
                
                if row_num % 400000 == 0:
                    print(f"Verarbeitet: {row_num:,} | Flächenprämien: {included_leads} | Ausgeschlossen: {excluded_leads}")
    
    except Exception as e:
        print(f"FEHLER: {e}")
        return
    
    # Betriebsgröße schätzen basierend auf Flächenprämien
    for farm_key, farm in farm_data.items():
        amount = farm["total_area_premiums"]
        
        # Grosse Schätzung: ~300 EUR/ha Direktzahlungen
        estimated_hectares = amount / 300
        
        if amount >= 100000:
            farm["farm_size_estimate"] = f"Grossbetrieb ({estimated_hectares:.0f}+ ha)"
            farm["lead_score"] = 10
        elif amount >= 50000:
            farm["farm_size_estimate"] = f"Mittelgrosser Betrieb ({estimated_hectares:.0f} ha)"
            farm["lead_score"] = 8
        elif amount >= 20000:
            farm["farm_size_estimate"] = f"Kleinbetrieb ({estimated_hectares:.0f} ha)" 
            farm["lead_score"] = 6
        elif amount >= 10000:
            farm["farm_size_estimate"] = f"Sehr kleiner Betrieb ({estimated_hectares:.0f} ha)"
            farm["lead_score"] = 4
        else:
            farm["farm_size_estimate"] = f"Kleinstbetrieb ({estimated_hectares:.0f} ha)"
            farm["lead_score"] = 2
    
    # Ergebnisse 
    print()
    print("FLAECHENPRAEMIEN-BASIERTE LEAD-ANALYSE")
    print("=" * 60)
    print(f"Gesamt verarbeitete Zahlungen: {included_leads + excluded_leads:,}")
    print(f"Flächenprämien-Zahlungen: {included_leads:,} ({included_leads/(included_leads + excluded_leads)*100:.1f}%)")
    print(f"Ausgeschlossene Zahlungen: {excluded_leads:,} ({excluded_leads/(included_leads + excluded_leads)*100:.1f}%)")
    print(f"Unique Betriebe: {len(farm_data):,}")
    print(f"Gesamt Flächenprämien: {total_premium_amount:,.2f} EUR")
    print(f"Durchschnitt pro Betrieb: {total_premium_amount/len(farm_data):,.2f} EUR")
    print()
    
    # Top Leads nach Flächenprämien
    sorted_farms = sorted(farm_data.values(), key=lambda x: x["total_area_premiums"], reverse=True)
    
    print("TOP 20 OSTFRIESLAND-LEADS (NACH FLAECHENPRÄMIEN):")
    print("-" * 60)
    for i, farm in enumerate(sorted_farms[:20], 1):
        codes_str = ", ".join([f"{p['code']}" for p in farm["premium_codes"]])
        print(f"{i:2d}. {farm['name'][:35]}...")
        print(f"    PLZ {farm['plz']} | {farm['city']}")
        print(f"    Flächenprämien: {farm['total_area_premiums']:,.0f} EUR")
        print(f"    {farm['farm_size_estimate']} | Score: {farm['lead_score']}/10")
        print(f"    Codes: {codes_str}")
        print()
    
    # Betriebsgrößen-Verteilung
    size_distribution = defaultdict(int)
    for farm in farm_data.values():
        if "Grossbetrieb" in farm["farm_size_estimate"]:
            size_distribution["Grossbetrieb"] += 1
        elif "Mittelgrosser" in farm["farm_size_estimate"]:
            size_distribution["Mittelgrosser Betrieb"] += 1  
        elif "Kleinbetrieb" in farm["farm_size_estimate"]:
            size_distribution["Kleinbetrieb"] += 1
        elif "Sehr kleiner" in farm["farm_size_estimate"]:
            size_distribution["Sehr kleiner Betrieb"] += 1
        else:
            size_distribution["Kleinstbetrieb"] += 1
    
    print("BETRIEBSGRÖSSEN-VERTEILUNG:")
    print("-" * 35)
    for size, count in sorted(size_distribution.items(), key=lambda x: x[1], reverse=True):
        percentage = count / len(farm_data) * 100
        print(f"{size}: {count:,} Betriebe ({percentage:.1f}%)")
    
    # JSON Export 
    result_data = {
        "timestamp": datetime.now().isoformat(),
        "analysis_focus": "Flächenprämien zur Betriebsgrösse-Bewertung",
        "area_premium_codes": area_premium_codes,
        "statistics": {
            "total_payments_processed": included_leads + excluded_leads,
            "area_premium_payments": included_leads,
            "excluded_payments": excluded_leads,
            "unique_farms": len(farm_data),
            "total_area_premiums_eur": total_premium_amount,
            "avg_premiums_per_farm": total_premium_amount/len(farm_data) if len(farm_data) > 0 else 0
        },
        "farm_size_distribution": dict(size_distribution),
        "top_leads": sorted_farms[:100]  # Top 100
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)
    
    print()
    print(f"Detaillierte Analyse gespeichert: {output_file}")
    print()
    print("ERFOLG: Ostfriesland-Leads nach Flächenprämien bewertet!")
    print("Nur Betriebe mit signifikanten Flächenprämien = potentielle Kunden")

if __name__ == "__main__":
    analyze_ostfriesland_area_premiums()
