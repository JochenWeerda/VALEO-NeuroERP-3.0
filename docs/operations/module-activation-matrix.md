---
title: Modul-Aktivierungsmatrix
type: reference
audience: [betrieb, lead, entwickler]
owner: Claude
status: aktiv
last_reviewed: 2026-08-23
version: 1.1.0
description: Produktionsentscheidung je 503-by-design- und Fallback-Modul (SPEC-P0-03) — AKTIV/AUS, Voraussetzungen, readyz-Verdrahtung, Fallback-Semantik.
---

# Modul-Aktivierungsmatrix (SPEC-P0-03)

Grundregel (hart, umgesetzt): **Finance-, Bestands- und Beleg-Endpoints liefern bei
DB-/Schemafehlern niemals still leere Daten.** Sie antworten mit RFC-7807-Fehler (503)
und erhoehen `critical_data_path_errors_total` (Alerting: `> 0 in 5 min => Page`).
Regressionstests: `tests/test_critical_data_path_errors.py`.

Readiness: `/api/v1/health/ready` prueft neben DB/EventBus jetzt die kritischen
Schemaobjekte `domain_erp.journal_entries`, `domain_inventory.inventory_stock_movements`,
`domain_shared.tenants` — eine unmigrierte Installation nimmt keinen Traffic an.

Sweep-Governance: Jede 503-by-design-Route steht mit Begruendung und Ablaufdatum in
`config/runtime_sweep_allowlist.yaml`; der nightly Runtime-Sweep schlaegt bei neuen
oder abgelaufenen Ausnahmen fehl.

## Kategorie B — 503-by-design (Migration/Config erforderlich)

| Modul / Route(n) | Entscheidung | Voraussetzung fuer AKTIV | Verhalten bis dahin |
|---|---|---|---|
| Analytics (`/analytics`) | AUS bis Betreiber-Entscheid | Analytics-Migration + Konfiguration | 503 + Problem-Details (allowgelistet bis 2026-09-30) |
| WhatsApp-Kanal (`/channels/whatsapp/webhook`) | AUS bis Provider-Anbindung | Provider-Credentials (Meta/Twilio), AVV | 503 |
| DSGVO-Erasure (`/compliance/dsgvo/erasure-requests`) | AKTIV anstreben (P1) | Compliance-Migration; DSB-Freigabe Loeschkonzept | 503 |
| LkSG (`/compliance/lksg/*`) | AUS bis Fachentscheid | LkSG-Migration + Stammdaten | 503 |
| Whistleblower (`/compliance/whistleblower/reports`) | AUS bis Fachentscheid | Migration + Meldestellen-Prozess | 503 |
| Contracts (`/contracts`) | AKTIV anstreben (P1) | Contracts-Migration | 503 |
| Anlagenbuchhaltung (`/finance/asset-accounting/*`) | AKTIV anstreben (P1) | Anlagen-Migration + Konfiguration AfA | 503 |
| Budgets (`/finance/budgets*`) | AUS bis Fachentscheid | Budget-Migration | 503 |
| Org-Chart (`/personal/org-chart`) | AUS bis HR-Stammdaten | HR-Konfiguration | 503 |
| Rohware-Schemata (`/rohware/schemata`) | AKTIV anstreben (P1) | Tenant-Schema-Konfiguration | 503 |
| Blanket-Orders (`/sales/blanket-orders/`) | AUS bis Fachentscheid | Migration | 503 |
| Quality-Evidence (`/admin/quality-evidence*`) | AKTIV in CI-Umgebungen | generierte `artifacts/`-Reports | 503 |

## Externe Abhaengigkeiten — 503 bei Nichtverfuegbarkeit (by design)

| Route | Upstream | Verhalten |
|---|---|---|
| `/agrar/psm/proplanta/*` | Proplanta-PSM | 503 mit Problem-Details wenn nicht konfiguriert/erreichbar (HTTPException-Passthrough gefixt — vorher als 500 re-raised) |
| `/sustainability/nutrients/crop` | FAOSTAT | 503 statt 502 bei Upstream-Ausfall |

## Kategorie D — CRM-Proxys (crm-core/crm-sales/crm-service Sidecars)

Entscheidung: **AKTIV mit definiertem Degrade.** Wenn der Sidecar nicht erreichbar ist
(`httpx.RequestError`/`RuntimeError`), liefern Listen-Endpoints eine leere Liste (kein 5xx) —
CRM-Listen sind keine Buchungs-/Bestandsdaten; ein leerer Zustand ist fachlich darstellbar
und im Frontend sichtbar. Upstream-**Fehlerantworten** (HTTPStatusError) werden weiterhin
durchgereicht. Betroffen: `activities`, `cases`, `contacts`, `leads`, `farm-profiles`,
`opportunities` (einheitlich seit 2026-07-03).

## Harte Regel umgesetzt (kein stilles Leer-Liefern)

| Endpoint | Vorher | Jetzt |
|---|---|---|
| `GET /journal-entries/` (FIBU-Journal) | leere Liste bei `SQLAlchemyError` | 503 + Problem-Details + Metrik |
| `GET /lager/bestaende` (Bestandsaggregat) | leere Liste bei jedem DB-Fehler | 503 + Problem-Details + Metrik |
| `GET /finance/open-items/{id}/settlements` | leere Liste bei Exception | 503 + Problem-Details + Metrik (2026-08-23) |
| `GET /finance/payments/unmatched` | leere Liste bei Exception | 503 + Problem-Details + Metrik (2026-08-23) |
| `GET /finance/payments/open-items/{customer}` | leere Liste bei Exception | 503 + Problem-Details + Metrik (2026-08-23) |
| `GET /finance/payments/match-suggestions/{id}` | leere Liste bei Exception | 503 + Problem-Details + Metrik (2026-08-23) |
| `GET /finance/bank-statements/{id}/lines` | leere Liste bei Exception | 503 + Problem-Details + Metrik (2026-08-23) |

Gemeinsamer Helper: `app/core/critical_data_path.py` (`raise_critical_data_unavailable`).
Regression: `tests/test_critical_data_path_errors.py` (7 Cases).

Weitere Kandidaten werden ueber den nightly Runtime-Sweep sichtbar (jede neue stille
Degradierung faellt als Abweichung zwischen frischer DB und Bestandsverhalten auf).

## Offene Punkte

- Betreiber-Entscheid je "AUS bis Fachentscheid"-Modul mit Owner + Zieldatum ins
  Freigabe-Protokoll (Runbook) uebernehmen.
- Allowlist-Eintraege laufen am 2026-09-30 ab — bis dahin je Modul AKTIV-Migration
  oder bewusste Verlaengerung mit Begruendung.
