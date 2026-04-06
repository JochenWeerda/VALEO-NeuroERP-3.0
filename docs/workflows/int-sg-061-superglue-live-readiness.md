# INT-SG-061 - Superglue Live Readiness

## Ziel

Die verbleibenden operativen Restluecken nach dem Code-Rollout als belastbare API- und Admin-Sicht surfacen.

## Umgesetzt

- `GET /api/v1/agent/integrations/providers/superglue/live-readiness` liefert tenant-spezifische Readiness mit Ready-/Blocked-Counts, Connector-Blockern und Policy-Werten.
- Die Readiness prueft fehlende Credential-Felder, Platzhalter-Zielsysteme und Execute-Blocker.
- Die Admin-Seite `Agenten-Integration` zeigt die neue Karte `Superglue Live Readiness`.
- `app/core/config.py` enthaelt explizite Settings fuer Error-Rate-Alert, offene Quarantaene sowie Run-/Artifact-Retention.

## Verifikation

- `pytest tests/test_superglue_live_readiness.py tests/test_superglue_connector_registry.py tests/test_process_kernel_wave88_external_agent_integrations.py -q --no-cov`
- `python -m py_compile app/core/config.py app/integrations/services/superglue_connector_registry.py app/integrations/services/superglue_live_readiness.py app/api/v1/endpoints/external_agent_integrations.py tests/test_superglue_live_readiness.py tests/test_superglue_connector_registry.py tests/test_process_kernel_wave88_external_agent_integrations.py`
- `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/admin/agenten-integration.test.tsx`
- `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`
