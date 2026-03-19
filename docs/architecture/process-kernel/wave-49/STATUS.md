# Wave-49 Status

## Scope
Process Notification Contracts (Wave49) + Workflow Lock Contracts

## Zielbild

Wave 49 ergänzt den Process-Kernel um Benachrichtigungsvorlagen und Konkurrenzkontrolle:

1. **Process Notification Contracts (Wave49)**: Benachrichtigungsvorlagen mit Template-Rendering
   (`{{platzhalter}}`-Substitution), 5 Kanälen (EMAIL/SMS/PUSH/IN_APP/WEBHOOK), 4 Prioritäten
   und Zustellverfolgung mit `ZustellStatistik.erfolgsrate_pct`.
   `NotifikationsVorlage.render(kontext)`: ersetzt bekannte Platzhalter, unbekannte bleiben erhalten.
   `erstelle_zustellung()`: rendert Vorlage, setzt status=AUSSTEHEND.
   `berechne_zustellstatistik()`: filtert nach Kanal, zählt alle Status-Buckets.
   5 Standardvorlagen: NV-001 (EMAIL/HOCH Kontrakt-Freigabe), NV-002 (PUSH/HOCH Timeout-Warnung),
   NV-003 (SMS/KRITISCH Settlement-Eskalation), NV-004 (IN_APP/NORMAL Batch-Abschluss),
   NV-005 (WEBHOOK/KRITISCH Compliance-Alarm).
   Hinweis: Modul heißt `process_notification_contracts_wave49.py` — Wave-39-Vorgänger belegt
   den Basisnamen.

2. **Workflow Lock Contracts**: Optimistisches Sperren und Konkurrenzkontrolle mit 3 Lock-Typen
   (LESEN/SCHREIBEN/OPTIMISTISCH) und automatischem TTL-Ablauf.
   `WorkflowLock.pruefe_konflikt()`: SCHREIB_SCHREIB / LESE_SCHREIB / VERSION_KONFLIKT.
   `akquiriere_lock()`: LESEN blockiert LESEN nicht; abgelaufene und freigegebene Locks ignoriert;
   gleicher Inhaber erzeugt keinen Konflikt.
   5 Standardlocks: LK-001 (SCHREIBEN AKTIV), LK-002+LK-003 (LESEN AKTIV auf gleicher Ressource),
   LK-004 (OPTIMISTISCH FREIGEGEBEN), LK-005 (SCHREIBEN ABGELAUFEN).

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/process_notification_contracts_wave49.py` | `NotifikationsVorlage` (render), `NotifikationsZustellung` (ist_zugestellt, ist_fehlgeschlagen), `ZustellStatistik` (erfolgsrate_pct) | abgeschlossen |
| AP2 | `app/core/process_notification_contracts_wave49.py` | `erstelle_zustellung()`, `berechne_zustellstatistik()`, `get_default_notifikations_vorlagen()` (5) | abgeschlossen |
| AP3 | `app/core/workflow_lock_contracts.py` | `WorkflowLock` (ist_aktiv, ist_abgelaufen, pruefe_konflikt), `LockAkquisitionsErgebnis` | abgeschlossen |
| AP4 | `app/core/workflow_lock_contracts.py` | `akquiriere_lock()` (LESEN-Ausnahme, TTL-Check, Inhaber-Check), `get_default_locks()` (5) | abgeschlossen |
| AP5 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/notifications/vorlagen`, `POST /process/notifications/erstelle-zustellung` | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/locks/aktive`, `POST /process/locks/akquiriere` | abgeschlossen |

## Abnahmekriterien

- `NotifikationsVorlage.render()`: Unbekannte `{{x}}` bleiben unverändert
- `erstelle_zustellung()`: status immer AUSSTEHEND, kanal/prioritaet aus Vorlage
- `WorkflowLock.ablauf_am = erstellt_am + timedelta(seconds=ttl_sekunden)` (via `__post_init__`)
- `akquiriere_lock()`: LESEN vs LESEN → erfolg=True
- `akquiriere_lock()`: abgelaufener Lock wird ignoriert → kein Konflikt
- Kein Import von `app/api/` in `app/core/`

## Tests

`tests/test_process_kernel_wave49_notification_lock.py` — 115 Tests, alle grün

```bash
pytest tests/test_process_kernel_wave49_notification_lock.py -q --no-cov
# Ergebnis: 115 passed
```

## Status
`abgeschlossen`
Stand: 2026-03-19
