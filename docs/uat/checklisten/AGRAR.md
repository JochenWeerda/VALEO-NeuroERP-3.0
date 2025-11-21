***REMOVED*** UAT Checkliste: Agrar Domain

***REMOVED******REMOVED*** PSM-Liste (`/agrar/psm`)

***REMOVED******REMOVED******REMOVED*** Sichtprüfung
- [ ] Seite lädt ohne Fehler
- [ ] Tabelle/Grid sichtbar (PSM-Name, Zulassungsnr., Wirkstoff, Auflagen)
- [ ] Buttons: Neu, Export, Drucken, Filter

***REMOVED******REMOVED******REMOVED*** CRUD - Create
- [ ] Klicke "Neu" → Navigation zu `/agrar/psm/stamm`
- [ ] Formular mit Feldern: Name, Zulassungsnr., Wirkstoff, Auflagen
- [ ] Speichern → Erfolgsmeldung
- [ ] Neuer PSM-Eintrag in Liste

***REMOVED******REMOVED******REMOVED*** CRUD - Read/List
- [ ] Filter nach Wirkstoff
- [ ] Suche nach Zulassungsnummer
- [ ] Paging funktioniert

***REMOVED******REMOVED******REMOVED*** CRUD - Update
- [ ] Detail-Seite öffnen
- [ ] Auflagen ändern
- [ ] Speichern → Änderung reflektiert

***REMOVED******REMOVED******REMOVED*** CRUD - Delete
- [ ] Löschen mit Bestätigung
- [ ] Eintrag aus Liste entfernt

***REMOVED******REMOVED******REMOVED*** Validierung
- [ ] Auflagen-Validierung (z. B. Mindestabstand zu Gewässern)
- [ ] BVL-Konformität geprüft (Mock)

***REMOVED******REMOVED******REMOVED*** Print/Export
- [ ] Export → CSV mit allen Feldern
- [ ] Drucken → PSM-Übersicht als PDF

***REMOVED******REMOVED******REMOVED*** Compliance
- [ ] Sachkunde-Register erreichbar (`/agrar/psm/sachkunde-register`)
- [ ] VVVO-Register vorhanden

***REMOVED******REMOVED******REMOVED*** Fallback-Level
- [ ] Export → `FB:LEVEL=2` oder `FB:LEVEL=3`

---

***REMOVED******REMOVED*** Saatgut-Liste (`/agrar/saatgut-liste`)

***REMOVED******REMOVED******REMOVED*** Sichtprüfung
- [ ] Tabelle: Sorte, Kulturart, Z-Nummer, Verfügbarkeit
- [ ] Buttons: Neu, Export

***REMOVED******REMOVED******REMOVED*** CRUD
- [ ] Neu → `/agrar/saatgut-stamm`
- [ ] Formular: Sorte, Kulturart, Z-Nummer
- [ ] Speichern funktioniert
- [ ] Update & Delete funktionieren

***REMOVED******REMOVED******REMOVED*** Sortenregister
- [ ] `/agrar/saatgut/sortenregister` lädt
- [ ] Tabelle mit zugelassenen Sorten

---

***REMOVED******REMOVED*** Dünger-Liste (`/agrar/duenger-liste`)

***REMOVED******REMOVED******REMOVED*** Sichtprüfung
- [ ] Tabelle: Produkt, NPK-Werte, Zulassung
- [ ] Buttons: Neu, Export

***REMOVED******REMOVED******REMOVED*** CRUD
- [ ] Neu → `/agrar/duenger-stamm`
- [ ] Formular: Produkt, N, P, K, Zulassung
- [ ] Speichern funktioniert

***REMOVED******REMOVED******REMOVED*** Bedarfsrechner
- [ ] `/agrar/duenger/bedarfsrechner` lädt
- [ ] Eingabe: Fläche, Kulturart, Ziel-NPK
- [ ] Berechnung → Empfohlene Menge

---

***REMOVED******REMOVED*** Feldbuch

***REMOVED******REMOVED******REMOVED*** Schlagkartei (`/agrar/feldbuch/schlagkartei`)
- [ ] Tabelle: Schlag-Nr., Fläche, Kulturart
- [ ] CRUD funktioniert

***REMOVED******REMOVED******REMOVED*** Maßnahmen (`/agrar/feldbuch/massnahmen`)
- [ ] Tabelle: Datum, Maßnahme (Aussaat/Düngung/PSM), Schlag
- [ ] CRUD funktioniert

---

***REMOVED******REMOVED*** Wetter & Prognose

***REMOVED******REMOVED******REMOVED*** Wetterprognose (`/agrar/wetter/prognose`)
- [ ] Proplanta-Widget sichtbar (oder Dummy)
- [ ] 7-Tage-Prognose

***REMOVED******REMOVED******REMOVED*** Wetterwarnung (`/agrar/wetterwarnung`)
- [ ] Warnungen für aktuellen Standort
- [ ] DWD-Integration (oder Mock)

---

**Ergebnis:** ✅ Alle Checks bestanden | ❌ Fehler in Ticket `UAT-XXXX`

