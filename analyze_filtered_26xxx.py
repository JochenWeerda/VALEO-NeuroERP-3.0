#!/usr/bin/env python3
"""
Analyse der vorgefilteren PLZ 26XXX-Daten aus LibreOffice Calc
Fokus auf Flächenprämien für präzise Betriebsgrößen-Bewertung
"""

import csv
import json
from collections import defaultdict
from datetime import datetime

def analyze_filtered_26xxx():
    # Pfad zur vorgefilteren CSV
    csv_path = r"C:\Users\Jochen\Downloads\impdata2024_PLZ_26XXX.csv"
    output_file = "PLZ_26XXX_final_leads.json"
    
    print("ANALYSE DER VORGEFILERTEN PLZ 26XXX-DATEN")
    print("=" * 60)
    print("Quelle: LibreOffice Calc vorgefilterte CSV")
    print(f"Datei: {csv_path}")
    print()
    
    # Flächenprämien-Codes (basierend auf GAP-Systematik)
    area_premium_codes = {
        'I.1': 'Basis-Direktzahlung (Flächenprämie)',
        'I.2': 'Umverteilungsz. für Nachhaltigkeit (Flächenprämie)', 
        'I.3': 'Zahlung für Junglandwirte (Flächenprämie)',
        'I.4': 'Gekoppelte Einkommensstützung (Flächenprämie)', 
        'I.6': 'Kleinerzeugerregelung (Flächenprämie)',
        'V.1': 'Agrarumwelt-Klimamaßnahmen (meist flächenbezogen)',
    }
    
    print("FOCUS: NUR FLAECHENPRAEMIEN-CODES")
    print("-" * 40)
    for code, description in area_premium_codes.items():
        print(f"  {code}: {description}")
    print()
    
    # Container für Betriebsanalyse
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
    
    print("Lese vorgefilterte CSV...")
    
    # Verschiedene Encodings versuchen (LibreOffice Calc verwendet oft andere Encodings)
    encodings_to_try = ['utf-8-sig', 'utf-8', 'windows-1252', 'iso-8859-1', 'cp1252']
    
    for encoding in encodings_to_try:
        try:
            print(f"Versuche Encoding: {encoding}")
            with open(csv_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=';')
                
                headers = reader.fieldnames
                print(f"CSV-Headers: {len(headers) if headers else 0} Spalten")
                
                if headers:
                    print("Verfügbare Header:")
                    for i, header in enumerate(headers, 1):
                        print(f"  {i:2d}. {header}")
                print()
                
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
                
                print(f"Verwendete Headers:")
                print(f"  Betrag: {amount_header}")
                print(f"  Name: {name_header}")  
                print(f"  Measure: {measure_header}")
                print()
                
                print("Verarbeite Zeilen...")
                print("-" * 30)
                
                for row_num, row in enumerate(reader, 1):
                    total_rows += 1
                    
                    plz = row.get('PLZ', '').strip()
                    name = row.get(name_header, '').strip() if name_header else ''
                    city = row.get('Gemeinde', '').strip()
                    measure_code = row.get(measure_header, '').strip() if measure_header else ''
                    
                    # GAP-Betrag extrahieren
                    gap_amount = 0.0
                    if amount_header:
                        amount_field = row.get(amount_header, '').strip()
                        if amount_field:
                            try:
                                gap_amount = float(amount_field.replace(',', '.'))
                            except ValueError:
                                pass
                    
                    # PLZ-Verteilung tracken
                    if plz:
                        plz_distribution[plz] += 1
                    
                    # Measure Code Stats
                    if measure_code:
                        measure_code_stats[measure_code]["count"] += 1
                        measure_code_stats[measure_code]["amount"] += gap_amount
                    
                    # NUR Flächenprämien-Codes verarbeiten
                    if measure_code in area_premium_codes:
                        area_premium_rows += 1
                        total_amount += gap_amount
                        
                        # Farm-Key (Name + PLZ für Eindeutigkeit)
                        farm_key = f"{name}_{plz}"
                        farm = farm_data[farm_key]
                        
                        # Basisdaten setzen (beim ersten Mal)
                        if not farm["name"]:
                            farm["name"] = name[:60]
                            farm["plz"] = plz
                            farm["city"] = city
                            farm["premium_breakdown"] = {}
                        
                        # Flächenprämien aggregieren
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
                        
                        # Erste paar Zeilen ausgeben
                        if area_premium_rows <= 10:
                            print(f"Row {area_premium_rows:2d}: {name[:35]}... | PLZ {plz} | {measure_code} | {gap_amount:,.0f} EUR")
                    
                    else:
                        excluded_rows += 1
                    
                    # Progress
                    if total_rows % 1000 == 0:
                        print(f"Verarbeitet: {total_rows:,} | Flächenprämien: {area_premium_rows} | Ausgeschlossen: {excluded_rows}")
            
            print(f"Erfolgreich gelesen mit Encoding: {encoding}")
            break  # Erfolgreich gelesen, Schleife verlassen
            
        except UnicodeDecodeError:
            print(f"Encoding {encoding} fehlgeschlagen, versuche nächstes...")
            continue
        except Exception as e:
            print(f"Anderer Fehler mit {encoding}: {e}")
            continue
    else:
        print("FEHLER: Keines der Encodings funktioniert!")
        return
    
    except FileNotFoundError:
        print(f"FEHLER: Datei nicht gefunden: {csv_path}")
        return
    
    # Betriebsgrößen schätzen und kategorisieren
    for farm_key, farm in farm_data.items():
        amount = farm["total_area_premiums"]
        
        # Schätzung: ~300 EUR/ha Direktzahlungen (EU-Standard)
        farm["estimated_hectares"] = amount / 300
        
        # Betriebskategorisierung
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
    
    # Ergebnisse ausgeben
    print()
    print("PLZ 26XXX FINALE ANALYSE")
    print("=" * 50)
    print(f"Gesamt Zeilen verarbeitet: {total_rows:,}")
    print(f"Flächenprämien-Zahlungen: {area_premium_rows:,} ({area_premium_rows/total_rows*100:.1f}%)")
    print(f"Ausgeschlossene Zahlungen: {excluded_rows:,} ({excluded_rows/total_rows*100:.1f}%)")
    print(f"Einzigartige Betriebe: {len(farm_data):,}")
    print(f"Gesamt Flächenprämien: {total_amount:,.2f} EUR")
    print(f"Durchschnitt/Betrieb: {total_amount/len(farm_data):,.2f} EUR" if len(farm_data) > 0 else "N/A")
    print()
    
    # Top PLZ anzeigen
    print("PLZ-VERTEILUNG (TOP 15):")
    print("-" * 25)
    sorted_plz = sorted(plz_distribution.items(), key=lambda x: x[1], reverse=True)
    for plz, count in sorted_plz[:15]:
        print(f"PLZ {plz}: {count:,} Zahlungen")
    print()
    
    # Top Measure Codes
    print("MEASURE CODE VERTEILUNG:")
    print("-" * 28)
    sorted_measures = sorted(measure_code_stats.items(), key=lambda x: x[1]["count"], reverse=True)
    for code, stats in sorted_measures[:10]:
        in_focus = "✓" if code in area_premium_codes else "✗"
        print(f"{in_focus} {code}: {stats['count']:,} Zahlungen | {stats['amount']:,.0f} EUR")
    print()
    
    # Top Leads
    sorted_farms = sorted(farm_data.values(), key=lambda x: x["total_area_premiums"], reverse=True)
    
    print("TOP 15 PLZ 26XXX LEADS (NACH FLAECHENPRÄMIEN):")
    print("-" * 55)
    for i, farm in enumerate(sorted_farms[:15], 1):
        codes = list(farm["premium_breakdown"].keys())
        codes_str = ", ".join(codes[:4])  # Max 4 Codes anzeigen
        if len(codes) > 4:
            codes_str += f" (+{len(codes)-4})"
        
        print(f"{i:2d}. {farm['name'][:40]}...")
        print(f"    PLZ {farm['plz']} {farm['city']}")
        print(f"    Flächenprämien: {farm['total_area_premiums']:,.0f} EUR")
        print(f"    Geschätzte Fläche: {farm['estimated_hectares']:,.0f} ha")
        print(f"    Kategorie: {farm['farm_category']} (Score: {farm['lead_score']}/10)")
        print(f"    Codes: {codes_str} | Zahlungen: {farm['payment_count']}")
        print()
    
    # Betriebsgrößen-Verteilung
    category_distribution = defaultdict(int)
    for farm in farm_data.values():
        category_distribution[farm["farm_category"]] += 1
    
    print("BETRIEBSGROESSEN-VERTEILUNG:")
    print("-" * 32)
    for category, count in sorted(category_distribution.items(), key=lambda x: x[1], reverse=True):
        percentage = count / len(farm_data) * 100 if len(farm_data) > 0 else 0
        print(f"{category}: {count:,} Betriebe ({percentage:.1f}%)")
    
    # JSON Export
    result_data = {
        "source": "LibreOffice Calc gefilterte PLZ 26XXX CSV",
        "timestamp": datetime.now().isoformat(),
        "analysis_focus": "Flächenprämien für Betriebsgrößenschätzung",
        "statistics": {
            "total_rows_processed": total_rows,
            "area_premium_payments": area_premium_rows,
            "excluded_payments": excluded_rows,
            "unique_farms": len(farm_data),
            "total_area_premiums_eur": total_amount,
            "average_per_farm": total_amount/len(farm_data) if len(farm_data) > 0 else 0
        },
        "plz_distribution": dict(sorted_plz[:20]),
        "measure_code_stats": {code: stats for code, stats in sorted_measures},
        "farm_size_distribution": dict(category_distribution),
        "area_premium_codes_used": area_premium_codes,
        "top_leads": sorted_farms[:50]  # Top 50 Leads
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)
    
    print()
    print(f"Detaillierte Analyse gespeichert: {output_file}")
    print()
    print("SUCCESS! PLZ 26XXX-Leads mit präziser Flächenbewertung analysiert!")
    print(f"Ihre {len([f for f in farm_data.values() if f['lead_score'] >= 7]):,} Premium-Leads sind verkaufsbereit!")

if __name__ == "__main__":
    analyze_filtered_26xxx()
