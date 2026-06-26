---
card_id: COM-001
chain: compliance-to-report
chain_step: 0
card_type: overview
flow_spine: flow-spine-compliance-to-report
workflow_doc: docs/workflows/com-001-compliance-to-audit.md
---
# Card: COM-001 - Compliance-to-Audit

| Feld | Wert |
|------|------|
| **Card-ID** | COM-001 |
| **Name** | Compliance-to-Audit (Meldewesen bis Pruefung) |
| **Flow-Spine** | `flow-spine-compliance-to-report` |
| **Status** | P1/P2-Gaps repo-seitig geschlossen; externe Compliance-Fachabnahme bleibt Gate |
| **Erstellt** | 2026-03-28 |
| **Letzte Konsolidierung** | 2026-06-26 |

## Fixes

| Slice-ID | Thema | Status |
|----------|-------|--------|
| COM-002 | BVL-Umsaetze Endpoint implementiert (PSM-Absatzmengen) | **umgesetzt** |
| COM-003 | Compliance-Register `snake_case`/`camelCase` kompatibel | **umgesetzt** |
| COM-004 | `audit_evidence.py` registriert | **umgesetzt** |
| COM-005 | PCN-Liste Route + Seite vorhanden | **umgesetzt** |

## Geschlossene Gaps

| Gap | Stand 2026-06-26 | Quellen |
|-----|------------------|---------|
| ~~CamelCase-Mismatch in Compliance-Registern~~ | **behoben** | `app/api/v1/endpoints/compliance.py`, `packages/frontend-web/src/lib/api/betrieb.ts`, Register-Seiten |
| ~~audit_evidence.py nicht in api.py registriert~~ | **behoben** | Router in `app/api/v1/api.py` |
| ~~PCN-Navigation zu /compliance/pcn-liste ohne Route~~ | **behoben** | Route + Seite vorhanden |
| Flow-Spine Name: `compliance-to-report` vs. `compliance-to-audit` | **Doku-Rest** | Workflow-Benennung harmonisieren, kein Code-Blocker |

## Verbleibende Gates

- Fachliche Compliance-Abnahme der Register und Meldestrecken.
- Externe Meldesysteme/Behoerdenuebermittlung bleiben getrennte
  Production-Readiness-Gates.

## Reverse-Pflege

Bei Aenderungen an `app/api/v1/endpoints/compliance.py`,
`packages/frontend-web/src/lib/api/betrieb.ts` oder den Register-Seiten muss
diese Card gemeinsam mit `open-gaps-and-known-issues.md` und
`COM-REGISTER-CAMELCASE-001.yaml` neu geprueft werden.

## Workflow-Dokumentation

Siehe: [docs/workflows/com-001-compliance-to-audit.md](../../workflows/com-001-compliance-to-audit.md)
