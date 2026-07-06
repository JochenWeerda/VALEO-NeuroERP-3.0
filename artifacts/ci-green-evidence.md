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

## quality-gate — der Weg durch die latenten Fehlerschichten

`quality-gate` war seit vor 2026-05-26 dauerhaft rot und scheiterte immer am
jeweils **ersten** noch offenen Gate — jede grüne Schicht legte die nächste frei.
Alle Ursachen waren echte, seit Monaten latente Defekte, die nur nie in einem
CI-Volllauf sichtbar wurden (Kernbefund des Audits: „verifizieren statt behaupten"):

1. sql_fstrings-Gate (2 ungeflaggte Stellen)
2. response_model- + summary-Gate
3. Doku-Drift 15→0 (Inventare/C4/Route regeneriert)
4. Secret-Scan-False-Positives (artifacts-Prosa, tote `--baseline-path`-Referenz, `.env.example`)
5. docs-code-sync (Workflow-/app-Änderung ohne Workboard-Update)
6. Frontend erp-domain-Tests (typechekten gegen nie committetes `dist/`)
7. Mask-Performance-Gate (npx-TypeScript-Drift → gepinnte ts-node-Toolchain)
8. OpenAPI-Versions-Ping-Pong (0.1.0 vs 3.0.0 → fester Default im Generator)
9. Doc-Generator-Meta-Check-Kaskade (openapi/container-inventory/c4/architecture-index)
10. **pytest-Volllauf** — Model/Migrations-Divergenzen: `warehouses.address` JSONB↔String,
    `ownership_type='eigen'` gegen CHECK-Constraint, 2 Vertragskonflikte mit der Parallel-Session
11. Coverage-Ratchet — `psm_proplanta.py` 0,1 pp unter Schwelle durch eigene defensive Zeilen
    → Test statt Schwellensenkung (only-up-Regel)

## Grüne Runs auf main

| Workflow | Ergebnis | Commit | Run |
|---|---|---|---|
| **quality-gate** | ✅ success | `a4ce0f3c2` | https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/28732436888 |
| **security-scan** | ✅ success | `a4ce0f3c2` | https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/28732436857 |
| **universal-mask-ci** | ✅ success | `44d713a23` | https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/28620959114 |
| **runtime-sweep** | ✅ success (0×5xx) | `28b79b4d0` | https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/28731916535 |

Stand 2026-07-05: quality-gate erstmals seit Monaten vollständig grün auf `main`.
`universal-mask-ci` ist pfadgetriggert (grün, seit die zugehörigen Pfade zuletzt geändert
wurden); für den kontinuierlichen 3-Runs-Nachweis läuft er bei nächster Maskenänderung erneut.
Backend-pytest im CI-Volllauf: **11 810 passed, 0 Fehler**, Gesamt-Coverage 65,66 %.
