# Process Kernel Status

## Gesamtstatus
- Stand: `2026-03-14`
- Status: `Waves 1 bis 21 abgeschlossen; PKP-06 Frontend Explainability Integration abgeschlossen`
- Testergebnis: `1105 Tests gruen, 0 Fehler, 5 skipped, 1 xfailed`

## Waves

| Wave | Status | Tests | Referenz |
|------|--------|-------|----------|
| Wave 1 | abgeschlossen | 35 | `wave-1/STATUS.md` |
| Wave 2 | abgeschlossen | 37 | `wave-2/STATUS.md` |
| Wave 3 | abgeschlossen | 30 | `wave-3/STATUS.md` |
| Wave 4 | abgeschlossen | 49 | `wave-4/STATUS.md` |
| Wave 5 | abgeschlossen | 41 | `wave-5/STATUS.md` |
| Wave 6 | abgeschlossen | 44 | `wave-6/STATUS.md` |
| Wave 7 | abgeschlossen | 56 | `wave-7/STATUS.md` |
| Wave 8 | abgeschlossen | 69 | `wave-8/STATUS.md` |
| Wave 9 | abgeschlossen | 50 | `wave-9/STATUS.md` |
| Wave 10 | abgeschlossen | 11 | `wave-10/STATUS.md` |
| Wave 11 | abgeschlossen | 30 | `wave-11/STATUS.md` |
| Wave 12 | abgeschlossen | 22 | `wave-12/STATUS.md` |
| Wave 13 | abgeschlossen | 27 | `wave-13/STATUS.md` |
| Wave 14 | abgeschlossen | 31 | `wave-14/STATUS.md` |
| Wave 15 | abgeschlossen | 34 | `wave-15/STATUS.md` |
| Wave 16 | abgeschlossen | 31 | `wave-16/STATUS.md` |
| Wave 17 | abgeschlossen | 17 | `wave-17/STATUS.md` |
| Wave 18 | abgeschlossen | 55 | `wave-18/STATUS.md` |
| Wave 19 | abgeschlossen | 62 | `wave-19/STATUS.md` |
| Wave 20 | abgeschlossen | 43 | `wave-20/STATUS.md` |
| Wave 21 | abgeschlossen | 37 | `wave-21/STATUS.md` |

## PKP-06 Frontend Explainability Integration (2026-03-14)

### Ziel
Einheitliche Darstellung von `ExplainabilityView`-Daten (Wave-11 `app/core/explainability.py`) in allen
Prozessmasken — ohne Duplizierung des Rendering-Codes.

### Lieferumfang

| Artefakt | Pfad | Beschreibung |
|----------|------|--------------|
| `ProcessStatusPanel` | `packages/frontend-web/src/components/workflow/ProcessStatusPanel.tsx` | Neuer generischer React-Wrapper; rendert `DecisionView` (statusLabel, statusClassName, summary, details) als farbigen Block; unterstuetzt `children`-Prop fuer gemischte Layouts |
| `buildDecisionView()` | `packages/frontend-web/src/policy/decision-view.ts` | Bereits vorhanden (Wave-1-Frontend-Adapter); mappt `ExplainabilityView` auf `DecisionView` mit deutschen Labels und Tailwind-Farbklassen |

### Refactored Masks (DRY — 11-13 Zeilen Inline-JSX durch Komponente ersetzt)

| Maske | Datei | Art der Integration |
|-------|-------|---------------------|
| AP-Invoice Approval Panel | `features/workflow/APInvoiceApprovalPanel.tsx` | Direktersatz 13-zeiliger Inline-Block |
| Qualitaets-Check Annahme | `pages/annahme/qualitaets-check.tsx` | Direktersatz 13-zeiliger Inline-Block |
| Abrechnungsvorschau Annahme | `pages/annahme/abrechnung.tsx` | Direktersatz 11-zeiliger Inline-Block (Badge in Tabellenzelle bleibt inline) |
| AP Invoice Form | `pages/finance/ap-invoice-form.tsx` | Direktersatz 11-zeiliger Inline-Block |
| Kontraktdetail | `pages/kontrakte/FrmKontraktDetail.tsx` | Client-seitige Synthese: ExplainabilityView aus Vertragsstatus (STORNIERT/ERLEDIGT/OFFEN+matif); kein neuer Backend-Endpoint |

### Mixed-Layout Masks (children-Prop)

| Maske | Datei | Layout |
|-------|-------|--------|
| Abschluss | `pages/finance/abschluss.tsx` | ProcessStatusPanel + 3-spaltige Domain-Grid (Checklistenstatus, Freigabestatus, Abschliessbar) |
| UStVA | `pages/finance/ustva.tsx` | ProcessStatusPanel + 3-spaltige Domain-Grid (Workflowstatus, Abgabefaehig, Regel) |
| Zahlungslauf Kreditoren | `pages/finance/zahlungslauf-kreditoren.tsx` | ProcessStatusPanel + 3-spaltige Domain-Grid (Workflowstatus, Ausfuehrbar, Regel) |
| Lastschriften Debitoren | `pages/finance/lastschriften-debitoren.tsx` | ProcessStatusPanel + 3-spaltige Domain-Grid (Workflowstatus, Ausfuehrbar, Regel) |

### Status-Farbklassen

| ExplainabilityView-Status | Tailwind-Klassen | Deutsches Label |
|--------------------------|------------------|-----------------|
| `blocked` | `bg-red-50 border-red-300 text-red-900` | Blockiert |
| `approval-required` | `bg-amber-50 border-amber-300 text-amber-900` | Freigabe erforderlich |
| `exception` | `bg-orange-50 border-orange-300 text-orange-900` | Ausnahme |
| `allowed` | `bg-blue-50 border-blue-300 text-blue-900` | Freigegeben |
| `auto-execute` | `bg-emerald-50 border-emerald-300 text-emerald-900` | Automatisch |

### Commits
- `[erste Runde]` — ProcessStatusPanel + APInvoiceApprovalPanel + Qualitaets-Check + Abrechnung + FrmKontraktDetail
- `4e3fa372` — Extend ProcessStatusPanel (children/className) + alle Finance-Masken (abschluss, ustva, zahlungslauf, lastschriften, ap-invoice-form)

## Bugfixes (nach Wave-10)

| Fix | Datei | Beschreibung |
|-----|-------|--------------|
| Test-Isolation Wave-10 | `tests/test_process_kernel_wave10_process_mining.py` | `register_*_loader()` durch `monkeypatch.setattr(_gw, ...)` ersetzt — verhindert globale Gateway-Verschmutzung zwischen Tests |
| Schichtverletzung runtime_operations | `app/api/v1/endpoints/runtime_operations.py` + `app/core/projection_cursor_service.py` | `persist_projection_cursor` und `REPLAY_PROJECTION_CONSUMER_ID` aus `finance_read_models` in Core-Modul extrahiert |
| Syntax-Blocker sustainability | `app/api/v1/endpoints/sustainability.py` | abgeschnittenes `StreamingResponse(` im PDF-Export ergaenzt; verhinderte Collection aller Tests die `app.main` importierten |
| NameError crm_reports | `app/api/v1/api.py` | `crm_reports`-Import nach Verwendung; in den Paket-Import-Block vorgezogen |
| Fehlende Wave-6-9-Router | `app/api/v1/api.py` | `agrar_p0`, `supplier_portal`, `silo_operations_api`, `contract_pricing_api`, `reklamation_api`, `price_hedge_api`, `read_model_snapshots`, `edi_api`, `zertifikate_api`, `ernte_kampagne_api` registriert — resultierten in 404 fuer alle Wave-6-9-Tests |
| LangGraph-API-Drift | `tests/test_workflows.py` | `callable(workflow)` durch `hasattr(workflow, 'invoke')` ersetzt — `CompiledStateGraph` ist in aktuellem LangGraph nicht callable |

## Gesamtverifikation

```bash
rg -n --glob '!app/api/v1/endpoints/__init__.py' "from app\.api\.v1\.endpoints|import app\.api\.v1\.endpoints|from \. import [a-zA-Z0-9_]+" app/core app/api/v1/endpoints
# Ergebnis: keine direkten Endpoint-Querimporte in app/core und app/api/v1/endpoints ausser Paket-__init__.py; Kompositionspunkt app/api/v1/api.py ist ausgenommen

pytest tests/test_process_kernel_wave7_read_models.py -q --no-cov
# Ergebnis: 28 passed

pytest tests/test_process_kernel_wave7_domain.py -q --no-cov
# Ergebnis: 28 passed

pytest tests/test_process_kernel_wave8_reporting.py -q --no-cov
# Ergebnis: 13 passed

pytest tests/test_process_kernel_wave8_isolation_retention.py -q --no-cov
# Ergebnis: 30 passed

pytest tests/test_process_kernel_wave8_agent.py -q --no-cov
# Ergebnis: 26 passed

pytest tests/test_process_kernel_wave9_integration.py -q --no-cov
# Ergebnis: 28 passed

pytest tests/test_process_kernel_wave9_domain.py -q --no-cov
# Ergebnis: 22 passed

pytest tests/test_process_kernel_wave10_process_mining.py -q --no-cov
# Ergebnis: 11 passed

pytest tests/test_process_kernel_wave1_contracts.py -q --no-cov
# Ergebnis: 35 passed

pytest tests/test_process_kernel_wave2_events.py -q --no-cov
# Ergebnis: 14 passed

pytest tests/test_process_kernel_wave2_read_models.py -q --no-cov
# Ergebnis: 23 passed

pytest tests/test_agrar_contract_status.py -q --no-cov
# Ergebnis: 4 passed

pytest tests/test_silo_weighted_snapshot.py -q --no-cov
# Ergebnis: 3 passed

pytest tests/test_weighing_ticket_validation.py -q --no-cov
# Ergebnis: 4 passed

pytest tests/test_weighing_ticket_contract_allocation.py -q --no-cov
# Ergebnis: 4 passed

pytest tests/test_tax_keys_validation.py -q --no-cov
# Ergebnis: 4 passed

pytest tests/test_agrar_settlement_calculation.py -q --no-cov
# Ergebnis: 3 passed

pytest tests/test_agrar_compliance_exports.py -q --no-cov
# Ergebnis: 3 passed

pytest tests/test_wasserschutz_zonen_api.py -q --no-cov
# Ergebnis: 26 passed

pytest tests/test_process_kernel_wave10_process_mining.py -q --no-cov
# Ergebnis: 11 passed

pytest tests/test_process_kernel_wave11_commands_policy.py -q --no-cov
# Ergebnis: 30 passed

pytest tests/test_process_kernel_wave14_command_dispatcher.py -q --no-cov
# Ergebnis: 31 passed

pytest tests/test_process_kernel_wave16_aggregate_registry.py -q --no-cov
# Ergebnis: 31 passed

pytest tests/test_process_kernel_wave17_action_execution.py -q --no-cov
# Ergebnis: 17 passed

pytest tests/test_process_kernel_wave18_settlement_contract_propagation.py -q --no-cov
# Ergebnis: 5 passed

pytest tests/test_process_kernel_wave12_sla_commands_dunning.py -q --no-cov
# Ergebnis: 22 passed

pytest tests/test_process_kernel_wave1_contracts.py tests/test_process_kernel_wave12_sla_commands_dunning.py tests/test_process_kernel_wave17_action_execution.py -q --no-cov
# Ergebnis: 74 passed

pytest -q --no-cov
# Ergebnis: 943 passed, 20 failed, 5 skipped, 1 xfailed
# Offene Cluster: Position-Service/Fixtures, Wave-6-Agrar-API-Routen, Wave-7-API-Wiring, Wave-9-Integrationsrouten, Workflow-Build-Contract

pytest tests/test_position_service.py -q --no-cov
# Ergebnis: 14 passed

pytest -q --no-cov
# Ergebnis: 960 passed, 3 failed, 5 skipped, 1 xfailed
# Offene Cluster: Wave-6-Supplier-Compat-Routen (`/contract-pricing/price-matrix`, `/contract-pricing/lots`) und `tests/test_workflows.py::test_bestellvorschlag_workflow_build`

pytest tests/test_process_kernel_wave6_supplier.py::test_api_price_matrix_post tests/test_process_kernel_wave6_supplier.py::test_api_lot_post tests/test_workflows.py::test_bestellvorschlag_workflow_build -q --no-cov
# Ergebnis: 3 passed

pytest -q --no-cov
# Ergebnis: 963 passed, 5 skipped, 1 xfailed
# Verbleibend: nur Warnungen (`Field(env=...)`, `json_encoders`, class-based `Config`, pytest-asyncio event-loop warning)

pytest tests/test_process_kernel_wave1_contracts.py tests/test_process_kernel_wave12_sla_commands_dunning.py tests/test_process_kernel_wave17_action_execution.py -q --no-cov -W default
# Ergebnis: 74 passed, 0 warnings

python -W error::DeprecationWarning -m pytest tests/test_process_kernel_wave1_contracts.py tests/test_process_kernel_wave12_sla_commands_dunning.py tests/test_process_kernel_wave17_action_execution.py -q --no-cov
# Ergebnis: 74 passed

python -W error::DeprecationWarning -c "import app.crm.schemas, app.einkauf.schemas, app.verkauf.schemas"
# Ergebnis: ok

pytest tests/test_workflows.py -q --no-cov -W default
# Ergebnis: 4 passed, 0 warnings

pytest -q --no-cov -W default
# Ergebnis: 1025 passed, 5 skipped, 1 xfailed, 0 warnings
```

## Handoff - Koordination paralleler Arbeit

Dieser Abschnitt ist der verbindliche Uebergabepunkt fuer jeden Agent oder Entwickler,
der an diesem Repository weiterarbeitet. Vor dem Start einer neuen Aufgabe lesen,
nach dem Abschluss aktualisieren.

### Aktueller Belegungsstand (2026-03-14)

| Bereich | Datei / Pfad | Status | Naechste Aktion |
|---------|-------------|--------|-----------------|
| Process Kernel Core | `app/core/workflow_runtime.py` | fertig, stabil | nur erweitern, nicht umbauen |
| Process Kernel Core | `app/core/projection_consumer.py` | fertig, stabil | nur erweitern |
| Process Kernel Core | `app/core/process_sla.py` | fertig, stabil | nur erweitern |
| Process Kernel Core | `app/core/operational_governance.py` | fertig, stabil | nur erweitern |
| Process Kernel Core | `app/core/finance_followup.py` | fertig, stabil | nur erweitern |
| Process Kernel Core | `app/core/runtime_operations.py` | fertig, stabil | nur erweitern |
| API-Router | `app/api/v1/api.py` | aktuell | neue Router nur am Ende neuer Wave-Bloecke anhaengen |
| Finance Read-Models | `app/api/v1/endpoints/finance_read_models.py` | fertig, stabil | `schema_version` nicht aendern; Snapshot- und Cursor-Persistenz ist vorhanden |
| Wave-7-Lieferung | `app/core/read_model_persistence.py` | fertig, stabil | als Basis fuer Datenprodukte nutzen, nicht umbauen |
| Wave-7-Lieferung | `app/infrastructure/models/read_model_snapshots.py` | fertig, stabil | nur erweitern, nicht umbauen |
| Wave-7-Lieferung | `app/core/event_consumer_wiring.py` | fertig, stabil | nicht umbauen |
| Wave-7-Lieferung | `app/api/v1/endpoints/read_model_snapshots.py` | fertig, stabil | nicht umbauen |
| Wave-8-Lieferung | `app/core/reporting_layer.py` | fertig, stabil | Reporting nur erweitern |
| Wave-8-Lieferung | `app/core/tenant_isolation_guard.py` | fertig, stabil | zentrale Guard-Quelle, keine Schattenpruefungen bauen |
| Wave-8-Lieferung | `app/core/multi_context_agent.py` | fertig, stabil | nur erweitern |
| Wave-8-Lieferung | `app/core/betriebskennzahlen.py` | fertig, stabil | nur erweitern |
| Wave-8-Lieferung | `app/core/gobd_retention.py` | fertig, stabil | nur erweitern |
| Wave-8-Lieferung | `app/api/v1/endpoints/reporting_api.py` | fertig, stabil | Tenant-Isolation nicht umgehen |
| Wave-8-Lieferung | `app/api/v1/endpoints/agent_context_api.py` | fertig, stabil | Guard-Anbindung beibehalten |
| Wave-8-Lieferung | `app/api/v1/endpoints/benchmark_api.py` | fertig, stabil | nur erweitern |
| Wave-9-Lieferung | `app/core/edi_integration.py` | fertig, stabil | nur erweitern |
| Wave-9-Lieferung | `app/core/api_gateway_manifest.py` | fertig, stabil | nur erweitern |
| Wave-9-Lieferung | `app/core/zertifikate.py` | fertig, stabil | nur erweitern |
| Wave-9-Lieferung | `app/core/ernte_kampagne.py` | fertig, stabil | nur erweitern |
| Wave-9-Lieferung | `app/core/frontend_process_binding.py` | fertig, stabil | nur erweitern |
| Wave-9-Lieferung | `app/api/v1/endpoints/edi_api.py` | fertig, stabil | nur erweitern |
| Wave-9-Lieferung | `app/api/v1/endpoints/zertifikate_api.py` | fertig, stabil | nur erweitern |
| Wave-9-Lieferung | `app/api/v1/endpoints/ernte_kampagne_api.py` | fertig, stabil | nur erweitern |
| Wave-10-Lieferung | `app/core/process_mining.py` | fertig, stabil | gemeinsame Mining-Sicht fuer Reporting und Benchmark weiterverwenden |
| Wave-10-Lieferung | `app/core/process_mining_application.py` | fertig, stabil | zentrale Orchestrierung; keine Endpoint-Querimporte wieder einfuehren |
| Wave-10-Lieferung | `app/api/v1/endpoints/process_mining_api.py` | fertig, stabil | neue Mining-Sichten nur auf derselben Kernlogik aufsetzen |
| Wave-10-Lieferung | `app/api/v1/endpoints/reporting_api.py` | erweitert, stabil | Mining-Reporting nicht ausserhalb dieses Pfads duplizieren |
| Wave-10-Lieferung | `app/api/v1/endpoints/benchmark_api.py` | erweitert, stabil | Benchmarking weiter aus Mining- und Kennzahl-Contracts ableiten |
| Wave-1-Compat-Fix | `app/api/v1/endpoints/policies.py` | erweitert, stabil | strukturierte Override-/Explainability-Antworten beibehalten |
| Wave-1-Compat-Fix | `app/api/v1/endpoints/ap_approval_workflow.py` | erweitert, stabil | Audit-/Workflow-Ref-Helfer und Dokumentstatus-Sync nicht entfernen |
| Wave-1-Compat-Fix | `app/api/v1/endpoints/ap_invoices.py` | erweitert, stabil | `semantic_status` und Approval-Snapshots als kompatiblen Response-Vertrag beibehalten |
| Wave-1-Compat-Fix | `app/api/v1/endpoints/payment_runs.py` | erweitert, stabil | Approval-Snapshot + Outbox-Kompatibilitaet beibehalten |
| Wave-1-Compat-Fix | `app/api/v1/endpoints/closing_checklists.py` | erweitert, stabil | Closing-Workspace-Kompatibilitaetsfunktionen als Fassade erhalten |
| Wave-1-Compat-Fix | `app/api/v1/endpoints/vat_return_export.py` | erweitert, stabil | Approval-/Submission-Contract fuer UStVA nicht rueckbauen |
| Deprecation-Cleanup | `app/core/database.py` + `app/models/documents.py` | reduziert | `declarative_base()` auf `sqlalchemy.orm.declarative_base` umgestellt |
| Deprecation-Cleanup | `app/core/config.py` | weiter reduziert | verbliebenes `Field(env=...)` entfernt; Settings laufen ohne Pydantic-v2-Extra-Keyword-Warnung |
| Deprecation-Cleanup | `app/api/v1/schemas/base.py` + zentrale API-/Finance-Schemas | weiter reduziert | `json_encoders` entfernt und breit importierte `class Config`-Modelle auf `ConfigDict` umgestellt |
| Deprecation-Cleanup | `app/crm/schemas.py` + `app/einkauf/schemas.py` + `app/verkauf/schemas.py` | weiter reduziert | restliche v1-`class Config`-Altmodule der Kern-Domänen auf `ConfigDict` umgestellt; direkter Import laeuft unter `-W error::DeprecationWarning` |
| Position-Service | `app/services/position_service.py` | erweitert, stabil | Negativpositionen innerhalb Toleranz bleiben gelb; nicht wieder auf gruen zurueckdrehen |
| Position-Service | `app/services/position_guard_service.py` | erweitert, stabil | ohne aktive Regel keine implizite Short-Blockade erzeugen |
| Position-Service | `tests/test_position_service.py` | isoliert | Tenant-basierte Bereinigung + Nested-Transaction-Fixture fuer reproduzierbare DB-Tests beibehalten |
| Test-Kompatibilitaet | `app/main.py` | leichtgewichtig, testfokussiert | fuer TestClient/Fallback beibehalten; produktive App bleibt `main.py` |
| Tests Wave 1-4 | `tests/test_process_kernel_wave[1-4]_*.py` | Abnahme-Contracts | nicht aendern |
| Core-Hilfsdienst | `app/core/projection_cursor_service.py` | fertig, stabil | Cursor-Persistenz und REPLAY_PROJECTION_CONSUMER_ID; von runtime_operations und finance_read_models importieren |
| Test-Isolation | `tests/test_process_kernel_wave10_process_mining.py` | korrigiert | gateway-Registrierungen via monkeypatch.setattr — nie register_*_loader() direkt in Tests aufrufen |
| Wave-11-Lieferung | `app/core/process_commands.py` | fertig, stabil | Command-Katalog (13 Commands); get_process_command_catalog() ist stabiler Export |
| Wave-11-Lieferung | `app/core/process_references.py` | fertig, stabil | ProcessReferenceChain/Context; nur erweitern |
| Wave-11-Lieferung | `app/core/agrar_process_references.py` | fertig, stabil | agrar-spezifische Reference Builder |
| Wave-11-Lieferung | `app/core/exception_rules.py` | fertig, stabil | ProcessExceptionCatalog; neue Prozesse als eigenes Catalog-Objekt |
| Wave-11-Lieferung | `app/core/explainability.py` | fertig, stabil | ExplainabilityView + build_policy_explainability_view() |
| Wave-11-Lieferung | `app/core/policy_decisions.py` | fertig, stabil | PolicyOverrideResolution + resolve_policy_override_layers() |
| Wave-11-Lieferung | `app/api/v1/endpoints/process_kernel_api.py` | fertig, stabil | Wave-11-Router (prefix /process); alle 6 APs |
| Wave-14-Lieferung | `app/core/business_commands.py` | fertig, stabil | build_core_command_catalog() — 9 Commands mit Preconditions, Rollen, Agent-Types |
| Wave-14-Lieferung | `app/core/command_dispatcher.py` | fertig, stabil | CommandDispatcher.dispatch() — check_role + check_preconditions + human_confirmation |
| Wave-14-Lieferung | `app/core/agent_command_manifest.py` | fertig, stabil | AgentCommandManifest — restricted + fully_blocked; build_agent_command_manifest() |
| Wave-15-Lieferung | `app/core/ap_approval_status.py` | fertig, stabil | ApprovalStatusResponse + Status-Mapping-Dicts + build_approval_status_response() |
| Wave-15-Lieferung | `app/core/ap_approval_events.py` | fertig, stabil | build_ap_approval_outbox_event() — alle 4 Ereignispfade |
| Wave-15-Lieferung | `app/core/workflow_simulation.py` | fertig, stabil | simulate_workflow() — 5 Szenarien; rein modellbasiert, keine DB |
| Wave-15-Lieferung | `app/core/silo_quality.py` | fertig, stabil | weighted_quality_snapshot() — gewichtete Durchschnitte, inactive-Filter |
| Wave-15-Lieferung | `app/core/e2e_chain.py` | fertig, stabil | E2EProcessChain + ChainCompletenessReport.build() |
| Wave-16-Lieferung | `app/core/aggregate_registry.py` | fertig, stabil | 8 Aggregate mit Besitzer, Commands, Read-Models, Agent-Tools; get_aggregate_definition() wirft KeyError bei unbekanntem Typ |
| Wave-17-Lieferung | `app/core/action_execution.py` | fertig, stabil | zentraler Execute-Orchestrator; keine zweite Action-Logik ausserhalb dieses Moduls bauen |
| Wave-17-Lieferung | `app/core/action_idempotency.py` | fertig, stabil | Replay und Konflikte nur ueber diesen Store modellieren |
| Wave-17-Lieferung | `app/api/v1/endpoints/process_kernel_api.py` | erweitert, stabil | Execute-, Execution- und Idempotency-Lookups nur in diesem Router erweitern |
| Wave-18-Lieferung | `app/core/canonical_process_definitions.py` | fertig, stabil | zentrales Register fuer Canonical Process Definitions; neue Kernprozesse nur hier verankern |
| Wave-18-Lieferung | `app/core/workflow_versioning.py` | fertig, stabil | aktive Versionen, Draft-Nachfolger und Aktivierungsregeln nur ueber dieses Modul modellieren |
| Wave-18-Lieferung | `app/core/process_audit_contracts.py` | fertig, stabil | Prozess-Audit immer ueber `process_definition_key` und `WorkflowDefinitionRef` anbinden |
| Wave-18-Lieferung | `app/core/process_sla.py` | erweitert, stabil | SLA-Metadaten fuer `process_definition_key` und Workflow-Version pflegen; alte `process_key`-Contracts bleiben kompatibel |
| Wave-18-Lieferung | `app/core/action_execution.py` + `app/core/business_commands.py` | erweitert, stabil | Execute-/Command-Contracts tragen jetzt Wave-18-Prozessmetadaten; keine zweite Action-Validierung ausserhalb dieses Pfads bauen |
| Wave-18-Lieferung | `app/api/v1/endpoints/process_kernel_api.py` | erweitert, stabil | lesende Surfacing-Endpoints fuer Process Definitions und Workflow-Versionen sind vorhanden; keine schreibenden Sonderpfade aufbauen |
| Wave-18-Follow-up | `app/core/process_audit_contracts.py` | erweitert, stabil | Audit-Bruecke vom Action-Layer in `ProcessAuditEntry` ist vorhanden; keine Audit-Logik in Endpoints duplizieren |
| Wave-18-Follow-up | `app/core/settlement_compatibility.py` | fertig, stabil | Legacy-`settlement` und Canonical-`agrar_settlement` nur ueber diesen Vertrag zusammenfuehren |
| Wave-18-Follow-up | `app/core/process_references.py` + `app/core/agrar_process_references.py` + `app/core/e2e_chain.py` | erweitert, stabil | Legacy-Surfaces bleiben bestehen, tragen aber jetzt explizite Canonical-Metadaten statt impliziter Aliase |
| Wave-18-Follow-up | `app/core/process_commands.py` + `app/core/exception_rules.py` + `app/core/process_config.py` + `app/core/settlement_commands.py` | erweitert, stabil | ausserhalb des direkten Kerns tragen Settlement-Altpfade jetzt kanonische Metadaten statt freier Zusatz-Aliase |
| Externer Testblocker | `app/api/v1/endpoints/compat.py` + `app/core/workflow_definitions.py` | behoben | Importblocker fuer breitere Regressionslaeufe beseitigt; Wave-11/12 laufen wieder |
| Sichtbar gewordene Altlast | `tests/test_process_kernel_wave1_contracts.py` | offen | nach Blocker-Fix jetzt 26 fachliche Fehler in Finance-/Approval-/VAT-/Closing-Pfaden sichtbar; separat priorisieren |
| Wave-18-Naechster Schritt | `docs/architecture/process-kernel/wave-18/STATUS.md` | vorbereitet | die freigelegten Wave-1-Altbaustellen geordnet angehen, statt weitere Infrastruktur-Blocker zu suchen |
| PKP-06-Frontend | `packages/frontend-web/src/components/workflow/ProcessStatusPanel.tsx` | fertig, stabil | einzige Renderquelle fuer ExplainabilityView/DecisionView; kein zweites Inline-Rendering bauen |
| PKP-06-Frontend | `packages/frontend-web/src/policy/decision-view.ts` | fertig, stabil | buildDecisionView() ist der einzige Adapter zwischen Backend-ExplainabilityView und Frontend-DecisionView |
| PKP-06-Frontend | `packages/frontend-web/src/features/workflow/APInvoiceApprovalPanel.tsx` | refactored, stabil | ProcessStatusPanel eingebunden; kein Rueckfall auf Inline-Rendering |
| PKP-06-Frontend | `packages/frontend-web/src/pages/annahme/qualitaets-check.tsx` | refactored, stabil | ProcessStatusPanel eingebunden |
| PKP-06-Frontend | `packages/frontend-web/src/pages/annahme/abrechnung.tsx` | refactored, stabil | ProcessStatusPanel fuer Vorschau-Block; Badge in Tabellenzelle bleibt inline |
| PKP-06-Frontend | `packages/frontend-web/src/pages/finance/ap-invoice-form.tsx` | refactored, stabil | ProcessStatusPanel eingebunden |
| PKP-06-Frontend | `packages/frontend-web/src/pages/finance/abschluss.tsx` | refactored, stabil | Mixed-Layout via children-Prop |
| PKP-06-Frontend | `packages/frontend-web/src/pages/finance/ustva.tsx` | refactored, stabil | Mixed-Layout via children-Prop |
| PKP-06-Frontend | `packages/frontend-web/src/pages/finance/zahlungslauf-kreditoren.tsx` | refactored, stabil | Mixed-Layout via children-Prop |
| PKP-06-Frontend | `packages/frontend-web/src/pages/finance/lastschriften-debitoren.tsx` | refactored, stabil | Mixed-Layout via children-Prop |
| PKP-06-Frontend | `packages/frontend-web/src/pages/kontrakte/FrmKontraktDetail.tsx` | erweitert, stabil | Client-seitige ExplainabilityView-Synthese aus Vertragsstatus; kein neuer Backend-Endpoint |

### Konfliktregeln

1. **Bestehende `schema_version`-Felder nicht aendern** - Contract-Tests schlagen sonst fehl
2. **`app/api/v1/api.py` nur am Ende neuer Wave-Bloecke erweitern** - nie bestehende `include_router`-Zeilen entfernen
3. **`app/core/` - neue Dateien anlegen statt bestehende umzustrukturieren** - jeder Schritt baut auf dem vorherigen auf
4. **Tests in `tests/test_process_kernel_wave[1-4]_*.py` sind unveraenderlich** - sie sind die Abnahme-Contracts der abgeschlossenen Waves
5. **DB-Tests: Fixture muss `join_transaction_mode="create_savepoint"` verwenden** - siehe `tests/test_position_service.py` als Referenz
6. **Keine Schichtverletzungen** - `app/core/` darf nichts aus `app/api/` importieren; gemeinsame Orchestrierung gehoert in Core-Services, nicht in Endpoint-Querimporte
7. **Keine Endpoint-Querimporte** - Endpoints konsumieren gemeinsame Gateways/Services oder Infrastrukturbausteine; Route-Module importieren keine anderen Route-Module direkt
8. **Kompositionspunkte sind explizit** - Router-Aggregation in `app/api/v1/api.py` und Paket-`__init__.py` ist erlaubt; fachliche Logik darf dort nicht neu entstehen
9. **Tests patchen keine Endpoint-Interna, wenn bereits stabile Pure Functions oder Core-Services existieren** - Event-Building, Projektionen und Ableitungen gegen Core-/Projektions-Contracts testen, nicht gegen private Route-Helfer
10. **Gateway-Registrierungen in Tests immer via `monkeypatch.setattr(_gw, "_loader_name", ...)` durchfuehren** - `register_*()` direkt aufzurufen verschmutzt globalen Zustand und bricht andere Tests; monkeypatch stellt automatisch den Ursprungswert wieder her

## Laufende offene Punkte

- Event-Loop-Warnung in `ap_approval_workflow.py` ist weiter best-effort und nicht blockierend
- im breit genutzten Process-Kernel-/Finance-Schnitt (`Wave 1/12/17`) sind die zuvor offenen Pydantic-Deprecation-Warnungen jetzt eliminiert; verbleibende Repo-weite Warnungen separat pruefen
- die frueheren Altmodule in `app/crm`, `app/einkauf` und `app/verkauf` sind als weitere Pydantic-v1-Warnungsquelle bereinigt; naechste Repo-weite Quellen gezielt isolieren
- der repo-weite Warnungsabbau ist aktuell abgeschlossen; auch die frueheren `pytest_asyncio`-Event-Loop-Warnungen in `tests/test_workflows.py` sind beseitigt
- Der globale Roadmap-Status ausserhalb dieses Ordners kann hinter den Paket-STATUS-Dateien liegen und muss bei grossen Abschlussstaenden separat nachgezogen werden
- keine inhaltlichen offenen Punkte in Wave 10; weitere Arbeit gehoert in die naechste Wave
- Schichtgrenzen sind repo-weit bei neuer Arbeit aktiv gegen `rg` zu pruefen; Paket-`__init__.py` ist davon ausgenommen
- Wave-1-/Wave-2-Testkopplungen wurden fuer AP-Approval-Outbox und Cash-Closing-Ableitungen auf Core-/Projektionsfunktionen reduziert; weitere Testbereinigungen sollen demselben Muster folgen
- Agrar-/Silo-/Wiegeschein-Pure-Functions liegen jetzt in neutralen Modulen (`app/core/agrar_contract_status.py`, `app/core/silo_quality.py`, `modules/agrar/services/weighing_domain.py`); direkte Test-Imports privater Endpoint-Helfer wurden fuer diese Bereiche entfernt
- Reine Validierungs- und Kalkulationsmodelle liegen ebenfalls ausserhalb der Endpoints (`app/core/tax_key_models.py`, `app/core/agrar_settlement_models.py`, `app/core/agrar_settlement_calculation.py`); Modell- und Rechen-Tests importieren diese Bausteine nicht mehr aus Route-Modulen
- Compliance-Export- und Wasserschutz-Zonen-Helfer liegen ebenfalls neutral in `app/core/compliance_exports.py` und `app/core/wasserschutz_zonen.py`; die zugehoerigen Tests importieren keine API-Module mehr
- Projection-Status-Datenvertraege fuer Mining-Tests liegen zusaetzlich neutral in `app/core/finance_projection_status.py`; Wave-10-Tests importieren diese Typen nicht mehr aus `finance_read_models.py`
- die volle Repo-Suite hat weiterhin 6 Fehler in `tests/test_workflow_api.py`; sie liegen ausserhalb des Process-Kernel-Wave-17-Scopes und blockieren die Wave-17-Contracts nicht

## Offene Follow-ups

- Dunning-, Lastschrift- und Kassen-Folgesichten nur auf `finance_followup.py`-Contracts aufsetzen
- Externe Integrations- und Frontend-Arbeit ab Wave 10 auf den abgeschlossenen Wave-9-Bausteinen aufsetzen, nicht ueber neue Sonderpfade
- Wave-10-Ausbau auf `process_mining.py`, `reporting_layer.py` und bestehende Runtime-Metriken konzentrieren statt neue Schatten-Analytics zu bauen
- Bei neuer Arbeit Schichtgrenzen aktiv pruefen: kein Core-Code darf auf API-/Endpoint-Module zeigen
- Echte fachliche Mutationen und persistente Idempotenz erst hinter `ActionExecutionService` und `ActionIdempotencyStore` nachziehen; keine zweite Execute-API aufbauen

## Priorisierte naechste Wave

- Referenz: `wave-18/STATUS.md`
- Strategischer Ursprung: `C:\Users\Jochen\.cursor\plans\valeo_wettbewerbsanalyse_spitzenposition_79027aec.plan.md`
- Ziel: den Process Kernel von abgeschlossenen Infrastrukturbausteinen auf verbindliche, versionsfaehige Prozess- und Command-Contracts fuer die Landhandel-Kernprozesse heben
- Prioritaet vor weiterer API-Breite: Canonical Process Definitions, Workflow-Versionierung, SLA/Audit-Verankerung, Human-in-the-loop-faehige Action-Contracts
