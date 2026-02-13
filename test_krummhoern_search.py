#!/usr/bin/env python3
"""
🔍 KRUMMHÖRN CSV-SUCHE - Spaltenverschiebungs-Diagnose
Direkte Analyse der GAP-CSV ohne Backend-Abhängigkeit
"""

import csv
import os

def search_krummhoern_in_csv():
    csv_path = "data/gap/impdata2024.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV-Datei nicht gefunden: {csv_path}")
        return
    
    print(f"🔍 Analysiere CSV: {csv_path}")
    print("=" * 60)
    
    results = {
        "plz_26736_matches": [],
        "krummhoern_matches": [], 
        "plz_267xx_matches": [],
        "statistics": {
            "total_rows": 0,
            "plz_26736_count": 0,
            "krummhoern_count": 0,
            "plz_267xx_count": 0
        }
    }
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            # Header analysieren
            headers = reader.fieldnames
            print(f"📊 Gefundene Header ({len(headers)}):")
            for i, header in enumerate(headers[:10]):  # Erste 10
                print(f"  {i+1:2d}. {header}")
            if len(headers) > 10:
                print(f"  ... und {len(headers)-10} weitere")
            
            print()
            print("🎯 Relevante Header:")
            name_header = None
            plz_header = None
            city_header = None
            
            for header in headers:
                if 'begünstigten' in header.lower() and 'rechtsträgers' in header.lower():
                    name_header = header
                    print(f"  ✅ Name-Header: {header}")
                elif header.strip() == 'PLZ':
                    plz_header = header
                    print(f"  ✅ PLZ-Header: {header}")
                elif 'gemeinde' in header.lower():
                    city_header = header
                    print(f"  ✅ Stadt-Header: {header}")
            
            print()
            print("🔍 Suche nach Krummhörn-Daten...")
            print("-" * 40)
            
            # Daten durchsuchen
            for row_num, row in enumerate(reader, 1):
                results["statistics"]["total_rows"] = row_num
                
                # Maximal 50.000 Zeilen für schnelle Analyse
                if row_num > 50000:
                    print(f"⏹️  Scan gestoppt bei Zeile {row_num} (Performance)")
                    break
                    
                plz = row.get('PLZ', '').strip()
                name = row.get('Name des Begünstigten/Rechtsträgers/Verdands', '').strip()
                city = row.get('Gemeinde', '').strip()
                
                # Suche nach PLZ 26736
                if plz == '26736':
                    results["statistics"]["plz_26736_count"] += 1
                    if len(results["plz_26736_matches"]) < 5:
                        results["plz_26736_matches"].append({
                            "row": row_num,
                            "name": name[:50],
                            "plz": plz,
                            "city": city
                        })
                        print(f"🎯 PLZ 26736 gefunden! Zeile {row_num}: {name[:30]}... | {city}")
                
                # Suche nach Krummhörn-Text
                if ('krumm' in name.lower() or 'krumm' in city.lower() or 
                    'hörn' in name.lower() or 'hörn' in city.lower()):
                    results["statistics"]["krummhoern_count"] += 1
                    if len(results["krummhoern_matches"]) < 5:
                        results["krummhoern_matches"].append({
                            "row": row_num,
                            "name": name[:50],
                            "plz": plz,
                            "city": city
                        })
                        print(f"🏘️  Krummhörn-Text gefunden! Zeile {row_num}: {name[:30]}... | PLZ {plz} | {city}")
                
                # Suche nach PLZ 267xx
                if plz.startswith('267'):
                    results["statistics"]["plz_267xx_count"] += 1
                    if len(results["plz_267xx_matches"]) < 10:
                        results["plz_267xx_matches"].append({
                            "row": row_num,
                            "name": name[:30],
                            "plz": plz,
                            "city": city
                        })
                
                # Progress-Update
                if row_num % 10000 == 0:
                    print(f"📊 Zeile {row_num}: PLZ 26736={results['statistics']['plz_26736_count']}, "
                          f"Krummhörn={results['statistics']['krummhoern_count']}, "
                          f"267xx={results['statistics']['plz_267xx_count']}")
    
    except Exception as e:
        print(f"❌ Fehler beim CSV-Lesen: {e}")
        return
    
    # Ergebnisse zusammenfassen
    print()
    print("📋 ANALYSE-ERGEBNISSE:")
    print("=" * 60)
    print(f"📊 Zeilen gescannt: {results['statistics']['total_rows']:,}")
    print(f"🎯 PLZ 26736 Treffer: {results['statistics']['plz_26736_count']}")
    print(f"🏘️  Krummhörn-Text Treffer: {results['statistics']['krummhoern_count']}")
    print(f"📍 PLZ 267xx Treffer: {results['statistics']['plz_267xx_count']}")
    
    print()
    print("🏘️  PLZ-267xx Beispiele:")
    for match in results["plz_267xx_matches"][:5]:
        print(f"  PLZ {match['plz']}: {match['name']} | {match['city']}")
    
    if results['statistics']['plz_26736_count'] == 0 and results['statistics']['krummhoern_count'] == 0:
        print()
        print("⚠️  RESULTAT: Keine PLZ 26736 oder Krummhörn-Daten gefunden!")
        print("🔍 MÖGLICHE URSACHEN:")
        print("   1. PLZ 26736 ist nicht in den GAP-Daten 2024 enthalten")
        print("   2. Krummhörn-Landwirte haben andere PLZ oder sind nicht GAP-berechtigt")
        print("   3. Daten sind unter anderem Namen/PLZ gespeichert")
    
    return results

if __name__ == "__main__":
    search_krummhoern_in_csv()


