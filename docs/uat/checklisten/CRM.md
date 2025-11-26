# UAT Checkliste: CRM Domain

## Kontakte-Liste (`/crm/kontakte-liste`)

### Sichtprüfung
- [ ] Tabelle: Name, Firma, E-Mail, Telefon, Typ (Kunde/Lieferant/Lead)
- [ ] Buttons: Neu, Export, Drucken

### CRUD - Create
- [ ] Klicke "Neu" → Navigation zu `/crm/kontakt/neu` oder Modal
- [ ] Formular: Vorname, Nachname, Firma, E-Mail, Telefon
- [ ] Speichern → Erfolgsmeldung
- [ ] Neuer Kontakt in Liste

### CRUD - Read/List
- [ ] Filter nach Typ (Kunde/Lieferant)
- [ ] Suche nach Name
- [ ] Paging funktioniert

### CRUD - Update
- [ ] Detail-Seite (`/crm/kontakt/:id`)
- [ ] Felder ändern
- [ ] Speichern → Änderung reflektiert

### CRUD - Delete
- [ ] Löschen mit Bestätigung
- [ ] Soft-Delete (Status = Inaktiv) oder Hard-Delete

### Print/Export
- [ ] Export → CSV mit allen Feldern
- [ ] Drucken → Kontaktliste als PDF

### Fallback-Level
- [ ] Export → `FB:LEVEL=2` oder `FB:LEVEL=3`
- [ ] Drucken → `FB:LEVEL=2` oder `FB:LEVEL=3`

---

## Leads (`/crm/leads`)

### Sichtprüfung
- [ ] Tabelle: Lead-Name, Quelle, Status, Bewertung
- [ ] Buttons: Neu, Export

### CRUD
- [ ] Neu → Lead-Formular
- [ ] Felder: Name, Quelle, Status (Neu/Qualifiziert/Konvertiert)
- [ ] Speichern funktioniert

### Workflow
- [ ] Status-Übergänge: Neu → Qualifiziert → Konvertiert
- [ ] Ungültiger Wechsel blockiert

### Lead-Conversion
- [ ] Button "In Kunde umwandeln"
- [ ] Lead → Kontakt mit Typ=Kunde
- [ ] Lead-Status = Konvertiert

---

## Aktivitäten (`/crm/aktivitaeten`)

### Sichtprüfung
- [ ] Tabelle: Datum, Typ (Anruf/E-Mail/Besuch), Kontakt, Notizen
- [ ] Buttons: Neu, Export

### CRUD
- [ ] Neu → Aktivität-Formular
- [ ] Felder: Typ, Kontakt (Lookup), Datum, Notizen
- [ ] Speichern funktioniert

### Besuchsbericht
- [ ] Typ = Besuch
- [ ] Notizen-Feld mit Rich-Text (oder Plain)
- [ ] Speichern → Aktivität in Liste

---

## Betriebsprofile (`/crm/betriebsprofile-liste`)

### Sichtprüfung
- [ ] Tabelle: Betrieb, Betriebsform, Fläche, Tierbestand
- [ ] Buttons: Neu, Export

### CRUD
- [ ] Neu → Betriebsprofil-Formular
- [ ] Felder: Name, Betriebsform (Ackerbau/Viehzucht), Fläche, Tiere
- [ ] Speichern funktioniert

### Detail
- [ ] `/crm/betriebsprofil/:id`
- [ ] Tabs: Stammdaten, Flächen, Tiere, Dokumente
- [ ] Alle Tabs laden

---

**Ergebnis:** ✅ Alle Checks bestanden | ❌ Fehler in Ticket `UAT-XXXX`

