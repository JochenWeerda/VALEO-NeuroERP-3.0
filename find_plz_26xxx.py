#!/usr/bin/env python3
"""
Suche nach PLZ 26xxx in der GAP-CSV (insbesondere 26736 Krummhörn)
"""

import csv
import re

def find_plz_26xxx():
    csv_path = "data/gap/impdata2024.csv"
    
    print("🔍 VOLLSTÄNDIGE PLZ-26xxx-ANALYSE (GAP-Daten 2024)")
    print("="*65)
    
    # Ergebnis-Container
    plz_26_found = {}
    krummhoern_found = []
    total_rows = 0
    
    # Erweiterte Statistiken
    stats = {
        'plz_prefixes': {},  # PLZ-Präfixe (erste 2 Ziffern)
        'cities_with_26xxx': set(),
        'names_with_krumm': [],
        'column_debug': {
            'plz_column_found': False,
            'name_column_found': False,
            'city_column_found': False,
            'sample_headers': []
        }
    }
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            # Header-Analyse für Spaltenverschiebungs-Diagnose
            headers = reader.fieldnames
            if headers:
                stats['column_debug']['sample_headers'] = headers[:15]  # Erste 15 Header
                
                # Suche nach korrekten Spalten
                for header in headers:
                    if 'PLZ' in header.upper():
                        stats['column_debug']['plz_column_found'] = True
                        print(f"✅ PLZ-Spalte gefunden: '{header}'")
                    elif 'BEGÜNSTIGTEN' in header.upper() and 'RECHTSTRÄGERS' in header.upper():
                        stats['column_debug']['name_column_found'] = True  
                        print(f"✅ Name-Spalte gefunden: '{header}'")
                        print(f"   ⚠️ TYPO-Check: {'VERDANDS' if 'VERDANDS' in header else 'VERBANDS'} in Header")
                    elif 'GEMEINDE' in header.upper():
                        stats['column_debug']['city_column_found'] = True
                        print(f"✅ Stadt-Spalte gefunden: '{header}'")
            
            print(f"\n📊 CSV-Header analysiert: {len(headers)} Spalten")
            print("🔍 Starte Daten-Scanning...")
            
            for row_num, row in enumerate(reader, 1):
                total_rows = row_num
                
                # Spalten-Extraktion mit TYPO-Berücksichtigung
                plz = row.get('PLZ', '').strip()
                name = row.get('Name des Begünstigten/Rechtsträgers/Verdands', '').strip()  # MIT TYPO
                city = row.get('Gemeinde', '').strip()
                
                # PLZ-Präfix-Statistik (erste 2 Ziffern)
                if plz and len(plz) >= 2:
                    prefix = plz[:2]
                    if prefix not in stats['plz_prefixes']:
                        stats['plz_prefixes'][prefix] = 0
                    stats['plz_prefixes'][prefix] += 1
                
                # Suche nach PLZ 26xxx
                if plz.startswith('26'):
                    if plz not in plz_26_found:
                        plz_26_found[plz] = []
                    
                    if len(plz_26_found[plz]) < 5:  # Erste 5 Beispiele pro PLZ
                        plz_26_found[plz].append({
                            'name': name[:40],
                            'city': city,
                            'row': row_num
                        })
                    
                    # Städte sammeln
                    if city:
                        stats['cities_with_26xxx'].add(city)
                
                # Erweiterte Krummhörn-Suche
                krumm_match = False
                match_reasons = []
                
                if plz == '26736':
                    krumm_match = True
                    match_reasons.append('PLZ 26736')
                
                if 'krumm' in name.lower():
                    krumm_match = True
                    match_reasons.append('Name enthält "krumm"')
                    stats['names_with_krumm'].append(name[:40])
                
                if 'krumm' in city.lower():
                    krumm_match = True
                    match_reasons.append('Stadt enthält "krumm"')
                
                if 'hörn' in name.lower() or 'hörn' in city.lower():
                    krumm_match = True
                    match_reasons.append('Enthält "hörn"')
                
                if krumm_match:
                    krummhoern_found.append({
                        'row': row_num,
                        'plz': plz,
                        'name': name[:50],
                        'city': city,
                        'match_reasons': match_reasons
                    })
                
                # Progress mit erweiterten Infos
                if row_num % 200000 == 0:
                    print(f"📊 Zeile {row_num:,}: PLZ 26xxx={len(plz_26_found)}, Krummhörn={len(krummhoern_found)}, PLZ-Präfixe={len(stats['plz_prefixes'])}")
    
    except Exception as e:
        print(f"❌ Fehler beim CSV-Lesen: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Detaillierte Ergebnisse
    print(f"\n📊 VOLLSTÄNDIGE ANALYSE-ERGEBNISSE")
    print(f"📋 Gescannte Zeilen: {total_rows:,}")
    print("="*65)
    
    # Header-Diagnose
    print("🔧 SPALTEN-MAPPING-DIAGNOSE:")
    print(f"  ✅ PLZ-Spalte erkannt: {stats['column_debug']['plz_column_found']}")
    print(f"  ✅ Name-Spalte erkannt: {stats['column_debug']['name_column_found']}")
    print(f"  ✅ Stadt-Spalte erkannt: {stats['column_debug']['city_column_found']}")
    
    # PLZ-Präfix-Verteilung (Top 10)
    print(f"\n📍 PLZ-VERTEILUNG (Top 10):")
    top_prefixes = sorted(stats['plz_prefixes'].items(), key=lambda x: x[1], reverse=True)[:10]
    for prefix, count in top_prefixes:
        print(f"  PLZ {prefix}xxx: {count:,} Einträge")
    
    # PLZ 26xxx spezifische Ergebnisse
    print(f"\n🎯 PLZ 26xxx ANALYSE:")
    print(f"  📊 Verschiedene 26xxx PLZ gefunden: {len(plz_26_found)}")
    print(f"  🏘️ Verschiedene Städte in 26xxx: {len(stats['cities_with_26xxx'])}")
    
    if plz_26_found:
        print(f"\n📋 ALLE PLZ 26xxx BEREICHE ({len(plz_26_found)}):")
        for plz in sorted(plz_26_found.keys()):
            entries = len(plz_26_found[plz])
            print(f"  PLZ {plz}: {entries}+ Einträge")
            # Erste 2 Beispiele pro PLZ zeigen
            for entry in plz_26_found[plz][:2]:
                print(f"    - Zeile {entry['row']}: {entry['name']} | {entry['city']}")
            if len(plz_26_found[plz]) > 2:
                print(f"    ... und {len(plz_26_found[plz])-2} weitere")
        
        print(f"\n🏘️ STÄDTE IM 26xxx-BEREICH:")
        for city in sorted(stats['cities_with_26xxx']):
            if city.strip():
                print(f"  - {city}")
    
    # Krummhörn-spezifische Analyse
    print(f"\n🔍 KRUMMHÖRN-SPEZIFISCHE SUCHE:")
    print(f"  🎯 Treffer insgesamt: {len(krummhoern_found)}")
    
    if krummhoern_found:
        print(f"\n🏘️ ALLE KRUMMHÖRN-TREFFER:")
        for i, match in enumerate(krummhoern_found):
            print(f"  {i+1}. Zeile {match['row']}: PLZ {match['plz']} | {match['name']}")
            print(f"     Stadt: {match['city']}")
            print(f"     Match: {', '.join(match['match_reasons'])}")
            print()
    
    if 'krumm' in ''.join(stats['names_with_krumm']).lower():
        print(f"📝 NAMEN MIT 'KRUMM': {len(stats['names_with_krumm'])}")
        for name in stats['names_with_krumm'][:5]:  # Erste 5
            print(f"  - {name}")
    
    # Finale Bewertung
    print(f"\n🎯 FINALE BEWERTUNG:")
    if '26736' in plz_26_found:
        print(f"  ✅ PLZ 26736 (Krummhörn) ERFOLGREICH GEFUNDEN!")
        print(f"     {len(plz_26_found['26736'])}+ Landwirte in Krummhörn")
    else:
        print(f"  ❌ PLZ 26736 (Krummhörn) NICHT in GAP-Daten 2024!")
        
        # Nächste PLZ analysieren
        nearby_plz = [plz for plz in plz_26_found.keys() if plz.startswith('267')]
        if nearby_plz:
            print(f"  🔍 267xx-Bereich vorhanden: {sorted(nearby_plz)}")
        else:
            print(f"  🔍 Kein 267xx-Bereich in GAP-Daten")
        
        # Mögliche Ursachen
        print(f"\n💡 MÖGLICHE URSACHEN:")
        print(f"  1. 🏘️ Krummhörn hat wenige/keine GAP-berechtigte Betriebe 2024")
        print(f"  2. 📍 Krummhörn-Landwirte nutzen andere PLZ (Nachbarorte)")
        print(f"  3. 📊 Betriebe unter anderen Namen registriert")
        print(f"  4. 🏛️ Kommunale Zuordnung zu anderen PLZ-Bereichen")
    
    if not stats['column_debug']['plz_column_found']:
        print(f"\n⚠️ WARNUNG: PLZ-Spalte nicht erkannt - Spaltenverschiebung möglich!")
    elif not stats['column_debug']['name_column_found']:
        print(f"\n⚠️ WARNUNG: Name-Spalte nicht erkannt - TYPO-Problem bestätigt!")
    else:
        print(f"\n✅ SPALTEN-MAPPING: Erfolgreich - keine Verschiebung erkannt")

if __name__ == "__main__":
    find_plz_26xxx()
