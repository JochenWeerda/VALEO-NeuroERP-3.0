***REMOVED*** L3 → VALEO-NeuroERP OCR-Migration Pipeline

Automatisierte Extraktion und Migration aller L3-Masken zu strukturierten Tabellendefinitionen für den VALEO-NeuroERP Mask Builder.

***REMOVED******REMOVED*** 🎯 Ziel

**Input:** L3-Screenshots (Guacamole RDP)  
**Output:** Mask Builder JSON-Schemas + SQL CREATE TABLE Statements

***REMOVED******REMOVED*** 🏗️ Architektur

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

***REMOVED******REMOVED*** 📦 Installation

***REMOVED******REMOVED******REMOVED*** 1. Python-Dependencies

```bash
pip install pytesseract pillow opencv-python
```

***REMOVED******REMOVED******REMOVED*** 2. Tesseract-OCR Binary

**Windows:**
```powershell
***REMOVED*** Als Administrator:
choco install tesseract

***REMOVED*** Oder manuell von:
***REMOVED*** https://github.com/UB-Mannheim/tesseract/wiki
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-deu
```

***REMOVED******REMOVED******REMOVED*** 3. Verifikation

```bash
python -c "import pytesseract; print('✅ pytesseract OK')"
tesseract --version
```

***REMOVED******REMOVED*** 🚀 Quick Start

***REMOVED******REMOVED******REMOVED*** Option A: Vollautomatisch (Batch-Modus)

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

***REMOVED******REMOVED******REMOVED*** Option B: Einzelne Maske (manuell)

```bash
***REMOVED*** 1. Screenshot erstellen (manuell)
***REMOVED*** 2. OCR-Analyse
python ocr-pipeline.py screenshots/l3-masks/artikelstamm.png --debug

***REMOVED*** 3. LLM-Analyse
python llm-field-analyzer.py artikelstamm.ocr.json --mask-name "Artikelstamm"

***REMOVED*** 4. Schema-Generator
python analyze-mask-fields.py
```

***REMOVED******REMOVED*** 📋 Zu erfassende Masken (15+)

***REMOVED******REMOVED******REMOVED*** ⭐⭐⭐⭐⭐ KRITISCH
- [x] Artikelstamm
- [ ] Kundenstamm
- [ ] Lieferschein
- [ ] Rechnung
- [ ] Auftrag
- [ ] Bestellung
- [ ] Lager-Bestand
- [ ] PSM-Abgabe (Agrar!)

***REMOVED******REMOVED******REMOVED*** ⭐⭐⭐⭐ WICHTIG
- [ ] Lieferantenstamm
- [ ] Angebot
- [ ] Wareneingang
- [ ] Kunden-Kontoauszug

***REMOVED******REMOVED******REMOVED*** ⭐⭐⭐ NICE-TO-HAVE
- [ ] Inventur
- [ ] Saatgut
- [ ] Dünger

***REMOVED******REMOVED*** 🔧 Module

***REMOVED******REMOVED******REMOVED*** 1. `ocr-pipeline.py`

**Funktion:** Screenshot → OCR → Strukturierte Felder

```python
from ocr_pipeline import L3MaskOCR

ocr = L3MaskOCR()
results = ocr.extract_fields("artikelstamm.png")

print(results['fields'])  ***REMOVED*** Liste erkannter Felder
print(results['tabs'])    ***REMOVED*** Liste erkannter Tabs
```

**Features:**
- Preprocessing (Graustufen, Kontrast, Rauschreduzierung)
- Bounding Boxes für präzise Feldposition
- Feldtyp-Erkennung (Lookup, Dropdown, Checkbox, etc.)
- Tab-Extraktion

***REMOVED******REMOVED******REMOVED*** 2. `llm-field-analyzer.py`

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

***REMOVED******REMOVED******REMOVED*** 3. `analyze-mask-fields.py`

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

***REMOVED******REMOVED******REMOVED*** 4. `auto-capture-all-masks.py`

**Funktion:** Orchestrierung - 15+ Masken automatisch erfassen

```bash
python auto-capture-all-masks.py
```

***REMOVED******REMOVED*** 📊 Erfolgsmetriken

- ✅ **100%** der L3-Masken gescreenshottet
- ✅ **95%+** OCR-Genauigkeit (manuelles Review)
- ✅ **Alle Schemas** importierbar in Mask Builder
- ✅ **SQL-Statements** direkt ausführbar in PostgreSQL

***REMOVED******REMOVED*** 🔗 Integration mit existierendem L3-Mapping

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

***REMOVED******REMOVED*** 🐛 Troubleshooting

***REMOVED******REMOVED******REMOVED*** Problem: Tesseract nicht gefunden

```
FileNotFoundError: [WinError 2] The system cannot find the file specified
```

**Lösung:**
```python
***REMOVED*** In ocr-pipeline.py:
ocr = L3MaskOCR(tesseract_path="C:/Program Files/Tesseract-OCR/tesseract.exe")
```

***REMOVED******REMOVED******REMOVED*** Problem: Niedrige OCR-Genauigkeit

**Lösung:**
1. Screenshot-Qualität erhöhen (höhere Auflösung)
2. Debug-Modus aktivieren: `--debug`
3. Preprocessing-Parameter anpassen (in `ocr-pipeline.py`)

***REMOVED******REMOVED******REMOVED*** Problem: LLM-Integration fehlt

**Lösung:**
```python
***REMOVED*** In llm-field-analyzer.py, _call_llm():
import openai

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)
```

***REMOVED******REMOVED*** 📚 Weiterführende Dokumentation

- [L3-Tabellenstruktur](../scripts/l3_tables_postgres.sql)
- [L3-Import-Mapping](../scripts/l3_import_mapping.json)
- [VALEO-NeuroERP Mask Builder](../docs/MASK-BUILDER-GUIDE.md)

***REMOVED******REMOVED*** 🤝 Workflow-Beispiel

```bash
***REMOVED*** Terminal 1: Browser öffnen
http://localhost:8090/guacamole/***REMOVED***/client/MQBjAHBvc3RncmVzcWw

***REMOVED*** Terminal 2: Pipeline starten
cd l3-migration-toolkit
python auto-capture-all-masks.py

***REMOVED*** Schritt 1: Artikelstamm
***REMOVED*** - In L3: ERFASSUNG → Artikel-Stamm öffnen
***REMOVED*** - Enter drücken
***REMOVED*** - Screenshot wird erstellt
***REMOVED*** - OCR + LLM analysiert (30s)
***REMOVED*** - JSON + SQL exportiert

***REMOVED*** Schritt 2: Kundenstamm
***REMOVED*** - In L3: ERFASSUNG → Kunden öffnen
***REMOVED*** - Enter drücken
***REMOVED*** ...

***REMOVED*** Nach 15+ Masken:
***REMOVED*** ✅ schemas/mask-builder/ enthält alle JSONs
***REMOVED*** ✅ schemas/sql/ enthält alle SQL-Statements
```

***REMOVED******REMOVED*** 📈 Status

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

