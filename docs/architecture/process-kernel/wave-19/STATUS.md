# Wave-19 Status

## Scope
Settlement-Freigabe-Flow + Finance-Cockpit-Read-Models + Human-Gate fuer Agenten

## Zielbild

Wave 19 schließt die letzte kritische Luecke aus dem Top-50-Gap-Backlog (Gap 004, 033):
Abrechnungen werden nicht mehr per CRUD gebucht, sondern durchlaufen einen
expliziten Freigabe-Flow mit Audit-Trail und Human-in-the-Loop-Gate.
Parallel werden Settlement- und Positions-Cockpits auf stabile Read-Model-Contracts
umgestellt (schema_version=1).

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/settlement_approval.py` | SettlementApprovalRequest/State/Result — Freigabe-Zustandsmaschine fuer Abrechnungen (ENTWURF/ZUR_FREIGABE/FREIGEGEBEN/ABGELEHNT/VERBUCHT); Audit-Entry-Integration | abgeschlossen |
| AP2 | `app/api/v1/endpoints/finance_read_models.py` | Settlement-Cockpit Read-Model `GET /finance/read-models/settlement-cockpit` (schema_version=1) + Position-Exposure Read-Model `GET /finance/read-models/position-exposure` | abgeschlossen |
| AP3 | `app/core/settlement_human_gate.py` | Human-Gate-Regeln fuer KI-Agenten: 6 Regeln (HG-01 BLOCK >100k, HG-02 HOLD Agent+>10k, HG-03 Qualitaet, HG-04 Preis-Override, HG-05 >30d, HG-06 Verbund); DelegationPolicy-Integration | abgeschlossen |
| AP4 | `app/core/process_sla.py` | SLA-Policy fuer `agrar_settlement` (warning 24h, critical 48h), `agrar_settlement_approval` (warning 8h, critical 24h) und Verbuchungs-Gate (warning 4h, critical 12h) | abgeschlossen |
| AP5 | `app/api/v1/endpoints/process_kernel_api.py` | Settlement-Approval-Status-Surfacing: `GET /process/settlement/approval-status/{settlement_id}` mit Status, erlaubten Uebergaengen, Human-Gate-Regeln und SLA-Policies | abgeschlossen |
| AP6 | `app/core/finance_read_model_contracts.py` | Gemeinsame Vertragstypen fuer alle Finance-Read-Models: SettlementCockpitRow, PositionExposureRow, SettlementCockpitSnapshot, PositionExposureSnapshot; schema_version=1-Enforcement | abgeschlossen |

## Abnahmekriterien — Erfuellt

- [x] `SettlementApprovalRequest` traegt `process_definition_key` und `workflow_version` aus Wave-18-Canonical-Process-Definitions
- [x] Freigabe-Zustandsmaschine verhindert Buchung ohne explizite Freigabe
- [x] Human-Gate blockiert KI-Agenten-Buchung bei Betrag > Schwellwert oder unsicherem Prozesskontext
- [x] Finance-Read-Models liefern `schema_version=1` und sind rueckwaertskompatibel
- [x] SLA-Policy fuer Settlement ist auditierbar und maschinenlesbar
- [x] Keine Schichtverletzungen: `app/core/` importiert keine API-Module

## Tests

| Datei | Tests | Scope |
|-------|-------|-------|
| `tests/test_process_kernel_wave19_settlement_approval.py` | 20 | AP1: Zustandsmaschine, Rollenregeln, Human-Gate, Audit-Entry |
| `tests/test_process_kernel_wave19_human_gate.py` | 21 | AP3: alle 6 HG-Regeln, Prioritaet, Summary, Serialisierung |
| `tests/test_process_kernel_wave19_read_model_contracts.py` | 21 | AP2/AP4/AP5/AP6: Contracts, SLA, API-Endpoints |

**Gesamt Wave 19: 62 Tests gruen**

## Router-Aktivierung (Nebenlieferung)

`finance_read_models` und `process_kernel_api` waren nicht in `app/api/v1/api.py` registriert
(Waves 2 + 11). Nachregistrierung in Wave 19 durchgefuehrt.

## Status
`abgeschlossen` — 2026-03-14 — 1025 Tests Gesamtsuite gruen
