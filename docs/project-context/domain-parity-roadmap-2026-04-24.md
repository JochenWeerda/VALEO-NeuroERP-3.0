# Domain Parity Roadmap

Stand: `2026-04-24`

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
| Finance/FIBU | Cutover-Mapping, Payment-Return, Read-Model-Coverage | `check_fibu_cutover_mapping.py`, Finance-API-Tests |
| Supply/Inventory | Transfers, Warehouses, Inventur-Coverage | Inventory-/Warehouse-Tests |
| Procurement | Rechnungseingang, Lieferantendokumente, Superglue-Livepfad | P2P-Browsermatrix |
| Contracts | Kontraktposition, Alarm, Settlement-Uebergabe | Contract-to-Settlement-Checks |
| CRM/Service | Downstream-Readiness, Opportunity/Servicefall-Tiefe | CRM-Probe-Plan + UI-Abnahme |
| Documents/DMS | Upload, DMS-Redirect, Audit-Paket | Finance-Followup-/DMS-Tests |

## Naechste Code-Slices

1. `COV-FIN-003`: Finance-Read-Models und Dunning auf Ratchet-Niveau bringen.
2. `COV-INV-002`: Warehouses, Warehouse-Transfers und Waage gezielt testen.
3. `CRUD-P2P-001`: Procure-to-Pay Playwright-Pfad mit Seed-Daten stabilisieren.
4. `CUTOVER-FIBU-002`: fachlich freigegebene Mappingdatei gegen Template validieren.
5. `DOC-DMS-002`: DMS-Live-Probe und Redirect-Failure-Cases abdecken.
