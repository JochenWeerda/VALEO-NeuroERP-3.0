---
card_id: COM-001
chain: compliance-to-report
chain_step: 0
card_type: overview
flow_spine: flow-spine-compliance-to-report
workflow_doc: docs/workflows/com-001-compliance-to-audit.md
---
# Card: COM-001 — Compliance-to-Audit

| Feld | Wert |
|------|------|
| **Card-ID** | COM-001 |
| **Name** | Compliance-to-Audit (Meldewesen bis Pruefung) |
| **Flow-Spine** | `flow-spine-compliance-to-report` |
| **Status** | P1-Fixes umgesetzt; Gap-Audit 2026-06-25 |
| **Erstellt** | 2026-03-28 |

## Fixes

| Slice-ID | Thema | Status |
|----------|-------|--------|
| COM-002 | BVL-Umsaetze Endpoint implementiert (PSM-Absatzmengen) | **umgesetzt** |

## Offene Gaps

| Gap | Stand 2026-06-25 |
|-----|------------------|
| CamelCase-Mismatch in 5 Compliance-Registern | **offen** — UI/API-Namensangleichung ausstehend |
| ~~audit_evidence.py nicht in api.py registriert~~ | **behoben** — Router in `app/api/v1/api.py` |
| ~~PCN-Navigation zu /compliance/pcn-liste ohne Route~~ | **behoben** — Route + Seite vorhanden |
| Flow-Spine Name: compliance-to-report vs. compliance-to-audit | **Doku** — Benennung in Workflow-Doku harmonisieren |

## Workflow-Dokumentation

Siehe: [docs/workflows/com-001-compliance-to-audit.md](../../workflows/com-001-compliance-to-audit.md)
