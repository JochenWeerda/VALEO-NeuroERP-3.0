---
title: OpenAPI-Drift-Gate ohne Branch-Selbstmutation
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-29
description: Nachweis des read-only und fail-closed OpenAPI-Workflows.
---

# OpenAPI-Drift-Gate ohne Branch-Selbstmutation

Der Workflow `.github/workflows/openapi-drift.yml` besitzt nur noch
`contents: read` und führt `generate_openapi.py --check` direkt aus. Bei Drift
endet der Job rot. Er regeneriert, committet und pusht keine Datei mehr auf
`main` oder `develop`.

Die erzeugte `docs/schnittstellen/openapi.json` gehört damit zur verursachenden
API-Änderung und durchläuft denselben Review- und Branch-Schutz.

## Nachweis

`pytest tests/test_openapi_drift_workflow.py -q --no-cov`

Zusätzlich wird die Workflow-Datei als YAML geladen. Doku- und Governance-Gates
laufen für Slice, QA-Nachweis und Workboard.
