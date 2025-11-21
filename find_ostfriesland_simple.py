#!/usr/bin/env python3
"""
Vollstaendige Ostfriesland-Suche PLZ 26400-26999
Findet ALLE potentiellen Leads im gewuenschten Ostfriesland-Bereich
"""

import csv
import json
from datetime import datetime

def find_ostfriesland_complete():
    csv_path = "data/gap/impdata2024.csv"
    output_file = "ostfriesland_leads_26400-26999.json"
    
    print("VOLLSTAENDIGE OSTFRIESLAND-LEAD-ANALYSE")
    print("=" * 60)
    print("PLZ-Bereich: 26400 - 26999")
    print("Zielregion: Gesamtes Ostfriesland")
    print()
    
    # Ergebnis-Container
    leads_found = []
    plz_stats = {}
    total_scanned = 0
    total_gap_amount = 0.0
    
    print("Starte CSV-Scan...")
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            # Header pruefen
            headers = reader.fieldnames
            print(f"CSV-Header gefunden: {len(headers)} Spalten")
            
            # Korrekte Name-Header finden (mit TYPO)
            name_header = None
            for header in headers:
                if 'beguestigten' in header.lower() and 'rechtstraegers' in header.lower():
                    name_header = header
                    break
            
            if not name_header:
                name_header = 'Name des Beguenstigten/Rechtstraegers/Verdands'  # Fallback
            
            print(f"Name-Header: {name_header}")
            print()
            print("Scanne nach PLZ 26400-26999...")
            print("-" * 40)
            
            for row_num, row in enumerate(reader, 1):
                total_scanned = row_num
                
                plz = row.get('PLZ', '').strip()
                
                # Pruefe PLZ-Bereich 26400-26999
                if plz and len(plz) >= 5:
                    try:
                        plz_num = int(plz)
                        if 26400 <= plz_num <= 26999:
                            # Lead gefunden!
                            name = row.get(name_header, '').strip()
                            city = row.get('Gemeinde', '').strip()
                            
                            # GAP-Betrag extrahieren
                            gap_amount = 0.0
                            amount_field = row.get('EU-Betrag (EGFL und ELER) und kofinanzierter Betrag insgesamt fuer diesen Beguenstigten*', '').strip()
                            if amount_field:
                                try:
                                    gap_amount = float(amount_field.replace(',', '.'))
                                    total_gap_amount += gap_amount
                                except:
                                    pass
                            
                            # Lead-Daten sammeln
                            lead = {
                                "row": row_num,
                                "plz": plz,
                                "name": name[:60],  # Begrenzen fuer Ausgabe
                                "city": city,
                                "gap_amount": gap_amount
                            }
                            
                            leads_found.append(lead)
                            
                            # PLZ-Statistik
                            if plz not in plz_stats:
                                plz_stats[plz] = {"count": 0, "total_amount": 0.0, "cities": set()}
                            
                            plz_stats[plz]["count"] += 1
                            plz_stats[plz]["total_amount"] += gap_amount
                            if city:
                                plz_stats[plz]["cities"].add(city)
                            
                            # Erste Treffer ausgeben
                            if len(leads_found) <= 10:
                                print(f"LEAD #{len(leads_found)}: PLZ {plz} - {name[:40]}... | {city} | {gap_amount:.0f} EUR")
                    
                    except ValueError:
                        continue  # PLZ nicht numerisch
                
                # Progress
                if row_num % 200000 == 0:
                    print(f"Zeile {row_num:,}: {len(leads_found)} Leads gefunden")
    
    except Exception as e:
        print(f"FEHLER beim CSV-Lesen: {e}")
        return
    
    # Ergebnisse ausgeben
    print()
    print("FINALE OSTFRIESLAND-ANALYSE")
    print("=" * 60)
    print(f"Gescannte Zeilen: {total_scanned:,}")
    print(f"Gefundene Leads: {len(leads_found):,}")
    print(f"Verschiedene PLZ: {len(plz_stats)}")
    print(f"Gesamt GAP-Betrag: {total_gap_amount:,.2f} EUR")
    print()
    
    if leads_found:
        print("TOP PLZ-BEREICHE IN OSTFRIESLAND:")
        print("-" * 40)
        
        # Nach Anzahl Leads sortieren
        sorted_plz = sorted(plz_stats.items(), key=lambda x: x[1]["count"], reverse=True)
        
        for plz, stats in sorted_plz[:15]:  # Top 15 PLZ
            cities = list(stats["cities"])[:3]  # Erste 3 Staedte
            cities_str = ", ".join(cities)
            if len(stats["cities"]) > 3:
                cities_str += f" (+{len(stats['cities'])-3} weitere)"
            
            print(f"PLZ {plz}: {stats['count']} Leads | {stats['total_amount']:,.0f} EUR")
            print(f"  Orte: {cities_str}")
            
            # Beispiel-Lead fuer diese PLZ
            example_leads = [l for l in leads_found if l["plz"] == plz]
            if example_leads:
                example = max(example_leads, key=lambda x: x["gap_amount"])
                print(f"  Top Lead: {example['name']} ({example['gap_amount']:,.0f} EUR)")
            print()
        
        # Daten in JSON speichern
        result_data = {
            "timestamp": datetime.now().isoformat(),
            "total_leads": len(leads_found),
            "total_plz": len(plz_stats),
            "total_gap_amount": total_gap_amount,
            "plz_stats": {plz: {
                "count": stats["count"],
                "total_amount": stats["total_amount"],
                "cities": list(stats["cities"])
            } for plz, stats in plz_stats.items()},
            "sample_leads": leads_found[:20]  # Erste 20 als Beispiel
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        print(f"Vollstaendige Ergebnisse gespeichert in: {output_file}")
        print()
        print("HANDLUNGSEMPFEHLUNG:")
        print("1. Diese PLZ-Bereiche in Lead Explorer eingeben")
        print("2. Pipeline mit korrigierten Mappings neu starten")
        print("3. Ihre Ostfriesland-Leads sollten verfuegbar sein!")
        
    else:
        print("KEINE LEADS IM BEREICH PLZ 26400-26999 GEFUNDEN!")
        print()
        print("Moegliche Ursachen:")
        print("- PLZ-Bereich enthaelt keine GAP-Empfaenger")
        print("- Daten unter anderen PLZ-Bereichen gespeichert")
        print("- Header-Mapping-Probleme")

if __name__ == "__main__":
    find_ostfriesland_complete()

