# Wave-23 Status

## Scope
Nebenkosten-Automatik (Gap 007) + Intrastat-Meldungsmodell (Gap 042)

## Zielbild

Wave 23 schliesst zwei P0/P1-Luecken:
Gap 007 (Nebenkosten/Fracht/Lagergeld automatisch im Prozess,
>=90% automatische Kostenzuordnung) und Gap 042 (Intrastat/Zoll produktiv,
0 versaeumte Meldefristen).
Die Nebenkosten-Engine erweitert die Wave-21-Settlement-Bridge
um automatisch berechnete Kostenpositionen.
Das Intrastat-Modell ist maschinenlesbar und vollstaendigkeitsgeprueft.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/nebenkosten_engine.py` | Nebenkosten-Regelwerk: Fracht (km-basiert + Pauschale), Lagergeld (tagesbasiert + monatsbasiert EUR/dt/Monat, Stichtag 1. des Monats), Verwiegekosten, Reinigung; `compute_nebenkosten()` → `NebenkostenBreakdown` | abgeschlossen |
| AP2 | `app/core/intrastat_model.py` | Intrastat-Meldungsmodell: `IntrastatMeldung`, `WarenbewegungsPosition`, CN8-Warencode, Ursprungsland, Wert/Gewicht; Vollstaendigkeitspruefung nach VO (EG) 638/2004 | abgeschlossen |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/settlement/nebenkosten-preview/{settlement_id}` — Nebenkosten-Vorschau mit Aufschluesselung | abgeschlossen |
| AP4 | `app/api/v1/endpoints/compliance.py` | `GET /api/v1/compliance/intrastat/meldungen` — Meldungsliste + `POST` Anlage + `GET /{id}/validate` | abgeschlossen |
| AP5 | `app/core/intrastat_model.py` | `validate_intrastat_meldung()` — Vollstaendigkeitspruefung aller Pflichtfelder | abgeschlossen |
| AP6 | `app/core/nebenkosten_engine.py` | `NebenkostenRule`-Registry: versionierte Regelsets pro Tenant/Saison; `get_default_nebenkosten_rules()` (4 Regeln) | abgeschlossen |

## Abnahmekriterien

- `compute_nebenkosten()` berechnet alle Kostenarten deterministisch und reproduzierbar
- `NebenkostenBreakdown` ist vollstaendig serialisierbar (schema_version=1)
- `validate_intrastat_meldung()` erkennt alle Pflichtfeld-Luecken nach EU-VO 638/2004
- Intrastat-Endpoint liefert maschinenlesbares Meldungsformat
- Keine Schichtverletzungen; `app/core/` importiert keine API-Module

## Tests

| Datei | Tests | Scope |
|-------|-------|-------|
| `tests/test_process_kernel_wave23_nebenkosten_intrastat.py` | 46 | AP1/AP6: Nebenkosten (alle Modi + Min/Max + Inaktiv + Default-Regelset); AP2/AP5: Intrastat-Meldungsmodell (Struktur, Vollstaendigkeitspruefung, EU-Laender); AP3/AP4: API-Endpoints |

**Gesamt Wave 23: 46 Tests gruen**

## Gaps geschlossen

| Gap-ID | Beschreibung | Massnahme |
|--------|-------------|-----------|
| Gap 007 | Nebenkosten/Fracht/Lagergeld automatisch im Prozess (>=90% auto) | `nebenkosten_engine.py` mit `compute_nebenkosten()`, 5 Modi inkl. monatsbasiertem Lagergeld EUR/dt/Monat |
| Gap 042 | Intrastat/Zoll produktiv, 0 versaeumte Meldefristen | `intrastat_model.py` mit `validate_intrastat_meldung()` nach VO (EG) 638/2004; Endpoints in `compliance.py` |

## Status
`abgeschlossen` — 2026-03-14
