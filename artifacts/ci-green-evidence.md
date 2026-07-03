---
title: CI-Green-Evidence
type: report
audience: [lead, betrieb, agent]
owner: Claude
status: aktiv
last_reviewed: 2026-07-03
version: 1.0.0
description: Nachweis gruener CI-Runs der drei Ziel-Workflows auf main (SPEC-P0-01 / Prompt A1) mit Run-URLs.
---

# CI-Green-Evidence (SPEC-P0-01)

Ziel: `quality-gate.yml`, `security-scan.yml`, `universal-mask-ci.yml` sichtbar grün auf `main`.
Regel: keine Tests gelöscht, keine Schwellen gesenkt, kein `continue-on-error` auf fachlichen Gates.

## Ausgangslage (2026-07-02)

| Workflow | Status vor A1 | Ursache |
|---|---|---|
| quality-gate | ❌ dauerhaft rot (letzte 5+ Runs) | Backend-Job: `check_sql_fstrings` (2 ungeflaggte Stellen); dahinter weitere nie erreichte rote Gates (response_model 100>80, summary 1>0, Doku-Drift 15) |
| security-scan | ✅ (seit Run 28582265012) | – |
| universal-mask-ci | ✅ (seit Run 28582264967) | – |

## Behobene Ursachen (chronologisch)

1. **Runde 1** (`44d713a23`): sql_fstrings-nosec-Reviews, Low-Stock-Doppelprefix, 4 Klasse-A-Masken
   explainability/wave1_contract, 34 Routen typisiert, Doku-Drift 15→0 (Inventare/C4/Route regeneriert,
   vordruck-editor geroutet, Pilot/Legacy-Fallback-Klassifizierung im Drift-Checker).
   → Ergebnis: Backend-Job kam weiter, **Secret-Scan neu rot** (False Positive auf Audit-Report-Prosa
   + tote `--baseline-path`-Referenz).
2. **Runde 2** (`89d1ea4ca`): `.gitleaks.toml` `^artifacts/`-Allowlist (analog `^docs/`), Baseline-Referenz
   aus quality-gate.yml entfernt, `.env.example`-Platzhalter.
   → Ergebnis: **Docs/code-sync neu rot** (Workflow-Änderung ohne Workboard-Update).
3. **Runde 3** (dieser Stand): Workboard-Eintrag SPEC-P0-01/02; zusätzlich Runtime-Sweep-Programm
   (32×5xx auf frischer DB behoben: Repair-Migration + init_db-create_all + 15 Code-Bugfixes).

## Grüne Runs auf main (wird je Runde ergänzt)

| # | Workflow | Run | Commit | Datum |
|---|---|---|---|---|
| 1 | security-scan | https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/28582265012 | `4a32d41c7` | 2026-07-02 |
| 2 | security-scan | https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/28621749137 | `89d1ea4ca` | 2026-07-02 |
| 1 | universal-mask-ci | https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/28582264967 | `4a32d41c7` | 2026-07-02 |
| – | quality-gate | _ausstehend — Runde 3 nach diesem Push_ | | |

Akzeptanz (3 aufeinanderfolgende grüne Runs je Workflow) wird nach Runde 3 fortgeschrieben.
