# E2E CRUD Acceptance Matrix

Stand: `2026-04-24`

## Zweck

Priorisierte Browser-/CRUD-Abnahme der wichtigsten End-to-End-Prozesse.
Diese Matrix ergaenzt `browser-use-checklists.md` und macht die naechsten Prueflaeufe steuerbar.

## P0-Prozesse

| Prozess | Create | Read | Update | Statuswechsel | Korrektur/Storno | Folgeprozess | Repo-Pruefung |
|---|---|---|---|---|---|---|---|
| Procure-to-Pay | Bestellung aus Flow Spine | Bestellungsliste | Position/Lieferant nachpflegen | Freigabe/Bestellung | Ruecksprung vor Abschluss | Wareneingang/Rechnungseingang | `pnpm --dir packages/frontend-web test:run src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx` |
| Harvest-to-Settlement | Ernte-Annahme | Annahme/Settlement-Liste | Qualitaets-/Mengenwerte | Freigabe/Verbuchen | Kampagnen-Backfill/Korrektur | Abrechnung/Journal | `pytest tests/test_process_kernel_wave1_contracts.py -q` |
| Finance-to-Close | Zahlungslauf/Closing | Read-Model/Cockpit | Freigabeparameter | Approve/Execute/Return | Ruecklaeufer/Storno | Journal/OP | `pytest tests/test_finance_payment_runs_api.py tests/test_process_kernel_wave1_contracts.py -q` |
| Inventory-to-Settlement | Bestand/Bewegung | Lagerbestand | Korrektur/Transfer | Reservieren/Buchen | Inventurdifferenz | Charge/FIBU | `pytest tests/test_inventory_operations.py tests/test_inventory_counts.py -q` |

## P1-Prozesse

| Prozess | Pflichtpfad | Sonderfall | Repo-Pruefung |
|---|---|---|---|
| Order-to-Cash | Auftrag -> Lieferung -> Rechnung | Kreditlimit/Mahnung | `pnpm --dir packages/frontend-web test:run src/__tests__/pages/sales/order-editor.test.tsx` |
| Contract-to-Settlement | Kontrakt -> Position -> Alarm | Mengen-/Preisabweichung | `pytest tests/test_process_kernel_wave1_contracts.py -q` |
| Complaint-to-Resolution | Reklamation -> Entscheidung | Sperre/Sonderfreigabe | Browser-Use manuell bis Playwright-Fixture existiert |
| Service-to-Customer | Anfrage -> Fall -> Abschluss | Eskalation | Browser-Use manuell bis Playwright-Fixture existiert |
| Compliance-to-Report | CO2/Meldung -> Nachweis | Audit-Nachforderung | `pytest tests/test_process_kernel_wave1_contracts.py -q` |

## Abnahmeregel

Ein Prozess gilt als browserfest, wenn:

- Create, Read und Update in der UI ohne Sackgasse laufen.
- Statuswechsel auditierbar und wiederauffindbar sind.
- fachlich unzulaessige Deletes durch Storno, Ruecknahme oder Abschluss ersetzt sind.
- der Folgeprozess mit stabiler Referenz geoeffnet wird.
- mindestens ein Sonderfall dokumentiert oder automatisiert ist.
