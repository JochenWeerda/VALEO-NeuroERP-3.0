#!/usr/bin/env python3
"""
VALEO-NeuroERP - L3 Tabellen Analyzer
Analysiert die L3-Tabellenstruktur und generiert PostgreSQL-Äquivalente
"""

import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

# Wichtige L3-Tabellen für Landhandel/ERP
PRIORITY_TABLES = [
    'ADRESSEN',          # Kundenadressen
    'ARTIKEL',           # Artikel/Produkte
    'BESTAND',           # Lagerbestand
    'BELEGE',            # Belege (Angebote, Aufträge, Rechnungen)
    'BELEGPOSITIONEN',   # Belegpositionen
    'BUCHUNG',           # Buchungen
    'KONTO',             # Kontenplan
    'LIEFERANT',         # Lieferanten
    'KUNDE',             # Kunden
    'RECHNUNG',          # Rechnungen
    'AUFTRAG',           # Aufträge
    'ANGEBOT',           # Angebote
    'SAATGUT',           # Saatgut
    'DUENGEMITTEL',      # Düngemittel
    'PSM',               # Pflanzenschutzmittel
]

def parse_l3_xhtml(file_path: str) -> Dict[str, List[str]]:
    """Parst die L3 XHTML-Datei und extrahiert Tabellen + Spalten"""
    print(f"📖 Lese L3-Datei: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extrahiere Tabellennamen und Spaltennamen
    tables = defaultdict(list)
    current_table = None
    
    # Regex für Tabellenzeilen
    row_pattern = re.compile(r'<p>(.*?)</p>')
    
    lines = content.split('</tr>')
    for line in lines:
        matches = row_pattern.findall(line)
        if len(matches) >= 2:
            table_name = matches[0].strip()
            column_name = matches[1].strip()
            
            if table_name and column_name:
                if table_name != 'TABLE_NAME':  # Header überspringen
                    tables[table_name].append(column_name)
    
    print(f"✅ {len(tables)} Tabellen gefunden")
    return dict(tables)

def map_l3_to_postgres_type(column_name: str) -> str:
    """Mapped L3-Spaltentypen auf PostgreSQL-Typen"""
    column_upper = column_name.upper()
    
    # ID/Key-Felder
    if column_upper in ['ID', 'DBID', 'NUMMER', 'NR', 'SCHLUESSEL']:
        return 'SERIAL PRIMARY KEY' if column_upper == 'ID' else 'INTEGER'
    
    # Datums-Felder
    if 'DATUM' in column_upper or column_upper in ['LTDATUM', 'BUCHDATUM']:
        return 'DATE'
    
    # Betrags-Felder
    if column_upper.startswith('D') or 'BETRAG' in column_upper or 'PREIS' in column_upper:
        if 'DBETRAG' in column_upper or 'DPREIS' in column_upper:
            return 'DECIMAL(12,2)'
    
    # Boolean-Felder
    if column_upper.startswith('I') and len(column_upper) > 1:
        return 'BOOLEAN DEFAULT FALSE'
    
    # Mengen-Felder
    if 'MENGE' in column_upper or 'ANZAHL' in column_upper:
        return 'DECIMAL(10,2)'
    
    # Text-Felder
    if any(x in column_upper for x in ['NAME', 'BEZEICH', 'TEXT', 'BESCHR', 'ORT', 'STRASSE']):
        if 'NAME1' in column_upper or 'TEXT' in column_upper:
            return 'VARCHAR(255)'
        return 'VARCHAR(255)'
    
    # Codes/Kennzeichen
    if any(x in column_upper for x in ['CODE', 'PLZ', 'TELEFON', 'FAX', 'EMAIL']):
        if 'EMAIL' in column_upper:
            return 'VARCHAR(255)'
        return 'VARCHAR(100)'
    
    # Default
    return 'VARCHAR(255)'

def generate_postgresql_create_table(table_name: str, columns: List[str]) -> str:
    """Generiert CREATE TABLE Statement für PostgreSQL"""
    
    # Tabellenname in Kleinbuchstaben + l3_ Präfix
    pg_table_name = f"l3_{table_name.lower()}"
    
    sql = f"-- {table_name}\n"
    sql += f"CREATE TABLE IF NOT EXISTS {pg_table_name} (\n"
    
    column_defs = []
    indices = []
    
    for i, col in enumerate(columns):
        col_name = col.lower()
        col_type = map_l3_to_postgres_type(col)
        
        # Erste Spalte ist meist Primary Key
        if i == 0 and col.upper() in ['ID', 'SCHLUESSEL', 'NUMMER']:
            col_type = 'SERIAL PRIMARY KEY'
        
        column_defs.append(f"    {col_name} {col_type}")
        
        # Indices erstellen für wichtige Felder
        if any(x in col.upper() for x in ['NUMMER', 'NAME', 'DATUM', 'KUNDE', 'ARTIKEL']):
            if 'PRIMARY KEY' not in col_type:
                indices.append(f"CREATE INDEX IF NOT EXISTS idx_{pg_table_name}_{col_name} ON {pg_table_name}({col_name});")
    
    # Timestamp-Felder hinzufügen
    column_defs.append("    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    column_defs.append("    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    
    sql += ",\n".join(column_defs)
    sql += "\n);\n"
    
    # Indices anhängen
    if indices:
        sql += "\n" + "\n".join(indices) + "\n"
    
    return sql

def generate_import_mapping(tables: Dict[str, List[str]]) -> str:
    """Generiert ein JSON-Mapping für den Datenimport"""
    import json
    
    mapping = {}
    for table_name, columns in tables.items():
        if table_name.upper() in PRIORITY_TABLES:
            pg_table_name = f"l3_{table_name.lower()}"
            mapping[table_name] = {
                "target_table": pg_table_name,
                "columns": {col: col.lower() for col in columns}
            }
    
    return json.dumps(mapping, indent=2, ensure_ascii=False)

def main():
    l3_file = r"C:\Users\Jochen\Desktop\L3_Uebersicht Tabellen und Spalten.xhtml"
    output_sql = "scripts/l3_tables_postgres.sql"
    output_mapping = "scripts/l3_import_mapping.json"
    
    print("=" * 80)
    print("VALEO-NeuroERP - L3 Tabellen Analyzer")
    print("=" * 80)
    
    # Parse L3-Struktur
    tables = parse_l3_xhtml(l3_file)
    
    # Generiere SQL für Prioritäts-Tabellen
    print(f"\n📝 Generiere PostgreSQL CREATE TABLE Statements...")
    sql_output = "-- ============================================================================\n"
    sql_output += "-- VALEO-NeuroERP - L3 Import Tabellen (PostgreSQL)\n"
    sql_output += "-- Auto-generated from L3 Database Schema\n"
    sql_output += "-- ============================================================================\n\n"
    
    priority_count = 0
    for table_name in PRIORITY_TABLES:
        if table_name in tables:
            columns = tables[table_name]
            sql_output += generate_postgresql_create_table(table_name, columns)
            sql_output += "\n"
            priority_count += 1
    
    # Schreibe SQL-Datei
    with open(output_sql, 'w', encoding='utf-8') as f:
        f.write(sql_output)
    print(f"✅ SQL generiert: {output_sql} ({priority_count} Tabellen)")
    
    # Generiere Import-Mapping
    print(f"\n📊 Generiere Import-Mapping...")
    mapping_json = generate_import_mapping(tables)
    with open(output_mapping, 'w', encoding='utf-8') as f:
        f.write(mapping_json)
    print(f"✅ Mapping generiert: {output_mapping}")
    
    # Statistik
    print(f"\n📈 Statistik:")
    print(f"   - Gesamt-Tabellen in L3: {len(tables)}")
    print(f"   - Prioritäts-Tabellen gefunden: {priority_count}/{len(PRIORITY_TABLES)}")
    print(f"   - SQL-Datei: {output_sql}")
    print(f"   - Mapping-Datei: {output_mapping}")
    
    # Zeige fehlende Prioritäts-Tabellen
    missing = set(PRIORITY_TABLES) - set(tables.keys())
    if missing:
        print(f"\n⚠️  Fehlende Prioritäts-Tabellen in L3:")
        for m in sorted(missing):
            print(f"   - {m}")
    
    print("\n" + "=" * 80)
    print("✅ Fertig!")
    print("=" * 80)

if __name__ == "__main__":
    main()

