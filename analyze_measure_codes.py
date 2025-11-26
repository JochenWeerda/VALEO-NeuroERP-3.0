#!/usr/bin/env python3
"""
Analysiert die Measure Codes in den Ostfriesland-Daten
um Flächenprämien von anderen Zahlungen zu unterscheiden
"""

import csv
import json
from collections import defaultdict

def analyze_measure_codes():
    csv_path = "data/gap/impdata2024.csv"
    output_file = "ostfriesland_measure_codes_analysis.json"
    
    print("ANALYSE DER MASSNAHMEN-CODES (PLZ 26400-26999)")
    print("=" * 60)
    print("Ziel: Flächenprämien von anderen Zahlungen trennen")
    print()
    
    # Container für Analyse
    measure_stats = defaultdict(lambda: {
        "count": 0,
        "total_amount": 0.0,
        "leads": [],
        "plz_distribution": defaultdict(int),
        "avg_amount": 0.0
    })
    
    total_leads = 0
    total_amount = 0.0
    
    # Korrekte Header
    amount_header = "EU-Betrag (EGFL und ELER) und kofinanzierter Betrag insgesamt für diesen Begünstigten*"
    name_header = "Name des Begünstigten/Rechtsträgers/Verdands"
    measure_header = "Code der Maßnahme/der Interventionskategorie/des Sektors gemäß Anhang IX "
    
    print("Scanne CSV nach Measure Codes...")
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            # Header-Mapping prüfen
            headers = reader.fieldnames
            
            # Finde korrekte Header (mit möglichen Encoding-Problemen)
            for header in headers:
                if 'EU-Betrag' in header and 'EGFL' in header and 'ELER' in header:
                    amount_header = header
                if 'begünstigten' in header.lower() and 'rechtsträgers' in header.lower():
                    name_header = header
                if 'code der maßnahme' in header.lower() or 'code der massnahme' in header.lower():
                    measure_header = header
            
            print(f"Verwende Headers:")
            print(f"  Amount: {amount_header}")
            print(f"  Name: {name_header}")
            print(f"  Measure: {measure_header}")
            print()
            
            for row_num, row in enumerate(reader, 1):
                plz = row.get('PLZ', '').strip()
                
                # Nur PLZ 26400-26999 (Ostfriesland)
                if plz and len(plz) >= 5:
                    try:
                        plz_num = int(plz)
                        if 26400 <= plz_num <= 26999:
                            total_leads += 1
                            
                            # Daten extrahieren
                            name = row.get(name_header, '').strip()
                            city = row.get('Gemeinde', '').strip()
                            measure_code = row.get(measure_header, '').strip()
                            
                            # GAP-Betrag
                            gap_amount = 0.0
                            amount_field = row.get(amount_header, '').strip()
                            if amount_field:
                                try:
                                    gap_amount = float(amount_field.replace(',', '.'))
                                    total_amount += gap_amount
                                except ValueError:
                                    pass
                            
                            # Measure Code Statistik
                            if not measure_code:
                                measure_code = "LEER/UNBEKANNT"
                            
                            measure_stats[measure_code]["count"] += 1
                            measure_stats[measure_code]["total_amount"] += gap_amount
                            measure_stats[measure_code]["plz_distribution"][plz] += 1
                            
                            # Sample Lead speichern (max 3 pro Measure Code)
                            if len(measure_stats[measure_code]["leads"]) < 3:
                                measure_stats[measure_code]["leads"].append({
                                    "name": name[:40],
                                    "plz": plz,
                                    "city": city,
                                    "amount": gap_amount
                                })
                    
                    except ValueError:
                        continue
                
                if row_num % 300000 == 0:
                    print(f"Verarbeitet: {row_num:,} Zeilen, {total_leads} Ostfriesland-Leads")
    
    except Exception as e:
        print(f"FEHLER: {e}")
        return
    
    # Durchschnitte berechnen
    for code, stats in measure_stats.items():
        if stats["count"] > 0:
            stats["avg_amount"] = stats["total_amount"] / stats["count"]
    
    # Ergebnisse ausgeben
    print()
    print("MEASURE CODES ANALYSE - OSTFRIESLAND (PLZ 26400-26999)")
    print("=" * 70)
    print(f"Gesamt Leads: {total_leads:,}")
    print(f"Gesamt Betrag: {total_amount:,.2f} EUR")
    print(f"Verschiedene Measure Codes: {len(measure_stats)}")
    print()
    
    # Nach Häufigkeit sortieren
    sorted_by_count = sorted(measure_stats.items(), key=lambda x: x[1]["count"], reverse=True)
    
    print("TOP MEASURE CODES NACH HÄUFIGKEIT:")
    print("-" * 50)
    for i, (code, stats) in enumerate(sorted_by_count[:20], 1):
        print(f"{i:2d}. Code '{code}': {stats['count']:,} Leads | {stats['total_amount']:,.0f} EUR | Ø {stats['avg_amount']:,.0f} EUR")
        
        # Beispiel-Lead zeigen
        if stats["leads"]:
            example = stats["leads"][0]
            print(f"    Beispiel: {example['name']} | PLZ {example['plz']} | {example['amount']:,.0f} EUR")
        
        # PLZ-Verteilung (Top 3)
        top_plz = sorted(stats["plz_distribution"].items(), key=lambda x: x[1], reverse=True)[:3]
        plz_str = ", ".join([f"PLZ {plz}({count})" for plz, count in top_plz])
        print(f"    Top PLZ: {plz_str}")
        print()
    
    # Nach Durchschnittsbetrag sortieren
    print("TOP MEASURE CODES NACH DURCHSCHNITTSBETRAG:")
    print("-" * 50)
    sorted_by_avg = sorted(measure_stats.items(), key=lambda x: x[1]["avg_amount"], reverse=True)
    
    for i, (code, stats) in enumerate(sorted_by_avg[:15], 1):
        if stats["count"] >= 10:  # Mindestens 10 Leads für aussagekräftige Durchschnitte
            print(f"{i:2d}. Code '{code}': Ø {stats['avg_amount']:,.0f} EUR | {stats['count']:,} Leads | {stats['total_amount']:,.0f} EUR total")
    
    print()
    
    # Leere/Unbekannte Codes analysieren
    if "LEER/UNBEKANNT" in measure_stats:
        empty_stats = measure_stats["LEER/UNBEKANNT"]
        print("ANALYSE LEERER MEASURE CODES:")
        print("-" * 35)
        print(f"Leads ohne Measure Code: {empty_stats['count']:,} ({empty_stats['count']/total_leads*100:.1f}%)")
        print(f"Gesamtbetrag: {empty_stats['total_amount']:,.2f} EUR")
        print(f"Durchschnittsbetrag: {empty_stats['avg_amount']:,.2f} EUR")
        print()
    
    # JSON speichern
    result_data = {
        "timestamp": "2024-11-20",
        "total_leads": total_leads,
        "total_amount": total_amount,
        "measure_codes": {code: {
            "count": stats["count"],
            "total_amount": stats["total_amount"],
            "avg_amount": stats["avg_amount"],
            "percentage": (stats["count"] / total_leads * 100) if total_leads > 0 else 0,
            "top_plz": dict(sorted(stats["plz_distribution"].items(), key=lambda x: x[1], reverse=True)[:10]),
            "sample_leads": stats["leads"]
        } for code, stats in measure_stats.items()}
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)
    
    print(f"Detaillierte Analyse gespeichert in: {output_file}")
    print()
    print("🎯 NÄCHSTER SCHRITT:")
    print("   Mit diesen Measure Codes können wir nun die")
    print("   Flächenprämien-Codes identifizieren und")
    print("   nur diese für die Lead-Bewertung verwenden!")

if __name__ == "__main__":
    analyze_measure_codes()

