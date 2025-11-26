***REMOVED*** UAT Checkliste: Finance Domain

***REMOVED******REMOVED*** Buchungsjournal (`/finance/bookings/new`)

***REMOVED******REMOVED******REMOVED*** Sichtprüfung
- [ ] Formular: Datum, Konto, Soll, Haben, Text
- [ ] Buttons: Speichern, Abbrechen

***REMOVED******REMOVED******REMOVED*** CRUD - Create
- [ ] Fülle Felder: Datum, Konto (Lookup), Soll, Haben, Text
- [ ] Speichern → Erfolgsmeldung
- [ ] Buchung in Journal-Liste sichtbar (falls vorhanden)

***REMOVED******REMOVED******REMOVED*** Validierung
- [ ] Soll + Haben müssen ausgeglichen sein
- [ ] Fehler bei Ungleichgewicht → Toast/Fehlermeldung

***REMOVED******REMOVED******REMOVED*** DATEV-Export (Mock)
- [ ] Button "DATEV-Export" sichtbar (oder in Menü)
- [ ] Click → CSV-Download (DATEV-Format-Mock)
- [ ] Dateiname: `datev-export-YYYY-MM-DD.csv`

---

***REMOVED******REMOVED*** Debitoren (`/fibu/debitoren`)

***REMOVED******REMOVED******REMOVED*** Sichtprüfung
- [ ] Tabelle: Debitor-Nr., Name, Saldo, Überfällig
- [ ] Buttons: Neu, Export

***REMOVED******REMOVED******REMOVED*** CRUD
- [ ] Neu → Debitor-Formular
- [ ] Felder: Nummer, Name, Adresse, Kreditlimit
- [ ] Speichern funktioniert

***REMOVED******REMOVED******REMOVED*** OP-Verwaltung
- [ ] Navigation zu `/fibu/op-verwaltung`
- [ ] Tabelle: Rechnungsnr., Debitor, Betrag, Fälligkeit, Status
- [ ] Filter nach Überfällig

***REMOVED******REMOVED******REMOVED*** Zahlungseingang
- [ ] Button "Zahlung erfassen"
- [ ] Formular: Rechnung, Betrag, Datum
- [ ] Speichern → OP-Status = Bezahlt

---

***REMOVED******REMOVED*** Offene Posten (`/fibu/offene-posten`)

***REMOVED******REMOVED******REMOVED*** Sichtprüfung
- [ ] Tabelle: Rechnungsnr., Kunde, Betrag, Fälligkeit, Tage überfällig
- [ ] Filter: Überfällig, Alle

***REMOVED******REMOVED******REMOVED*** Export
- [ ] Export → CSV mit allen OPs
- [ ] Spalten: Nummer, Kunde, Betrag, Fälligkeit, Status

---

***REMOVED******REMOVED*** Zahlungsläufe (`/fibu/zahlungslaeufe`)

***REMOVED******REMOVED******REMOVED*** Sichtprüfung
- [ ] Tabelle: Lauf-Nr., Datum, Anzahl Zahlungen, Summe
- [ ] Buttons: Neu, Export

***REMOVED******REMOVED******REMOVED*** CRUD
- [ ] Neu → Zahlungsvorschlag generieren
- [ ] Liste offener OPs mit Fälligkeit heute/gestern
- [ ] Auswahl → SEPA-Datei generieren

***REMOVED******REMOVED******REMOVED*** SEPA-Export (Mock)
- [ ] Button "SEPA-XML generieren"
- [ ] Download: `sepa-YYYY-MM-DD.xml`
- [ ] Format: SEPA pain.001 (Mock)

---

***REMOVED******REMOVED*** Kreditoren (`/fibu/kreditoren`)

***REMOVED******REMOVED******REMOVED*** Sichtprüfung
- [ ] Tabelle: Kreditor-Nr., Name, Saldo
- [ ] Buttons: Neu, Export

***REMOVED******REMOVED******REMOVED*** CRUD
- [ ] Neu → Kreditor-Formular
- [ ] Speichern funktioniert

---

***REMOVED******REMOVED*** Hauptbuch (`/fibu/hauptbuch`)

***REMOVED******REMOVED******REMOVED*** Sichtprüfung
- [ ] Tabelle: Konto-Nr., Bezeichnung, Soll, Haben, Saldo
- [ ] Export → CSV

---

***REMOVED******REMOVED*** Kontenplan (`/fibu/kontenplan`)

***REMOVED******REMOVED******REMOVED*** Sichtprüfung
- [ ] Tabelle: Konto, Bezeichnung, Typ (Aktiv/Passiv/GuV)
- [ ] CRUD funktioniert

---

**Ergebnis:** ✅ Alle Checks bestanden | ❌ Fehler in Ticket `UAT-XXXX`

