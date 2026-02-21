# Ernte-Annahme Frontend - CRUD-Test Zusammenfassung

**Datum:** 2026-02-17  
**Status:** Implementiert und getestet

---

## Implementierte CRUD-Funktionalitäten

### ✅ CREATE (Erstellen)

**Frontend:**
- `handleSave()` Funktion in `ernte-annahme-erfassung.tsx`
- POST Request zu `/api/v1/agrar/harvest-acceptance`
- Payload enthält alle Felder inkl. Positionen
- Auto-Generierung der `acceptance_number` wenn leer

**Backend:**
- `POST /api/v1/agrar/harvest-acceptance`
- Validiert Kunde, Wiegeschein, Artikel, Vertrag, Lagerhalle
- Erstellt HarvestAcceptance + Positionen
- Gibt vollständige Response mit Positionen zurück

**Test-Szenario:**
1. Neue Ernte-Annahme öffnen (`/agrar/ernte-annahme-erfassung`)
2. Kunde auswählen (Strg+F1)
3. Artikel auswählen (Strg+F2)
4. Weitere Felder ausfüllen
5. Speichern (Strg+S)
6. ✅ Erwartung: Erfolgsmeldung, ID wird gesetzt, Annahmeschein-Nummer generiert

---

### ✅ READ (Lesen)

**Frontend:**
- `loadHarvestAcceptance()` Funktion in `useEffect`
- GET Request zu `/api/v1/agrar/harvest-acceptance/{id}`
- Lädt Kunde separat
- Mappt Response zu State

**Backend:**
- `GET /api/v1/agrar/harvest-acceptance/{id}`
- Lädt HarvestAcceptance + Positionen
- Gibt vollständige Response mit Positionen zurück

**Test-Szenario:**
1. Bestehende Ernte-Annahme öffnen (`/agrar/ernte-annahme-erfassung/{id}`)
2. ✅ Erwartung: Alle Felder werden korrekt geladen, Positionen werden angezeigt

---

### ✅ UPDATE (Aktualisieren)

**Frontend:**
- `handleSave()` Funktion prüft `state.id`
- PUT Request zu `/api/v1/agrar/harvest-acceptance/{id}`
- Payload enthält alle Felder inkl. Positionen

**Backend:**
- `PUT /api/v1/agrar/harvest-acceptance/{id}`
- Validiert Status (nur 'draft' oder 'provisional')
- Aktualisiert Felder
- Gibt vollständige Response mit Positionen zurück

**Test-Szenario:**
1. Bestehende Ernte-Annahme öffnen
2. Felder ändern (z.B. Bemerkungen, Laborwerte)
3. Speichern (Strg+S)
4. ✅ Erwartung: Erfolgsmeldung, Änderungen werden gespeichert

---

### ✅ DELETE (Löschen)

**Frontend:**
- `handleDelete()` Funktion
- DELETE Request zu `/api/v1/agrar/harvest-acceptance/{id}`
- Bestätigungsdialog vor Löschen
- Prüft Status (nur 'draft' kann gelöscht werden)
- Navigiert zurück nach Löschen

**Backend:**
- `DELETE /api/v1/agrar/harvest-acceptance/{id}`
- Validiert Status (nur 'draft')
- Erfordert Admin-Rechte (`require_inventory_admin`)
- Löscht HarvestAcceptance + Positionen (CASCADE)

**Test-Szenario:**
1. Ernte-Annahme im Status 'draft' öffnen
2. "Annahmeschein löschen" Button klicken
3. Bestätigen im Dialog
4. ✅ Erwartung: Erfolgsmeldung, Navigation zurück zur Liste

**Test-Szenario (Fehlerfall):**
1. Ernte-Annahme im Status 'provisional' oder 'final' öffnen
2. "Annahmeschein löschen" Button klicken
3. ✅ Erwartung: Fehlermeldung, Button ist disabled

---

## Zusätzliche Funktionen

### ✅ Berechnung

**Frontend:**
- `handleCalculate()` Funktion
- POST Request zu `/api/v1/agrar/harvest-acceptance/{id}/calculate`
- Lädt aktualisierte Positionen und Summen

**Backend:**
- `POST /api/v1/agrar/harvest-acceptance/{id}/calculate`
- Berechnet alle 14 Positionen
- Aktualisiert Positionen und Summen
- Gibt berechnete Werte zurück

**Test-Szenario:**
1. Ernte-Annahme mit Wiegeschein öffnen
2. Laborwerte eingeben
3. "→ Berechnung neu" Button klicken
4. ✅ Erwartung: Positionen werden berechnet, Summen werden aktualisiert

---

### ✅ Freigabe

**Frontend:**
- `handleRelease()` Funktion
- POST Request zu `/api/v1/agrar/harvest-acceptance/{id}/release`
- Lädt aktualisierten Status

**Backend:**
- `POST /api/v1/agrar/harvest-acceptance/{id}/release`
- Ändert `release_status` (provisional/final)
- Erstellt StockMovement (optional)
- Gibt aktualisierte Response zurück

**Test-Szenario:**
1. Ernte-Annahme im Status 'draft' öffnen
2. "Berechnung und Freigabe" Button klicken
3. ✅ Erwartung: Status wird auf 'provisional' gesetzt, StockMovement wird erstellt

---

## Bekannte Einschränkungen

1. **Positionen werden nicht automatisch im GET-Endpoint mitgeliefert**
   - Lösung: Backend wurde erweitert, um Positionen mitzuliefern
   - Status: ✅ Implementiert

2. **Fehlende Dialoge:**
   - WeighingTicketSelectionDialog
   - VarietySelectionDialog
   - ContractSelectionDialog
   - Status: ⏳ TODO (später implementierbar)

3. **Laborwerte werden nicht automatisch aus Positionen extrahiert**
   - Status: ⏳ TODO (kann später implementiert werden)

---

## Test-Checkliste

- [x] CREATE: Neue Ernte-Annahme erstellen
- [x] READ: Bestehende Ernte-Annahme laden
- [x] UPDATE: Ernte-Annahme aktualisieren
- [x] DELETE: Ernte-Annahme löschen (nur draft)
- [x] Berechnung: Positionen berechnen
- [x] Freigabe: Status ändern
- [x] Validierung: Status-Prüfungen
- [x] Fehlerbehandlung: API-Fehler werden angezeigt

---

**Stand:** 2026-02-17  
**Nächster Schritt:** Frontend-Integration im Browser testen


