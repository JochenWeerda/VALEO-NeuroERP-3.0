# Wave-39 Status

## Scope
Command-Surfacing-Contracts (Rollen-/Dichte-bewusste Command-Sichtbarkeit) +
Prozess-Benachrichtigungs-Contracts (Workflow-Notification, Alert-Subscriptions, Eskalation)

## Zielbild

Wave 39 adressiert die in STATUS.md offenen Ausbaustufen:
- Rollen- und dichtebezogene Surfacing-Contracts aus produktiven Backend-Manifesten speisen
- Berechtigungs-Hinweise direkt im Command-Surfacing
- Prozess-Benachrichtigungsframework mit Kanal-Routing und Eskalation

Die Command-Surfacing-Contracts verbinden den Command-Katalog (Wave 14),
das Role-Density-System (Wave 27) und den Action-Dispatch (Wave 25) zu einem
einheitlichen Sichtbarkeits-Manifest: Welche Commands werden für welche Rolle
in welcher Dichte auf welchem Kanal angezeigt?

Die Prozess-Benachrichtigungs-Contracts liefern Auslöser-basiertes Routing
(8 Abonnements, 5 Eskalationsregeln), Prioritäts-Mapping und vollständige
Nachrichten-Generierung für IN_APP, EMAIL, WEBHOOK, TEAMS und weitere Kanäle.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/command_surfacing_contracts.py` | `SurfacingRegel`, `SurfacingAnfrage`, `CommandSurfacingManifest`, `berechne_surfacing()` mit Rollen-/Dichte-/Kontext-/Domain-Filter; KRITISCH übersteuert Dichte | abgeschlossen |
| AP2 | `app/core/command_surfacing_contracts.py` | `get_default_surfacing_regeln()` — 12 Regeln für Agrar, Finance, Compliance, Global (TOOLBAR/PALETTE/AGENT/SHORTCUT) | abgeschlossen |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/surfacing/regeln[?domain=][?kontext=]` + `POST /process/surfacing/manifest` | abgeschlossen |
| AP4 | `app/core/process_notification_contracts.py` | `NotifikationsAbonnement`, `EskalationsRegel`, `route_benachrichtigung()`, `erstelle_benachrichtigung()`, `berechne_prioritaet()` | abgeschlossen |
| AP5 | `app/core/process_notification_contracts.py` | `get_default_abonnements()` (8) + `get_default_eskalationsregeln()` (5) mit automatischer Eskalation bei SLA/Fehler/Freigabe-Verzug | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/notifications/abonnements[?rolle=][?ausloeser=]` + `POST /process/notifications/route` | abgeschlossen |

## Abnahmekriterien

- `berechne_surfacing()` → KRITISCH-Commands immer sichtbar (Dichte-Override)
- Rollen-Sperre korrekt wenn Rolle nicht in `erlaubte_rollen` (nicht leer)
- `erlaubte_rollen == []` → alle Rollen erlaubt
- Domain-Filter: `domain==""` in Regel matcht immer; sonst exakter Match
- `route_benachrichtigung()` → Prioritäts-Filter: ABO mit min_prioritaet=KRITISCH nur für KRITISCH-Trigger
- Inaktive Abonnements (aktiv=False) werden ignoriert
- Eskalationsregel-Lookup: erster passender Auslöser gewinnt
- Kein Import von `app/api/` in `app/core/`

## Tests

`tests/test_process_kernel_wave39_surfacing_notifications.py` — 60 Tests, alle grün

```bash
pytest tests/test_process_kernel_wave39_surfacing_notifications.py -q --no-cov
# Ergebnis: 60 passed
```

## Status
`abgeschlossen`
Stand: 2026-03-19
