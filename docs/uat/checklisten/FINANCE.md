# UAT Checkliste: Finance Domain

## Buchungsjournal (`/finance/bookings/new`)

### Sichtprüfung
- [ ] Formular: Datum, Konto, Soll, Haben, Text
- [ ] Buttons: Speichern, Abbrechen

### CRUD - Create
- [ ] Fülle Felder: Datum, Konto (Lookup), Soll, Haben, Text
- [ ] Speichern → Erfolgsmeldung
- [ ] Buchung in Journal-Liste sichtbar (falls vorhanden)

### Validierung
- [ ] Soll + Haben müssen ausgeglichen sein
- [ ] Fehler bei Ungleichgewicht → Toast/Fehlermeldung

### DATEV-Export (Mock)
- [ ] Button "DATEV-Export" sichtbar (oder in Menü)
- [ ] Click → CSV-Download (DATEV-Format-Mock)
- [ ] Dateiname: `datev-export-YYYY-MM-DD.csv`

---

## Debitoren (`/fibu/debitoren`)

### Sichtprüfung
- [ ] Tabelle: Debitor-Nr., Name, Saldo, Überfällig
- [ ] Buttons: Neu, Export

### CRUD
- [ ] Neu → Debitor-Formular
- [ ] Felder: Nummer, Name, Adresse, Kreditlimit
- [ ] Speichern funktioniert

### OP-Verwaltung
- [ ] Navigation zu `/fibu/op-verwaltung`
- [ ] Tabelle: Rechnungsnr., Debitor, Betrag, Fälligkeit, Status
- [ ] Filter nach Überfällig

### Zahlungseingang
- [ ] Button "Zahlung erfassen"
- [ ] Formular: Rechnung, Betrag, Datum
- [ ] Speichern → OP-Status = Bezahlt

---

## Offene Posten (`/fibu/offene-posten`)

### Sichtprüfung
- [ ] Tabelle: Rechnungsnr., Kunde, Betrag, Fälligkeit, Tage überfällig
- [ ] Filter: Überfällig, Alle

### Export
- [ ] Export → CSV mit allen OPs
- [ ] Spalten: Nummer, Kunde, Betrag, Fälligkeit, Status

---

## Zahlungsläufe (`/fibu/zahlungslaeufe`)

### Sichtprüfung
- [ ] Tabelle: Lauf-Nr., Datum, Anzahl Zahlungen, Summe
- [ ] Buttons: Neu, Export

### CRUD
- [ ] Neu → Zahlungsvorschlag generieren
- [ ] Liste offener OPs mit Fälligkeit heute/gestern
- [ ] Auswahl → SEPA-Datei generieren

### SEPA-Export (Mock)
- [ ] Button "SEPA-XML generieren"
- [ ] Download: `sepa-YYYY-MM-DD.xml`
- [ ] Format: SEPA pain.001 (Mock)

---

## Kreditoren (`/fibu/kreditoren`)

### Sichtprüfung
- [ ] Tabelle: Kreditor-Nr., Name, Saldo
- [ ] Buttons: Neu, Export

### CRUD
- [ ] Neu → Kreditor-Formular
- [ ] Speichern funktioniert

---

## Hauptbuch (`/fibu/hauptbuch`)

### Sichtprüfung
- [ ] Tabelle: Konto-Nr., Bezeichnung, Soll, Haben, Saldo
- [ ] Export → CSV

---

## Kontenplan (`/fibu/kontenplan`)

### Sichtprüfung
- [ ] Tabelle: Konto, Bezeichnung, Typ (Aktiv/Passiv/GuV)
- [ ] CRUD funktioniert

---

**Ergebnis:** ✅ Alle Checks bestanden | ❌ Fehler in Ticket `UAT-XXXX`

