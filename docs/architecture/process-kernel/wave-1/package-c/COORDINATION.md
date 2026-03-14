# Wave 1 Coordination

## Zweck
- Konflikte zwischen parallelen Coding-Agents auf Wave-1-Freigabe- und Explainability-Pfaden vermeiden.

## Bereits auf Wave-1-Contract gezogen
- `packages/frontend-web/src/pages/policy-manager.tsx`
- `packages/frontend-web/src/pages/workflow/workflow-sandbox.tsx`
- `packages/frontend-web/src/pages/annahme/qualitaets-check.tsx`
- `packages/frontend-web/src/pages/annahme/abrechnung.tsx`
- `packages/frontend-web/src/pages/finance/ap-invoices-list.tsx`
- `packages/frontend-web/src/pages/finance/ap-invoice-form.tsx`
- `packages/frontend-web/src/pages/finance/index.tsx`
- `packages/frontend-web/src/pages/finance/zahlungslauf-kreditoren.tsx`
- `packages/frontend-web/src/pages/finance/abschluss.tsx`
- `packages/frontend-web/src/pages/finance/ustva.tsx`
- `packages/frontend-web/src/pages/finance/mahnwesen.tsx`
- `packages/frontend-web/src/pages/finance/dunning-editor.tsx`
- `packages/frontend-web/src/pages/finance/lastschriften-debitoren.tsx`
- `packages/frontend-web/src/pages/finance/op-debitoren.tsx`
- `packages/frontend-web/src/pages/finance/kasse.tsx`

## Zugehoerige Backend-Contracts
- `app/api/v1/endpoints/policies.py`
- `app/api/v1/endpoints/admin_core.py`
- `app/api/v1/endpoints/harvest_acceptance.py`
- `app/api/v1/endpoints/quality_protocols.py`
- `app/api/v1/endpoints/agrar_settlements.py`
- `app/api/v1/endpoints/ap_approval_workflow.py`
- `app/api/v1/endpoints/ap_invoices.py`
- `app/api/v1/endpoints/payment_runs.py`
- `app/api/v1/endpoints/direct_debits.py`
- `app/api/v1/endpoints/closing_checklists.py`
- `app/api/v1/endpoints/finance_actions.py`
- `app/api/v1/endpoints/finance_read_models.py`
- `app/api/v1/endpoints/vat_return_export.py`

## Bereits abgesicherte Tests
- `tests/test_app_bootstrap_imports.py`
- `tests/test_process_kernel_wave1_contracts.py` (28 Tests, deckt die produktiven Wave-1-Contracts ab)

## Offene Luecken, bewusst noch nicht parallel anfassen
- Keine neue Wave-1-Luecke fuer `finance/kasse`: Liste, Analyse und Detail laufen bereits ueber getrennte Read-Contracts.
- Weitere Ausbaustufen in `finance/kasse` nur lesend auf `app/api/v1/endpoints/finance_read_models.py:/finance/read-models/cash-closings`, `/analysis`, `/reporting` und `/{id}` aufsetzen.
- Kein neuer Schreibpfad auf `/finance/cash` und keine zweite Abschlusslogik neben POS.

## Arbeitsregel fuer parallele Agents
- Keine neue zweite Explainability- oder Freigabelogik in bereits umgestellten Dateien einfuehren.
- Bestehende Snapshot-Felder weiterverwenden:
  - `approval_status`
- `approval_can_*`
- `approval_override_resolution`
- `approval_explainability`
- `buildDecisionView(...)` bleibt einziger UI-Adapter fuer Explainability.
- Bei `kasse` nur noch auf einen lesenden Snapshot-Contract aufsetzen, nicht auf dem Phantom-CRUD `/finance/cash` weiterbauen.
