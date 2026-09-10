---
title: L3 Desktop und Docker Wiederaufnahme
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-10
version: 1.0.0
description: Aktuelle Verifikation und offene Abnahme des Desktop-Rebuild-Slices.
---

# L3 Desktop und Docker

## Wiederaufnahme 2026-09-10

Fortsetzung des bestehenden Codex-Slices `L3-DESKTOP-REBUILD-20260908`.
Annahme: Der Auftrag "weiter" setzt dessen lokale Fehlerbehebung und Abnahme
fort. Der Arbeitsbaum enthaelt weitere fremde und bereits vorbereitete
Aenderungen; diese werden nicht pauschal committet oder zurueckgesetzt.

## Verifikation

| Pruefung | Ergebnis |
|---|---|
| API-Sweep-, Lieferschein-UUID-, Kennzahlen- und Input-Flow-Regressionen | 13 passed |
| Frontend Mask-Builder Runtime, acht Testdateien | 66 passed |
| Meridian-Visual-Audit gegen Docker-Frontend | 12 passed, drei Viewports |
| Docker-Zustand vor Neubau | Backend und Frontend healthy |
| Einkauf-Abgleich und L3-Runtime-/Gewohnheitsvertraege | 35 passed |
| TypeScript | bestanden |
| Masken-Endpoint-Inventar / Agent-Handbuch / Slice-Readiness | bestanden |
| Docker-Neubau Backend und Frontend | bestanden, beide Container neu gestartet |
| Lesender API-Sweep im neuen Backend-Container | 980 Routen: 907 2xx, 49 4xx, 18 erlaubte 503, 5 HTTP 500, readyz 503, 0 Transportfehler |

Der Visual-Audit verwendet kontrollierte ScreenDefinition-, Entity- und
Tabellendaten. Er belegt Layout und Rendering, keine reale Fachtransaktion.
Windows-Aufrufe des API-Sweeps liefen beim OpenAPI-Abruf in Timeouts; direkt
im Container antwortete derselbe Pfad mit HTTP 200 in 1,11 Sekunden.
Die Ursache des Windows-Zugriffs ist noch nicht abschliessend geklaert.
Im alten Container fehlt `config/runtime_sweep_allowlist.yaml`; der Sweep
erfasste dadurch 981 Routen ohne Ausnahmen. Waehrend des Laufs beendeten sich
Serverprozesse; die alte Startkonfiguration enthaelt `--limit-max-requests 250`.
Der Lauf wurde beendet und wird nach dem Neubau erneut ausgefuehrt.

## Offene Abnahme

Offen: HTTP 500 bei `/api/crm-sales/opportunities/`,
`/api/v1/crm/opportunities/`, `/api/mcp/policy/backup`,
`/api/v1/admin/report-permissions` und `/api/v1/journal-entries/`;
`/readyz` liefert unerwartet 503. Ursachen noch in Pruefung.
Die vorbereitete additive Datenbank-Reparaturmigration
ist durch die oben genannten Tests nicht abgenommen. Fachliche Pilotfreigaben
bleiben extern. Der Slice bleibt bis zur vollstaendigen Abnahme in Arbeit.

## Zwischenstand in Git

`ccef6c96e` wurde nach `origin/main` gepusht. Der Visual-Audit nach dem
Neubau bestand ebenfalls mit 12/12. Die Readiness-Ursache ist korrigiert:
Alembic fuehrt `version_num`, nicht `version`. Zwei Regressionen pruefen
eine echte Versionstabelle und den unmigrierten Zustand. Direkter Aufruf
gegen die lokale PostgreSQL-DB ist erfolgreich; die laufenden HTTP-Worker
muessen die Aenderung noch durch einen Neustart laden.

Die Journal-Source-Regressionsarbeit ist auf User-Auftrag als offener
Claude-Code-Slice `L3-JOURNAL-SOURCE-20260910` ausgegliedert. Claim und
Liefermeldung erfolgen ueber das Workboard; bisher keine Uebernahme bestaetigt.

User-Auftrag vom 2026-09-10: gepruefte Zwischenstaende nach jeder Welle
committen und nach GitHub pushen; Workboard fortlaufend nachziehen.
Der erste Commit umfasst API-/ActionRuntime-Korrekturen, ihre Tests und
Docker-Konfiguration. Die ungetestete Reparaturmigration, generierte
Inventare und Alt-Slice-Nachzuege bleiben getrennt. Der Doku-Drift-Bericht
meldet null Luecken; der Inventar-Generator meldet im geteilten Arbeitsbaum
noch Abweichungen bei Service- und Migrationsinventar.
