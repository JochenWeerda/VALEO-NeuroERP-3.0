# Ernte-Annahme - Seeding Scripts Zusammenfassung

**Datum:** 2026-02-17  
**Status:** ✅ Seeding Scripts erstellt

---

## Übersicht

Zwei Seeding Scripts wurden erstellt, um die Datenbank mit Beispiel-Daten zu füllen:

1. **NUTS-2 Postal Code Mappings** - PLZ zu NUTS-2 Zuordnungen
2. **Price Adjustment Rules** - Beispiel-Regeln für Preis-Anpassungen

---

## 1. NUTS-2 Postal Code Seeding ✅

### Script

**Datei:** `scripts/seed_nuts2_postal_codes.py`

### Funktionen

- ✅ Importiert NUTS-2 Postal Code Zuordnungen für Deutschland
- ✅ Verwendet `bulk_import_nuts2_postal_codes()` Service
- ✅ Überspringt bereits vorhandene Einträge (Idempotent)

### Beispiel-Daten

- **Sachsen (DE12)**: Dresden, Leipzig
- **Sachsen-Anhalt (DE14)**: Halle, Magdeburg
- **Thüringen (DE16)**: Erfurt, Jena
- **Brandenburg (DE40)**: Potsdam, Cottbus
- **Mecklenburg-Vorpommern (DE80)**: Rostock, Schwerin
- **Bayern (DE21)**: München
- **Niedersachsen (DE91)**: Hannover
- **Nordrhein-Westfalen (DEA1)**: Düsseldorf

### Verwendung

```bash
python scripts/seed_nuts2_postal_codes.py
```

### Hinweis

In Produktion sollten die Daten aus offiziellen Eurostat-Quellen importiert werden:
- CSV/XML von https://ec.europa.eu/eurostat/web/nuts/correspondence-tables
- Automatischer Import-Job möglich

---

## 2. Price Adjustment Rules Seeding ✅

### Script

**Datei:** `scripts/seed_price_adjustment_rules.py`

### Funktionen

- ✅ Erstellt Beispiel-Regeln für HL-Gewicht, Besatz, Mykotoxin
- ✅ Verschiedene Methoden: `table`, `factor`, `percentage`
- ✅ Artikel- und Warengruppe-spezifische Regeln

### Beispiel-Regeln

#### 1. HL-Gewicht Anpassung (Hafer)

- **Methode:** `factor`
- **Basis:** 50.0 kg/hl
- **Anpassung:** 2.5 EUR/t je 0.1 kg/hl über Basis

#### 2. Besatz Anpassung (Raps)

- **Methode:** `table`
- **Regel:** "2% frei", darüber gestaffelte Abzüge
  - 0-2%: Kein Abzug
  - 2-3%: -5 EUR/t
  - 3-4%: -10 EUR/t
  - >4%: -20 EUR/t

#### 3. Besatz Anpassung (Getreide, allgemein)

- **Methode:** `percentage`
- **Regel:** -1% Preis je 1% Besatz (Mengenabzug 1:1)

#### 4. Mykotoxin Anpassung

- **Methode:** `table`
- **Grenzwerte:**
  - 0-1250 ppb: Kein Abzug
  - 1250-2000 ppb: -10 EUR/t
  - >2000 ppb: -50 EUR/t

### Verwendung

```bash
python scripts/seed_price_adjustment_rules.py
```

---

## Nächste Schritte

### 1. Migration ausführen

```bash
alembic upgrade head
```

### 2. Seeding Scripts ausführen

```bash
# NUTS-2 Postal Codes
python scripts/seed_nuts2_postal_codes.py

# Price Adjustment Rules
python scripts/seed_price_adjustment_rules.py
```

### 3. Vollständige NUTS-2 Daten importieren

Für Produktion:
- Eurostat CSV/XML herunterladen
- Import-Script erweitern
- Automatischer Import-Job einrichten

### 4. Weitere Price Adjustment Rules

- Artikel-spezifische Regeln anlegen
- Kunden-spezifische Sonderregelungen
- Jahreszeitliche Anpassungen

---

## Dateien

### Seeding Scripts

- ✅ `scripts/seed_nuts2_postal_codes.py`
- ✅ `scripts/seed_price_adjustment_rules.py`

### Dokumentation

- ✅ `docs/ernte-annahme-seeding-summary.md` (dieses Dokument)

---

**Stand:** 2026-02-17  
**Status:** ✅ Seeding Scripts erstellt, bereit für Ausführung


