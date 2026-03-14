# Agrar-P0-Gap-Report

Generiert durch `scripts/process_kernel/build_agrar_p0_gap_report.py`

## Schlagkartei

| Pruefpunkt | Status |
|-----------|--------|
| FeldbuchSchlag.flik_id | ❌ FEHLT |
| FeldbuchSchlag.geometry_wkt | ❌ FEHLT |
| Feldblockfinder-Endpoint /find-by-flik | ❌ FEHLT |
| GeoJSON-Export-Endpoint | ❌ FEHLT |

## Duengung

| Pruefpunkt | Status |
|-----------|--------|
| NaehrstoffInput-Modell | ❌ FEHLT |
| DuengeBilanzPeriode.compliance_check() | ❌ FEHLT |
| N-Saldo-Grenzwert 50 kg/ha | ❌ FEHLT |
| Bilanz-Endpoint /api/v1/agrar/duengung/bilanz | ❌ FEHLT |

## PSM

| Pruefpunkt | Status |
|-----------|--------|
| PsmAnwendungProtokoll.sachkunde_nr | ❌ FEHLT |
| PsmAnwendungProtokoll.wasser_schutzgebiet | ❌ FEHLT |
| PSM-Finalisierung /finalize → GoBD-Beleg | ❌ FEHLT |
| PSM-Export CSV/PDF | ❌ FEHLT |

## Zusammenfassung

- Gesamt: 12 Pruefpunkte
- Erfuellt: 0
- Offen: 12
- P0-Abdeckung: 0%

## Offene Wave-6-AP-Aufgaben

- [Schlagkartei] FeldbuchSchlag.flik_id
- [Schlagkartei] FeldbuchSchlag.geometry_wkt
- [Schlagkartei] Feldblockfinder-Endpoint /find-by-flik
- [Schlagkartei] GeoJSON-Export-Endpoint
- [Duengung] NaehrstoffInput-Modell
- [Duengung] DuengeBilanzPeriode.compliance_check()
- [Duengung] N-Saldo-Grenzwert 50 kg/ha
- [Duengung] Bilanz-Endpoint /api/v1/agrar/duengung/bilanz
- [PSM] PsmAnwendungProtokoll.sachkunde_nr
- [PSM] PsmAnwendungProtokoll.wasser_schutzgebiet
- [PSM] PSM-Finalisierung /finalize → GoBD-Beleg
- [PSM] PSM-Export CSV/PDF