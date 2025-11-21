#!/usr/bin/env python3
"""
🔍 DIREKTE KRUMMHÖRN-ANALYSE mit Datei-Output
Analysiert GAP-CSV für PLZ 26736 und Spaltenverschiebungs-Probleme
"""

import csv
import json
from datetime import datetime

def analyze_krummhoern():
    csv_path = "data/gap/impdata2024.csv"
    output_path = "krummhoern_analysis_results.json"
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "csv_file": csv_path,
        "analysis": {
            "total_rows_scanned": 0,
            "headers_found": [],
            "column_mapping": {
                "plz_column": None,
                "name_column": None,
                "city_column": None,
                "typo_detected": False
            },
            "plz_distribution": {},
            "plz_26xxx_found": {},
            "krummhoern_matches": [],
            "cities_in_26xxx": [],
            "sample_data": []
        },
        "conclusions": []
    }
    
    try:
        print("🔍 Starte Krummhörn-Analyse...")
        
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            # Header-Analyse
            headers = reader.fieldnames or []
            results["analysis"]["headers_found"] = headers
            
            # Spalten-Mapping
            for header in headers:
                if 'PLZ' in header.upper():
                    results["analysis"]["column_mapping"]["plz_column"] = header
                elif 'BEGÜNSTIGTEN' in header.upper() and 'RECHTSTRÄGERS' in header.upper():
                    results["analysis"]["column_mapping"]["name_column"] = header
                    if 'VERDANDS' in header:
                        results["analysis"]["column_mapping"]["typo_detected"] = True
                elif 'GEMEINDE' in header.upper():
                    results["analysis"]["column_mapping"]["city_column"] = header
            
            # Daten-Scan
            for row_num, row in enumerate(reader, 1):
                results["analysis"]["total_rows_scanned"] = row_num
                
                # Maximal 500.000 Zeilen für Performance
                if row_num > 500000:
                    results["conclusions"].append("Scan bei 500.000 Zeilen gestoppt (Performance)")
                    break
                
                plz = row.get('PLZ', '').strip()
                name = row.get('Name des Begünstigten/Rechtsträgers/Verdands', '').strip()
                city = row.get('Gemeinde', '').strip()
                
                # Erste 10 Zeilen als Beispiel speichern
                if row_num <= 10:
                    results["analysis"]["sample_data"].append({
                        "row": row_num,
                        "plz": plz,
                        "name": name[:50],
                        "city": city
                    })
                
                # PLZ-Verteilung
                if plz:
                    prefix = plz[:2] if len(plz) >= 2 else plz
                    if prefix not in results["analysis"]["plz_distribution"]:
                        results["analysis"]["plz_distribution"][prefix] = 0
                    results["analysis"]["plz_distribution"][prefix] += 1
                
                # PLZ 26xxx sammeln
                if plz.startswith('26'):
                    if plz not in results["analysis"]["plz_26xxx_found"]:
                        results["analysis"]["plz_26xxx_found"][plz] = []
                    
                    if len(results["analysis"]["plz_26xxx_found"][plz]) < 3:
                        results["analysis"]["plz_26xxx_found"][plz].append({
                            "row": row_num,
                            "name": name[:40],
                            "city": city
                        })
                    
                    # Städte sammeln
                    if city and city not in results["analysis"]["cities_in_26xxx"]:
                        results["analysis"]["cities_in_26xxx"].append(city)
                
                # Krummhörn-Suche
                is_krummhoern_match = False
                match_reasons = []
                
                if plz == '26736':
                    is_krummhoern_match = True
                    match_reasons.append("PLZ 26736")
                
                if 'krumm' in name.lower():
                    is_krummhoern_match = True
                    match_reasons.append("Name enthält 'krumm'")
                
                if 'krumm' in city.lower():
                    is_krummhoern_match = True
                    match_reasons.append("Stadt enthält 'krumm'")
                
                if 'hörn' in name.lower() or 'hörn' in city.lower():
                    is_krummhoern_match = True
                    match_reasons.append("Enthält 'hörn'")
                
                if is_krummhoern_match and len(results["analysis"]["krummhoern_matches"]) < 20:
                    results["analysis"]["krummhoern_matches"].append({
                        "row": row_num,
                        "plz": plz,
                        "name": name[:50],
                        "city": city,
                        "reasons": match_reasons
                    })
        
        # Schlussfolgerungen
        if '26736' in results["analysis"]["plz_26xxx_found"]:
            results["conclusions"].append("✅ PLZ 26736 (Krummhörn) GEFUNDEN!")
            count = len(results["analysis"]["plz_26xxx_found"]['26736'])
            results["conclusions"].append(f"📊 {count}+ Landwirte in PLZ 26736")
        else:
            results["conclusions"].append("❌ PLZ 26736 (Krummhörn) NICHT gefunden")
        
        if results["analysis"]["column_mapping"]["typo_detected"]:
            results["conclusions"].append("⚠️ TYPO im Header erkannt: 'Verdands' statt 'Verbands'")
        
        if not results["analysis"]["column_mapping"]["plz_column"]:
            results["conclusions"].append("❌ PLZ-Spalte nicht erkannt - Spaltenverschiebung möglich")
        
        total_26xxx = len(results["analysis"]["plz_26xxx_found"])
        results["conclusions"].append(f"📍 {total_26xxx} verschiedene PLZ im 26xxx-Bereich gefunden")
        
    except Exception as e:
        results["error"] = str(e)
        results["conclusions"].append(f"❌ Fehler bei Analyse: {e}")
    
    # Ergebnisse in Datei schreiben
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Analyse abgeschlossen. Ergebnisse in: {output_path}")
    
    # Kurze Zusammenfassung ausgeben
    print(f"\n📊 KURZÜBERSICHT:")
    print(f"Zeilen gescannt: {results['analysis']['total_rows_scanned']:,}")
    print(f"PLZ 26xxx Bereiche: {len(results['analysis']['plz_26xxx_found'])}")
    print(f"Krummhörn-Treffer: {len(results['analysis']['krummhoern_matches'])}")
    print(f"Spalten-Mapping OK: {bool(results['analysis']['column_mapping']['plz_column'])}")
    
    return results

if __name__ == "__main__":
    analyze_krummhoern()

