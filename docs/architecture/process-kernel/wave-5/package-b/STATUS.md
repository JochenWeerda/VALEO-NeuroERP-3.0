# Wave 5 Paket B Status

## Paket
- Name: `E2E-Referenzkette, Settlement-Finalisierung und Workflow-Simulation`
- Zugeordnete Aufgaben: `AP2`, `AP3`, `AP4`
- Status: `in Arbeit`

## Ziel
Die Referenzkette Kontrakt → Settlement → FiBu ist lueckenlos.
Workflow-Simulation liefert erklaerbare Entscheidungen fuer alle Kernszenarien.

## Gelieferte Artefakte

| Datei | Inhalt | Status |
|-------|--------|--------|
| `app/core/e2e_chain.py` | `E2EProcessChain`, `E2EChainLink`, `ChainCompletenessReport` | in Arbeit |
| `app/core/workflow_simulation.py` | `SimulationScenario`, `SimulationInput`, `SimulationResult`, `simulate_workflow()` | in Arbeit |
| `app/api/v1/endpoints/e2e_chain.py` | CRUD E2E-Ketten + `GET /completeness` | in Arbeit |
| `app/api/v1/endpoints/workflow_simulation.py` | `POST /workflow/simulation/run` | in Arbeit |
| `tests/test_process_kernel_wave5_e2e_chain.py` | ≥ 18 Tests | in Arbeit |

## E2E-Kettenstruktur (Zielstand)

```
KonContract           → contract_id
  HarvestAcceptance   → harvest_acceptance_id
    QualityProtocol   → quality_protocol_id
      AgrarSettlement → settlement_id
        APInvoice     → ap_invoice_id      (Wave 5 neu)
          JournalEntry → journal_entry_id  (Wave 5 neu)
```

`completeness_pct()` = vorhandene IDs / 6 Kettenglieder × 100

## Simulations-Szenarien

| Szenario | Erwartetes Ergebnis | Schritte |
|----------|---------------------|---------|
| `standard_approval` | `completed` | submit → waiting_approval (12h) → post |
| `rejection` | `rejected` | submit → waiting_approval (4h, abgelehnt) |
| `escalation` | `escalated` | submit → waiting_approval (72h, SLA-Breach) |
| `four_eyes_exception` | `completed` | submit → blocked → second_approval → post |
| `sla_breach` | `escalated` | submit → waiting_approval (96h, WARNING+CRITICAL) |

## Abnahmekriterien
- `E2EProcessChain.completeness_pct()` = 0 fuer leere Kette, 100 fuer vollstaendige
- `ChainCompletenessReport.build()` aggregiert korrekt ueber mehrere Ketten
- `simulate_workflow()` gibt fuer alle 5 Szenarien korrekte `final_status` zurueck
- `SimulationResult.explainability` enthaelt `step_count`, `total_simulated_hours`, `rule_chain`
- `POST /workflow/simulation/run` gibt `SimulationResult` mit `schema_version=1` zurueck

## Abhaengigkeiten
- `app/core/process_references.py` (Wave 1) — wird NICHT veraendert
- `app/core/workflow_runtime.py` (Wave 4 AP1) — `WorkflowInstance` fuer Simulationskontext
- `app/core/process_sla.py` (Wave 4 AP3) — SLA-Szenarien nutzen `evaluate_sla()`-Logik
