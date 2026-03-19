# Wave-42 Status

## Scope
Domain Event Schema Registry + Process Compensation Contracts

## Zielbild

Wave 42 ergänzt den Process-Kernel um zwei Event-Sourcing-Querschnittsthemen:

1. **Domain Event Schema Registry**: Zentrales Verzeichnis für Domain-Event-Schemata mit
   Payload-Validierung (Pflichtfelder), SHA256-Versions-Hash, Kompatibilitätsprüfung
   (VOLL/ERWEITERUNG/BREAKING) und Tenant-priorisierten Schema-Lookups.
   6 Standardschemata decken kontrakt.erstellt, wiegeschein.erfasst, settlement.freigegeben,
   ap_rechnung.eingegangen und compliance.pruefung_abgeschlossen ab.

2. **Process Compensation Contracts**: Saga-Pattern für verteilte Prozesse mit
   Kompensationsketten (RUECKGAENGIG/AUSGLEICH/BENACHRICHTIGUNG/MANUELL),
   naechster_schritt (höchste Reihenfolge unter AUSSTEHEND), saga_status-Ableitung
   und Ketteninstanziierung aus Saga-Definitionen.
   3 Standardsagas: Kontrakt-Storno (4 Schritte), Settlement-Rückbuchung (3), AP-Ablehnung (3).

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/domain_event_schema_registry.py` | `EventSchemaEintrag` (versions_hash SHA256[:12], validiere_payload(), ist_aktiv), `KompatibilitaetsPruefung` (ist_kompatibel) | abgeschlossen |
| AP2 | `app/core/domain_event_schema_registry.py` | `pruefe_schema_kompatibilitaet()` (VOLL/ERWEITERUNG/BREAKING), `finde_aktives_schema()` (Tenant-Vorrang), `get_default_event_schemas()` (6) | abgeschlossen |
| AP3 | `app/core/process_compensation_contracts.py` | `KompensationsSchritt` (ist_abgeschlossen), `KompensationsKette` (ist_vollstaendig, naechster_schritt, fehlgeschlagene_schritte, saga_status) | abgeschlossen |
| AP4 | `app/core/process_compensation_contracts.py` | `SagaDefinition`, `erstelle_kompensations_kette()`, `get_default_saga_definitionen()` (3) | abgeschlossen |
| AP5 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/event-schema/schemata`, `POST /process/event-schema/validiere-payload` | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/compensation/saga-definitionen`, `POST /process/compensation/erstelle-kette` | abgeschlossen |

## Abnahmekriterien

- `pruefe_schema_kompatibilitaet()`: VOLL wenn identisch, ERWEITERUNG wenn nur neue Felder, BREAKING wenn Felder entfernt
- `finde_aktives_schema()`: Tenant-spezifisch vor global, max(version)
- `validiere_payload()`: gibt (True, []) oder (False, [fehlende...]) zurück
- `naechster_schritt`: max(reihenfolge) unter AUSSTEHEND-Schritten (Kompensation umgekehrter Reihenfolge)
- `saga_status`: ABGESCHLOSSEN nur wenn ist_vollstaendig und kein FEHLGESCHLAGEN
- `erstelle_kompensations_kette()`: kette_id = f"KK-{workflow_instanz_id}", alle Schritte mit AUSSTEHEND
- Kein Import von `app/api/` in `app/core/`

## Tests

`tests/test_process_kernel_wave42_schema_compensation.py` — 60 Tests, alle grün

```bash
pytest tests/test_process_kernel_wave42_schema_compensation.py -q --no-cov
# Ergebnis: 60 passed
```

## Status
`abgeschlossen`
Stand: 2026-03-19
