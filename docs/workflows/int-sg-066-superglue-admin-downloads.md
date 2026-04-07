# INT-SG-066 - Superglue Admin Downloads

## Ziel

Ops soll Onboarding-Artefakte direkt aus der Admin-Seite herunterladen koennen.

## Umgesetzt

- `packages/frontend-web/src/pages/admin/agenten-integration.tsx` bietet Downloads fuer `Onboarding JSON`, `ENV Template` und `Vault Template`.
- Die Downloads basieren auf demselben Onboarding-Pack wie API und CLI.

## Verifikation

- `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/admin/agenten-integration.test.tsx`
- `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`
