#!/usr/bin/env python3
"""
Debug CSV Headers um den korrekten GAP-Betrag-Header zu finden
"""

import csv

def debug_csv_headers():
    csv_path = "data/gap/impdata2024.csv"
    
    print("DEBUG: CSV-HEADER UND ERSTE DATENZEILE")
    print("=" * 60)
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            headers = reader.fieldnames
            print(f"Anzahl Header: {len(headers)}")
            print()
            print("ALLE HEADER:")
            print("-" * 30)
            
            for i, header in enumerate(headers, 1):
                print(f"{i:2d}. {header}")
            
            print()
            print("SUCHE NACH BETRAG-HEADERN:")
            print("-" * 30)
            
            betrag_headers = []
            for i, header in enumerate(headers, 1):
                if 'betrag' in header.lower() or 'eur' in header.lower() or 'euro' in header.lower():
                    betrag_headers.append((i, header))
                    print(f"{i:2d}. {header}")
            
            print()
            print("ERSTE DATENZEILE MIT BETRAEGEN:")
            print("-" * 40)
            
            # Erste Zeile lesen
            first_row = next(reader)
            
            for i, header in betrag_headers:
                value = first_row.get(header, '')
                print(f"{header}: '{value}'")
            
    except Exception as e:
        print(f"FEHLER: {e}")

if __name__ == "__main__":
    debug_csv_headers()

