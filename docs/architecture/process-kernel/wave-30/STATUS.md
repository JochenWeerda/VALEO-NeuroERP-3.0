# Wave-30 Status

## Scope
Human-in-the-loop AI-Freigaben (Gap 015) + SLO/SLI-Definitionen (Gap 050)

## Zielbild

Wave 30 schliesst zwei P0-Luecken:
Gap 015 (Human-in-the-loop Freigaben fuer AI Aktionen — 100% AI-Aktionen mit Approval-Trail)
und Gap 050 (Produktive Betriebsfuehrung mit SLO/SLI — Verfuegbarkeit >=99.9%).

Der Human-Approval-Gate klassifiziert jede Agent-Aktion nach Risikostufe
und erzwingt fuer HOCH/KRITISCH eine menschliche Freigabe mit Audit-Trail.
Die SLO/SLI-Definitions liefern typisierte Service-Level-Objectives fuer
alle Kernprozesse sowie pruefbare Compliance-Auswertung.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/human_approval_gate.py` | `ApprovalRisikostufe`, `HumanApprovalRequirement`, `evaluate_approval_requirement()` — klassifiziert Agent-Aktionen nach Risiko | abgeschlossen |
| AP2 | `app/core/human_approval_gate.py` | `ApprovalDecision`, `ApprovalRecord`, `record_approval_decision()`; `get_default_approval_rules()` — Default-Regeln fuer Agrar-Commands | abgeschlossen |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | `POST /process/agent/approval-evaluate` + `GET /process/agent/approval-rules` | abgeschlossen |
| AP4 | `app/core/slo_definitions.py` | `SLOTyp`, `SLODefinition`, `SLIDefinition`, `get_process_kernel_slos()` — Default-SLOs fuer Kern-Dienste | abgeschlossen |
| AP5 | `app/core/slo_definitions.py` | `check_slo_compliance(slo, ist_wert)` → `SLOComplianceResult`; `validate_slo_definition()` | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/slo/registry[?dienst=]` + `POST /process/slo/check` | abgeschlossen |

## Abnahmekriterien

- `evaluate_approval_requirement()` klassifiziert NIEDRIG/MITTEL/HOCH/KRITISCH deterministisch
- HOCH und KRITISCH erzwingen menschliche Freigabe (`requires_human_approval=True`)
- `ApprovalRecord` ist unveraenderlich und traegt Zeitstempel + Begruendung (Audit-Trail)
- SLO-Definitions decken Verfuegbarkeit, Latenz, Fehlerrate und Durchsatz ab
- `check_slo_compliance()` vergleicht Ist-Wert gegen Zielwert + Toleranzband
- Keine Schichtverletzungen; `app/core/` importiert kein `app/api/`

## Tests

| Datei | Tests | Scope |
|-------|-------|-------|
| `tests/test_process_kernel_wave30_approval_slo.py` | 44 | AP1: evaluate_approval_requirement() (10 Tests, alle Risikostufen + Grenzwerte); AP2: record_approval_decision() (4 Tests, Immutabilitaet, Hash, Determinismus); AP4: SLORegistry (7 Tests); AP5: check_slo_compliance() (8 Tests, alle Status + Typen); validate_slo_definition() (4 Tests); AP3/AP6: API-Endpoints (11 Tests) |

**Gesamt Wave 30: 44 Tests gruen**

## Gaps geschlossen

| Gap-ID | Beschreibung | Massnahme |
|--------|-------------|-----------|
| Gap 015 | Human-in-the-loop Freigaben fuer AI Aktionen | `human_approval_gate.py`: `evaluate_approval_requirement()` (NIEDRIG/MITTEL/HOCH/KRITISCH), `record_approval_decision()` (frozen ApprovalRecord, SHA-256 kontext_hash, Audit-Trail), 8 Default-Regeln fuer Agrar-Commands; API GET /process/agent/approval-rules + POST /process/agent/approval-evaluate |
| Gap 050 | Produktive Betriebsfuehrung mit SLO/SLI | `slo_definitions.py`: `SLODefinition` + `SLIDefinition`, `check_slo_compliance()` (ERFUELLT/TOLERANZBEREICH/VERLETZT/UNBEKANNT), `validate_slo_definition()`, 9 Default-SLOs (api_gateway×3, agrar_settlement×2, wareneingang×2, workflow_engine, compliance_service); API GET /process/slo/registry + POST /process/slo/check |

## Status
`abgeschlossen` — 2026-03-15 — 44 Tests gruen, Gaps 015 + 050 geschlossen
