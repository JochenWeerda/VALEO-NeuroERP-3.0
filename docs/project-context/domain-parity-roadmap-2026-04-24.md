# Domain Parity Roadmap

Stand: `2026-05-05`

## Ziel

Die breite ERP-Abdeckung wird in den schwaecheren Bereichen messbar vertieft.
Bewertet wird nicht die Anzahl Masken, sondern produktive Tragfaehigkeit.

## Bewertungsraster

| Kriterium | Bedeutung |
|---|---|
| Fachlogik | Kernfaelle, Sonderfaelle, Abschluss-/Stornopfade |
| Testtiefe | Unit-, API-, Contract- und Browser-Abdeckung |
| Integration | Zielsysteme, Secrets, Import/Export, Monitoring |
| UI-Operationalisierung | Fallkopf, Status, Blocker, Folgeaktion |
| Audit/Governance | Tenant, Rechte, Nachweis, Policy |

## Aktuelle Prioritaet

| Domaene | Naechster Ausbau | Primaerer Nachweis |
|---|---|---|
| Finance/FIBU | Cutover-Mapping, Ratchet-Schwellen-Review, externe Export-/DMS-Fehlerpfade | `check_fibu_cutover_mapping.py`, kritischer Coverage-Ratchet |
| Supply/Inventory | Browser-/CRUD-Abnahme und physische Folgeobjektkette | Inventory-/Warehouse-Tests, Flow-Spine-CRUD-Matrix |
| Procurement | Rechnungseingang, Lieferantendokumente, Superglue-Livepfad | P2P-Browsermatrix |
| Contracts | Kontraktposition, Alarm, Settlement-Uebergabe | Contract-to-Settlement-Checks |
| CRM/Service | Downstream-Readiness, Opportunity/Servicefall-Tiefe | CRM-Probe-Plan + UI-Abnahme |
| Documents/DMS | Upload, DMS-Redirect, Audit-Paket | Finance-Followup-/DMS-Tests |

## Naechste Code-Slices

1. `CRUD-P2P-001`: Procure-to-Pay Playwright-Pfad mit Seed-Daten stabilisieren.
2. `CUTOVER-FIBU-002`: fachlich freigegebene Mappingdatei gegen Template validieren.
3. `DOC-DMS-002`: DMS-Live-Probe und Redirect-Failure-Cases abdecken.
4. `COV-INT-002`: Integrations-Governance tiefer testen und ggf. neue Ratchet-Pfade aufnehmen.
5. `COV-RATCHET-004`: Schwellen fuer bereits gruene kritische Pfade kontrolliert anheben.

## Zuletzt abgeschlossen

- `COV-FIN-003`: `booking_templates.py` und `chart_of_accounts.py` sind im kritischen Coverage-Ratchet gruen.
- `COV-INV-002`: `waage.py`, `warehouses.py`, `warehouse_transfers.py`, `inventory_counts.py` und `inventory_operations.py` sind im kritischen Coverage-Ratchet gruen.
