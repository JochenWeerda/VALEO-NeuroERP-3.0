# Druck & Archiv

## Überblick

VALEO-NeuroERP bietet PDF-Druck und automatische Archivierung für alle Belege.

## Einzeldruck

### Beleg drucken

**1. Beleg öffnen:**
```
Navigation → Sales → Orders → SO-00001
```

**2. Druck-Button klicken:**
```
[Print] Button (oben rechts)
```

**3. PDF wird generiert:**
```
→ Download startet automatisch
→ Dateiname: SO-00001_2025-10-09.pdf
```

### Druck-Optionen

**Sprache wählen:**
```
[Print ▼] → Deutsch / English
```

**Seitengröße wählen:**
```
[Print ▼] → A4 / Letter
```

**Mit QR-Code:**
```
[Print ▼] → Mit Verifikations-QR-Code
→ QR-Code am Ende des Dokuments
→ Scannen zum Verifizieren
```

## Batch-Druck (Mehrere Belege)

### 1. Belege auswählen

```
Navigation → Sales → Orders
→ Checkboxen aktivieren für gewünschte Belege
→ [x] SO-00001
→ [x] SO-00002
→ [x] SO-00003
```

### 2. Batch-Druck starten

```
[Print Selected] Button
→ Dialog: "3 Belege werden gedruckt"
→ [Confirm]
```

### 3. ZIP-Download

```
→ Download startet: sales_orders_2025-10-09.zip
→ Enthält:
   - SO-00001_2025-10-09.pdf
   - SO-00002_2025-10-09.pdf
   - SO-00003_2025-10-09.pdf
```

## Archiv

### Automatische Archivierung

Alle gedruckten Belege werden automatisch archiviert:

- **Speicherort:** Server-seitig (nicht lokal)
- **Aufbewahrung:** 10 Jahre (gesetzlich)
- **Unveränderlich:** PDFs sind signiert und können nicht geändert werden

### Archiv durchsuchen

```
Navigation → Documents → Archive

Filter:
- Belegtyp: [Sales Order ▼]
- Zeitraum: [01.01.2025] bis [31.12.2025]
- Belegnummer: [SO-*]

[Search]
```

### Archiv-PDF herunterladen

```
Archiv-Liste → Beleg auswählen → [Download]
→ Original-PDF wird heruntergeladen
```

### Archiv-Historie

```
Beleg öffnen → Tab "Archive"
→ Liste aller Drucke:
   - 09.10.2025 14:30 - Max Mustermann - SHA256: abc123...
   - 08.10.2025 10:15 - Anna Schmidt - SHA256: def456...
```

## QR-Code-Verifikation

### QR-Code scannen

**1. PDF öffnen:**
```
→ QR-Code befindet sich am Ende des Dokuments
```

**2. Mit Smartphone scannen:**
```
→ Kamera-App öffnen
→ QR-Code scannen
→ Link öffnet sich automatisch
```

**3. Verifikations-Seite:**
```
✅ Dokument gültig
Belegnummer: SO-00001
Datum: 09.10.2025
Status: Posted
SHA256: abc123def456...
```

### Manuell verifizieren

```
Browser öffnen:
https://erp.valeo.example.com/verify/sales/SO-00001/abc123def456

→ Verifikations-Ergebnis wird angezeigt
```

## E-Mail-Versand

### Beleg per E-Mail versenden

**1. Beleg öffnen:**
```
Navigation → Sales → Orders → SO-00001
```

**2. E-Mail-Button klicken:**
```
[Email] Button
→ Dialog öffnet sich
```

**3. E-Mail-Details eingeben:**
```
An: kunde@example.com
CC: (optional)
Betreff: Auftragsbestätigung SO-00001
Nachricht: (optional, Vorlage wird verwendet)

[x] PDF anhängen
[x] QR-Code einbinden

[Send]
```

**4. Bestätigung:**
```
✅ E-Mail erfolgreich versendet
```

## Druck-Historie

### Wer hat wann gedruckt?

```
Beleg öffnen → Tab "History"
→ Audit-Trail:
   - 09.10.2025 14:30 - Max Mustermann - Gedruckt (PDF)
   - 09.10.2025 14:35 - Max Mustermann - Per E-Mail versendet
   - 08.10.2025 10:15 - Anna Schmidt - Gedruckt (PDF)
```

## Berechtigungen

| Rolle | Drucken | Batch-Druck | Archiv-Zugriff | E-Mail |
|-------|---------|-------------|----------------|--------|
| Operator | ✅ | ✅ | ✅ (eigene) | ✅ |
| Manager | ✅ | ✅ | ✅ (alle) | ✅ |
| Accountant | ✅ | ✅ | ✅ (alle) | ✅ |
| Admin | ✅ | ✅ | ✅ (alle) | ✅ |

## Troubleshooting

### Problem: PDF-Download startet nicht

**Ursache:** Browser blockiert Download

**Lösung:** 
1. Pop-up-Blocker deaktivieren
2. Browser-Einstellungen prüfen
3. Rechtsklick → "Link speichern unter..."

### Problem: QR-Code nicht lesbar

**Ursache:** Zu klein gedruckt oder schlechte Qualität

**Lösung:**
1. PDF in höherer Auflösung drucken
2. QR-Code vergrößern (Admin-Einstellung)
3. Manuell verifizieren (siehe oben)

### Problem: E-Mail kommt nicht an

**Ursache:** Spam-Filter oder falsche E-Mail-Adresse

**Lösung:**
1. E-Mail-Adresse prüfen
2. Spam-Ordner prüfen
3. IT-Admin kontaktieren (SMTP-Konfiguration)

### Problem: "Archive not found"

**Ursache:** Beleg wurde noch nie gedruckt

**Lösung:** Beleg einmal drucken, dann ist er im Archiv

## Tipps & Tricks

### Schnelldruck mit Tastatur

```
Beleg öffnen → Strg+P (Windows) / Cmd+P (Mac)
→ PDF-Druck wird gestartet
```

### Standardsprache ändern

```
Profil → Einstellungen → Sprache → [Deutsch ▼]
→ Alle PDFs werden in dieser Sprache gedruckt
```

### Batch-Druck mit Filter

```
Orders-Liste → Filter: Status = "Approved"
→ [Select All] (oben)
→ [Print Selected]
→ Alle freigegebenen Aufträge werden gedruckt
```

## Support

Bei Fragen: support@valeo-erp.com

