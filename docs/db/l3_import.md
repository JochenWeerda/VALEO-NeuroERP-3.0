# L3 → VALEO NeuroERP Import Pipeline

Dieses Dokument beschreibt den vorgeschlagenen Prozess, um Daten aus dem bestehenden L3-System sicher und reproduzierbar in die neuen VALEO-NeuroERP-Schemas zu übernehmen.

## 1. Überblick

1. **Rohdaten erfassen**: L3 liefert eine XHTML-Datei mit Tabellen/Spalten sowie die eigentlichen Daten (z. B. CSV/SQL-Dump).
2. **Metadaten extrahieren**: Mit `tools/l3_import/extract_mapping.py` konvertieren wir die tabellarische Übersicht in ein maschinenlesbares JSON.
3. **Mapping definieren**: `config/l3_mapping.template.yaml` dient als Vorlage. Für jede L3-Spalte wird definiert, wie sie in ein VALEO-Ziel (Schema.Table.Column) übertragen wird – inkl. Datentypen und Transformationen.
4. **Schema-Bootstrap**: `scripts/bootstrap_db.py` legt alle benötigten Schemas/Tabellen an (idempotent) und kann optional Seed-Daten einspielen. In Produktivumgebungen wird nur ausgeführt, wenn der Admin dies explizit bestätigt.
5. **ETL ausführen**: `scripts/import_l3.py` liest den Mapping-Plan plus Rohdaten, überführt sie ins produktive Schema und protokolliert Abweichungen.

## 2. Metadaten extrahieren

```bash
python tools/l3_import/extract_mapping.py \
  --input "C:/Users/Jochen/Desktop/L3_Uebersicht Tabellen und Spalten.xhtml" \
  --output docs/data/l3/raw_tables.json
```

> Hinweis: Die JSON-Datei enthält **nur** Quelltabellen/-spalten. Die Zuordnung zu VALEO-Strukturen wird im nächsten Schritt gepflegt.

## 3. Mapping pflegen

- Kopiere `config/l3_mapping.template.yaml` zu `config/l3_mapping.yaml`.
- Ergänze für jede L3-Spalte:
  - `target`: Ziel in unserem Schema (`domain_inventory.articles.article_number`)
  - `type`: erwarteter Typ (integer, decimal, text, date, uuid, …)
  - `transform`: optionaler Hinweis (z. B. `strip`, `uppercase`, `map_enum`, `split(';')`)
  - `notes`: Kontext oder offene Fragen

Nach jedem Update der Mapping-Datei sollte der Validator ausgeführt werden:

```bash
python scripts/validate_mapping.py \
  --mapping config/l3_mapping.yaml \
  --raw docs/data/l3/raw_tables.json
```

Der Validator prüft u. a. auf fehlende Targets, unbekannte Quellspalten sowie doppelt zugewiesene Ziel-Felder und bricht mit Exit-Code `1` bei Fehlern ab (Option `--fail-on-warn` macht Warnungen fatal). Domänenspezifische Regeln (z. B. Pflicht-Typen für `domain_finance.currency_code` oder `domain_inventory.lot_id`) werden dabei ebenfalls ausgewertet.

Die Mapping-Datei dient als „Single Source of Truth“ für Transformationslogik und erleichtert Reviews.

## 4. Datenbank-Bootstrap

```bash
python scripts/bootstrap_db.py
```

- Prüft, ob die Datenbank leer ist. Wenn nicht, wird der Vorgang abgebrochen.
- Option `--force` löscht **alle** Tabellen (Drop & Re-Create) – nur für lokale/CI-Umgebungen geeignet.
- Option `--seed` führt `scripts/init_db.py` und `python -m app.seeds.inventory_seed` aus.

> In Produktivsystemen **nie** ohne `--force` und explizite Bestätigung ausführen.

## 5. L3-Import

```bash
python scripts/import_l3.py \
  --mapping config/l3_mapping.yaml \
  --source data/l3_export \
  --dry-run
```

- Erwartet pro L3-Tabelle eine Datei im `--source` Verzeichnis (z. B. `ABSCHLUSS.csv`).
- `--dry-run` validiert das Mapping, ohne Inserts/Updates auszuführen.
- Ohne `--dry-run` führt der ETL die eigentlichen Transformationen + Inserts durch.

## 6. CI / QA

Für automatisierte Tests (z. B. Playwright-Masken) empfiehlt sich ein CI-Job:

1. Frische Postgres-DB starten.
2. `python scripts/bootstrap_db.py --seed`.
3. L3-Staging-Daten importieren (`--dry-run` im PR, ohne `--dry-run` im Merge).
4. Masken-Tests gegen die gefüllte DB ausführen.

## 7. Produktive Sicherheit

- Produktivsysteme sollten nur via genehmigte Pipelines oder Admin-Skripte zurückgesetzt werden.
- Vor jedem Import: automatisches Backup (z. B. `pg_dump`) erstellen.
- Import-Script loggt alle Änderungen (Rows affected, Fehler). Bei Abweichungen -> Abbruch & manueller Review.

## 8. Offene Punkte

- Vollständige Mapping-Datei bearbeiten (derzeit nur Template).
- Transformationsregeln (Enum-Konvertierung, Datumsumrechnung) feinjustieren.
- Automatisierte Tests für kritische Masken erweitern.

Sobald Mapping und ETL vollständig sind, können die 181 Masken mit echten Daten getestet werden – ohne Risiko, produktive Instanzen unbeabsichtigt zu überschreiben.
