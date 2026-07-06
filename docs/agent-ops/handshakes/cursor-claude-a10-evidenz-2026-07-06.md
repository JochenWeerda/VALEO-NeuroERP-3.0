# Handshake: Cursor Agent → Claude Code (A10 Evidenzkette, Teilstand)

Stand: 2026-07-06
Von: Cursor Agent
An: Claude Code
Slice: `A10-DOKU-EVIDENZ-001`
Branch: `fix/pii-remediation`

## Kontext

Prompt A10 verlangt gemessene Werte in README/Open-Gaps/Process-Kernel sowie grüne Drift- und Release-Evidence-Kette. Umsetzbar **ohne** A9-Abschluss.

## Erledigt (2026-07-06)

| Artefakt | Ergebnis |
|---|---|
| `doc_drift_report.py --fail-over 0` | Exit 0, 0 Items |
| `generate_drift_dashboard_page.py` | `drift-dashboard.md` aktualisiert |
| `generate_openapi.py` | 2537 Pfade → `openapi.json` |
| `release_evidence_report.py --fail-on-red` | Exit 0, overall **WARN** (coverage + external) |
| README Statusblock | gemessene Werte 2026-07-06 |
| Open-Gaps | P0-01/02 erledigt; A10-Teilstand-Section |
| Process-Kernel STATUS | Querschnitt 2026-07-06 |
| `.gitignore` | `release_evidence.{json,md}` versionierbar |

## Release-Evidence WARN — erwartet

- **coverage:** 63 Pfade unter Ratchet ohne Vollsuite-`coverage.xml` lokal
- **external:** `production-readiness-assessment.json` wird in CI erzeugt, nicht lokal committed

Kein FAIL — Staging-Release laut Gate-Logik nicht blockiert.

## Claude: Nächste Schritte (Voll-A10)

1. Nach A9-Merge: `release_evidence_report.py` auf `main`-SHA erneut laufen lassen
2. Optional: `simulate_external_assessors.py`-Output in `check_external()` auswerten (Format `{profiles: [...]}`)
3. CI-Artefakt `production-readiness-assessment.json` in Release-Gates committen oder API-Gate anpassen
4. README-CI-Zeile nach Branch-Merge mit frischem `main`-Run aktualisieren

## Verifikation

```bash
python scripts/doc_drift_report.py --fail-over 0
python scripts/generate_openapi.py --check
python scripts/release_evidence_report.py --fail-on-red --sha $(git rev-parse --short HEAD)
```
