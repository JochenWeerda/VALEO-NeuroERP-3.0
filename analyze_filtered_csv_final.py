#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
from collections import defaultdict

def analyze_filtered_csv():
    """
    Analysiere die vorgefilterte PLZ 26XXX CSV ohne Header-Zeile
    """
    csv_path = r"C:\Users\Jochen\Downloads\impdata2024_PLZ_26XXX.csv"
    
    if not os.path.exists(csv_path):
        print("FEHLER: CSV-Datei nicht gefunden:", csv_path)
        return
    
    print("=== ANALYSE DER VORGEFILTERTEN PLZ 26XXX CSV (FINAL) ===")
    print(f"Datei: {csv_path}")
    
    # Flächenprämien Codes (basierend auf PDF)
    FLAECHENPRAEMIEN_CODES = ['I.1', 'I.2', 'I.3', 'I.4', 'I.6', 'V.1']
    
    # Spalten-Mapping basierend auf den bereitgestellten Headern
    COLUMN_MAP = {
        'year': 0,                    # Haushaltsjahr
        'name': 1,                    # Name des Begünstigten/Rechtsträgers/Verdands
        'parent_company': 2,          # Wenn Teil einer Gruppe: Name des Mutterunternehmens
        'tax_id': 3,                  # Wenn Teil einer Gruppe: Steuerliches Identifikationsmerkmal
        'plz': 4,                     # PLZ
        'city': 5,                    # Gemeinde
        'country': 6,                 # Betroffener Staat
        'measure_code': 7,            # Code der Maßnahme/der Interventionskategorie/des Sektors gemäß Anhang IX
        'specific_goal': 8,           # Spezifisches Ziel
        'start_date': 9,              # Anfangsdatum
        'end_date': 10,               # Enddatum
        'egfl_amount': 11,            # Betrag je Vorhaben im Rahmen des EGFL
        'egfl_total': 12,             # EGFL- Gesamtbetrag für diesen Begünstigten
        'eler_amount': 13,            # Betrag je Vorhaben im Rahmen des ELER (EU-Mittel)
        'eler_total': 14,             # ELER-Gesamtbetrag für diesen Begünstigten (EU-Mittel)
        'national_amount': 15,        # Betrag je Vorhaben im Rahmen der nationalen Kofinanzierung
        'national_total': 16,         # National kofinanzierter Gesamtbetrag für diesen Begünstigten
        'eler_plus_national': 17,     # Summe des ELER-Betrags (EU-Mittel) und des kofinanzierten Betrags
        'total_amount': 18            # EU-Betrag (EGFL und ELER) und kofinanzierter Betrag insgesamt für diesen Begünstigten*
    }
    
    try:
        with open(csv_path, 'r', encoding='windows-1252') as file:
            reader = csv.reader(file, delimiter=',', quotechar='"')
            
            # Daten analysieren (ohne Header)
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
                if len(row) < 19:
                    continue  # Überspringe unvollständige Zeilen
                
                total_rows += 1
                
                # Daten extrahieren
                year = row[COLUMN_MAP['year']].strip()
                name = row[COLUMN_MAP['name']].strip()
                plz = row[COLUMN_MAP['plz']].strip()
                city = row[COLUMN_MAP['city']].strip()
                measure_code = row[COLUMN_MAP['measure_code']].strip()
                
                # GAP Betrag (Gesamtbetrag)
                amount_str = row[COLUMN_MAP['total_amount']].strip()
                try:
                    # Deutsche Zahlenformate und Anführungszeichen entfernen
                    amount_str = amount_str.replace('"', '').replace(',', '.')
                    gap_amount = float(amount_str) if amount_str else 0.0
                except ValueError:
                    gap_amount = 0.0
                
                if name and plz and year == '2024':  # Nur 2024 Daten
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
                
                # Debug: erste 5 Zeilen anzeigen
                if total_rows <= 5:
                    print(f"Zeile {total_rows}: Jahr={year}, Name='{name[:30]}...', PLZ={plz}, Stadt='{city[:20]}...', Code={measure_code}, Betrag={gap_amount:.2f}")
            
            print(f"\n=== ANALYSE ERGEBNISSE ===")
            print(f"Gesamte Zahlungszeilen: {total_rows}")
            print(f"Flächenprämien-Zeilen: {flaechenpraemien_rows}")
            print(f"Einzigartige Betriebe: {len(leads_data)}")
            
            # Flächenprämien-Statistiken
            qualified_farms = 0
            large_farms = 0
            medium_farms = 0
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
                    elif estimated_ha >= 50:  # Mittelbetrieb
                        medium_farms += 1
            
            print(f"\nFLÄCHENPRÄMIEN ANALYSE:")
            print(f"Betriebe mit Flächenprämien: {qualified_farms}")
            print(f"- Großbetriebe (>100 ha): {large_farms}")
            print(f"- Mittelbetriebe (50-100 ha): {medium_farms}")
            print(f"- Kleinbetriebe (<50 ha): {qualified_farms - large_farms - medium_farms}")
            print(f"Gesamt Flächenprämien: {total_flaechenpraemien:,.2f} EUR")
            print(f"Gesamt GAP (alle Maßnahmen): {total_gap_all:,.2f} EUR")
            
            if qualified_farms > 0:
                avg_flaechenpraemien = total_flaechenpraemien / qualified_farms
                avg_ha = avg_flaechenpraemien / 300
                print(f"Durchschnitt Flächenprämien: {avg_flaechenpraemien:,.2f} EUR")
                print(f"Durchschnitt geschätzte Betriebsgröße: {avg_ha:.1f} ha")
            
            # Top 15 Betriebe mit höchsten Flächenprämien
            print(f"\nTOP 15 BETRIEBE (Flächenprämien):")
            sorted_leads = sorted(
                [(k, v) for k, v in leads_data.items() if v['total_flaechenpraemien'] > 0],
                key=lambda x: x[1]['total_flaechenpraemien'],
                reverse=True
            )
            
            for i, (key, lead_data) in enumerate(sorted_leads[:15]):
                estimated_ha = lead_data['total_flaechenpraemien'] / 300
                size_category = "GROSS" if estimated_ha >= 100 else "MITTEL" if estimated_ha >= 50 else "KLEIN"
                print(f"  {i+1:2d}. {lead_data['name'][:40]:40} (PLZ {lead_data['plz']})")
                print(f"       {lead_data['total_flaechenpraemien']:8,.0f} EUR (~{estimated_ha:5.0f} ha) [{size_category}]")
            
            # PLZ-Statistiken (Top 15)
            plz_stats = defaultdict(lambda: {'count': 0, 'flaechenpraemien': 0.0, 'total_gap': 0.0})
            for lead_data in leads_data.values():
                plz_key = lead_data['plz']
                plz_stats[plz_key]['total_gap'] += lead_data['total_gap']
                if lead_data['total_flaechenpraemien'] > 0:
                    plz_stats[plz_key]['count'] += 1
                    plz_stats[plz_key]['flaechenpraemien'] += lead_data['total_flaechenpraemien']
            
            print(f"\nTOP 15 PLZ (mit Flächenprämien):")
            sorted_plz = sorted(plz_stats.items(), key=lambda x: x[1]['flaechenpraemien'], reverse=True)
            for plz, stats in sorted_plz[:15]:
                if stats['count'] > 0:
                    avg_per_farm = stats['flaechenpraemien'] / stats['count']
                    print(f"  {plz}: {stats['count']:3d} Betriebe, {stats['flaechenpraemien']:8,.0f} EUR (Avg {avg_per_farm:6,.0f} EUR)")
            
            # Maßnahmencode-Statistiken
            measure_stats = defaultdict(lambda: {'count': 0, 'amount': 0.0})
            with open(csv_path, 'r', encoding='windows-1252') as file:
                reader = csv.reader(file, delimiter=',', quotechar='"')
                for row in reader:
                    if len(row) >= 19:
                        measure_code = row[COLUMN_MAP['measure_code']].strip()
                        amount_str = row[COLUMN_MAP['total_amount']].strip().replace('"', '').replace(',', '.')
                        try:
                            amount = float(amount_str) if amount_str else 0.0
                            measure_stats[measure_code]['count'] += 1
                            measure_stats[measure_code]['amount'] += amount
                        except ValueError:
                            pass
            
            print(f"\nMAßNAHMENCODE STATISTIKEN:")
            sorted_measures = sorted(measure_stats.items(), key=lambda x: x[1]['amount'], reverse=True)
            for code, stats in sorted_measures[:10]:
                is_flaechenpraemie = "[FLAECHE]" if code in FLAECHENPRAEMIEN_CODES else "[andere]"
                print(f"  {code:6s}: {stats['count']:5d} Zahlungen, {stats['amount']:10,.0f} EUR [{is_flaechenpraemie}]")
    
    except Exception as e:
        print(f"FEHLER: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_filtered_csv()
