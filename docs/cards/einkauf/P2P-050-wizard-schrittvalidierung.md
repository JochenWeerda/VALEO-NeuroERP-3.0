# Card: P2P-050 - Wizard-Schrittvalidierung vor Weiter

## 1. Einordnung
- Prozessbereich: Einkauf
- Workflow: Procure-to-Pay
- Teilprozess: Bestellanlage Wizard-Schrittvalidierung
- Rolle(n): Einkauf, Disposition, operativer Sachbearbeiter
- Prioritaet: hoch
- Status: abgeschlossen

## 2. Fachlicher Zweck
- Ziel des Schrittes: Verhindern, dass ein Nutzer mit leeren Pflichtfeldern auf den naechsten Wizard-Schritt wechselt.
- Fachliche Beschreibung: Jeder relevante Schritt prueft beim Klick auf `Weiter` seine eigenen Pflichtdaten und blockiert die Navigation bei Fehlern mit einer Toast-Fehlermeldung.
- Geschaeftlicher Nutzen: Fachlich unbrauchbare Bestellentwuerfe werden fruehzeitig abgefangen statt erst beim finalen Submit.

## 3. Start / Trigger
- Startbedingung: Nutzer klickt `Weiter` in einem Wizard-Schritt mit Pflichtfeldern.
- Ausloeser: Button-Klick `Weiter` in Schritt 1 (Lieferant) oder Schritt 2 (Positionen).
- Startpunkt-Typ:
  - [ ] Standardstart
  - [ ] Alternativstart
  - [ ] Externer Import
  - [ ] Manueller Direktstart
  - [x] Systemtrigger (Wizard-Navigation)

## 4. Vorbedingungen
- Muss vorhanden sein: Wizard mit `getStepValidationError`-Prop.
- Muss geprueft sein: Validierungsfunktion gibt `string | null` zurueck.

## 5. Validierungsregeln

| Schritt | Pflichtfeld | Fehlermeldung |
|---------|------------|---------------|
| `lieferant` | `lieferant` nicht leer | Lieferant ist ein Pflichtfeld. |
| `lieferant` | `liefertermin` gesetzt | Liefertermin ist ein Pflichtfeld. |
| `positionen` | Mindestens 1 Position | Mindestens eine Position ist erforderlich. |
| `positionen` | `artikel` nicht leer, `menge > 0`, `preis >= 0` | Alle Positionen brauchen Artikel, Menge groesser 0 und einen nicht negativen Preis. |
| `lieferung` | keine | — |
| `zusammenfassung` | keine (Submit-Sicherheitsnetz via `validateBestellung()`) | — |

## 6. UI / Systembezug
- Seite / Maske: `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`
- Dialog / Untermaske: Wizard-Schritt-Navigation.
- Button / Aktion: `Weiter` — loest `getStepValidationError(stepId)` aus.
- Status vor Ausfuehrung: Nutzer befindet sich auf einem Schritt mit Pflichtfeldern.
- Status nach Ausfuehrung: Navigation zum naechsten Schritt ODER Toast-Fehlermeldung.

## 7. Aktion
- Benutzeraktion: Klick auf `Weiter`.
- Systemaktion: `validateStep(activeStepId)` wird aufgerufen; bei Fehler → `onStepValidationError` → Toast.
- Automatische Folgeaktion: bei Erfolg Navigation zum naechsten Schritt.
- Synchron / asynchron: synchron.

## 8. Geschaeftsregeln
- Pflichtfelder Schritt 1: Lieferant, Liefertermin.
- Pflichtfelder Schritt 2: Mindestens eine Position mit Artikel und Menge > 0.
- Kein Pflichtfeld: Lieferadresse, Incoterms, Notizen, Preis.
- Doppelte Sicherheit: `validateBestellung()` beim Submit bleibt als Sicherheitsnetz.

## 9. Ergebnisse
- Output-Daten: keine neuen Daten — nur Navigation blockiert oder freigegeben.
- Folgeprozess Standard: Weiternavigation zum naechsten Schritt.
- Folgeprozess alternativ: Toast-Fehlermeldung, Nutzer bleibt auf aktuellem Schritt.

## 10. CRUD-Pruefung
- Benutzeraktion pruefbar: ja
- Browser-Use pruefbar: ja — Weiter ohne Lieferant klicken, Toast pruefen

## 11. Soll-Ist-Bewertung
- Soll-Prozess: Wizard blockiert bei unvollstaendigen Schritten.
- Ist-Umsetzung (vor diesem Slice): `getStepValidationError`-Prop war nicht verdrahtet; Wizard navigierte ohne Pruefung.
- Abweichung: Nutzer konnte leere Schritte durchklicken.
- Fehlende Umsetzung: keine nach diesem Slice.

## 12. Risiko
- Risiko-Level:
  - [ ] kritisch
  - [x] hoch
  - [ ] mittel
  - [ ] niedrig
- Risiko-Beschreibung: Ohne Schrittvalidierung konnten Disponenten leere Bestellentwuerfe anlegen; Fehler traten erst beim finalen Submit auf.

## 13. Testhinweise
- Positiver Testfall: Lieferant gesetzt → `Weiter` navigiert zu Schritt 2.
- Negativer Testfall: Lieferant leer → `Weiter` blockiert, Toast erscheint.
- Negativer Testfall: Position ohne Artikel → `Weiter` blockiert, Toast erscheint.
- Browser-Use-Pruefschritt: Bestellmaske oeffnen, `Weiter` ohne Lieferant klicken, Toast pruefen, Lieferant eintragen, `Weiter` erneut klicken, Navigation pruefen.

## 14. Annahmen
- `Wizard.getStepValidationError` wird synchron ausgewertet.
- Schritte `lieferung` und `zusammenfassung` haben keine Pflichtfelder.
- `validateBestellung()` beim finalen Submit bleibt als Sicherheitsnetz.
