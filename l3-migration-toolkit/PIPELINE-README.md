# L3 → VALEO-NeuroERP OCR-Migration Pipeline

Automatisierte Extraktion und Migration aller L3-Masken zu strukturierten Tabellendefinitionen für den VALEO-NeuroERP Mask Builder.

## 🎯 Ziel

**Input:** L3-Screenshots (Guacamole RDP)  
**Output:** Mask Builder JSON-Schemas + SQL CREATE TABLE Statements

## 🏗️ Architektur

```
┌─────────────────┐
│ L3-Screenshot   │
│ (Guacamole RDP) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ OCR-Pipeline    │ ← pytesseract + OpenCV
│ (Feldextraktion)│    image_to_data (Bounding Boxes)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ LLM-Analyse     │ ← Claude/GPT
│ (Strukturierung)│    Typ-Erkennung, Validierung
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Schema-Generator│ ← Mask Builder Format
│ + L3-Mapping    │    + SQL CREATE TABLE
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ JSON + SQL      │
│ Export          │
└─────────────────┘
```

## 📦 Installation

### 1. Python-Dependencies

```bash
pip install pytesseract pillow opencv-python
```

### 2. Tesseract-OCR Binary

**Windows:**
```powershell
# Als Administrator:
choco install tesseract

# Oder manuell von:
# https://github.com/UB-Mannheim/tesseract/wiki
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-deu
```

### 3. Verifikation

```bash
python -c "import pytesseract; print('✅ pytesseract OK')"
tesseract --version
```

## 🚀 Quick Start

### Option A: Vollautomatisch (Batch-Modus)

```bash
cd l3-migration-toolkit
python auto-capture-all-masks.py
```

**Workflow:**
1. Script zeigt Maske an (z.B. "Artikelstamm")
2. Sie öffnen Maske in L3 (Browser)
3. Sie drücken Enter
4. Screenshot wird erstellt
5. OCR-Analyse läuft automatisch
6. JSON + SQL wird exportiert
7. Weiter zur nächsten Maske

**Output:**
- `schemas/mask-builder/*.json` - Mask Builder Schemas
- `schemas/sql/*.sql` - SQL CREATE TABLE Statements
- `screenshots/l3-masks/*.png` - Screenshots

### Option B: Einzelne Maske (manuell)

```bash
# 1. Screenshot erstellen (manuell)
# 2. OCR-Analyse
python ocr-pipeline.py screenshots/l3-masks/artikelstamm.png --debug

# 3. LLM-Analyse
python llm-field-analyzer.py artikelstamm.ocr.json --mask-name "Artikelstamm"

# 4. Schema-Generator
python analyze-mask-fields.py
```

## 📋 Zu erfassende Masken (15+)

### ⭐⭐⭐⭐⭐ KRITISCH
- [x] Artikelstamm
- [ ] Kundenstamm
- [ ] Lieferschein
- [ ] Rechnung
- [ ] Auftrag
- [ ] Bestellung
- [ ] Lager-Bestand
- [ ] PSM-Abgabe (Agrar!)

### ⭐⭐⭐⭐ WICHTIG
- [ ] Lieferantenstamm
- [ ] Angebot
- [ ] Wareneingang
- [ ] Kunden-Kontoauszug

### ⭐⭐⭐ NICE-TO-HAVE
- [ ] Inventur
- [ ] Saatgut
- [ ] Dünger

## 🔧 Module

### 1. `ocr-pipeline.py`

**Funktion:** Screenshot → OCR → Strukturierte Felder

```python
from ocr_pipeline import L3MaskOCR

ocr = L3MaskOCR()
results = ocr.extract_fields("artikelstamm.png")

print(results['fields'])  # Liste erkannter Felder
print(results['tabs'])    # Liste erkannter Tabs
```

**Features:**
- Preprocessing (Graustufen, Kontrast, Rauschreduzierung)
- Bounding Boxes für präzise Feldposition
- Feldtyp-Erkennung (Lookup, Dropdown, Checkbox, etc.)
- Tab-Extraktion

### 2. `llm-field-analyzer.py`

**Funktion:** OCR-Rohdaten → LLM → Strukturierte Felddefinition

```python
from llm_field_analyzer import LLMFieldAnalyzer

analyzer = LLMFieldAnalyzer()
analyzed = analyzer.analyze_ocr_with_llm(
    ocr_text=results['raw_text'],
    ocr_fields=results['fields'],
    context={'mask_name': 'Artikelstamm'}
)
```

**Features:**
- Intelligente Typzuordnung (Text, Nummer, Datum, Currency, etc.)
- Validierungs-Erkennung (required, unique, max_length)
- L3 → VALEO Mapping-Integration
- Relations-Erkennung (Foreign Keys)

### 3. `analyze-mask-fields.py`

**Funktion:** Structured Fields → Mask Builder JSON + SQL

```python
from analyze_mask_fields import L3MaskAnalyzer

analyzer = L3MaskAnalyzer()
schema = analyzer.generate_from_ocr("artikelstamm.png", "Artikelstamm")

analyzer.export_to_json(schema, "schemas/mask-builder/artikelstamm.json")
analyzer.export_to_sql(schema, "schemas/sql/artikelstamm.sql")
```

**Output-Format:**
```json
{
  "schema_version": "1.0",
  "mask": {
    "id": "artikelstamm",
    "name": "Artikel-Stammdaten",
    "route": "/artikel/stamm"
  },
  "form": {
    "fields": [...],
    "validation": {...},
    "layout": {"type": "tabs"}
  },
  "database": {
    "table": "artikelstamm",
    "columns": [...],
    "relations": [...]
  }
}
```

### 4. `auto-capture-all-masks.py`

**Funktion:** Orchestrierung - 15+ Masken automatisch erfassen

```bash
python auto-capture-all-masks.py
```

## 📊 Erfolgsmetriken

- ✅ **100%** der L3-Masken gescreenshottet
- ✅ **95%+** OCR-Genauigkeit (manuelles Review)
- ✅ **Alle Schemas** importierbar in Mask Builder
- ✅ **SQL-Statements** direkt ausführbar in PostgreSQL

## 🔗 Integration mit existierendem L3-Mapping

Die Pipeline nutzt automatisch das existierende Mapping:

**Datei:** `scripts/l3_import_mapping.json`

```json
{
  "ARTIKEL": {
    "ARTIKEL_NR": {
      "source_column": "ARTIKEL_NR",
      "target_column": "artikel_nr",
      "type": "VARCHAR(20)"
    },
    ...
  }
}
```

**Verwendung:**
- Automatische Zuordnung von L3-Feldnamen zu VALEO-Spaltennamen
- Typkonvertierung
- Relations-Ableitung

## 🐛 Troubleshooting

### Problem: Tesseract nicht gefunden

```
FileNotFoundError: [WinError 2] The system cannot find the file specified
```

**Lösung:**
```python
# In ocr-pipeline.py:
ocr = L3MaskOCR(tesseract_path="C:/Program Files/Tesseract-OCR/tesseract.exe")
```

### Problem: Niedrige OCR-Genauigkeit

**Lösung:**
1. Screenshot-Qualität erhöhen (höhere Auflösung)
2. Debug-Modus aktivieren: `--debug`
3. Preprocessing-Parameter anpassen (in `ocr-pipeline.py`)

### Problem: LLM-Integration fehlt

**Lösung:**
```python
# In llm-field-analyzer.py, _call_llm():
import openai

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)
```

## 📚 Weiterführende Dokumentation

- [L3-Tabellenstruktur](../scripts/l3_tables_postgres.sql)
- [L3-Import-Mapping](../scripts/l3_import_mapping.json)
- [VALEO-NeuroERP Mask Builder](../docs/MASK-BUILDER-GUIDE.md)

## 🤝 Workflow-Beispiel

```bash
# Terminal 1: Browser öffnen
http://localhost:8090/guacamole/#/client/MQBjAHBvc3RncmVzcWw

# Terminal 2: Pipeline starten
cd l3-migration-toolkit
python auto-capture-all-masks.py

# Schritt 1: Artikelstamm
# - In L3: ERFASSUNG → Artikel-Stamm öffnen
# - Enter drücken
# - Screenshot wird erstellt
# - OCR + LLM analysiert (30s)
# - JSON + SQL exportiert

# Schritt 2: Kundenstamm
# - In L3: ERFASSUNG → Kunden öffnen
# - Enter drücken
# ...

# Nach 15+ Masken:
# ✅ schemas/mask-builder/ enthält alle JSONs
# ✅ schemas/sql/ enthält alle SQL-Statements
```

## 📈 Status

**Aktuell implementiert:**
- [x] OCR-Pipeline mit Preprocessing
- [x] LLM-Feldanalyse (Struktur)
- [x] Schema-Generator (JSON + SQL)
- [x] L3-Mapping-Integration
- [x] Batch-Automation-Script
- [ ] LLM-API-Integration (OpenAI/Anthropic)
- [ ] Playwright-MCP Screenshot-Automation
- [ ] Mask Builder Import-Funktion

**Nächste Schritte:**
1. Tesseract installieren (einmalig)
2. Erste 5 Masken manuell erfassen
3. OCR-Parameter optimieren
4. LLM-API einbinden
5. Vollautomatische Erfassung aller 15+ Masken

---

**Bereit für die Migration! 🚀**

