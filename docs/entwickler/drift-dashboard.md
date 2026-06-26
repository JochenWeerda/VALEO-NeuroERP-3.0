---
title: Doku-Code-Drift-Dashboard
description: Aktueller Status des Doku-Code-Drift-Reports (DOC-DRIFT-GATE-002).
type: reference
audience: [entwickler, lead]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-26
version: 3.0.0
---

# Doku-Code-Drift-Dashboard

> Generiert via `scripts/generate_drift_dashboard_page.py`
> Quelle: `artifacts/doc_drift_report.json` · `scripts/doc_drift_report.py`

## Status

| Metrik | Wert |
|---|---|
| Gesamter Drift | **0** |
| Status | **GRUEN** |
| Stand | 2026-06-26 08:17 UTC |
| Gate | `--fail-over 0` (DOC-DRIFT-GATE-002) |

## Dimensionen

| Dimension | Anzahl | Status |
|---|---|---|
| Endpoints ohne Doku | 0 | GRUEN |
| Migrationen ohne Runbook | 0 | GRUEN |
| Services ohne Doku | 0 | GRUEN |
| Frontend-Seiten ohne Route/Nav | 0 | GRUEN |

## Offene Punkte

Kein Drift erkannt — Gate ist grün.

## Gate-Verhalten

Der Drift-Gate-Step in `quality-gate.yml` bricht den Build wenn `total_drift_items > 0`:

```bash
python scripts/doc_drift_report.py --fail-over 0
```

Bei neuem Drift sofort beheben:

1. Endpoint/Migration/Service/Seite in bestehendem Inventar-Dokument ergänzen
2. Oder Generator neu ausführen (z. B. `python scripts/generate_code_inventories.py`)
3. Committen — Gate wird grün

## Verlauf

> Historische Drift-Reports werden als CI-Artefakte unter `.github/workflows/doc-drift-report.yml`
> für 90 Tage aufbewahrt (retention-days: 90).

*Stand: 2026-06-26 08:17 UTC · 0 Drift-Items · Slice: DOC-DRIFT-DASHBOARD-002*
