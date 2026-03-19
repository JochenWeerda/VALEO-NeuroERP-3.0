# Wave-41 Status

## Scope
Process Capacity Contracts + Event Replay Contracts

## Zielbild

Wave 41 ergänzt den Process-Kernel um zwei Querschnittsthemen:

1. **Process Capacity Contracts**: Kapazitätsmodell für Ressourceneinheiten (ROLLE, WORKSTATION, SYSTEM, QUEUE)
   mit Auslastungsgraden (UNTERAUSGELASTET/NORMAL/AUSGELASTET/UEBERLASTET), Engpass-Erkennung und
   Workflow-Kapazitätsprüfung vor Workflow-Start. Standarddatensatz mit 6 Einheiten (KE-001 bis KE-006)
   deckt Agrar, Finance, Compliance und DMS ab.

2. **Event Replay Contracts**: Steuerung von Event-Replay-Aufträgen (4 Modi: VOLLSTAENDIG, TEILWEISE,
   SNAPSHOT_BASIERT, DELTA), Cursor-Tracking für Verbraucher, Snapshot-Management und
   Konsistenzprüfung (Lücken + Duplikate) für Event-Streams.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/process_capacity_contracts.py` | `KapazitaetsEinheit` (auslastung_pct, auslastungs_status, ist_engpass), `WorkloadPrognose` (deckungsgrad_pct), `KapazitaetsPruefungErgebnis` | abgeschlossen |
| AP2 | `app/core/process_capacity_contracts.py` | `berechne_engpass_stufe()`, `pruefe_workflow_kapazitaet()` (Domain-Filter, Engpass-Empfehlungen), `get_default_kapazitaets_einheiten()` (6 Einheiten) | abgeschlossen |
| AP3 | `app/core/event_replay_contracts.py` | `EventReplayAuftrag` (ist_abgeschlossen, dauer_sekunden, durchsatz_pro_sekunde), `ReplayCursor`, `EventSnapshot` (alter_stunden) | abgeschlossen |
| AP4 | `app/core/event_replay_contracts.py` | `ReplayKonsistenzPruefung` (hat_probleme), `pruefe_replay_konsistenz()` (Lücken+Duplikate), `erstelle_replay_auftrag()`, `get_default_replay_auftraege()` (3) | abgeschlossen |
| AP5 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/capacity/einheiten`, `POST /process/capacity/pruefe-workflow` | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/event-replay/auftraege`, `POST /process/event-replay/konsistenz-pruefen` | abgeschlossen |

## Abnahmekriterien

- `auslastungs_status`: UEBERLASTET >90%, AUSGELASTET >75%, NORMAL >=30%, UNTERAUSGELASTET sonst
- `ist_engpass`: True ab 90% Auslastung
- `pruefe_workflow_kapazitaet()`: Domain-Filter (domain=="" matcht immer); 1 Engpass → 2 Empfehlungen mit einheit_id; N Engpässe → 2 Empfehlungen mit Zähler
- `pruefe_replay_konsistenz()`: leere Liste → konsistent; Lücken korrekt erkannt; Duplikate korrekt erkannt
- `dauer_sekunden`: None wenn gestartet_am oder abgeschlossen_am fehlt
- Kein Import von `app/api/` in `app/core/`

## Tests

`tests/test_process_kernel_wave41_capacity_replay.py` — 82 Tests, alle grün

```bash
pytest tests/test_process_kernel_wave41_capacity_replay.py -q --no-cov
# Ergebnis: 82 passed
```

## Status
`abgeschlossen`
Stand: 2026-03-19
