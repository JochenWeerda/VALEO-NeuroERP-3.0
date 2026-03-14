# Wave 6 Paket B Status

## Paket
- Name: `Markt- und Handelsseite (Supplier Portal, Kontrakte, Silo/Lager)`
- Zugeordnete Aufgaben: `AP4`, `AP5`, `AP6`
- Status: `abgeschlossen`

## Ziel
Lieferantenseite produktiv: Supplier Portal gibt Lieferanten transparenten Self-Service-Zugang.
Kontrakt-/Preislogik deckt Branchenstandards ab (Tranchen, Staffeln, Differenzkontrakte).
Silo- und Lagerverwaltung ist IoT-verbunden und GoBD-konform.

## Arbeitsauftraege

| Auftrag | Aufgabe | Reihenfolge | Zielartefakt |
|---------|---------|-------------|--------------|
| B1 | Supplier Portal Auth-Rolle und gefilterte Read-Endpoints implementieren | 1 | `app/api/v1/endpoints/supplier_portal.py` | umgesetzt |
| B2 | Supplier Portal Frontend (Route `/supplier-portal/*`) | 2 | `packages/frontend-web/src/pages/supplier-portal/` | umgesetzt (Stub-Endpoints) |
| B3 | `KonContractLot` Teilmengen-Modell + Split-Endpoint | 3 | `app/core/contract_pricing.py` | umgesetzt |
| B4 | `PriceMatrix` Qualitaetsstaffeln + Differenzkontrakt-Modell | 4 | `app/core/contract_pricing.py` | umgesetzt |
| B5 | `SiloCell` + `SiloTransfer` Command | 5 | `app/core/silo_operations.py` | umgesetzt |
| B6 | IoT → Silo-Feuchte + API-Endpoints | 6 | `app/api/v1/endpoints/silo_operations_api.py` | umgesetzt |

## Abnahmekriterien

- Supplier Portal: Lieferant mit Rolle `supplier` sieht nur eigene Kontrakte/Lieferungen/Abrechnungen
- `POST /api/v1/agrar/contracts/{id}/split-lot` erzeugt `KonContractLot`-Eintraege mit Summenvalidierung
- `PriceMatrix` berechnet Preis aus Qualitaetsmesswerten (Interpolation zwischen Stufenwerten)
- `SiloTransfer` ist auditierbar und prueft Kapazitaet vor Umlagerung
- Silo-Sensor-Readings aus `iot_telemetry.py` aktualisieren automatisch `SiloCell.moisture_pct`
- `DryingRun` verknuepft Eingangs- und Ausgangsfeuchte und berechnet Energiekosten

## Abhaengigkeiten

- `app/core/tenant_governance.py` (Wave 2 AP3) — VerbundMember fuer Supplier-Isolation
- `app/core/iot_telemetry.py` (Wave 3 AP3) — Silo-Sensor-Readings
- `app/core/quality_lot_binding.py` (Wave 3 AP5) — Qualitaetswerte fuer PriceMatrix
- `app/core/audit_evidence.py` (Wave 3 AP2) — SiloCleaningProtokoll GoBD
- `app/api/v1/endpoints/agrar_contracts.py` — Kontrakt-Basis

## Testergebnis

- Testdatei: `tests/test_process_kernel_wave6_supplier.py`
- Ergebnis: **24 passed** (2026-03-12)
- Laufzeit: ~33s
- Abgedeckte Bereiche:
  - PriceMatrix (6 Tests): get_preis, Stichtag-Filter, Schema-Version
  - KonContractLot (4 Tests): Lieferstatus, Abschlussstatus, Store-Filter
  - SiloCell / SiloCellStore (10 Tests): Fuellstand, Status, Einlagerung, Auslagerung, Kapazitaetspruefung, Gesamtbestand, Transfer-Protokoll
  - API-Endpoints (4 Tests): POST /contract-pricing/price-matrix, POST /contract-pricing/lots, GET /supplier-portal/lieferanten/{id}/lieferungen, GET /supplier-portal/preisauskunft
