***REMOVED*** UAT Checkliste: CRM Domain

***REMOVED******REMOVED*** Kontakte-Liste (`/crm/kontakte-liste`)

***REMOVED******REMOVED******REMOVED*** Sichtprüfung
- [ ] Tabelle: Name, Firma, E-Mail, Telefon, Typ (Kunde/Lieferant/Lead)
- [ ] Buttons: Neu, Export, Drucken

***REMOVED******REMOVED******REMOVED*** CRUD - Create
- [ ] Klicke "Neu" → Navigation zu `/crm/kontakt/neu` oder Modal
- [ ] Formular: Vorname, Nachname, Firma, E-Mail, Telefon
- [ ] Speichern → Erfolgsmeldung
- [ ] Neuer Kontakt in Liste

***REMOVED******REMOVED******REMOVED*** CRUD - Read/List
- [ ] Filter nach Typ (Kunde/Lieferant)
- [ ] Suche nach Name
- [ ] Paging funktioniert

***REMOVED******REMOVED******REMOVED*** CRUD - Update
- [ ] Detail-Seite (`/crm/kontakt/:id`)
- [ ] Felder ändern
- [ ] Speichern → Änderung reflektiert

***REMOVED******REMOVED******REMOVED*** CRUD - Delete
- [ ] Löschen mit Bestätigung
- [ ] Soft-Delete (Status = Inaktiv) oder Hard-Delete

***REMOVED******REMOVED******REMOVED*** Print/Export
- [ ] Export → CSV mit allen Feldern
- [ ] Drucken → Kontaktliste als PDF

***REMOVED******REMOVED******REMOVED*** Fallback-Level
- [ ] Export → `FB:LEVEL=2` oder `FB:LEVEL=3`
- [ ] Drucken → `FB:LEVEL=2` oder `FB:LEVEL=3`

---

***REMOVED******REMOVED*** Leads (`/crm/leads`)

***REMOVED******REMOVED******REMOVED*** Sichtprüfung
- [ ] Tabelle: Lead-Name, Quelle, Status, Bewertung
- [ ] Buttons: Neu, Export

***REMOVED******REMOVED******REMOVED*** CRUD
- [ ] Neu → Lead-Formular
- [ ] Felder: Name, Quelle, Status (Neu/Qualifiziert/Konvertiert)
- [ ] Speichern funktioniert

***REMOVED******REMOVED******REMOVED*** Workflow
- [ ] Status-Übergänge: Neu → Qualifiziert → Konvertiert
- [ ] Ungültiger Wechsel blockiert

***REMOVED******REMOVED******REMOVED*** Lead-Conversion
- [ ] Button "In Kunde umwandeln"
- [ ] Lead → Kontakt mit Typ=Kunde
- [ ] Lead-Status = Konvertiert

---

***REMOVED******REMOVED*** Aktivitäten (`/crm/aktivitaeten`)

***REMOVED******REMOVED******REMOVED*** Sichtprüfung
- [ ] Tabelle: Datum, Typ (Anruf/E-Mail/Besuch), Kontakt, Notizen
- [ ] Buttons: Neu, Export

***REMOVED******REMOVED******REMOVED*** CRUD
- [ ] Neu → Aktivität-Formular
- [ ] Felder: Typ, Kontakt (Lookup), Datum, Notizen
- [ ] Speichern funktioniert

***REMOVED******REMOVED******REMOVED*** Besuchsbericht
- [ ] Typ = Besuch
- [ ] Notizen-Feld mit Rich-Text (oder Plain)
- [ ] Speichern → Aktivität in Liste

---

***REMOVED******REMOVED*** Betriebsprofile (`/crm/betriebsprofile-liste`)

***REMOVED******REMOVED******REMOVED*** Sichtprüfung
- [ ] Tabelle: Betrieb, Betriebsform, Fläche, Tierbestand
- [ ] Buttons: Neu, Export

***REMOVED******REMOVED******REMOVED*** CRUD
- [ ] Neu → Betriebsprofil-Formular
- [ ] Felder: Name, Betriebsform (Ackerbau/Viehzucht), Fläche, Tiere
- [ ] Speichern funktioniert

***REMOVED******REMOVED******REMOVED*** Detail
- [ ] `/crm/betriebsprofil/:id`
- [ ] Tabs: Stammdaten, Flächen, Tiere, Dokumente
- [ ] Alle Tabs laden

---

**Ergebnis:** ✅ Alle Checks bestanden | ❌ Fehler in Ticket `UAT-XXXX`

