# Wave 87 — Lasttest-SLA-Contracts + Testharness Erntepeak (Gap 037)

**Status:** ABGESCHLOSSEN (Contracts + Testharness)
**Datum:** 2026-03-20
**Tests:** 35 (Unit-Tests der Contracts)

## Wichtiger Hinweis

Diese Wave liefert:
1. **SLA-Contracts** (`app/core/load_test_contracts.py`) — Datenmodell und Schwellwerte
2. **Echtes k6-Script** (`load-tests/erntepeak-load-test.js`) — generiert realen HTTP-Traffic
3. **Echtes Locust-Script** (`load-tests/locustfile.py`) — Python-basierte Lastgenerierung
4. **Auswertungs-Helper** (`load-tests/evaluate_results.py`) — wertet CSV gegen SLA aus

Die Unit-Tests (35 Stk.) testen die Contract-Logik mit Fixture-Daten.
**Der Gap 037 gilt als vollstaendig geschlossen sobald ein echter Lasttest
mit 500 gleichzeitigen Usern alle SLA-Schwellwerte einhält.**

## Gap

**Gap 037**: Lasttests Erntepeak — 500 gleichzeitige User stabil
**KPI**: Error Rate < 1%, p95 global < 2s, Dashboard p95 < 250ms

## SLA-Schwellwerte (ErntepeakSLAContract)

| Kriterium | Ziel | Endpunkte |
|---|---|---|
| Error Rate | < 1% | alle |
| p95 global | < 2000ms | alle |
| p95 Dashboard | < 250ms | /controlling/dashboards, /kpis, /timeseries |
| p95 Annahme | < 1000ms | /agrar/harvest-acceptance |
| Gleichzeitige User | >= 500 | alle |

## Echte Testdurchführung

```bash
# Stack starten
docker compose up -d

# k6 Erntepeak (500 User, 20 Min Volllast)
k6 run load-tests/erntepeak-load-test.js

# Locust headless (500 User, 30 Min)
locust -f load-tests/locustfile.py \
    --host http://localhost:8000 \
    --users 500 --spawn-rate 8 \
    --run-time 30m --headless \
    --csv load-tests/results/erntepeak

# Ergebnis auswerten
python load-tests/evaluate_results.py load-tests/results/erntepeak_stats.csv
```

## Simulierte User-Rollen (Locust)

| Rolle | Anteil | Endpoints | SLA |
|---|---|---|---|
| Disponent/GF (Dashboard) | 40% | /controlling/dashboards, /kpis | p95 < 250ms |
| Waagen-Operator (Annahme) | 30% | /agrar/harvest-acceptance, /contracts | p95 < 1s |
| Buchhalter (Controlling) | 20% | /finance/open-items, /payment-runs | p95 < 500ms |
| Abrechnungssachb. (Settlement) | 10% | /agrar/settlements, /self-billing | p95 < 2s |

## Gelieferte Dateien

| Datei | Typ | Beschreibung |
|---|---|---|
| `app/core/load_test_contracts.py` | Python | SLA-Datenmodell + Auswertungslogik |
| `load-tests/erntepeak-load-test.js` | k6 | Echter Lasttest (500 User) |
| `load-tests/locustfile.py` | Locust | Echter Lasttest (Python) |
| `load-tests/evaluate_results.py` | Python | CSV-Auswertung gegen SLA |
