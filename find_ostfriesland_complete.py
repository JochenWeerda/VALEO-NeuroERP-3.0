***REMOVED***!/usr/bin/env python3
"""
🔍 VOLLSTÄNDIGE OSTFRIESLAND-SUCHE PLZ 26400-26999
Findet ALLE potentiellen Leads im gewünschten Ostfriesland-Bereich
"""

import csv
import json
from datetime import datetime

def find_ostfriesland_complete():
    csv_path = "data/gap/impdata2024.csv"
    output_file = "ostfriesland_leads_26400-26999.json"
    
    print("🏘️ VOLLSTÄNDIGE OSTFRIESLAND-LEAD-ANALYSE")
    print("=" * 60)
    print("🎯 PLZ-Bereich: 26400 - 26999")
    print("📍 Zielregion: Gesamtes Ostfriesland")
    print()
    
    results = {
        "search_config": {
            "plz_range": "26400-26999",
            "target_region": "Ostfriesland",
            "timestamp": datetime.now().isoformat(),
            "csv_file": csv_path
        },
        "statistics": {
            "total_rows_scanned": 0,
            "leads_found": 0,
            "unique_plz_found": 0,
            "total_gap_amount": 0.0
        },
        "leads_by_plz": {},
        "all_leads": [],
        "plz_summary": {}
    }
    
    print("🔍 Starte CSV-Scan...")
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            ***REMOVED*** Header validieren
            headers = reader.fieldnames
            required_headers = ['PLZ', 'Name des Begünstigten/Rechtsträgers/Verdands', 'Gemeinde']
            
            print(f"📊 CSV-Header gefunden: {len(headers)} Spalten")
            
            missing_headers = [h for h in required_headers if h not in headers]
            if missing_headers:
                print(f"⚠️ Fehlende Header: {missing_headers}")
                ***REMOVED*** Versuche alternativen Header-Namen
                alt_name_header = None
                for header in headers:
                    if 'begünstigten' in header.lower() and 'rechtsträgers' in header.lower():
                        alt_name_header = header
                        break
                
                if alt_name_header:
                    print(f"✅ Alternativer Name-Header gefunden: {alt_name_header}")
                    name_header = alt_name_header
                else:
                    print("❌ Kein Name-Header gefunden!")
                    return
            else:
                name_header = 'Name des Begünstigten/Rechtsträgers/Verdands'
            
            print()
            print("🔍 Scanne nach PLZ 26400-26999...")
            print("-" * 40)
            
            for row_num, row in enumerate(reader, 1):
                results["statistics"]["total_rows_scanned"] = row_num
                
                plz = row.get('PLZ', '').strip()
                
                ***REMOVED*** Prüfe PLZ-Bereich 26400-26999
                if plz and len(plz) >= 5:
                    try:
                        plz_num = int(plz)
                        if 26400 <= plz_num <= 26999:
                            results["statistics"]["leads_found"] += 1
                            
                            ***REMOVED*** Extrahiere alle relevanten Daten
                            name = row.get(name_header, '').strip()
                            city = row.get('Gemeinde', '').strip()
                            
                            ***REMOVED*** GAP-Betrag extrahieren
                            gap_amount = 0.0
                            amount_field = row.get('EU-Betrag (EGFL und ELER) und kofinanzierter Betrag insgesamt für diesen Begünstigten*', '').strip()
                            if amount_field:
                                try:
                                    gap_amount = float(amount_field.replace(',', '.'))
                                    results["statistics"]["total_gap_amount"] += gap_amount
                                except:
                                    pass
                            
                            ***REMOVED*** Lead-Objekt erstellen
                            lead = {
                                "row_number": row_num,
                                "plz": plz,
                                "name": name,
                                "city": city,
                                "gap_amount_eur": gap_amount,
                                "measure_code": row.get('Code der Maßnahme/der Interventionskategorie/des Sektors gemäß Anhang IX', '').strip(),
                                "year": row.get('Haushaltsjahr', '').strip()
                            }
                            
                            ***REMOVED*** Nach PLZ gruppieren
                            if plz not in results["leads_by_plz"]:
                                results["leads_by_plz"][plz] = []
                                results["statistics"]["unique_plz_found"] += 1
                            
                            results["leads_by_plz"][plz].append(lead)
                            results["all_leads"].append(lead)
                            
                            ***REMOVED*** Erste Treffer sofort ausgeben
                            if results["statistics"]["leads_found"] <= 10:
                                print(f"🎯 LEAD ***REMOVED***{results['statistics']['leads_found']}: PLZ {plz} - {name[:40]}... | {city} | {gap_amount:,.2f} EUR")
                    
                    except ValueError:
                        continue  ***REMOVED*** PLZ ist nicht numerisch
                
                ***REMOVED*** Progress alle 200.000 Zeilen
                if row_num % 200000 == 0:
                    print(f"📊 Zeile {row_num:,}: {results['statistics']['leads_found']} Leads gefunden")
    
    except Exception as e:
        print(f"❌ Fehler beim CSV-Lesen: {e}")
        import traceback
        traceback.print_exc()
        return
    
    ***REMOVED*** PLZ-Zusammenfassung erstellen
    for plz, leads in results["leads_by_plz"].items():
        total_amount = sum(lead["gap_amount_eur"] for lead in leads)
        unique_names = len(set(lead["name"] for lead in leads))
        cities = set(lead["city"] for lead in leads if lead["city"])
        
        results["plz_summary"][plz] = {
            "lead_count": len(leads),
            "unique_farmers": unique_names,
            "total_gap_amount": total_amount,
            "cities": list(cities),
            "top_leads": sorted(leads, key=lambda x: x["gap_amount_eur"], reverse=True)[:3]
        }
    
    ***REMOVED*** Ergebnisse in Datei speichern
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    ***REMOVED*** Finale Ausgabe
    print()
    print("📋 FINALE OSTFRIESLAND-ANALYSE")
    print("=" * 60)
    print(f"📊 Gescannte Zeilen: {results['statistics']['total_rows_scanned']:,}")
    print(f"🎯 Gefundene Leads: {results['statistics']['leads_found']:,}")
    print(f"📍 Verschiedene PLZ: {results['statistics']['unique_plz_found']}")
    print(f"💰 Gesamt GAP-Betrag: {results['statistics']['total_gap_amount']:,.2f} EUR")
    print()
    
    if results["statistics"]["leads_found"] > 0:
        print("🏘️ TOP PLZ-BEREICHE IN OSTFRIESLAND:")
        sorted_plz = sorted(results["plz_summary"].items(), 
                           key=lambda x: x[1]["lead_count"], reverse=True)
        
        for plz, summary in sorted_plz[:10]:  ***REMOVED*** Top 10 PLZ
            cities_str = ", ".join(summary["cities"][:3])
            if len(summary["cities"]) > 3:
                cities_str += f" (+{len(summary['cities'])-3} weitere)"
            
            print(f"📍 PLZ {plz}: {summary['lead_count']} Leads | {summary['total_gap_amount']:,.0f} EUR")
            print(f"   🏘️ Orte: {cities_str}")
            
            ***REMOVED*** Top Lead pro PLZ zeigen
            if summary["top_leads"]:
                top_lead = summary["top_leads"][0]
                print(f"   🌟 Top Lead: {top_lead['name'][:30]}... ({top_lead['gap_amount_eur']:,.0f} EUR)")
            print()
        
        print(f"💾 Vollständige Ergebnisse gespeichert in: {output_file}")
        print()
        print("🎯 HANDLUNGSEMPFEHLUNG:")
        print("   1. Diese PLZ-Bereiche in Lead Explorer eingeben")
        print("   2. Pipeline mit korrigierten Header-Mappings neu starten")
        print("   3. Ihre Ostfriesland-Leads sollten verfügbar sein!")
        
    else:
        print("❌ KEINE LEADS IM BEREICH PLZ 26400-26999 GEFUNDEN!")
        print("💡 Mögliche Ursachen:")
        print("   - PLZ-Bereich zu spezifisch")
        print("   - Daten unter anderen PLZ-Bereichen")
        print("   - CSV-Header-Probleme")

if __name__ == "__main__":
    find_ostfriesland_complete()

