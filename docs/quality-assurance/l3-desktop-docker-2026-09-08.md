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

## Aktueller Stand nach Claudes Uebergabe

Die unten dokumentierten fuenf HTTP-500 und die Readiness-503 sind inzwischen
geschlossen. Claudes Uebergabe im Workboard belegt den Runtime-Sweep mit
Sidecars sowie 979 Ziele unter nachgestellten CI-Bedingungen ohne 5xx oder
unerwartete 503. Laut uebergebenem CI-Nachweis sind sieben von neun Workflows
gruen; E2E Smoke und Security Scan bleiben offen. Das ist ein uebernommener
CI-Nachweis, kein neuer Vollsuite-Lauf dieses Zwischenstands.

Codex-Nachzug: Die lokal bereits angewandte Reparaturmigration wird mit ihrer
unveraenderten Revision `desktop_runtime_repair_20260909` in Git aufgenommen.
Zusaetzlich repariert sie fehlende `domain_shared.admin_report_permissions`
mit der unveraenderten Tabellendefinition aus der historischen Migration.
Der idempotente Zusatz ist auf der vorhandenen DB ein No-op; dort hat Claude
die Tabelle bereits angelegt. Es wird keine zweite Alembic-Kette eingefuehrt.

| Nachweis 2026-09-10 | Ergebnis |
|---|---|
| Vier Migrations-Vertragstests | bestanden |
| Vollstaendige Reparatur zweimal in zurueckgerollter PostgreSQL-Transaktion | bestanden; vorhandene Tabellenidentitaeten erhalten |
| Frische isolierte DB: gesamte Alembic-Kette und ORM-Initialisierung | bestanden; ein erwarteter Head, Reportberechtigungen vorhanden |
| Testdatenbank nach Test | ausschliesslich neu angelegte Testdatenbank entfernt |
| Code-Inventare und Architektur-Index | aktuell, 927/927 Routen |

Die veralteten generierten Arbeitskopien wurden nach Diff-Pruefung auf HEAD
gebracht; ihre vorherigen Bytes liegen unter
`artifacts/pre-inventory-reconcile-20260910/`. Das Migrationsinventar wird
danach aus dem aktuellen Code inklusive der Reparatur neu erzeugt.

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

### CRM-Folgewelle

Beide Opportunities-HTTP-500 stammen aus demselben CRM-Sales-Dienst.
`crm_sales_alembic_version` hatte keine Revision: Migration 002 verwendet
eine in PostgreSQL unzulaessige Fensterfunktion direkt im UPDATE. Danach
blockierte ein Text-Fremdschluessel auf eine UUID-ID die gesamte Kette.
Die bisher nicht ausfuehrbare Migration wurde ohne Aenderung ihrer
Revision oder ihres Zielmodells repariert: Nummerierung per CTE, Historien-
Fremdschluessel als UUID entsprechend dem bestehenden ORM-Modell.

`alembic upgrade head` im lokalen CRM-Sales-Container: 001 und 002 bestanden.
`python -m unittest discover -s tests -p test_migration_numbering.py -v`:
ein PostgreSQL-Test bestanden (temporaere Tabelle, stabile Reihenfolge,
Erhalt bestehender Referenz und Wiederholung). Beide Backend-Aliasse
`/api/crm-sales/opportunities/` und `/api/v1/crm/opportunities/`: HTTP 200.
Die Schemaanlage verwendet die vorhandenen Migrationen; kein CRM-Container
wurde neu gebaut oder neu gestartet.

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
