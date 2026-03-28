# Card: COM-001 — Compliance-to-Audit

| Feld | Wert |
|------|------|
| **Card-ID** | COM-001 |
| **Name** | Compliance-to-Audit (Meldewesen bis Pruefung) |
| **Flow-Spine** | `flow-spine-compliance-to-report` |
| **Status** | P1-Fixes umgesetzt |
| **Erstellt** | 2026-03-28 |

## Fixes

| Slice-ID | Thema | Status |
|----------|-------|--------|
| COM-002 | BVL-Umsaetze Endpoint implementiert (PSM-Absatzmengen) | **umgesetzt** |

## Offene Gaps

- CamelCase-Mismatch in 5 Compliance-Registern
- audit_evidence.py nicht in api.py registriert
- PCN-Navigation zu /compliance/pcn-liste ohne Route
- Flow-Spine Name: compliance-to-report vs. compliance-to-audit

## Workflow-Dokumentation

Siehe: [docs/workflows/com-001-compliance-to-audit.md](../../workflows/com-001-compliance-to-audit.md)
