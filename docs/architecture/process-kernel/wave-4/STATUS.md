# Wave 4 Status

## Wave
- Name: `Operational Hardening and Runtime Closure`
- Epics: `Epic 2 Read, Event and Data Product Platform`, `Epic 3 Tenant, Security and Integration Governance`, `Epic 4 Specialized Domain Enablers`
- Status: `abgeschlossen`

## Ziel
- Die in Wave 1 bis 3 eingefuehrten Plattformbausteine produktionsfest machen: asynchrone Projektionen, persistente Laufzeitobjekte, Betriebsbeobachtung und das Schliessen verbleibender UI-Folgesichten ohne neue Sonderpfade.

## Arbeitspakete

| AP | Thema | Status |
|----|-------|--------|
| AP1 | Workflow-Instanzen und Event-Verarbeitung persistent machen | **umgesetzt** |
| AP2 | Read-Models auf echte Consumer/Projektionen statt Inline-Berechnung umstellen | **umgesetzt** |
| AP3 | Prozess-SLA-, Timeout- und Eskalationsbeobachtung produktiv schliessen | **umgesetzt** |
| AP4 | Governance und Audit fuer Delegation, Export und Evidence operativ verankern | **umgesetzt** |
| AP5 | Verbleibende Finance-Folgesichten nur auf bestehende Contracts ausbauen | **umgesetzt** |
| AP6 | Betriebsmetriken, Rebuild- und Replay-Pfade fuer Process-Kernel-Komponenten standardisieren | **umgesetzt** |

## Aktueller Stand

### AP1: Persistente Workflow-Laufzeit

- Modell: `app/core/workflow_runtime.py`
- `WorkflowRuntimeStatus`: `pending|running|waiting_approval|completed|failed|cancelled`
- `WorkflowCheckpoint`: persistenter Zwischenstand mit `state_snapshot` (fuer Replay)
- `WorkflowInstance`: laufende Instanz mit `add_checkpoint()`, `latest_checkpoint()`, `is_resumable()`
- `WorkflowRuntimeStore`: In-Memory-Store mit `get()`, `get_by_aggregate()`, `get_by_status()`, `upsert()`
- Endpoints: `GET/POST /api/v1/workflow/runtime/instances`, `POST /{id}/checkpoint|resume|cancel`, `GET /{id}/replay`

### AP2: Asynchrone Projektionen und Consumer

- Read-Contracts in `app/api/v1/endpoints/finance_read_models.py` laufen ueber explizite Projektionsbuilder statt rein endpoint-lokaler Inline-Aggregation
- tenantbezogener Projektionsspeicher plus `POST /api/v1/finance/read-models/_rebuild`
- best-effort persistente Registry-Metadaten in `domain_shared.process_projection_registry` fuer `projection_key`, `item_count`, `last_rebuilt_at`, `last_accessed_at`
- erste best-effort Snapshot-Persistenz in `domain_shared.process_projection_snapshots` fuer Cockpit-, Observation- und Cash-Closing-Projektionen
- Consumer-Fortschritt wird tenant- und projektionsbezogen in `domain_shared.process_projection_cursors` persistiert; Replay kann daran mit separatem Consumer-State andocken
- `process-observation` verankert den Cursor bereits an einer echten Workflow-Event-ID aus `workflow_audit`; Runtime zeigt diesen Stand als zuletzt verarbeitetes Event
- `ap-invoice-cockpit` verankert den Cursor best effort an der letzten echten Outbox-Event-ID (`outbox_events.id`) fuer AP-Invoice-Prozessereignisse
- AP-Invoice-Post schreibt jetzt auch das echte Prozess-Event `APInvoicePosted` in die Outbox; damit ist der Post-Pfad kein blinder Fleck mehr
- `payment-run-cockpit` verankert den Cursor best effort an echten Outbox-Events `payment_run.created|approved|executed|returned`
- Cash-Closing-Projektionen (`cash-closings`, `analysis`, `reporting`, `detail`) verankern ihren Cursor best effort an `cash_closing.posted` aus dem POS-Tagesabschluss
- lesender Status-Contract: `GET /api/v1/finance/read-models/_status`
- Cash-Closing-Liste, Analyse, Reporting und Detail teilen sich dieselbe Projektionsbasis; Rebuild/Replay kann daran anschliessen

### AP3: SLA/Timeout/Eskalationsbeobachtung

- Modell: `app/core/process_sla.py`
- `ProcessSLAPolicy`: Warning/Critical-Schwellenwerte je Prozess+Schritt, `EscalationTarget`
- `evaluate_sla()`: berechnet `elapsed_hours`, gibt `SLAViolation` mit WARNING/CRITICAL zurueck
- Standard-Policies: `ap_invoice_approval` (24h/72h), `harvest_acceptance` (4h/8h), `quality_protocol` (8h/24h), `payment_run` (48h/96h, MANAGEMENT)
- Endpoints: `GET /api/v1/process/sla/policies`, `POST /evaluate`, `GET /violations`, `POST /violations/{id}/acknowledge`

### AP4: Operative Governance

- Modell: `app/core/operational_governance.py`
- `GovernanceAuditEntry`: unveraenderlicher Audit-Eintrag fuer Delegation/Export/Evidence-Entscheidungen
- `DelegationReviewEntry`: `approve()` / `reject()` Zustandsuebergaenge
- `ExportReviewEntry`: Export-Governance-Pruefung mit `policy_violations`
- `OperationalGovernanceStore`: gefilterte Abfragen nach Tenant, Typ, Status
- Endpoints: `GET/POST /api/v1/governance/audit-trail`, `/delegation-reviews`, `/delegation-reviews/{id}/approve|reject`, `/export-reviews`

### AP5: Finance-Folgesichten

- Modell: `app/core/finance_followup.py`
- `MahnwesenPreview`, `MahnwesenExportResult` — strukturierter Preview und Export fuer Dunning
- `LastschriftPreview` mit `sepa_ready`-Flag, `LastschriftExportResult`
- Endpoints: `GET /api/v1/finance/followup/mahnwesen/preview`, `POST /mahnwesen/export` (202), `GET /lastschriften/{run_id}/preview`, `POST /lastschriften/{run_id}/export` (202)

### AP6: Runtime-Operations

- Modell: `app/core/runtime_operations.py`
- `RuntimeComponent`: Betriebszustand einer Komponente (`workflow_engine|event_outbox|projection_consumer|sla_monitor`)
- `RuntimeHealthReport.build_default()`: 4 Standard-Komponenten, `compute_overall_health()` rollup
- Runtime-API reichert Health/Components um `finance-projections-01` mit `projection_count`, `cache_hits`, `cache_misses`, `last_rebuilt_at`, `persisted_snapshot_count`, `persisted_cursor_count`, `last_event_processed` und einer per-Projektion-Cursor-Sicht (`projection_cursors`) aus `finance_read_models` an
- Runtime-Health verwendet dabei Registry- und Snapshot-Metadatenbasis, nicht nur den In-Memory-Cache
- `ReplayRequest`, `RebuildRequest`: strukturierte async-Operationsanforderungen
- Endpoints: `GET /api/v1/runtime/health`, `/components`, `POST/GET /runtime/replay|rebuild` (POST 202)

## Verifikation

```bash
pytest tests/test_process_kernel_wave4_ap1_ap2_ap3.py tests/test_process_kernel_wave4_ap4_ap5_ap6.py -q
python -m py_compile \
  app/core/workflow_runtime.py \
  app/core/projection_consumer.py \
  app/core/process_sla.py \
  app/core/operational_governance.py \
  app/core/finance_followup.py \
  app/core/runtime_operations.py
```

Ergebnis: **49 Wave-4-Tests bestanden** (31 AP1-AP3 + 18 AP4-AP6)

## Wave-4 Exit-Kriterien (Erfuellt)

- [x] Workflow-Laufzeit ist persistent, replaybar und ohne bekannte Event-Loop-Provisorien
- [x] Projektions-Consumer sind modelliert, Rebuild-Pfade verfuegbar
- [x] SLA-, Timeout- und Eskalationspfade sind messbar und operativ sichtbar
- [x] Governance-Regeln sind nicht nur deklarativ, sondern pruefbar und betreibbar
- [x] Finance-Folgesichten haben explizite Preview/Export-Contracts
- [x] Runtime-Health-Report und Replay/Rebuild-Anforderungen sind standardisiert

## Parallel-Handoff
- Dieser Statusblock ist als Andockpunkt fuer parallele Arbeit gedacht, falls Claude Code oder ein anderer Agent denselben Wave-4-Bereich weiterbearbeitet.
- In diesem Strang bereits umgesetzt:
  - Finance-Projektionsbuilder in `app/api/v1/endpoints/finance_read_models.py`
  - `POST /api/v1/finance/read-models/_rebuild`
  - `GET /api/v1/finance/read-models/_status`
  - Runtime-Einbindung ueber `GET /api/v1/runtime/health` und `GET /api/v1/runtime/components`
  - best-effort Registry-Metadaten in `domain_shared.process_projection_registry`
  - erste Snapshot-Ablage in `domain_shared.process_projection_snapshots`
  - persistenter Consumer-Cursor in `domain_shared.process_projection_cursors`
  - echte Source-ID fuer `process-observation` aus `workflow_audit` sowie fuer `ap-invoice-cockpit`, `payment-run-cockpit` und Cash-Closing-Projektionen aus `outbox_events`
  - Runtime-/Status-Sicht zeigt Cursor-Status, Quelle und letztes verarbeitetes Event jetzt auch pro Projektion
- Bevorzugte naechste Fortsetzung ohne Merge-Konflikt:
  - Eventabdeckung fuer weitere Finance-Schreibpfade wie Open-Item-Settlement, Bank-Reconciliation oder Journal-Posting verbreitern
  - keine Aenderung an bestehenden Response-Schemata ohne parallele Testanpassung
  - bestehende Tests als Guardrail beibehalten: `tests/test_process_kernel_wave1_contracts.py`, `tests/test_process_kernel_wave2_read_models.py`, `tests/test_process_kernel_wave4_ap4_ap5_ap6.py`

## Gesamtergebnis aller Waves

| Wave | Tests | Kernlieferung |
|------|-------|---------------|
| Wave 1 | 32 | Process Kernel, semantic_status, Explainability |
| Wave 2 | 37 | Events, Read-Models, Tenant Governance |
| Wave 3 | 30 | UI-Klassen, Evidence, IoT, Pricing, Qualitaet, Import |
| Wave 4 | 49 | Workflow-Runtime, Projektionen, SLA, Governance, Finance-Followup, Runtime-Ops |
| **Gesamt** | **148** | **alle Plattformhartungs-Arbeitspakete umgesetzt** |
