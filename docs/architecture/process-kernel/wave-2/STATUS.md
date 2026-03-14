# Wave 2 Status

## Wave
- Name: `Data, Event and Governance Build-out`
- Epics: `Epic 2 Read, Event and Data Product Platform`, `Epic 3 Tenant, Security and Integration Governance`
- Status: `abgeschlossen`
- Abschlussdatum: `2026-03-11`

## Arbeitspakete

| AP | Thema | Status |
|----|-------|--------|
| AP1 | Outbox-/Event-Namenskonvention und erste produktive Event-Pfade | **umgesetzt** |
| AP2 | Read-Models fuer Cockpits, KPI- und Prozessbeobachtung | **umgesetzt** |
| AP3 | Tenant-/Verbundmodell konkretisieren | **umgesetzt** |
| AP4 | Rollen- und Berechtigungsvererbung definieren | **umgesetzt** |
| AP5 | Agenten- und Delegationssicherheitsmodell ausarbeiten | **umgesetzt** |
| AP6 | Export- und Datenresidenzregeln fuer kritische Pfade modellieren | **umgesetzt** |

## Aktueller Stand

### AP1: Outbox-/Event-Namenskonvention

- Event-Modell: `app/domains/shared/process_events.py`
- Namenskonvention: `{tenant_id}.{domain}.{aggregate}.{verb}` (NATS-Subject)
- ADR: `docs/adr/adr-027-process-kernel-event-namenskonvention.md`
- Produktive Events: `APInvoiceApprovalRequested/Granted/Approved/Rejected/Posted`
- Outbox-Writes: AP-Approval-Workflow, Ernte-Annahme (final), Qualitaetsprotokoll (finalize)
- Direct-Debit Wave-1-Contract: `direct_debits.py` mit `/approve` + `/execute`
- Frontend: `lastschriften-debitoren.tsx` auf Wave-1-Endpoints umgestellt

### AP2: Read-Models

- Endpoints: `app/api/v1/endpoints/finance_read_models.py`
- Router: `GET /api/v1/finance/read-models/ap-invoice-cockpit`
- Router: `GET /api/v1/finance/read-models/payment-run-cockpit`
- Router: `GET /api/v1/finance/read-models/process-observation`
- Pydantic-Contracts: `APInvoiceCockpitReadModel`, `PaymentRunCockpitReadModel`, `ProcessObservationReadModel`
- Alle mit `schema_version: int = 1` fuer stabile Query-Contracts
- Architektur-Dok: `docs/architecture/process-kernel/wave-2/package-ap2/READ-MODELS.md`

### AP3: Tenant-/Verbundmodell

- Modelle: `app/core/tenant_governance.py` — `TenantStructure`, `VerbundMember`, `TenantTier`
- Vererbungsregeln: `inherits_policies_from_parent`, `inherits_roles_from_parent`, `data_scope`
- Endpoint: `GET /api/v1/tenant/structure`
- Architektur-Dok: `docs/architecture/process-kernel/wave-2/package-ap3-ap6/GOVERNANCE.md`

### AP4: Rollen- und Berechtigungsvererbung

- Modelle: `RoleInheritanceChain`, `RoleDefinition`, `RoleScope`
- Scopes: `global` / `verbund` / `tenant` / `process`
- Endpoint: `GET /api/v1/tenant/role-inheritance`
- Kernrollen: `fibu.read`, `fibu.write`, `fibu.admin`, `agrar.manager`

### AP5: Agenten- und Delegationssicherheitsmodell

- Modelle: `AgentManifest`, `DelegationPolicy`, `DelegationEntry`, `AgentCapabilityScope`
- Capability-Stufen: READ < WRITE < APPROVE < DELEGATE < EXECUTE_PAYMENT
- KI-Agenten: EXECUTE_PAYMENT gesperrt, human confirmation fuer approve/execute_payment
- Endpoints: `GET /api/v1/tenant/agent-manifests`, `GET /api/v1/tenant/delegation-policy`
- Helper: `build_default_agent_manifest(agent_id, agent_type)`

### AP6: Export- und Datenresidenzregeln

- Modelle: `ExportGovernancePolicy`, `DataResidencyRule`, `DataResidencyZone`, `ExportClassification`
- GoBD-Pflichtregeln: `ap_invoice` (10 Jahre, DE, confidential), `customer_master` (7 Jahre, EU, restricted)
- Endpoint: `GET /api/v1/tenant/data-residency`
- Helper: `build_default_governance(tenant_id)` liefert GoBD-konforme Standardregeln

## Verifikation

```bash
# Alle Wave-2-Tests
pytest tests/test_process_kernel_wave2_events.py tests/test_process_kernel_wave2_read_models.py tests/test_process_kernel_wave2_governance.py -q

# Compile-Check
python -m py_compile \
  app/domains/shared/process_events.py \
  app/api/v1/endpoints/ap_approval_workflow.py \
  app/api/v1/endpoints/harvest_acceptance.py \
  app/api/v1/endpoints/quality_protocols.py \
  app/api/v1/endpoints/direct_debits.py \
  app/api/v1/endpoints/finance_read_models.py \
  app/api/v1/endpoints/tenant_governance.py \
  app/core/tenant_governance.py
```

Ergebnis: **37 Wave-2-Tests passed** (13 Events + 5 Read-Models + 19 Governance)

## Wave-2 Exit-Kriterien (Erfuellt)

- [x] Erste produktive Event-Konsumenten und Read-Models laufen stabil
- [x] Agenten- und Integrationsgrenzen sind technisch und fachlich definiert
- [x] Tenant- und Governance-Regeln sind nicht mehr implizit

## Naechste Schritte

- Wave 2 ist abgeschlossen; Folgearbeit laeuft in Wave 3 oder in nachgelagerten Fachausbaustufen
- Nicht blockierende Warnung aus Testlauf beobachten: Event-Loop-/Outbox-Aufruf in `ap_approval_workflow.py`
