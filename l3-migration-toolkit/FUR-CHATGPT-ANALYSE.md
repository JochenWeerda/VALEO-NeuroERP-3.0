# L3-Screenshots für ChatGPT-Analyse

## 📸 Screenshots erstellt von Jochen

Speicherort: `l3-migration-toolkit/screenshots/l3-masks/`

## 🤖 Aufgabe für ChatGPT

**Analysiere jeden Screenshot und extrahiere ALLE Formularfelder!**

### Output-Format pro Maske:

```json
{
  "mask_id": "kundenstamm",
  "mask_name": "Kundenstamm",
  "l3_original": "Kunden",
  "valeo_route": "/verkauf/kunden-stamm",
  "priority": 5,
  "category": "Stammdaten",
  "fields": [
    {
      "id": "kunden_nr",
      "label": "Kundennummer",
      "label_de": "Kundennummer",
      "l3_original_field": "Kunden-Nr.",
      "type": "lookup",
      "required": true,
      "validation": "unique",
      "ui_hint": "with_search_button",
      "max_length": 20,
      "database_column": "kunden_nr",
      "tab": "allgemein"
    },
    {
      "id": "name1",
      "label": "Name 1",
      "label_de": "Name 1",
      "l3_original_field": "Name 1:",
      "type": "string",
      "required": true,
      "max_length": 100,
      "database_column": "name1",
      "tab": "kunden_anschrift"
    }
    // ... ALLE weiteren Felder
  ],
  "tabs": [
    {
      "id": "kunden_anschrift",
      "label": "Kunden-Anschrift",
      "fields": ["name1", "name2", "strasse", "plz", "ort", "tel", "email"]
    },
    {
      "id": "allgemein",
      "label": "Allgemein", 
      "fields": ["kunde_seit", "debitoren_konto", "kunden_gruppe"]
    }
  ],
  "relations": [
    {
      "table": "kunden_gruppen",
      "foreign_key": "kunden_gruppe_id",
      "display_field": "bezeichnung"
    }
  ]
}
```

### Wichtige Regeln:

1. **ALLE Felder erfassen** - keine überspringen!
2. **Feldtypen erkennen:**
   - `lookup` = Feld mit "..." Button
   - `select` = Dropdown (▼)
   - `boolean` = Checkbox
   - `date` = Datumsfeld
   - `number` = Numerisches Feld
   - `currency` = Preisfeld mit €
   - `string` = Textfeld
   - `text` = Mehrzeilig

3. **Tabs identifizieren** (oben in der Maske)
4. **Required-Felder** = Meist Primärschlüssel (Nummern-Felder)
5. **Relations** = Lookup-Felder → Foreign Keys

### Output-Dateien:

Für jede Maske erstellen:
1. **JSON-Schema:** `schemas/mask-builder/{maske}.json`
2. **SQL-Statement:** `schemas/sql/{maske}.sql`

## 📋 Zu analysierende Masken (Priorität)

### ⭐⭐⭐⭐⭐ KRITISCH
1. Artikelstamm
2. Kundenstamm
3. Lieferantenstamm
4. Lieferschein
5. Rechnung
6. Auftrag
7. Bestellung
8. PSM-Abgabe (Pflanzenschutzmittel!)

### ⭐⭐⭐⭐ WICHTIG
9. Lager-Bestand
10. Angebot
11. Wareneingang
12. Kunden-Kontoauszug

## 🔄 Workflow

1. **Jochen:** Erstellt Screenshots aller Masken
2. **ChatGPT:** Analysiert und erstellt JSON + SQL
3. **Import:** Schemas werden in VALEO-NeuroERP Mask Builder importiert
4. **Auto-Generate:** Frontend-Masken werden automatisch generiert

## 💾 Speicherorte

- **Screenshots:** `l3-migration-toolkit/screenshots/l3-masks/`
- **JSON-Schemas:** `l3-migration-toolkit/schemas/mask-builder/`
- **SQL-Statements:** `l3-migration-toolkit/schemas/sql/`
- **Mapping:** `l3-migration-toolkit/schemas/mappings/l3-to-valeo.json`

---

**Bereit für ChatGPT-Analyse!** 🚀

