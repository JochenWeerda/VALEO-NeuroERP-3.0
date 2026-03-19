# Wave-38 Status

## Scope
Nachhaltigkeit/CO2-Reporting für Agrarkonzerne (Gap 046) + Branchenbenchmarking-Cockpit (Gap 047)

## Zielbild

Wave 38 schließt die letzten beiden offenen P2-Gaps des Top-50-Backlogs:
Gap 046 (Nachhaltigkeit/CO2-Reporting — ESG-Berichte in < 1 Tag erzeugbar)
und Gap 047 (Branchenbenchmarking-Cockpit — monatlicher Benchmarkreport automatisch).

Die Sustainability-Reporting-Contracts definieren Scope-1/2/3-Emissionen,
typbezogene Emissionsfaktoren (Transport, Energie, Landwirtschaft) und gewichtete
ESG-Scores mit SEHR_GUT/GUT/AUSREICHEND/MANGELHAFT-Bewertung.
Das Benchmark-Cockpit liefert Perzentil-Einstufung (TOP_10/TOP_25/MITTELFELD/UNTERES_VIERTEL),
Trend-Berechnung aus Zeitreihen und monatliche Reports je Genossenschaft.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/sustainability_reporting.py` | `EmissionsScope`, `EmissionsKategorie`, `berechne_transport_co2e()`, `berechne_energie_co2e()` mit typbezogenen Faktoren (LKW=0.062, BAHN=0.018, STROM=0.380 kg CO2e/Einheit) | abgeschlossen |
| AP2 | `app/core/sustainability_reporting.py` | `CO2Bilanz`, `ESGKennzahl`, `ESGBericht` (gewichteter Score, ESGBewertung), `erstelle_beispiel_co2_bilanz()`, `erstelle_beispiel_esg_bericht()` | abgeschlossen |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/sustainability/esg-bericht` + `POST /process/sustainability/co2-berechnen` | abgeschlossen |
| AP4 | `app/core/benchmark_cockpit.py` | `BenchmarkKennzahl` (Perzentil-Einstufung, hoeher_ist_besser-Logik), `berechne_trend()` (5 Stufen), `berechne_branchenperzentile()` | abgeschlossen |
| AP5 | `app/core/benchmark_cockpit.py` | `BenchmarkReport` (gesamtbewertung_score, top10/verbesserungspotenzial), `get_example_benchmark_report()` (6 Kennzahlen, 2 Trendreihen) | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/benchmark/report[?kategorie=]` + `POST /process/benchmark/perzentile` | abgeschlossen |

## Abnahmekriterien

- `berechne_transport_co2e()` raises ValueError bei menge_t/distanz_km <= 0 oder NaN/Inf
- `berechne_energie_co2e()` raises ValueError bei falscher Kategorie oder kwh <= 0
- `ESGKennzahl.zielerreichung_pct` = min(100, ziel_wert/ist_wert * 100) — kein Überschreiten von 100
- `ESGBericht.bewertung`: SEHR_GUT >= 80, GUT >= 60, AUSREICHEND >= 40, MANGELHAFT < 40
- `BenchmarkKennzahl.perzentil_stufe` korrekt für hoeher_ist_besser=True und =False
- `berechne_trend()` mit < 2 Werten → STABIL (kein Fehler)
- Kein Import von `app/api/` in `app/core/`

## Tests

`tests/test_process_kernel_wave38_sustainability_benchmark.py` — 60 Tests, alle grün

```bash
pytest tests/test_process_kernel_wave38_sustainability_benchmark.py -q --no-cov
# Ergebnis: 60 passed
```

## Status
`abgeschlossen`
Stand: 2026-03-19
