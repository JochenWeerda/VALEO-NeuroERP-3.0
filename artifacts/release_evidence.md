---
title: Release-Evidence-Report
description: Aggregierter Qualitätsnachweis für Staging-/Produktions-Release.
type: reference
audience: [lead, entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-07-06
version: 3.0.0
---

# Release-Evidence-Report

> Stand: 2026-07-06 12:14:57 UTC · SHA: `c2df41595`
> Slice: RELEASE-EVIDENCE-GATE-001

## Gesamtstatus: WARN

| Dimension | Status | Detail |
|---|---|---|
| drift | **PASS** | total_drift_items=0 |
| openapi | **PASS** | openapi.json aktuell |
| inventories | **PASS** | 4/4 Inventar-Dateien vorhanden |
| coverage | **WARN** | 63 Dateien unter Ratchet-Schwellwert |
| slice_harness | **PASS** | 30 Slice-YAMLs vorhanden |
| external | **WARN** | External assessment (2026-07-06): 6 Profile — 6x conditional |

**Zusammenfassung:** 4 PASS · 2 WARN · 0 FAIL

## Gate-Verhalten

Ein Staging-Release wird blockiert wenn `overall_status == fail`.
WARN-Dimensionen erzeugen eine Warnung, blockieren aber nicht.

```bash
# Lokal ausführen:
python scripts/release_evidence_report.py --fail-on-red
```

*Generiert via `scripts/release_evidence_report.py` · 2026-07-06 12:14:57 UTC*
