# UAT Checkliste: Agrar Domain

## PSM-Liste (`/agrar/psm`)

### Sichtprüfung
- [ ] Seite lädt ohne Fehler
- [ ] Tabelle/Grid sichtbar (PSM-Name, Zulassungsnr., Wirkstoff, Auflagen)
- [ ] Buttons: Neu, Export, Drucken, Filter

### CRUD - Create
- [ ] Klicke "Neu" → Navigation zu `/agrar/psm/stamm`
- [ ] Formular mit Feldern: Name, Zulassungsnr., Wirkstoff, Auflagen
- [ ] Speichern → Erfolgsmeldung
- [ ] Neuer PSM-Eintrag in Liste

### CRUD - Read/List
- [ ] Filter nach Wirkstoff
- [ ] Suche nach Zulassungsnummer
- [ ] Paging funktioniert

### CRUD - Update
- [ ] Detail-Seite öffnen
- [ ] Auflagen ändern
- [ ] Speichern → Änderung reflektiert

### CRUD - Delete
- [ ] Löschen mit Bestätigung
- [ ] Eintrag aus Liste entfernt

### Validierung
- [ ] Auflagen-Validierung (z. B. Mindestabstand zu Gewässern)
- [ ] BVL-Konformität geprüft (Mock)

### Print/Export
- [ ] Export → CSV mit allen Feldern
- [ ] Drucken → PSM-Übersicht als PDF

### Compliance
- [ ] Sachkunde-Register erreichbar (`/agrar/psm/sachkunde-register`)
- [ ] VVVO-Register vorhanden

### Fallback-Level
- [ ] Export → `FB:LEVEL=2` oder `FB:LEVEL=3`

---

## Saatgut-Liste (`/agrar/saatgut-liste`)

### Sichtprüfung
- [ ] Tabelle: Sorte, Kulturart, Z-Nummer, Verfügbarkeit
- [ ] Buttons: Neu, Export

### CRUD
- [ ] Neu → `/agrar/saatgut-stamm`
- [ ] Formular: Sorte, Kulturart, Z-Nummer
- [ ] Speichern funktioniert
- [ ] Update & Delete funktionieren

### Sortenregister
- [ ] `/agrar/saatgut/sortenregister` lädt
- [ ] Tabelle mit zugelassenen Sorten

---

## Dünger-Liste (`/agrar/duenger-liste`)

### Sichtprüfung
- [ ] Tabelle: Produkt, NPK-Werte, Zulassung
- [ ] Buttons: Neu, Export

### CRUD
- [ ] Neu → `/agrar/duenger-stamm`
- [ ] Formular: Produkt, N, P, K, Zulassung
- [ ] Speichern funktioniert

### Bedarfsrechner
- [ ] `/agrar/duenger/bedarfsrechner` lädt
- [ ] Eingabe: Fläche, Kulturart, Ziel-NPK
- [ ] Berechnung → Empfohlene Menge

---

## Feldbuch

### Schlagkartei (`/agrar/feldbuch/schlagkartei`)
- [ ] Tabelle: Schlag-Nr., Fläche, Kulturart
- [ ] CRUD funktioniert

### Maßnahmen (`/agrar/feldbuch/massnahmen`)
- [ ] Tabelle: Datum, Maßnahme (Aussaat/Düngung/PSM), Schlag
- [ ] CRUD funktioniert

---

## Wetter & Prognose

### Wetterprognose (`/agrar/wetter/prognose`)
- [ ] Proplanta-Widget sichtbar (oder Dummy)
- [ ] 7-Tage-Prognose

### Wetterwarnung (`/agrar/wetterwarnung`)
- [ ] Warnungen für aktuellen Standort
- [ ] DWD-Integration (oder Mock)

---

**Ergebnis:** ✅ Alle Checks bestanden | ❌ Fehler in Ticket `UAT-XXXX`

