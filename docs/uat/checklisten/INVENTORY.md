# UAT Checkliste: Inventory Domain

## Artikel-Liste (`/artikel/liste`)

### Sichtprüfung
- [ ] Tabelle: Artikelnr., Bezeichnung, Einheit, Preis, Bestand
- [ ] Buttons: Neu, Export, Drucken

### CRUD - Create
- [ ] Klicke "Neu" → Navigation zu `/artikel/stamm`
- [ ] Formular: Artikelnr., Bezeichnung, Einheit, VK-Preis, EK-Preis
- [ ] Speichern → Erfolgsmeldung
- [ ] Neuer Artikel in Liste

### CRUD - Read/List
- [ ] Filter nach Artikelgruppe
- [ ] Suche nach Artikelnummer/Bezeichnung
- [ ] Paging funktioniert

### CRUD - Update
- [ ] Detail-Seite öffnen
- [ ] Preis ändern
- [ ] Speichern → Änderung reflektiert

### CRUD - Delete
- [ ] Löschen mit Bestätigung
- [ ] Eintrag aus Liste entfernt (oder Status = Inaktiv)

### Validierung
- [ ] VK-Preis > EK-Preis (Warnung, nicht blockierend)
- [ ] Artikelnummer eindeutig (Fehler bei Duplikat)

### Print/Export
- [ ] Export → CSV mit allen Feldern
- [ ] Drucken → Artikel-Übersicht als PDF

### Fallback-Level
- [ ] Export → `FB:LEVEL=2` oder `FB:LEVEL=3`

---

## Artikel-Stamm (`/artikel/stamm`)

### Formular
- [ ] Tabs: Stammdaten, Preise, Lager, Lieferanten
- [ ] Stammdaten: Artikelnr., Bezeichnung, Einheit, Artikelgruppe
- [ ] Preise: VK-Preis, EK-Preis, Rabattgruppe
- [ ] Lager: Mindestbestand, Meldebestand, Lagerort
- [ ] Lieferanten: Standard-Lieferant (Lookup)

### Speichern
- [ ] Alle Tabs speichern korrekt
- [ ] Validierung aktiv

---

## Lagerbewegungen (`/lager/bewegungen`)

### Sichtprüfung
- [ ] Tabelle: Datum, Artikel, Menge, Typ (Zugang/Abgang), Lagerort
- [ ] Buttons: Neu, Export

### CRUD
- [ ] Neu → Lagerbewegung-Formular
- [ ] Felder: Artikel (Lookup), Menge, Typ, Lagerort
- [ ] Speichern → Bestand aktualisiert

### FIFO/FEFO (Mock)
- [ ] Abgang → Älteste Charge zuerst (FIFO)
- [ ] Mindesthaltbarkeit → Früheste MHD zuerst (FEFO)

---

## Lagerbestand (`/lager/bestand`)

### Sichtprüfung
- [ ] Tabelle: Artikel, Lagerort, Bestand, Wert
- [ ] Filter nach Lagerort

### Export
- [ ] Export → CSV mit Bestandsliste

---

## Inventory (`/inventory`)

### Sichtprüfung
- [ ] Dashboard: Gesamtbestand, Warenwert, Mindestbestand unterschritten
- [ ] Buttons: Inventur, Korrektur

### Inventur
- [ ] Button "Inventur starten"
- [ ] Formular: Lagerort, Artikel (alle/Auswahl)
- [ ] Erfassung: Gezählte Menge
- [ ] Differenz-Berechnung: Soll - Ist
- [ ] Buchen → Bestand korrigiert

---

## Charge-Liste (`/charge/liste`)

### Sichtprüfung
- [ ] Tabelle: Charge-Nr., Artikel, Menge, MHD, Lagerort
- [ ] Buttons: Neu, Export

### CRUD
- [ ] Neu → Charge-Formular
- [ ] Felder: Charge-Nr., Artikel, Menge, MHD
- [ ] Speichern funktioniert

### Rückverfolgung (`/charge/rueckverfolgung`)
- [ ] Eingabe: Charge-Nr.
- [ ] Anzeige: Lieferant, Wareneingang, Verwendungen (Verkäufe)
- [ ] Trace-Back & Trace-Forward

---

**Ergebnis:** ✅ Alle Checks bestanden | ❌ Fehler in Ticket `UAT-XXXX`

