#!/usr/bin/env python3
"""
🔍 SCHNELLE SUCHE NACH ALLEN PLZ 26xxx in GAP-CSV
"""

import csv
import re

def find_all_26xxx():
    csv_path = "data/gap/impdata2024.csv"
    
    print("🔍 SUCHE ALLE PLZ 26xxx in GAP-CSV")
    print("="*50)
    
    results = {}  # PLZ -> [Liste von Einträgen]
    total_rows = 0
    found_count = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            for row_num, row in enumerate(reader, 1):
                total_rows = row_num
                
                plz = row.get('PLZ', '').strip()
                
                # Suche nach PLZ 26xxx
                if plz.startswith('26'):
                    found_count += 1
                    
                    if plz not in results:
                        results[plz] = []
                    
                    # Maximal 3 Beispiele pro PLZ speichern
                    if len(results[plz]) < 3:
                        name = row.get('Name des Begünstigten/Rechtsträgers/Verdands', '').strip()
                        city = row.get('Gemeinde', '').strip()
                        
                        results[plz].append({
                            'row': row_num,
                            'name': name[:40],
                            'city': city
                        })
                    
                    # Sofortige Ausgabe für neue PLZ
                    if len(results[plz]) == 1:
                        print(f"🎯 PLZ {plz} gefunden! Zeile {row_num} | {city}")
                
                # Progress alle 250.000 Zeilen
                if row_num % 250000 == 0:
                    print(f"📊 Zeile {row_num:,}: {len(results)} verschiedene PLZ 26xxx")
    
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return
    
    # Ergebnisse ausgeben
    print()
    print("📋 FINALE ERGEBNISSE:")
    print("="*50)
    print(f"📊 Zeilen gescannt: {total_rows:,}")
    print(f"🎯 Treffer insgesamt: {found_count}")
    print(f"📍 Verschiedene PLZ 26xxx: {len(results)}")
    
    if results:
        print()
        print("🏘️ ALLE GEFUNDENEN PLZ 26xxx:")
        for plz in sorted(results.keys()):
            entries = results[plz]
            print(f"\n📍 PLZ {plz}: {len(entries)}+ Landwirte")
            for entry in entries:
                print(f"   Zeile {entry['row']}: {entry['name']} | {entry['city']}")
        
        # Ostfriesische Orte hervorheben
        ostfriesische_orte = ['dornum', 'wittmund', 'emden', 'aurich', 'norden', 'leer', 'moormerland', 'ihlow', 'krummhörn']
        print()
        print("🌊 OSTFRIESISCHE TREFFER:")
        for plz, entries in results.items():
            for entry in entries:
                city_lower = entry['city'].lower()
                for ort in ostfriesische_orte:
                    if ort in city_lower:
                        print(f"   ✅ PLZ {plz} {entry['city']} - OSTFRIESLAND!")
                        break
    else:
        print("\n❌ KEINE PLZ 26xxx GEFUNDEN!")

if __name__ == "__main__":
    find_all_26xxx()

