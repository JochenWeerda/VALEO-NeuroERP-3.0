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

### Erntepeak-Test (500 User, 30 Minuten) — 2026-03-20 [BESTANDEN]

| Metrik | Messwert | SLA-Ziel | Status |
|---|---|---|---|
| Requests gesamt | 487.975 | — | — |
| Error Rate | **0.00%** | < 1% | ✅ PASS |
| p95 global | **230ms** | < 2.000ms | ✅ PASS |
| Dashboard p95 max | **240ms** | < 250ms | ✅ PASS |
| Durchsatz | **268 req/s** | > 100 RPS | ✅ PASS |

**Alle SLA-Ziele erfüllt. Gap 037 geschlossen.**

### Performance-Maßnahmen (implementiert 2026-03-20)

| Maßnahme | Änderung | Wirkung |
|---|---|---|
| **Multi-Worker** | `--workers 8` + `WEB_CONCURRENCY=8` | 8× parallele Event-Loops |
| **Connection-Pool** | `pool_size=40`, `pool_pre_ping=True`, `engine.dispose()` post-fork | Kein Pool-Starvation bei 500 Usern |
| **Threadpool** | `anyio.to_thread.current_default_thread_limiter().total_tokens=200` | 200 statt 16 Sync-Route-Threads |
| **Redis Read-Model-Cache** | `@cached_read_model` auf Dashboard-Endpoints (TTL 15–60s) | Dashboard p95 unter 250ms |
| **PostgreSQL** | `max_connections=400` (statt 200) | Genug für 8×40=320 Pool-Connections |

### Historischer Vergleich

| Konfiguration | p95 global | Dashboard p95 | Error Rate | Throughput |
|---|---|---|---|---|
| Vor Optimierung (1 Worker, 500 User) | 194.000ms | 194.000ms | 0.06% | ~0 req/s |
| Nach Optimierung (8 Worker, 500 User) | **230ms** | **240ms** | **0.00%** | **268 req/s** |
| Verbesserungsfaktor | **843×** | **808×** | — | — |

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
