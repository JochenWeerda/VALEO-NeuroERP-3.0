# SEC-017 - Security-Regressionen als feste CI-Lane

## Ziel

Bereits behobene P0/P1-Security-Pfade sollen bei jedem relevanten Push reproduzierbar geprueft werden, statt nur auf Scanner-Triage zu warten.

## Scope

- `.github/workflows/security-agent.yml`
- `scripts/security/README.md`
- `docs/agent-ops/active-workboard.md`
- `docs/project-context/open-gaps-and-known-issues.md`

## Umsetzung

- neuer Job `security-regression` im bestehenden Security-Agent-Workflow
- Trigger erweitert auf Workflow-, Test-, Security-Script- und Frontend-Security-Pfade
- Backend-Regressionen:
  - `tests/test_security_*.py`
  - `tests/test_secrets_vault.py`
  - `tests/test_neuro_tool_execution.py`
- Frontend-Regression:
  - `packages/frontend-web/src/__tests__/lib/export-utils.test.ts`
- Docs-Governance wird in derselben Lane mitgeprueft

## Verifikation

- Workflow-YAML validiert lokal ueber bestehende Repo-Checks
- `node scripts/docs-governance-check.cjs`

## Restrisiken

- die Lane deckt gezielt die bisherigen Security-Fixes ab, ersetzt aber keine vollstaendige SAST-/DAST-/Infra-Pruefung
- Backend-Test-Setup bleibt relativ schwergewichtig, solange kein schmaleres Security-Test-Requirements-Set existiert
