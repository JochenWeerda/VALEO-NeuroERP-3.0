***REMOVED*** UAT Checkliste: Sales Domain

***REMOVED******REMOVED*** Angebote-Liste (`/sales/angebote`)

***REMOVED******REMOVED******REMOVED*** Sichtprüfung
- [ ] Seite lädt ohne Fehler (< 2s)
- [ ] Tabelle mit Spalten sichtbar (Nummer, Kunde, Datum, Betrag, Status)
- [ ] Buttons sichtbar: Neu, Export, Drucken

***REMOVED******REMOVED******REMOVED*** CRUD - Create
- [ ] Klicke "Neu" → Navigation zu `/sales/angebot/neu`
- [ ] Formular lädt vollständig
- [ ] Fülle Pflichtfelder: Kunde, Artikel, Menge, Preis
- [ ] Speichern → Erfolgsmeldung + Redirect zu Liste
- [ ] Neues Angebot in Liste sichtbar

***REMOVED******REMOVED******REMOVED*** CRUD - Read/List
- [ ] Filter nach Kundennamen funktioniert
- [ ] Suche nach Angebotsnummer funktioniert
- [ ] Paging: Nächste/Vorherige Seite (falls > 20 Einträge)
- [ ] Leere Liste zeigt Leer-State

***REMOVED******REMOVED******REMOVED*** CRUD - Update
- [ ] Klicke auf Angebot → Detail/Edit-Seite
- [ ] Ändere Menge
- [ ] Speichern → Erfolgsmeldung
- [ ] Änderung in Liste reflektiert

***REMOVED******REMOVED******REMOVED*** CRUD - Delete
- [ ] Lösch-Button sichtbar
- [ ] Klicke Löschen → Bestätigungs-Dialog
- [ ] Bestätige → Eintrag aus Liste entfernt
- [ ] Audit-Log-Eintrag (falls implementiert)

***REMOVED******REMOVED******REMOVED*** Workflow
- [ ] Status-Feld vorhanden (z. B. Entwurf, Versendet, Angenommen)
- [ ] Statuswechsel möglich (z. B. Entwurf → Versendet)
- [ ] Ungültiger Wechsel blockiert (klare Fehlermeldung)

***REMOVED******REMOVED******REMOVED*** Print/Export
- [ ] Export-Button → CSV/XLS-Download
- [ ] Dateiname: `angebote-export-YYYY-MM-DD.csv`
- [ ] Alle Spalten vorhanden, Encoding korrekt (UTF-8)
- [ ] Drucken-Button → PDF oder Print-Dialog
- [ ] PDF enthält: Logo, Adresse, Positionen, Summe

***REMOVED******REMOVED******REMOVED*** Navigation
- [ ] Tabs vor/zurück funktioniert ohne State-Verlust
- [ ] Breadcrumb: Home > Sales > Angebote
- [ ] Dirty-Guard: Warnung bei ungespeicherten Änderungen

***REMOVED******REMOVED******REMOVED*** Fallback-Level
- [ ] Export-Button-Click → Console-Log: `FB:LEVEL=2` oder `FB:LEVEL=3`
- [ ] Drucken-Button-Click → Console-Log: `FB:LEVEL=2` oder `FB:LEVEL=3`

***REMOVED******REMOVED******REMOVED*** RBAC
- [ ] Admin: Alle Aktionen möglich
- [ ] Power-User: Create/Update/Delete möglich
- [ ] Readonly: Nur View & Export (Create/Update/Delete versteckt oder blockiert)

---

***REMOVED******REMOVED*** Angebot erstellen (`/sales/angebot/neu`)

***REMOVED******REMOVED******REMOVED*** Formular
- [ ] Alle Felder sichtbar: Kunde, Artikel, Menge, Preis, Rabatt
- [ ] Lookup-Felder (Kunde, Artikel) mit Autocomplete
- [ ] Validierung: Pflichtfelder rot bei Fehler
- [ ] Zod-Fehler sichtbar (z. B. "Preis muss positiv sein")

***REMOVED******REMOVED******REMOVED*** Inline-Policy
- [ ] Preis < EK → Gelbe Warnung (Policy-Badge)
- [ ] Negative Menge → Rote Blockierung, Submit disabled
- [ ] Korrekte Eingabe → Submit enabled

***REMOVED******REMOVED******REMOVED*** Auto-Fill
- [ ] Artikel-Auswahl → Preis & EK automatisch gefüllt

***REMOVED******REMOVED******REMOVED*** Speichern
- [ ] Speichern → Erfolgsmeldung + Redirect
- [ ] Fehler → Toast mit konkreter Fehlermeldung

---

***REMOVED******REMOVED*** Order-Editor (`/sales/order`)

***REMOVED******REMOVED******REMOVED*** Formular
- [ ] FormBuilder-Maske lädt
- [ ] JSON-Schema korrekt (sales_order)
- [ ] Zod-Validierung aktiv

***REMOVED******REMOVED******REMOVED*** Workflow
- [ ] BelegFlowPanel sichtbar
- [ ] Status: Neu, Offen, Abgeschlossen
- [ ] Folgebeleg-Buttons: "Lieferschein erstellen", "Rechnung erstellen"

***REMOVED******REMOVED******REMOVED*** Folgebeleg
- [ ] Klicke "Lieferschein erstellen" → Navigation zu `/sales/delivery`
- [ ] Daten übernommen (Kunde, Artikel, Menge)

---

***REMOVED******REMOVED*** Delivery-Editor (`/sales/delivery`)

***REMOVED******REMOVED******REMOVED*** Formular
- [ ] FormBuilder-Maske lädt
- [ ] Copy-Rules aus Order funktionieren

***REMOVED******REMOVED******REMOVED*** Workflow
- [ ] Status: Vorbereitet, Versendet, Zugestellt
- [ ] Folgebeleg: "Rechnung erstellen"

---

***REMOVED******REMOVED*** Invoice-Editor (`/sales/invoice`)

***REMOVED******REMOVED******REMOVED*** Formular
- [ ] FormBuilder-Maske lädt
- [ ] Summen-Berechnung korrekt (Netto, MwSt, Brutto)

***REMOVED******REMOVED******REMOVED*** Workflow
- [ ] Status: Entwurf, Versendet, Bezahlt, Überfällig
- [ ] Keine Folgebelege (End-Dokument)

***REMOVED******REMOVED******REMOVED*** Print
- [ ] PDF-Generierung mit Nummernkreis
- [ ] Journal-Eintrag erstellt

---

**Ergebnis:** ✅ Alle Checks bestanden | ❌ Fehler in Ticket `UAT-XXXX`

