#!/usr/bin/env python3
"""
🔍 OSTFRIESLAND-SUCHE in GAP-CSV
Suche nach Emden, Moormerland, Ihlow in der gesamten CSV
"""

import csv
import re

def search_ostfriesland():
    csv_path = "data/gap/impdata2024.csv"
    
    print("🔍 SUCHE NACH OSTFRIESLAND in GAP-CSV 2024")
    print("="*60)
    print("🎯 Suchbegriffe: Emden, Moormerland, Ihlow")
    print()
    
    search_terms = ['emden', 'moormerland', 'ihlow']
    results = []
    total_rows = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            # Header anzeigen
            headers = reader.fieldnames
            print(f"📊 CSV-Header ({len(headers)} Spalten):")
            for i, header in enumerate(headers[:10]):
                print(f"  {i+1:2d}. {header}")
            if len(headers) > 10:
                print(f"  ... und {len(headers)-10} weitere")
            print()
            
            print("🔍 Starte Volltext-Suche...")
            print("-" * 50)
            
            for row_num, row in enumerate(reader, 1):
                total_rows = row_num
                
                # Progress alle 100.000 Zeilen
                if row_num % 100000 == 0:
                    print(f"📊 Zeile {row_num:,}: {len(results)} Treffer gefunden")
                
                # Alle Spalten nach Suchbegriffen durchsuchen
                row_found = False
                found_terms = []
                row_data = {}
                
                for key, value in row.items():
                    if value:  # Nur nicht-leere Werte
                        value_lower = value.lower()
                        for term in search_terms:
                            if term in value_lower:
                                if not row_found:
                                    # Ersten Treffer in dieser Zeile - alle Daten sammeln
                                    row_data = {
                                        'row_number': row_num,
                                        'plz': row.get('PLZ', '').strip(),
                                        'name': row.get('Name des Begünstigten/Rechtsträgers/Verdands', '').strip(),
                                        'city': row.get('Gemeinde', '').strip(),
                                        'full_row': dict(row)  # Komplette Zeile für Analyse
                                    }
                                    row_found = True
                                
                                if term not in found_terms:
                                    found_terms.append(term)
                                    
                                # Sofort ausgeben für ersten Treffer
                                if len(results) == 0:
                                    print(f"🎯 ERSTER TREFFER GEFUNDEN!")
                                    print(f"   Zeile: {row_num}")
                                    print(f"   Suchbegriff: '{term}' in Spalte '{key}'")
                                    print(f"   Wert: '{value}'")
                                    print(f"   PLZ: '{row_data['plz']}'")
                                    print(f"   Name: '{row_data['name'][:60]}...'")
                                    print(f"   Stadt: '{row_data['city']}'")
                                    print()
                
                if row_found:
                    row_data['found_terms'] = found_terms
                    results.append(row_data)
                    
                    # Nach 10 Treffern Details ausgeben
                    if len(results) <= 10:
                        print(f"🏘️ TREFFER #{len(results)}:")
                        print(f"   Zeile {row_num}: PLZ {row_data['plz']}")
                        print(f"   Name: {row_data['name'][:50]}...")
                        print(f"   Stadt: {row_data['city']}")
                        print(f"   Gefunden: {', '.join(found_terms)}")
                        print()
                
                # Stopp nach erstem Treffer falls gewünscht
                if len(results) >= 1:
                    print("⏹️ STOPP nach erstem Treffer für Analyse")
                    break
    
    except Exception as e:
        print(f"❌ Fehler beim CSV-Lesen: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Ergebnisse zusammenfassen
    print()
    print("📋 ENDERGEBNIS:")
    print("="*60)
    print(f"📊 Zeilen gescannt: {total_rows:,}")
    print(f"🎯 Ostfriesland-Treffer: {len(results)}")
    
    if results:
        print()
        print("🏘️ GEFUNDENE OSTFRIESISCHE ORTE:")
        for i, result in enumerate(results[:5], 1):  # Erste 5 Treffer
            print(f"\n{i}. Zeile {result['row_number']}:")
            print(f"   PLZ: {result['plz']}")
            print(f"   Name: {result['name'][:60]}...")
            print(f"   Stadt: {result['city']}")
            print(f"   Suchbegriffe: {', '.join(result['found_terms'])}")
            
            # Vollständige Zeile für ersten Treffer
            if i == 1:
                print(f"\n📋 VOLLSTÄNDIGE ZEILEN-ANALYSE (Treffer #{i}):")
                print("-" * 40)
                for key, value in result['full_row'].items():
                    if value and value.strip():  # Nur nicht-leere Werte
                        print(f"   {key}: {value}")
        
        # PLZ-Auswertung
        found_plz = [r['plz'] for r in results if r['plz']]
        if found_plz:
            print(f"\n📍 GEFUNDENE PLZ-BEREICHE:")
            unique_plz = list(set(found_plz))
            for plz in sorted(unique_plz):
                print(f"   PLZ {plz}")
    else:
        print("\n❌ KEINE OSTFRIESISCHEN ORTE IN GAP-DATEN 2024 GEFUNDEN!")
        print("💡 Mögliche Ursachen:")
        print("   1. Ostfriesland hat wenige GAP-berechtigte Betriebe")
        print("   2. Andere Schreibweisen der Ortsnamen")
        print("   3. Daten unter Landkreis-Namen statt Ortsnamen")

if __name__ == "__main__":
    search_ostfriesland()

