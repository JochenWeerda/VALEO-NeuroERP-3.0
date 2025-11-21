#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
from collections import defaultdict

def analyze_filtered_csv():
    """
    Analysiere die vorgefilterte PLZ 26XXX CSV mit korrektem CSV-Quoting
    """
    csv_path = r"C:\Users\Jochen\Downloads\impdata2024_PLZ_26XXX.csv"
    
    if not os.path.exists(csv_path):
        print("FEHLER: CSV-Datei nicht gefunden:", csv_path)
        return
    
    print("=== ANALYSE DER VORGEFILTERTEN PLZ 26XXX CSV (FIXED) ===")
    print(f"Datei: {csv_path}")
    
    # Flächenprämien Codes (basierend auf PDF)
    FLAECHENPRAEMIEN_CODES = ['I.1', 'I.2', 'I.3', 'I.4', 'I.6', 'V.1']
    
    try:
        # CSV mit korrektem Quoting lesen
        with open(csv_path, 'r', encoding='windows-1252') as file:
            # Automatische Delimiter-Erkennung mit csv.Sniffer
            sample = file.read(2048)
            file.seek(0)
            
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            print(f"Erkannter Delimiter: '{delimiter}'")
            
            reader = csv.reader(file, delimiter=delimiter, quotechar='"')
            
            # Erste Zeile als Header lesen
            headers = next(reader)
            print(f"Anzahl Spalten: {len(headers)}")
            
            # Header anzeigen
            print(f"\nErste 10 Header:")
            for i, header in enumerate(headers[:10]):
                print(f"  {i+1}: '{header}'")
            
            # Header-Mapping erstellen (flexibel für Variationen)
            header_map = {}
            for i, header in enumerate(headers):
                header_clean = header.strip()
                if 'Haushaltsjahr' in header_clean:
                    header_map['year'] = i
                elif 'Begünstigten' in header_clean and ('Rechtsträger' in header_clean or 'Verband' in header_clean or 'Verdand' in header_clean):
                    header_map['name'] = i
                elif header_clean == 'PLZ':
                    header_map['plz'] = i
                elif 'Gemeinde' in header_clean:
                    header_map['city'] = i
                elif 'Code der Maßnahme' in header_clean:
                    header_map['measure_code'] = i
                elif 'EU-Betrag (EGFL und ELER) und kofinanzierter Betrag insgesamt' in header_clean:
                    header_map['total_amount'] = i
            
            print(f"\nGefundene wichtige Spalten:")
            for key, idx in header_map.items():
                print(f"  {key}: Spalte {idx+1} ('{headers[idx][:50]}...')")
            
            if len(header_map) < 4:
                print("WARNUNG: Nicht alle wichtigen Spalten gefunden!")
                return
            
            # Daten analysieren
            leads_data = defaultdict(lambda: {
                'name': '', 
                'plz': '',
                'city': '',
                'total_flaechenpraemien': 0.0,
                'total_gap': 0.0,
                'measure_codes': set(),
                'payments_count': 0
            })
            
            total_rows = 0
            flaechenpraemien_rows = 0
            
            for row in reader:
                if len(row) < len(headers):
                    continue  # Überspringe unvollständige Zeilen
                
                total_rows += 1
                
                # Daten extrahieren
                name = row[header_map['name']].strip() if 'name' in header_map else ''
                plz = row[header_map['plz']].strip() if 'plz' in header_map else ''
                city = row[header_map['city']].strip() if 'city' in header_map else ''
                measure_code = row[header_map['measure_code']].strip() if 'measure_code' in header_map else ''
                
                # GAP Betrag
                amount_str = row[header_map['total_amount']].strip() if 'total_amount' in header_map else '0'
                try:
                    # Deutsche Zahlenformate handhaben (Komma als Dezimaltrennzeichen)
                    amount_str = amount_str.replace(',', '.')
                    gap_amount = float(amount_str) if amount_str else 0.0
                except ValueError:
                    gap_amount = 0.0
                
                if name and plz:
                    lead_key = f"{name}_{plz}_{city}"
                    leads_data[lead_key]['name'] = name
                    leads_data[lead_key]['plz'] = plz
                    leads_data[lead_key]['city'] = city
                    leads_data[lead_key]['total_gap'] += gap_amount
                    leads_data[lead_key]['measure_codes'].add(measure_code)
                    leads_data[lead_key]['payments_count'] += 1
                
                # Flächenprämien prüfen
                if measure_code in FLAECHENPRAEMIEN_CODES:
                    flaechenpraemien_rows += 1
                    if name and plz:
                        leads_data[lead_key]['total_flaechenpraemien'] += gap_amount
                
                # Debug: erste 3 Zeilen anzeigen
                if total_rows <= 3:
                    print(f"\nZeile {total_rows}: Name='{name}', PLZ='{plz}', Maßnahme='{measure_code}', Betrag={gap_amount}")
            
            print(f"\n=== ANALYSE ERGEBNISSE ===")
            print(f"Gesamte Zahlungszeilen: {total_rows}")
            print(f"Flächenprämien-Zeilen: {flaechenpraemien_rows}")
            print(f"Einzigartige Betriebe: {len(leads_data)}")
            
            # Flächenprämien-Statistiken
            qualified_farms = 0
            large_farms = 0
            total_flaechenpraemien = 0.0
            total_gap_all = 0.0
            
            for lead_data in leads_data.values():
                total_gap_all += lead_data['total_gap']
                
                if lead_data['total_flaechenpraemien'] > 0:
                    qualified_farms += 1
                    total_flaechenpraemien += lead_data['total_flaechenpraemien']
                    
                    # Geschätzte Betriebsgröße (300 EUR/ha Flächenprämie)
                    estimated_ha = lead_data['total_flaechenpraemien'] / 300
                    if estimated_ha >= 100:  # Großbetrieb
                        large_farms += 1
            
            print(f"\nFLÄCHENPRÄMIEN ANALYSE:")
            print(f"Betriebe mit Flächenprämien: {qualified_farms}")
            print(f"Großbetriebe (>100 ha): {large_farms}")
            print(f"Gesamt Flächenprämien: {total_flaechenpraemien:,.2f} EUR")
            print(f"Gesamt GAP (alle Maßnahmen): {total_gap_all:,.2f} EUR")
            
            if qualified_farms > 0:
                print(f"Durchschnitt Flächenprämien: {total_flaechenpraemien/qualified_farms:,.2f} EUR")
                print(f"Durchschnitt geschätzte Betriebsgröße: {(total_flaechenpraemien/qualified_farms)/300:.1f} ha")
            
            # Top 10 Betriebe mit höchsten Flächenprämien
            print(f"\nTOP 10 BETRIEBE (Flächenprämien):")
            sorted_leads = sorted(
                [(k, v) for k, v in leads_data.items() if v['total_flaechenpraemien'] > 0],
                key=lambda x: x[1]['total_flaechenpraemien'],
                reverse=True
            )
            
            for i, (key, lead_data) in enumerate(sorted_leads[:10]):
                estimated_ha = lead_data['total_flaechenpraemien'] / 300
                print(f"  {i+1}. {lead_data['name'][:30]}... (PLZ {lead_data['plz']})")
                print(f"      Flächenprämien: {lead_data['total_flaechenpraemien']:,.0f} EUR (~{estimated_ha:.0f} ha)")
            
            # PLZ-Statistiken
            plz_stats = defaultdict(lambda: {'count': 0, 'flaechenpraemien': 0.0})
            for lead_data in leads_data.values():
                if lead_data['total_flaechenpraemien'] > 0:
                    plz_key = lead_data['plz']
                    plz_stats[plz_key]['count'] += 1
                    plz_stats[plz_key]['flaechenpraemien'] += lead_data['total_flaechenpraemien']
            
            print(f"\nTOP 10 PLZ mit Flächenprämien:")
            sorted_plz = sorted(plz_stats.items(), key=lambda x: x[1]['flaechenpraemien'], reverse=True)
            for plz, stats in sorted_plz[:10]:
                print(f"  {plz}: {stats['count']} Betriebe, {stats['flaechenpraemien']:,.0f} EUR")
    
    except Exception as e:
        print(f"FEHLER: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_filtered_csv()

