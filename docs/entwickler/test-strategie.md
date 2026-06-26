---
title: Test-Strategie
type: explanation
audience: [entwickler, qa]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-26
version: 3.0.0
---

# Test-Strategie

Überblick über Testebenen und typische Befehle.

## Backend (pytest)

| Marker | Zweck |
|--------|-------|
| `unit` | Reine Logik, keine DB |
| `integration` | DB/API mit Test-Fixtures |
| `e2e` | End-to-End über HTTP |
| `slow` | Lange Läufe (optional auslassen) |

```bash
pytest                    # gesamt
pytest -m unit            # schnell
pytest tests/test_foo.py  # eine Datei
pytest --cov=app          # Coverage
```

Konfiguration: `pytest.ini`. Governance-Gates: Release-Matrix, Tenant-Isolation,
SQL-f-strings, Critical-Coverage-Ratchet.

## Frontend (Vitest)

```bash
cd packages/frontend-web
npm run test
npm run lint
npx tsc --noEmit
```

## E2E (Playwright)

```bash
cd packages/frontend-web
npx playwright test
```

Smoke-Specs unter `playwright-tests/specs/`. Vor E2E: App erreichbar (Health-Check),
Dev-Token/OIDC gemäß `.env`.

## Domänen-Paket (erp-domain)

Vom Repo-Root:

```bash
pnpm test:erp-domain
```

## Doku & Verträge

| Check | Befehl |
|-------|--------|
| MkDocs-Build | `python -m mkdocs build` |
| Staleness | `node scripts/docs-staleness-check.cjs --max-age-days 365` |
| ADR-Nav | `python scripts/generate_adr_nav.py --check` |
| Drift-Report | `python scripts/doc_drift_report.py` |

## Qualitätsziel

Neue Features: mindestens Unit-Tests für Service-Logik; API-Routen mit
`response_model`; UI-Mutationen mit vollständigem Lifecycle (siehe
[Konventionen](konventionen.md)).

Lieferstand offener Restpunkte: [Open Gaps](../project-context/open-gaps-and-known-issues.md)
(repo-only, nicht in MkDocs-Nav).
