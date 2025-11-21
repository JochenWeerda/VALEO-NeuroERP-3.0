#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
from collections import defaultdict

def analyze_filtered_csv():
    """
    Analysiere die vorgefilterte PLZ 26XXX CSV mit korrekten Headern und Delimiter
    """
    csv_path = r"C:\Users\Jochen\Downloads\impdata2024_PLZ_26XXX.csv"
    
    if not os.path.exists(csv_path):
        print("FEHLER: CSV-Datei nicht gefunden:", csv_path)
        return
    
    print("=== ANALYSE DER VORGEFILTERTEN PLZ 26XXX CSV ===")
    print(f"Datei: {csv_path}")
    
    # Flächenprämien Codes (basierend auf PDF)
    FLAECHENPRAEMIEN_CODES = ['I.1', 'I.2', 'I.3', 'I.4', 'I.6', 'V.1']
    
    try:
        # Teste verschiedene Delimiter
        for delimiter in ['\t', ';', ',']:
            print(f"\n--- TESTE DELIMITER: '{delimiter}' ---")
            
            with open(csv_path, 'r', encoding='windows-1252') as file:
                # Erste Zeile als Header lesen
                first_line = file.readline().strip()
                columns = first_line.split(delimiter)
                print(f"Anzahl Spalten: {len(columns)}")
                
                if len(columns) >= 19:  # Erwartete Anzahl Spalten
                    print("KORREKTE SPALTENANZAHL GEFUNDEN!")
                    print(f"Delimiter: '{delimiter}'")
                    
                    # Header anzeigen
                    expected_headers = [
                        "Haushaltsjahr",
                        "Name des Begünstigten/Rechtsträgers/Verdands", 
                        "Wenn Teil einer Gruppe: Name des Mutterunternehmens",
                        "Wenn Teil einer Gruppe: Steuerliches Identifikationsmerkmal",
                        "PLZ",
                        "Gemeinde", 
                        "Betroffener Staat",
                        "Code der Maßnahme/der Interventionskategorie/des Sektors gemäß Anhang IX",
                        "Spezifisches Ziel",
                        "Anfangsdatum",
                        "Enddatum", 
                        "Betrag je Vorhaben im Rahmen des EGFL",
                        "EGFL- Gesamtbetrag für diesen Begünstigten",
                        "Betrag je Vorhaben im Rahmen des ELER (EU-Mittel)",
                        "ELER-Gesamtbetrag für diesen Begünstigten (EU-Mittel)",
                        "Betrag je Vorhaben im Rahmen der nationalen Kofinanzierung", 
                        "National kofinanzierter Gesamtbetrag für diesen Begünstigten",
                        "Summe des ELER-Betrags (EU-Mittel) und des kofinanzierten Betrags",
                        "EU-Betrag (EGFL und ELER) und kofinanzierter Betrag insgesamt für diesen Begünstigten*"
                    ]
                    
                    print(f"\nErste 5 Header aus CSV:")
                    for i, header in enumerate(columns[:5]):
                        print(f"  {i+1}: '{header}'")
                    
                    # Jetzt die eigentliche Analyse
                    file.seek(0)  # Zurück zum Anfang
                    reader = csv.DictReader(file, delimiter=delimiter)
                    
                    leads_data = defaultdict(lambda: {
                        'name': '', 
                        'plz': '',
                        'gemeinde': '',
                        'total_flaechenpraemien': 0.0,
                        'total_gap': 0.0,
                        'measure_codes': set()
                    })
                    
                    total_rows = 0
                    flaechenpraemien_rows = 0
                    
                    for row in reader:
                        total_rows += 1
                        
                        # Basis-Daten extrahieren
                        name = row.get('Name des Begünstigten/Rechtsträgers/Verdands', '').strip()
                        plz = row.get('PLZ', '').strip()
                        gemeinde = row.get('Gemeinde', '').strip()
                        measure_code = row.get('Code der Maßnahme/der Interventionskategorie/des Sektors gemäß Anhang IX', '').strip()
                        
                        # GAP Betrag (Gesamt)
                        gap_amount_str = row.get('EU-Betrag (EGFL und ELER) und kofinanzierter Betrag insgesamt für diesen Begünstigten*', '0').strip()
                        try:
                            gap_amount = float(gap_amount_str.replace(',', '.')) if gap_amount_str else 0.0
                        except ValueError:
                            gap_amount = 0.0
                        
                        if name and plz:
                            lead_key = f"{name}_{plz}_{gemeinde}"
                            leads_data[lead_key]['name'] = name
                            leads_data[lead_key]['plz'] = plz
                            leads_data[lead_key]['gemeinde'] = gemeinde
                            leads_data[lead_key]['total_gap'] += gap_amount
                            leads_data[lead_key]['measure_codes'].add(measure_code)
                        
                        # Flächenprämien filtern
                        if measure_code in FLAECHENPRAEMIEN_CODES:
                            flaechenpraemien_rows += 1
                            if name and plz:
                                leads_data[lead_key]['total_flaechenpraemien'] += gap_amount
                    
                    print(f"\n=== ANALYSE ERGEBNISSE ===")
                    print(f"Gesamte Zeilen: {total_rows}")
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
                    print(f"Gesamt GAP (alle): {total_gap_all:,.2f} EUR")
                    print(f"Durchschnitt Flächenprämien: {total_flaechenpraemien/qualified_farms:,.2f} EUR" if qualified_farms > 0 else "Durchschnitt: 0 EUR")
                    
                    # Top 10 PLZ-Bereiche
                    plz_stats = defaultdict(lambda: {'count': 0, 'flaechenpraemien': 0.0})
                    for lead_data in leads_data.values():
                        if lead_data['total_flaechenpraemien'] > 0:
                            plz_prefix = lead_data['plz'][:3] if len(lead_data['plz']) >= 3 else lead_data['plz']
                            plz_stats[plz_prefix]['count'] += 1
                            plz_stats[plz_prefix]['flaechenpraemien'] += lead_data['total_flaechenpraemien']
                    
                    print(f"\nTOP PLZ-BEREICHE (mit Flächenprämien):")
                    sorted_plz = sorted(plz_stats.items(), key=lambda x: x[1]['flaechenpraemien'], reverse=True)
                    for plz, stats in sorted_plz[:10]:
                        print(f"  {plz}xxx: {stats['count']} Betriebe, {stats['flaechenpraemien']:,.0f} EUR")
                    
                    break  # Korrekter Delimiter gefunden
                else:
                    print(f"Zu wenige Spalten mit '{delimiter}': {len(columns)}")
    
    except Exception as e:
        print(f"FEHLER: {e}")

if __name__ == "__main__":
    analyze_filtered_csv()

