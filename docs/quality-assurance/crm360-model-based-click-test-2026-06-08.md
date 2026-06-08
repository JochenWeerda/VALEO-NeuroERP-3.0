# CRM360 modellbasierter Klicktest

Stand: 2026-06-08

## Ziel

Der Test prueft nicht nur, ob ein Element klickbar ist. Jede Aktion besitzt
einen typisierten Vertrag fuer Handler, benoetigten Kundenkontext, erwartetes
Ziel, CRUD-Art, Ruecksprung und fachlichen Workflow.

Quellen:

- Action-Matrix: `playwright-tests/specs/crm/crm360-action-contracts.ts`
- Prozessmodell: `playwright-tests/specs/crm/crm360-workflow-model.ts`
- Browserausfuehrung: `playwright-tests/specs/crm/crm360-model-based.spec.ts`
- Fehlerwaechter: `playwright-tests/helpers/interactionGuard.ts`

## Abdeckung

Die Matrix enthaelt 23 Vertraege: zehn primaere Kopfaktionen, neun
Arbeitsbereich-Tabs sowie vier delegierte oder lokale Aktionen. Playwright
prueft mit deterministischen API-Fixtures:

- Sichtbarkeit und Vollstaendigkeit der primaeren Action-IDs
- Kundeninformation, Praesente, Aktivitaetsanlage und Filter-Reset
- Stammdaten-Update mit korrekter `customerId`
- Telefonprotokoll als persistierten `POST`
- NeuroAI-Aufruf mit selektiertem Kunden
- Angebotserfassung mit Debitor, Name und `entryMode=crm360`
- OP-Debitoren mit `kunden_nr`
- Browser-Zurueck zu `/crm` ohne 404
- delegierte Beleg- und OP-Anlage mit ehrlicher Fachprozessmeldung
- Console-, Page-, HTTP- und 404-Fehler nach Interaktionen
- Modellpfad Kunde -> Angebot -> Auftrag -> Lieferschein -> Rechnung -> OP

## Behobene Befunde

| Befund | Klassifikation | Ergebnis |
| --- | --- | --- |
| Information hatte keinen Handler | fehlende Verknuepfung | echter Kundendialog |
| E-Mail hatte keinen fachlichen Effekt | fehlende Verknuepfung | `mailto:` mit Kundenadresse |
| Angebot/Faktur wechselten nur lokale Tabs | falscher Zielscreen | typisierte Fachrouten mit Kundenkontext |
| Filter-Reset war leer | fehlende Verknuepfung | Workspace und Tab werden zurueckgesetzt |
| Aktivitaetsaktion suchte eine nicht existente ID | fehlendes CRUD | korrekter Formular-Trigger |
| KIM-Toasts wurden nicht gerendert | Bedienfehler | lokaler Toaster eingebunden |
| Zwei Form-Labels waren nicht mit Feldern verbunden | Accessibility/Testbarkeit | `htmlFor`/`id` ergaenzt |
| Playwright-Teardown konnte zehn Minuten haengen | Testinfrastruktur | PID-basierter Serverabbau |
| Playwright-Specs enthielten Typ- und Skip-Fehler | Typfehler | kompletter Test-Typecheck gruen |
| POS lud Offline-Queue statisch und dynamisch | Build-/Chunk-Fehler | ein statischer Import |
| Regex erzeugte Tailwind-Regel `-: T` | CSS-Buildfehler | scannerfeste Zeitstempelbereinigung |

## Bewusste Grenzen

`mailto:` startet einen externen Betriebssystem-Client und ist daher kein
Browser-CRUD. Der Unterlagen-Tab arbeitet weiterhin nur lokal und ist kein
persistenter DMS-Nachweis. Beleg-, OP- und Kontrakt-Neuanlagen bleiben
delegierte Fachprozesse; KIM behauptet dort keine lokale Persistenz.

Der komplette Folgeprozess ab Angebot wird inzwischen mit deterministischen
API-Fixtures im echten Browser ausgefuehrt. Ein produktiver, persistenter
Durchstich durch Auftrag, Lieferschein, Rechnung und Finanzbuchhaltung
benoetigt weiterhin isolierte, aufraeumbare Backend-Testdaten und ist durch
diesen Browser-Handover nicht als Buchungsnachweis zu werten.

## Verifikation

- Kombinierter CRM360- und Revenue-Handover-Lauf: 11 bestanden
- `pnpm exec tsc -p playwright-tests/tsconfig.json --noEmit --pretty false`: bestanden
- `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`: bestanden
- Produktions-Build: bestanden; verbleibend ist nur der bekannte
  Groessenhinweis fuer den MapLibre-Chunk.
