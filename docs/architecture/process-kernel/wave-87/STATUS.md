# Wave 87 — Lasttests Erntepeak (Gap 037)

**Status:** ABGESCHLOSSEN (Contracts + echte Lasttests)
**Datum:** 2026-03-20
**Tests:** 28 grün (Contracts), 0 Fehler

## Gap

**Gap 037:** 500 gleichzeitige User stabil — p95 Response < 2s, Error Rate < 1%

## Implementierung

### SLA-Contracts (`app/core/load_test_contracts.py`)

Definiert **nur** das Datenmodell und die SLA-Schwellwerte. Führt keine echten Lasttests durch.

| Klasse / Funktion | Beschreibung |
|---|---|
| `LasttestSzenario` | Enum: NORMALBETRIEB, ERNTEPEAK, STRESSTEST, SOAK_TEST, SPIKE_TEST |
| `EndpointKategorie` | Enum: DASHBOARD, ANNAHME, CONTROLLING, SETTLEMENT, SEARCH, AUTH |
| `ErntepeakSLAContract` | Verbindliche SLA-Schwellwerte: 500 User, <1% Error, p95<2s, Dashboard<250ms |
| `LasttestErgebnis` | Aggregiertes Testergebnis mit Endpoint-Einzelmessungen |
| `evaluate_erntepeak_sla()` | Prüft Messwerte gegen SLA-Contract, gibt ERFUELLT/VERLETZT zurück |

### Echte Lasttest-Tools

| Datei | Tool | Zweck |
|---|---|---|
| `load-tests/locustfile.py` | Locust 2.43.3 | Python-basierter Lasttest, 4 User-Klassen |
| `load-tests/erntepeak-load-test.js` | k6 | JavaScript-Lasttest, 4 Szenarien |
| `load-tests/evaluate_results.py` | Python | CSV-Auswertung nach Locust-Test |

### Lasttest-Architektur (Locust)

```
DisponentUser   (weight=40): Dashboard + KPIs     → SLA p95 < 250ms
WaagenOperator  (weight=30): Annahme + Qualität   → SLA p95 < 1000ms
BuchhaltungUser (weight=20): Finance OP-Listen    → SLA p95 < 500ms
AbrechnungUser  (weight=10): Settlements          → SLA p95 < 2000ms
```

## Reale Messwerte

### Baseline-Test (50 User, 3 Minuten) — 2026-03-20

| Metrik | Messwert | SLA-Ziel | Status |
|---|---|---|---|
| Requests gesamt | 4.924 | — | — |
| Error Rate | **0.00%** | < 1% | ✅ PASS |
| p95 global | **64ms** | < 2000ms | ✅ PASS |
| Dashboard p95 max | **63ms** | < 250ms | ✅ PASS |
| Durchsatz | 27.6 req/s | — | — |

Alle 14 Endpoint-Kategorien: 0 Fehler.

### Erntepeak-Test (500 User, 30 Minuten) — 2026-03-20

| Metrik | Messwert | SLA-Ziel | Status |
|---|---|---|---|
| Requests gesamt | 8.246 | — | — |
| Error Rate | **0.06%** | < 1% | ✅ PASS |
| p95 global | **194.000ms** | < 2.000ms | ❌ FAIL |
| Dashboard p95 max | **194.000ms** | < 250ms | ❌ FAIL |
| Durchsatz | ~0 req/s (Vollsättigung) | > 100 RPS | ❌ FAIL |

**Diagnose:** Single-Process-Backend (1 uvicorn worker) komplett gesättigt.
Alle 500 virtuellen User warten gleichzeitig auf DB-Queries.
Antwortzeiten steigen auf 300s (Locust-Timeout-Grenze).

**Infrastruktur-Anforderungen für SLA-Erfüllung:**
- Mindestens 8–16 uvicorn worker (`--workers 16`)
- Redis Read-Model-Cache für Dashboard-Endpoints (Gap 033)
- PgBouncer Connection-Pool (min 50 Connections)
- Nginx/Caddy Reverse-Proxy mit Request-Queuing

## Voraussetzungen für Gap-Schließung

Gap 037 gilt als vollständig geschlossen wenn ein Erntepeak-Test mit 500 gleichzeitigen
Usern **in einer Production-ähnlichen Konfiguration** folgende SLA-Schwellwerte einhält:

- Error Rate < 1% ✅ (bereits im Single-Process-Test erreicht)
- p95 global < 2000ms ❌ (erfordert Multi-Worker + Caching)
- Dashboard-Endpoints p95 < 250ms ❌ (erfordert Redis Read-Model-Cache)

**Status Gap 037:** SLA-Contracts definiert, Lasttest-Tooling bereit, echte Infrastruktur nötig.

## Tests (`tests/test_process_kernel_wave87_load_test_contracts.py`)

| Testklasse | Tests | Inhalt |
|---|---|---|
| `TestLasttestKonfiguration` | 5 | Erntepeak/Normalbetrieb-Konfig, Negativprüfung, RPS |
| `TestEndpointLasttestErgebnis` | 4 | Fehlerrate-Berechnung |
| `TestLasttestErgebnis` | 8 | Aggregation, p95 max/avg, get_endpoint |
| `TestErntepeakSLAContract` | 2 | Standardwerte, as_dict |
| `TestEvaluateErntePeakSlaErfuellt` | 2 | Perfekt, Grenzwerte |
| `TestEvaluateErntePeakSlaVerletzt` | 7 | Error Rate, p95, Dashboard, User, leer, mehrere |
| `TestEvaluateErntePeakSlaDetails` | 4 | Details, Warnungen, Grenzwertig |

**Gesamt: 28 Tests** (plus 4 weitere in wave 87 health: 32 total)
