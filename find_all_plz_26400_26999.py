#!/usr/bin/env python3
"""
🔍 VOLLSTÄNDIGE PLZ-ANALYSE 26400-26999 für Ostfriesland/Norddeutschland
Findet ALLE potentiellen Leads im erweiterten PLZ-Bereich
"""

import csv
import json
from datetime import datetime

def find_all_plz_26400_26999():
    csv_path = "data/gap/impdata2024.csv"
    output_path = "plz_26400_26999_analysis.json"
    
    print("🔍 VOLLSTÄNDIGE PLZ-ANALYSE 26400-26999")
    print("="*60)
    print("🎯 Zielbereich: Ostfriesland, Oldenburg, Umgebung")
    print()
    
    results = {
        "analysis_timestamp": datetime.now().isoformat(),
        "plz_range": "26400-26999",
        "target_region": "Ostfriesland und Umgebung",
        "csv_file": csv_path,
        "statistics": {
            "total_rows_scanned": 0,
            "target_plz_count": 0,
            "unique_plz_found": 0,
            "unique_cities": 0,
            "total_landwirte": 0
        },
        "plz_data": {},  # PLZ -> {city, count, examples, total_amount}
        "city_mapping": {},  # Stadt -> [PLZ-Liste]
        "landwirte_examples": [],  # Erste 20 Beispiele
        "regional_breakdown": {
            "264xx": {"count": 0, "cities": set()},
            "265xx": {"count": 0, "cities": set()},
            "266xx": {"count": 0, "cities": set()},
            "267xx": {"count": 0, "cities": set()},
            "268xx": {"count": 0, "cities": set()},
            "269xx": {"count": 0, "cities": set()}
        }
    }
    
    try:
        print("📊 Starte CSV-Analyse...")
        
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            # Header-Info
            headers = reader.fieldnames
            print(f"✅ CSV-Header: {len(headers)} Spalten")
            print("📍 Relevante Spalten gefunden:")
            print(f"   - PLZ: {'✅' if 'PLZ' in headers else '❌'}")
            print(f"   - Name: {'✅' if any('Begünstigten' in h for h in headers) else '❌'}")
            print(f"   - Stadt: {'✅' if 'Gemeinde' in headers else '❌'}")
            print()
            
            for row_num, row in enumerate(reader, 1):
                results["statistics"]["total_rows_scanned"] = row_num
                
                plz = row.get('PLZ', '').strip()
                name = row.get('Name des Begünstigten/Rechtsträgers/Verdands', '').strip()
                city = row.get('Gemeinde', '').strip()
                amount_str = row.get('EU-Betrag (EGFL und ELER) und kofinanzierter Betrag insgesamt für diesen Begünstigten*', '').strip()
                
                # PLZ-Bereich-Check: 26400-26999
                if plz and len(plz) == 5 and plz.isdigit():
                    plz_num = int(plz)
                    if 26400 <= plz_num <= 26999:
                        results["statistics"]["target_plz_count"] += 1
                        
                        # PLZ-Daten sammeln
                        if plz not in results["plz_data"]:
                            results["plz_data"][plz] = {
                                "city": city,
                                "count": 0,
                                "examples": [],
                                "total_amount_eur": 0.0
                            }
                            results["statistics"]["unique_plz_found"] += 1
                        
                        results["plz_data"][plz]["count"] += 1
                        
                        # Beispiele sammeln (max 3 pro PLZ)
                        if len(results["plz_data"][plz]["examples"]) < 3:
                            results["plz_data"][plz]["examples"].append({
                                "row": row_num,
                                "name": name[:50],
                                "city": city
                            })
                        
                        # Gesamtbeispiele (erste 20)
                        if len(results["landwirte_examples"]) < 20:
                            results["landwirte_examples"].append({
                                "row": row_num,
                                "plz": plz,
                                "name": name[:50],
                                "city": city,
                                "amount": amount_str[:20] if amount_str else "N/A"
                            })
                        
                        # Betrag verarbeiten
                        try:
                            if amount_str:
                                amount = float(amount_str.replace(',', '.'))
                                results["plz_data"][plz]["total_amount_eur"] += amount
                        except:
                            pass
                        
                        # Stadt-Mapping
                        if city:
                            if city not in results["city_mapping"]:
                                results["city_mapping"][city] = []
                            if plz not in results["city_mapping"][city]:
                                results["city_mapping"][city].append(plz)
                        
                        # Regionale Aufschlüsselung
                        prefix = plz[:3] + "xx"
                        if prefix in results["regional_breakdown"]:
                            results["regional_breakdown"][prefix]["count"] += 1
                            if city:
                                results["regional_breakdown"][prefix]["cities"].add(city)
                        
                        # Progress-Output
                        if results["statistics"]["target_plz_count"] == 1:
                            print(f"🎯 ERSTER TREFFER! PLZ {plz} | {city} | {name[:30]}...")
                        elif results["statistics"]["target_plz_count"] % 50 == 0:
                            print(f"📊 {results['statistics']['target_plz_count']} Treffer | PLZ: {results['statistics']['unique_plz_found']} | Aktuell: {plz}")
                
                # Progress alle 200.000 Zeilen
                if row_num % 200000 == 0:
                    print(f"📋 Zeile {row_num:,}: {results['statistics']['target_plz_count']} Treffer im Zielbereich")
                    
    except Exception as e:
        print(f"❌ Fehler: {e}")
        results["error"] = str(e)
    
    # Nachbearbeitung
    results["statistics"]["unique_cities"] = len(results["city_mapping"])
    results["statistics"]["total_landwirte"] = results["statistics"]["target_plz_count"]
    
    # Sets zu Listen konvertieren
    for prefix_data in results["regional_breakdown"].values():
        if "cities" in prefix_data:
            prefix_data["cities"] = list(prefix_data["cities"])
    
    # Ergebnisse in Datei speichern
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Detaillierte Ausgabe
    print()
    print("📋 FINALE ERGEBNISSE PLZ 26400-26999:")
    print("="*60)
    print(f"📊 Zeilen gescannt: {results['statistics']['total_rows_scanned']:,}")
    print(f"🎯 Landwirte im Zielbereich: {results['statistics']['total_landwirte']:,}")
    print(f"📍 Verschiedene PLZ: {results['statistics']['unique_plz_found']}")
    print(f"🏘️ Verschiedene Cities: {results['statistics']['unique_cities']}")
    
    if results["statistics"]["unique_plz_found"] > 0:
        print()
        print("📍 GEFUNDENE PLZ (Top 10):")
        sorted_plz = sorted(results["plz_data"].items(), key=lambda x: x[1]["count"], reverse=True)
        for i, (plz, data) in enumerate(sorted_plz[:10], 1):
            print(f"  {i:2d}. PLZ {plz}: {data['count']:3d} Landwirte | {data['city']}")
        
        print()
        print("🏘️ REGIONALE VERTEILUNG:")
        for prefix, data in results["regional_breakdown"].items():
            if data["count"] > 0:
                cities_str = ", ".join(list(data["cities"])[:3])
                if len(data["cities"]) > 3:
                    cities_str += f" (+{len(data['cities'])-3} weitere)"
                print(f"  {prefix}: {data['count']:3d} Landwirte | {cities_str}")
        
        print()
        print("👥 BEISPIEL-LANDWIRTE (erste 10):")
        for i, example in enumerate(results["landwirte_examples"][:10], 1):
            print(f"  {i:2d}. PLZ {example['plz']} | {example['name']} | {example['city']}")
        
        print()
        print("🏘️ STÄDTE IM ZIELGEBIET:")
        city_list = sorted(results["city_mapping"].keys())
        for i, city in enumerate(city_list[:15]):  # Erste 15 Städte
            plz_list = ", ".join(results["city_mapping"][city])
            print(f"  - {city} (PLZ: {plz_list})")
        if len(city_list) > 15:
            print(f"  ... und {len(city_list)-15} weitere Städte")
    
    else:
        print("\n❌ KEINE LANDWIRTE IM PLZ-BEREICH 26400-26999 GEFUNDEN!")
        print("💡 Mögliche Ursachen:")
        print("   - PLZ-Bereich nicht in GAP-Daten 2024")
        print("   - Andere regionale Zuordnung")
        print("   - Daten unter anderen PLZ-Bereichen")
    
    print(f"\n💾 Detaillierte Ergebnisse gespeichert: {output_path}")
    
    return results

if __name__ == "__main__":
    find_all_plz_26400_26999()
