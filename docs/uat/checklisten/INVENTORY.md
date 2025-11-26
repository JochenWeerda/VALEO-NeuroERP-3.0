***REMOVED*** UAT Checkliste: Inventory Domain

***REMOVED******REMOVED*** Artikel-Liste (`/artikel/liste`)

***REMOVED******REMOVED******REMOVED*** Sichtprüfung
- [ ] Tabelle: Artikelnr., Bezeichnung, Einheit, Preis, Bestand
- [ ] Buttons: Neu, Export, Drucken

***REMOVED******REMOVED******REMOVED*** CRUD - Create
- [ ] Klicke "Neu" → Navigation zu `/artikel/stamm`
- [ ] Formular: Artikelnr., Bezeichnung, Einheit, VK-Preis, EK-Preis
- [ ] Speichern → Erfolgsmeldung
- [ ] Neuer Artikel in Liste

***REMOVED******REMOVED******REMOVED*** CRUD - Read/List
- [ ] Filter nach Artikelgruppe
- [ ] Suche nach Artikelnummer/Bezeichnung
- [ ] Paging funktioniert

***REMOVED******REMOVED******REMOVED*** CRUD - Update
- [ ] Detail-Seite öffnen
- [ ] Preis ändern
- [ ] Speichern → Änderung reflektiert

***REMOVED******REMOVED******REMOVED*** CRUD - Delete
- [ ] Löschen mit Bestätigung
- [ ] Eintrag aus Liste entfernt (oder Status = Inaktiv)

***REMOVED******REMOVED******REMOVED*** Validierung
- [ ] VK-Preis > EK-Preis (Warnung, nicht blockierend)
- [ ] Artikelnummer eindeutig (Fehler bei Duplikat)

***REMOVED******REMOVED******REMOVED*** Print/Export
- [ ] Export → CSV mit allen Feldern
- [ ] Drucken → Artikel-Übersicht als PDF

***REMOVED******REMOVED******REMOVED*** Fallback-Level
- [ ] Export → `FB:LEVEL=2` oder `FB:LEVEL=3`

---

***REMOVED******REMOVED*** Artikel-Stamm (`/artikel/stamm`)

***REMOVED******REMOVED******REMOVED*** Formular
- [ ] Tabs: Stammdaten, Preise, Lager, Lieferanten
- [ ] Stammdaten: Artikelnr., Bezeichnung, Einheit, Artikelgruppe
- [ ] Preise: VK-Preis, EK-Preis, Rabattgruppe
- [ ] Lager: Mindestbestand, Meldebestand, Lagerort
- [ ] Lieferanten: Standard-Lieferant (Lookup)

***REMOVED******REMOVED******REMOVED*** Speichern
- [ ] Alle Tabs speichern korrekt
- [ ] Validierung aktiv

---

***REMOVED******REMOVED*** Lagerbewegungen (`/lager/bewegungen`)

***REMOVED******REMOVED******REMOVED*** Sichtprüfung
- [ ] Tabelle: Datum, Artikel, Menge, Typ (Zugang/Abgang), Lagerort
- [ ] Buttons: Neu, Export

***REMOVED******REMOVED******REMOVED*** CRUD
- [ ] Neu → Lagerbewegung-Formular
- [ ] Felder: Artikel (Lookup), Menge, Typ, Lagerort
- [ ] Speichern → Bestand aktualisiert

***REMOVED******REMOVED******REMOVED*** FIFO/FEFO (Mock)
- [ ] Abgang → Älteste Charge zuerst (FIFO)
- [ ] Mindesthaltbarkeit → Früheste MHD zuerst (FEFO)

---

***REMOVED******REMOVED*** Lagerbestand (`/lager/bestand`)

***REMOVED******REMOVED******REMOVED*** Sichtprüfung
- [ ] Tabelle: Artikel, Lagerort, Bestand, Wert
- [ ] Filter nach Lagerort

***REMOVED******REMOVED******REMOVED*** Export
- [ ] Export → CSV mit Bestandsliste

---

***REMOVED******REMOVED*** Inventory (`/inventory`)

***REMOVED******REMOVED******REMOVED*** Sichtprüfung
- [ ] Dashboard: Gesamtbestand, Warenwert, Mindestbestand unterschritten
- [ ] Buttons: Inventur, Korrektur

***REMOVED******REMOVED******REMOVED*** Inventur
- [ ] Button "Inventur starten"
- [ ] Formular: Lagerort, Artikel (alle/Auswahl)
- [ ] Erfassung: Gezählte Menge
- [ ] Differenz-Berechnung: Soll - Ist
- [ ] Buchen → Bestand korrigiert

---

***REMOVED******REMOVED*** Charge-Liste (`/charge/liste`)

***REMOVED******REMOVED******REMOVED*** Sichtprüfung
- [ ] Tabelle: Charge-Nr., Artikel, Menge, MHD, Lagerort
- [ ] Buttons: Neu, Export

***REMOVED******REMOVED******REMOVED*** CRUD
- [ ] Neu → Charge-Formular
- [ ] Felder: Charge-Nr., Artikel, Menge, MHD
- [ ] Speichern funktioniert

***REMOVED******REMOVED******REMOVED*** Rückverfolgung (`/charge/rueckverfolgung`)
- [ ] Eingabe: Charge-Nr.
- [ ] Anzeige: Lieferant, Wareneingang, Verwendungen (Verkäufe)
- [ ] Trace-Back & Trace-Forward

---

**Ergebnis:** ✅ Alle Checks bestanden | ❌ Fehler in Ticket `UAT-XXXX`

