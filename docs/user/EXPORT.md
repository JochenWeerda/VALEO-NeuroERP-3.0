# CSV/XLSX-Export

## Überblick

VALEO-NeuroERP ermöglicht den Export von Belegen und Listen in CSV- und XLSX-Formaten.

## Einzelexport

### Beleg exportieren

**1. Beleg öffnen:**
```
Navigation → Sales → Orders → SO-00001
```

**2. Export-Button klicken:**
```
[Export ▼] → CSV / XLSX
```

**3. Download:**
```
→ Datei: SO-00001.csv oder SO-00001.xlsx
```

### Export-Inhalt

**Header-Daten:**
- Belegnummer
- Datum
- Kunde/Lieferant
- Status
- Gesamt

**Positionen:**
- Artikel-Nr.
- Beschreibung
- Menge
- Einzelpreis
- Gesamt

## Listen-Export

### Beleg-Liste exportieren

**1. Liste öffnen:**
```
Navigation → Sales → Orders
```

**2. Filter anwenden (optional):**
```
Status: [Approved ▼]
Zeitraum: [01.01.2025] bis [31.12.2025]
Kunde: [ACME Corp]
```

**3. Export starten:**
```
[Export List ▼] → CSV / XLSX
```

**4. Download:**
```
→ Datei: sales_orders_2025-10-09.csv
→ Enthält alle gefilterten Belege
```

### Spalten-Auswahl

**Standard-Spalten:**
- Belegnummer
- Datum
- Kunde
- Status
- Gesamt

**Erweiterte Spalten:**
```
[Export List ▼] → Customize Columns
→ Dialog öffnet sich

[x] Belegnummer
[x] Datum
[x] Kunde
[x] Status
[x] Gesamt
[ ] Erstellt von
[ ] Erstellt am
[x] Zahlungsziel
[ ] Lieferadresse

[Export]
```

## Batch-Export (Mehrere Belege)

### 1. Belege auswählen

```
Orders-Liste
→ [x] SO-00001
→ [x] SO-00002
→ [x] SO-00003
```

### 2. Export starten

```
[Export Selected ▼] → CSV / XLSX
```

### 3. Export-Optionen

**Einzelne Dateien:**
```
→ ZIP-Download: sales_orders_2025-10-09.zip
→ Enthält:
   - SO-00001.csv
   - SO-00002.csv
   - SO-00003.csv
```

**Zusammengefasst:**
```
→ Eine Datei: sales_orders_2025-10-09.csv
→ Alle Belege in einer Tabelle
```

## XLSX-Features

### Formatierung

**Automatische Formatierung:**
- Zahlen: Tausender-Trennzeichen
- Währung: € Symbol
- Datum: TT.MM.JJJJ
- Prozent: % Symbol

**Farben:**
- Header: Blau (Firmenfarbe)
- Summen: Fett
- Negative Werte: Rot

### Formeln

**Summen-Zeile:**
```
→ Letzte Zeile enthält Summen
→ Excel-Formel: =SUM(E2:E100)
```

**Berechnungen:**
```
→ Gesamt = Menge × Einzelpreis
→ Excel-Formel: =C2*D2
```

### Mehrere Sheets

**Sheet 1: Header**
```
Belegnummer | Datum | Kunde | Status | Gesamt
SO-00001 | 09.10.2025 | ACME Corp | Approved | 1.500,00 €
```

**Sheet 2: Positionen**
```
Belegnummer | Pos | Artikel-Nr. | Beschreibung | Menge | Preis
SO-00001 | 1 | SKU-001 | Widget A | 10 | 50,00 €
SO-00001 | 2 | SKU-002 | Widget B | 20 | 25,00 €
```

## API-Export

### Programmatischer Export

```bash
# CSV-Export
curl -H "Authorization: Bearer $TOKEN" \
  "https://erp.valeo.example.com/api/export/csv/sales?from=2025-01-01&to=2025-12-31" \
  -o sales_2025.csv

# XLSX-Export
curl -H "Authorization: Bearer $TOKEN" \
  "https://erp.valeo.example.com/api/export/xlsx/sales?from=2025-01-01&to=2025-12-31" \
  -o sales_2025.xlsx
```

### Query-Parameter

```
?from=2025-01-01          # Start-Datum
&to=2025-12-31            # End-Datum
&status=approved          # Filter nach Status
&customer_id=CUST-001     # Filter nach Kunde
&columns=number,date,total # Spalten-Auswahl
&format=csv               # Format (csv/xlsx)
```

## Automatisierte Exports

### Scheduled Exports (Admin)

**Konfiguration:**
```
Admin → Settings → Scheduled Exports

Name: Monatlicher Sales-Report
Format: XLSX
Zeitplan: Monatlich (1. des Monats, 08:00)
Filter: Status = Posted, Vormonat
E-Mail an: accounting@valeo.example.com

[Save]
```

**Ergebnis:**
```
→ Jeden 1. des Monats um 08:00
→ Export wird erstellt
→ E-Mail mit Anhang versendet
```

## Berechtigungen

| Rolle | Einzelexport | Listen-Export | Batch-Export | API-Export |
|-------|--------------|---------------|--------------|------------|
| Operator | ✅ (eigene) | ✅ (eigene) | ✅ (eigene) | ❌ |
| Manager | ✅ | ✅ | ✅ | ✅ |
| Accountant | ✅ | ✅ | ✅ | ✅ |
| Admin | ✅ | ✅ | ✅ | ✅ |

**Scope:** `docs:export`

## Datenschutz

### GDPR-Konformität

**Personenbezogene Daten:**
- Kunden-Namen
- Adressen
- E-Mail-Adressen

**Hinweis:**
```
⚠️ Exports enthalten personenbezogene Daten
→ Sicher speichern (verschlüsselt)
→ Nach Verwendung löschen
→ Nicht per unverschlüsselter E-Mail versenden
```

### Audit-Trail

Alle Exports werden protokolliert:

```
Admin → Audit Log → Export-Events

09.10.2025 14:30 - Max Mustermann - Export: sales_orders.csv (50 Belege)
08.10.2025 10:15 - Anna Schmidt - Export: SO-00001.xlsx
```

## Troubleshooting

### Problem: Excel zeigt falsche Zahlen

**Ursache:** Locale-Einstellung (Komma vs. Punkt)

**Lösung:**
1. CSV in Excel öffnen: Daten → Aus Text/CSV
2. Trennzeichen: Semikolon (;)
3. Dezimaltrennzeichen: Komma (,)

### Problem: Umlaute falsch dargestellt

**Ursache:** Encoding-Problem (UTF-8 vs. ISO-8859-1)

**Lösung:**
1. CSV in Notepad++ öffnen
2. Encoding → UTF-8 (ohne BOM)
3. Speichern und erneut in Excel öffnen

### Problem: Export dauert sehr lange

**Ursache:** Zu viele Belege (> 10.000)

**Lösung:**
1. Zeitraum einschränken (z.B. nur 1 Monat)
2. Filter anwenden
3. API-Export mit Pagination verwenden

### Problem: "Rate limit exceeded"

**Ursache:** Zu viele Exports in kurzer Zeit

**Lösung:**
1. 1 Minute warten
2. Exports zusammenfassen (Batch statt Einzel)
3. Admin kontaktieren (Rate-Limit erhöhen)

## Tipps & Tricks

### Excel-Pivot-Tabelle

```
1. XLSX-Export öffnen
2. Daten markieren
3. Einfügen → PivotTable
4. Zeilen: Kunde
5. Werte: Summe von Gesamt
→ Umsatz pro Kunde
```

### CSV in Google Sheets

```
1. Google Sheets öffnen
2. Datei → Importieren
3. CSV-Datei hochladen
4. Trennzeichen: Automatisch erkennen
5. [Importieren]
```

### Power BI Integration

```
1. Power BI Desktop öffnen
2. Daten abrufen → Web
3. URL: https://erp.valeo.example.com/api/export/csv/sales?from=2025-01-01
4. Authentifizierung: Bearer Token
5. [Laden]
→ Automatische Aktualisierung möglich
```

## Support

Bei Fragen: support@valeo-erp.com

