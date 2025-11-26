#!/usr/bin/env python3
"""
Korrigierte Ostfriesland-Suche mit richtigen GAP-Betraegen
"""

import csv
import json
from datetime import datetime

def find_ostfriesland_corrected():
    csv_path = "data/gap/impdata2024.csv"
    output_file = "ostfriesland_corrected_26400-26999.json"
    
    print("KORRIGIERTE OSTFRIESLAND-ANALYSE (PLZ 26400-26999)")
    print("=" * 60)
    print("Mit korrekten GAP-Betraegen!")
    print()
    
    # Korrekte Header-Namen (aus Debug gefunden)
    correct_amount_header = "EU-Betrag (EGFL und ELER) und kofinanzierter Betrag insgesamt fuer diesen Beguenstigten*"
    correct_name_header = "Name des Beguenstigten/Rechtstraegers/Verdands"
    
    # Ergebnis-Container
    leads_found = []
    plz_stats = {}
    total_scanned = 0
    total_gap_amount = 0.0
    
    print("Starte korrigierte CSV-Analyse...")
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            headers = reader.fieldnames
            print(f"CSV-Header: {len(headers)} Spalten")
            
            # Pruefe ob korrekte Header vorhanden
            if correct_amount_header not in headers:
                print("WARNUNG: Suche nach alternativem Betrag-Header...")
                for header in headers:
                    if 'EU-Betrag' in header and 'EGFL' in header and 'ELER' in header:
                        correct_amount_header = header
                        print(f"Alternativer Header gefunden: {header}")
                        break
            
            if correct_name_header not in headers:
                print("WARNUNG: Suche nach alternativem Name-Header...")
                for header in headers:
                    if 'beguenstigten' in header.lower() and 'rechtstraegers' in header.lower():
                        correct_name_header = header
                        print(f"Alternativer Name-Header: {header}")
                        break
            
            print(f"Verwende Betrag-Header: {correct_amount_header}")
            print(f"Verwende Name-Header: {correct_name_header}")
            print()
            print("Scanne nach PLZ 26400-26999 mit korrekten Betraegen...")
            print("-" * 60)
            
            for row_num, row in enumerate(reader, 1):
                total_scanned = row_num
                
                plz = row.get('PLZ', '').strip()
                
                # Pruefe PLZ-Bereich 26400-26999
                if plz and len(plz) >= 5:
                    try:
                        plz_num = int(plz)
                        if 26400 <= plz_num <= 26999:
                            # Lead gefunden!
                            name = row.get(correct_name_header, '').strip()
                            city = row.get('Gemeinde', '').strip()
                            
                            # GAP-Betrag mit korrektem Header
                            gap_amount = 0.0
                            amount_field = row.get(correct_amount_header, '').strip()
                            if amount_field:
                                try:
                                    # Komma durch Punkt ersetzen fuer float conversion
                                    gap_amount = float(amount_field.replace(',', '.'))
                                    total_gap_amount += gap_amount
                                except ValueError:
                                    # Falls Conversion fehlschlaegt, 0 verwenden
                                    pass
                            
                            # Lead-Daten sammeln
                            lead = {
                                "row": row_num,
                                "plz": plz,
                                "name": name[:50],  # Kuerzen fuer Output
                                "city": city,
                                "gap_amount": gap_amount,
                                "measure_code": row.get('Code der Massnahme/der Interventionskategorie/des Sektors gemaess Anhang IX ', '').strip()
                            }
                            
                            leads_found.append(lead)
                            
                            # PLZ-Statistik
                            if plz not in plz_stats:
                                plz_stats[plz] = {"count": 0, "total_amount": 0.0, "cities": set(), "top_lead": None}
                            
                            plz_stats[plz]["count"] += 1
                            plz_stats[plz]["total_amount"] += gap_amount
                            if city:
                                plz_stats[plz]["cities"].add(city)
                            
                            # Top Lead pro PLZ tracken
                            if plz_stats[plz]["top_lead"] is None or gap_amount > plz_stats[plz]["top_lead"]["gap_amount"]:
                                plz_stats[plz]["top_lead"] = lead.copy()
                            
                            # Erste Treffer mit Betraegen ausgeben
                            if len(leads_found) <= 15:
                                print(f"LEAD #{len(leads_found)}: PLZ {plz} - {name[:30]}... | {city} | {gap_amount:,.2f} EUR")
                    
                    except ValueError:
                        continue  # PLZ nicht numerisch
                
                # Progress
                if row_num % 300000 == 0:
                    print(f"Zeile {row_num:,}: {len(leads_found)} Leads | {total_gap_amount:,.2f} EUR")
    
    except Exception as e:
        print(f"FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Finale Ergebnisse
    print()
    print("FINALE KORRIGIERTE ANALYSE")
    print("=" * 60)
    print(f"Gescannte Zeilen: {total_scanned:,}")
    print(f"Gefundene Leads: {len(leads_found):,}")
    print(f"Verschiedene PLZ: {len(plz_stats)}")
    print(f"GESAMT GAP-BETRAG: {total_gap_amount:,.2f} EUR")
    print()
    
    if leads_found:
        print("TOP OSTFRIESLAND-PLZS NACH GAP-BETRAG:")
        print("-" * 50)
        
        # Nach Gesamtbetrag pro PLZ sortieren
        sorted_plz_by_amount = sorted(plz_stats.items(), 
                                    key=lambda x: x[1]["total_amount"], reverse=True)
        
        for i, (plz, stats) in enumerate(sorted_plz_by_amount[:20], 1):  # Top 20
            cities = list(stats["cities"])[:3]
            cities_str = ", ".join(cities)
            if len(stats["cities"]) > 3:
                cities_str += f" (+{len(stats['cities'])-3})"
            
            print(f"{i:2d}. PLZ {plz}: {stats['count']:3d} Leads | {stats['total_amount']:10,.0f} EUR")
            print(f"    Orte: {cities_str}")
            
            if stats["top_lead"]:
                top = stats["top_lead"]
                print(f"    Top: {top['name'][:35]}... ({top['gap_amount']:,.0f} EUR)")
            print()
        
        # Top 10 Einzelne Leads
        print("TOP 10 EINZELNE LEADS:")
        print("-" * 30)
        top_leads = sorted(leads_found, key=lambda x: x["gap_amount"], reverse=True)[:10]
        
        for i, lead in enumerate(top_leads, 1):
            print(f"{i:2d}. {lead['name'][:40]}... | PLZ {lead['plz']} | {lead['gap_amount']:,.0f} EUR")
        
        # Daten speichern
        result_data = {
            "timestamp": datetime.now().isoformat(),
            "total_leads": len(leads_found),
            "total_plz": len(plz_stats),
            "total_gap_amount": total_gap_amount,
            "average_amount_per_lead": total_gap_amount / len(leads_found) if leads_found else 0,
            "plz_stats": {plz: {
                "count": stats["count"],
                "total_amount": stats["total_amount"],
                "average_amount": stats["total_amount"] / stats["count"] if stats["count"] > 0 else 0,
                "cities": list(stats["cities"]),
                "top_lead": stats["top_lead"]
            } for plz, stats in plz_stats.items()},
            "top_leads": top_leads[:50]  # Top 50 Leads
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        print()
        print(f"Ergebnisse gespeichert in: {output_file}")
        print()
        print("ERFOLG! Ostfriesland-Daten mit korrekten GAP-Betraegen gefunden!")
        print(f"Durchschnitt pro Lead: {total_gap_amount / len(leads_found):,.2f} EUR")
        
    else:
        print("Keine Leads gefunden.")

if __name__ == "__main__":
    find_ostfriesland_corrected()

