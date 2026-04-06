# INT-SG-062 - Superglue Onboarding Pack

## Ziel

Einen expliziten Tenant-Onboarding-Pack fuer Ops exportieren, statt Secret-Keys und Zielsystemfelder manuell aus mehreren Stellen zusammensuchen zu muessen.

## Umgesetzt

- `GET /api/v1/agent/integrations/providers/superglue/onboarding-pack` liefert einen Tenant-Pack mit Plattform-Keys, connector-spezifischen Secret-Key-Kandidaten und Policy-Werten.
- Der Pack baut direkt auf der bestehenden Live-Readiness auf und fuehrt keine zweite Modellierung ein.
- Die Admin-Seite `Agenten-Integration` zeigt die neue Karte `Superglue Onboarding Pack`.

## Verifikation

- `pytest tests/test_superglue_onboarding_pack.py tests/test_process_kernel_wave88_external_agent_integrations.py -q --no-cov`
- `python -m py_compile app/integrations/services/superglue_onboarding_pack.py app/api/v1/endpoints/external_agent_integrations.py tests/test_superglue_onboarding_pack.py tests/test_process_kernel_wave88_external_agent_integrations.py`
- `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/admin/agenten-integration.test.tsx`
- `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`
