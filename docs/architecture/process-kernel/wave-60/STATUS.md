# Wave 60 — Process Forecasting + Workflow Handover

**Status:** DONE
**Datum:** 2026-03-16
**Tests:** 157 passed, 0 failed, 0 skipped

## Module

| Modul | Datei | Kernfunktionalität |
|-------|-------|--------------------|
| Process Forecast Contracts | `app/core/process_forecast_contracts.py` | Load Forecasting, Capacity Planning Predictions |
| Workflow Handover Contracts | `app/core/workflow_handover_contracts.py` | Team/Role Handover, Hand-off Tracking |

## Neue Klassen & Funktionen

### process_forecast_contracts.py
- `PrognoseTyp` — Enum: LAST, DURCHLAUFZEIT, FEHLERRATE, KAPAZITAET
- `PrognoseMethode` — Enum: GLEITENDER_DURCHSCHNITT, GEWICHTETER_DURCHSCHNITT, LINEARE_REGRESSION, SAISONBEREINIGT
- `KonfidenzNiveau` — Enum: NIEDRIG (<60%), MITTEL (60–80%), HOCH (>80%)
- `Datenpunkt` — Dataclass: zeitstempel + wert
- `PrognoseErgebnis` — Dataclass mit `konfidenz_niveau` Property
- `berechne_gleitenden_durchschnitt()` — Moving average over last N points
- `berechne_gewichteten_durchschnitt()` — Position-weighted average (recent = higher weight)
- `erstelle_prognose()` — Factory function dispatching to correct algorithm
- `get_default_prognosen()` — 4 demo forecasts (PG-001..PG-004)

### workflow_handover_contracts.py
- `UebergabeTyp` — Enum: ESKALATION, DELEGATION, STELLVERTRETUNG, ABSCHLUSS
- `UebergabeStatus` — Enum: ANGEFRAGT, ANGENOMMEN, ABGELEHNT, ABGESCHLOSSEN, ZURUECKGEZOGEN
- `DringlichkeitsStufe` — Enum: NORMAL, DRINGEND, SOFORT
- `UebergabeAnfrage` — Dataclass mit `ist_offen()` + `reaktionszeit_minuten()`
- `UebergabeProtokoll` — Dataclass mit `offene_anfragen()`, `angenommene_anfragen()`, `durchschnittliche_reaktionszeit_minuten()`, `eskalations_quote_pct()`
- `get_default_uebergabe_protokolle()` — 2 demo protokolle (UP-001..UP-002)

## FastAPI Endpoints

| Method | Path | Beschreibung |
|--------|------|--------------|
| GET | `/api/v1/process/prognose/ergebnisse` | Liste aller Default-Prognosen |
| POST | `/api/v1/process/prognose/berechne` | Berechne Prognose aus Werte-Array |
| GET | `/api/v1/process/handover/protokolle` | Liste aller Übergabe-Protokolle |
| POST | `/api/v1/process/handover/pruefe-offen` | Offene Anfragen eines Protokolls prüfen |

## Tests

- **157 Tests** in `tests/test_process_kernel_wave60_forecast_handover.py`
- Enums (13), Gleitender Durchschnitt (13), Gewichteter Durchschnitt (8)
- KonfidenzNiveau Property (9), erstelle_prognose (9), Default Prognosen (24)
- Handover Enums (13), ist_offen (6), reaktionszeit_minuten (6)
- UebergabeProtokoll methods (14), Default Protokolle (22), Endpoints (16)

## Regressions
- 4488 bestehende Tests weiterhin grün
- 3 vorbestehende Fehler in wave4_ap4_ap5_ap6 unverändert (nicht Wave-60-bedingt)
