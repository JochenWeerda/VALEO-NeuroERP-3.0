# Wave-36 Status

## Scope
EDI/API-Hub (Gap 043) + Lieferketten-Tracking (Gap 044)

## Zielbild

Wave 36 schließt zwei P1-Lücken:
Gap 043 (EDI/API-Hub — einheitliche Partner-, Nachrichtentyp- und Acknowledgment-Contracts)
und Gap 044 (Lieferketten-Tracking — ETA-Berechnung, Abweichungsalarme, Gesamtstatus).

Die EDI-Hub-Contracts definieren Partner, Nachrichtentypen, Übertragungskanäle und
deterministische ACK-SLA-Bewertung für alle relevanten EDIFACT-Nachrichtentypen.
Das Supply-Chain-Tracking liefert transportmodusspezifische ETA-Berechnung mit
Konfidenzwert sowie regelbasierte Abweichungsalarme für Zeit und Menge.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/edi_hub_contracts.py` | `EDIStandard`, `EDIPartner`, `EDINachricht`, `evaluate_ack_status()` mit SLA pro Kanal | abgeschlossen |
| AP2 | `app/core/edi_hub_contracts.py` | `get_default_edi_partners()` (5 Partner) + `get_edi_nachrichtentyp_katalog()` (9 Typen) | abgeschlossen |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/edi/partners[?typ=][?standard=]` + `GET /process/edi/nachrichtentypen` | abgeschlossen |
| AP4 | `app/core/supply_chain_tracking.py` | `berechne_eta()`, `bewerte_zeitliche_abweichung()`, `bewerte_mengenabweichung()`, `bewerte_lieferkettenstatus()` | abgeschlossen |
| AP5 | `app/core/supply_chain_tracking.py` | Schwellenwerte: Zeit <4h→INFO, 4–24h→WARNUNG, ≥24h→KRITISCH; Menge <2%→INFO, 2–5%→WARNUNG, ≥5%→KRITISCH | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `POST /process/supply-chain/eta` + `POST /process/supply-chain/status` | abgeschlossen |

## Abnahmekriterien

- `evaluate_ack_status()` erkennt quittungspflichtige Nachrichtentypen (ORDERS, INVOIC, DESADV, REMADV) korrekt
- SLA-Verletzung wenn `wartezeit_sekunden > _ACK_SLA_SEKUNDEN[kanal]` und keine Quittung
- `berechne_eta()` verwendet transportmodusabhängige km/h-Werte; raises ValueError bei distanz_km <= 0 oder NaN/Inf
- NaN/Inf-Schutz in ETA-Berechnung
- Abweichungsalarme sind deterministisch und eskalieren automatisch ab KRITISCH-Schwelle
- `bewerte_lieferkettenstatus()` → ABGESCHLOSSEN nur wenn Phase=AUSLIEFERUNG und kein aktiver KRITISCH-Alarm
- Kein Import von `app/api/` in `app/core/`

## Tests

`tests/test_process_kernel_wave36_edi_supplychain.py` — 60 Tests, alle grün

```bash
pytest tests/test_process_kernel_wave36_edi_supplychain.py -q --no-cov
# Ergebnis: 60 passed
```

## Status
`abgeschlossen`
Stand: 2026-03-19
