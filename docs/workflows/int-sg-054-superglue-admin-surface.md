# INT-SG-054 - Superglue Admin Surface

## Ziel

Betreiberpfade fuer Connectoren, Journal, Quarantaene und Rollouts surfacen.

## Umgesetzt

- `external_agent_integrations.py` liefert Admin-Overview, Monitoring und Domain-Rollouts.
- Die Admin-Seite `agenten-integration.tsx` zeigt die neuen Betriebs- und Rollout-Sichten.
- Secrets bleiben maskiert; nur Betriebsmetadaten werden angezeigt.

## Verifikation

- `pytest tests/test_process_kernel_wave88_external_agent_integrations.py -q --no-cov`
- `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/admin/agenten-integration.test.tsx`

