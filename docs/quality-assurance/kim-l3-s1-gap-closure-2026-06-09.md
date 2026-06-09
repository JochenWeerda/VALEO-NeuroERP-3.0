# KIM L3 S1 Gap Closure

Stand: 2026-06-09

## Gepruefter Scope

- Bestehende Angebote aus CRM360 mit Entity-ID oeffnen
- Neues Kontaktlog inklusive Art, Betreff, Kommentar und CC
- Fehlerfall beim Speichern ohne Verlust der Formulardaten
- Ansprechpartner-Auswahl, Details, E-Mail-Daten und Praesente-Kontext
- Ansprechpartner-Telefonie mit Nummernauswahl, TAPI und Folge-Log
- Neukundenroute und Browser-Zurueck
- CRM360-Druckansicht
- Action-Matrix und fachliche Zielrouten

## Behobene Fehler

1. `/sales/angebot/:id` lud bisher kein bestehendes Angebot.
2. Kontaktlog- und Ansprechpartnerformulare wurden vor bestaetigtem Speichern geleert.
3. Ansprechpartner-Telefonie verwendete `tel:` statt TAPI und erzeugte kein Kontaktlog.
4. Ansprechpartner-E-Mail wurde vom Backend nicht geliefert.
5. Der Ansprechpartner-POST verlangte faelschlich serverseitige `id`-/`customerId`-Felder.
6. Der globale Druck-Fallback blockierte den fachseitigen CRM360-Druckhandler.
7. Mehrere S1-Aktionen waren in Playwright nicht ausgefuehrt.

## Nachweis

- `python -m pytest tests/test_crm_kim_contacts.py tests/test_crm_kim_kontaktlog.py -q --no-cov`
  - 9 passed
- `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`
  - 0 Fehler
- `pnpm exec tsc --noEmit --pretty false -p playwright-tests/tsconfig.json`
  - 0 Fehler
- `pnpm exec playwright test playwright-tests/specs/crm/crm360-model-based.spec.ts --project=full --retries=1`
  - 15 passed
- Produktions-Build wurde durch das Playwright-Global-Setup erfolgreich erzeugt.

## Ergebnis

Die im Review von S1 festgestellten funktionalen und automatisierten Testluecken
sind geschlossen. Belegkontext, Mutationserfolg, TAPI, Druck und
Ruecknavigation sind nun explizit nachgewiesen.
