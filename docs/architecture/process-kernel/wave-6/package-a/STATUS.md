# Wave 6 Paket A Status

## Paket
- Name: `Agrar-P0 Closure (Schlagkartei, Duengung, PSM)`
- Zugeordnete Aufgaben: `AP1`, `AP2`, `AP3`, `AP4`
- Status: `abgeschlossen`

## Ziel
Die gesetzlich geforderten landwirtschaftlichen Dokumentationspflichten lueckenlos erfuellen:
GIS-faehige Schlagkartei, DueV-konforme Duengebilanz, vollstaendiges PSM-Spritztagebuch.

## Arbeitsauftraege

| Auftrag | Aufgabe | Status | Zielartefakt |
|---------|---------|--------|--------------|
| AP1 | `FeldbuchSchlag` um `flik_id`, `geometry_wkt`, `nuts3_region` erweitern | umgesetzt | `app/infrastructure/models/agrar_models.py` |
| AP2 | `DuengeBilanz` und DueV-Compliance-Check implementieren | umgesetzt | `app/core/duenge_bilanz.py` |
| AP3 | `PsmAnwendungProtokoll` mit PSM-Pflichtfeldern (Sachkunde, WSG, Wartezeit) + GoBD-Vollstaendigkeitspruefung | umgesetzt | `app/core/psm_protokoll.py` |
| AP4 | API-Endpoints (duenge-bilanz, psm-protokoll, schlag/flik) + Router-Registrierung | umgesetzt | `app/api/v1/endpoints/agrar_p0.py` |

## Testergebnis

- Testdatei: `tests/test_process_kernel_wave6_agrar_p0.py`
- Ergebnis: **20/20 Tests gruen** (2026-03-11)
- DueV-Bilanz Tests: 11 bestanden
- PSM-Protokoll Tests: 5 bestanden
- API-Tests: 4 bestanden

## Abnahmekriterien (erfuellt)

- `FeldbuchSchlag` hat `flik_id`, `geometry_wkt`, `nuts3_region` (Wave 6 AP1)
- `DuengeBilanz.berechne()` liefert strukturierten Bilanz-Report mit Grenzwert-Pruefung (N > 20 kg/ha, P > 10 kg/ha)
- `PsmAnwendungProtokoll.ist_gobd_vollstaendig()` prueft alle GoBD-Pflichtfelder nach § 11 PflSchG
- API-Endpoints unter `/api/v1/agrar/p0/` erreichbar und authentifiziert
- Alle Modelle verwenden `schema_version: int = 1`
- Keine DB-Abhaengigkeiten in Core-Modellen — reines Pydantic

## Abhaengigkeiten

- `app/infrastructure/models/agrar_models.py` — FeldbuchSchlag (erweitert)
- `app/core/duenge_bilanz.py` (neu)
- `app/core/psm_protokoll.py` (neu)
- `app/api/v1/endpoints/agrar_p0.py` (neu)
