# L3 Datenimport - Anleitung

## Übersicht

Dieses Dokument beschreibt den Import von Daten aus dem L3-ERP-System in VALEO-NeuroERP.

## Generierte Dateien

### 1. PostgreSQL-Tabellen

**Datei:** `scripts/l3_tables_postgres.sql`

Enthält CREATE TABLE Statements für:
- `l3_adressen` (31 Spalten) - Kundenadressen
- `l3_artikel` (26+ Spalten) - Artikel/Produkte
- `l3_auftrag` (239 Spalten) - Aufträge
- `l3_rechnung` (112 Spalten) - Rechnungen

**Tabellen erstellen:**
```bash
# Im Docker-Container
Get-Content scripts/l3_tables_postgres.sql | docker exec -i valeo_db psql -U postgres -d valeo

# Oder lokal via psql
psql -U postgres -d valeo -f scripts/l3_tables_postgres.sql
```

### 2. Import-Mapping

**Datei:** `scripts/l3_import_mapping.json`

JSON-Mapping von L3-Spalten zu PostgreSQL-Spalten:
```json
{
  "ADRESSEN": {
    "target_table": "l3_adressen",
    "columns": {
      "NUMMER": "nummer",
      "NAME1": "name1",
      ...
    }
  }
}
```

## Import-Prozess

### Schritt 1: L3-Daten exportieren

Aus L3:
1. SQL Server Management Studio öffnen
2. Datenbank exportieren als CSV:
   ```sql
   -- Beispiel: Adressen exportieren
   SELECT * FROM ADRESSEN
   ```
3. Als CSV speichern

### Schritt 2: CSV nach PostgreSQL importieren

```python
import psycopg2
import csv
import json

# Mapping laden
with open('scripts/l3_import_mapping.json') as f:
    mapping = json.load(f)

# CSV importieren
conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/valeo")
cur = conn.cursor()

# Beispiel: ADRESSEN
with open('l3_export/ADRESSEN.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    table_mapping = mapping['ADRESSEN']
    
    for row in reader:
        columns = []
        values = []
        
        for l3_col, pg_col in table_mapping['columns'].items():
            if l3_col in row:
                columns.append(pg_col)
                values.append(row[l3_col])
        
        sql = f"INSERT INTO {table_mapping['target_table']} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(values))})"
        cur.execute(sql, values)

conn.commit()
```

### Schritt 3: Daten-Mapping zu VALEO-Tabellen

Nach dem Import in `l3_*` Tabellen:

```sql
-- Beispiel: ADRESSEN → crm_contacts
INSERT INTO crm_contacts (
    first_name,
    last_name,
    company,
    email,
    phone,
    street,
    postal_code,
    city,
    country
)
SELECT 
    '',  -- L3 hat keine Trennung Vor-/Nachname
    name1,
    name2,
    email,
    telefon1,
    strasse,
    plz,
    ort,
    land
FROM l3_adressen
WHERE art = 'K';  -- Nur Kunden

-- Beispiel: ARTIKEL → inventory_artikel
INSERT INTO inventory_artikel (
    artikelnummer,
    artikelname,
    beschreibung,
    kategorie,
    einheit,
    verkaufspreis,
    barcode
)
SELECT 
    artikelnr,
    bezeichn1,
    beschreib,
    artikelgrp,
    me1,
    0.0,  -- Preis muss separat gemappt werden
    eancode
FROM l3_artikel;
```

## Automatischer Import (Python-Script)

**Datei erstellen:** `scripts/import_l3_data.py`

```python
#!/usr/bin/env python3
"""
VALEO-NeuroERP - L3 Datenimport
"""
import psycopg2
import csv
import json
import sys
from pathlib import Path

def import_table(conn, l3_csv_path: str, table_name: str, mapping: dict):
    """Importiert eine L3-CSV in PostgreSQL"""
    cur = conn.cursor()
    table_mapping = mapping.get(table_name)
    
    if not table_mapping:
        print(f"⚠️  Kein Mapping für {table_name}")
        return 0
    
    target_table = table_mapping['target_table']
    column_map = table_mapping['columns']
    
    count = 0
    with open(l3_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            columns = []
            values = []
            
            for l3_col, pg_col in column_map.items():
                if l3_col in row and row[l3_col]:
                    columns.append(pg_col)
                    values.append(row[l3_col])
            
            if columns:
                placeholders = ', '.join(['%s'] * len(values))
                sql = f"INSERT INTO {target_table} ({', '.join(columns)}) VALUES ({placeholders})"
                try:
                    cur.execute(sql, values)
                    count += 1
                except Exception as e:
                    print(f"❌ Fehler bei Zeile {count}: {e}")
                    continue
    
    conn.commit()
    print(f"✅ {count} Datensätze importiert: {table_name} → {target_table}")
    return count

def main():
    # Mapping laden
    with open('scripts/l3_import_mapping.json') as f:
        mapping = json.load(f)
    
    # PostgreSQL verbinden
    conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/valeo")
    
    # L3-Export-Verzeichnis
    l3_export_dir = Path("l3_export")
    
    if not l3_export_dir.exists():
        print(f"❌ Verzeichnis nicht gefunden: {l3_export_dir}")
        print("   Bitte L3-Daten als CSV in 'l3_export/' ablegen")
        return
    
    # Import durchführen
    total = 0
    for table in ['ADRESSEN', 'ARTIKEL', 'AUFTRAG', 'RECHNUNG']:
        csv_file = l3_export_dir / f"{table}.csv"
        if csv_file.exists():
            count = import_table(conn, str(csv_file), table, mapping)
            total += count
        else:
            print(f"⚠️  Datei nicht gefunden: {csv_file}")
    
    print(f"\n✅ Import abgeschlossen: {total} Datensätze gesamt")
    conn.close()

if __name__ == "__main__":
    main()
```

## Fehlende L3-Tabellen

Die folgenden Prioritäts-Tabellen wurden NICHT in der L3-Struktur gefunden:
- `ANGEBOT` (→ evtl. in AUFTRAG enthalten?)
- `BELEGE` (→ generische Tabelle?)
- `BELEGPOSITIONEN` (→ evtl. AUFTRAGPOS?)
- `BESTAND` (→ Lagerbest and?)
- `BUCHUNG` (→ FIBU-Buchungen)
- `DUENGEMITTEL`, `PSM`, `SAATGUT` (→ Agrar-spezifisch, evtl. in ARTIKEL?)
- `KONTO` (→ Kontenplan)
- `KUNDE` (→ evtl. in ADRESSEN mit ART='K'?)
- `LIEFERANT` (→ evtl. in ADRESSEN mit ART='L'?)

**Hinweis:** Diese Tabellen könnten in L3 anders benannt sein oder in übergeordneten Tabellen enthalten sein.

## Nächste Schritte

1. ✅ L3-Tabellen in PostgreSQL erstellt
2. ✅ Import-Mapping generiert
3. ⏳ L3-Daten als CSV exportieren
4. ⏳ Import-Script ausführen
5. ⏳ Daten-Transformation zu VALEO-Tabellen
6. ⏳ Datenvalidierung

## Support

Bei Fragen zum L3-Import:
- Analyzer-Script: `scripts/l3_table_analyzer.py`
- Import-Script: `scripts/import_l3_data.py`
- Mapping-Datei: `scripts/l3_import_mapping.json`

