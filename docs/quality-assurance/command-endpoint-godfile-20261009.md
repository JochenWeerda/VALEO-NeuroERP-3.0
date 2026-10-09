---
title: Command-Integration ohne Godfile-Rueckfall
type: reference
audience: [agent, entwickler, qa]
owner: Codex-01a0f3fc
status: abgeschlossen
last_reviewed: 2026-10-09
description: Interne Command-Auslagerung fuer Training, Bestellung und Tourenplanung mit sinkender Ratsche und erhaltenen API-Vertraegen.
---

# Command-Endpoint-Godfile-Abnahme 2026-10-09

## Originalbefund

Der isolierte committed Stand nach `6bfe6833c` verletzte drei harte Grenzen:
Training als neuer Godfile mit 1154 Zeilen, Bestellvorschlaege 1058 auf 1202
und Tourenplanung 1031 auf 1202. Eine Baseline-Erhoehung waere eine
Freigabeumgehung gewesen.

## Umsetzung

Bestehende Routen und ihre Signaturen bleiben in den bisherigen Endpunkten.
Die Implementierungen liegen in `app/api/v1/command_handlers/`. Die Router
reichen ihre kanonischen Fachdelegaten explizit weiter; bestehende Verbraucher
und Tests koennen diese weiter an derselben Stelle ersetzen. Tour-Insertion
und die Eingabeschemas sind ebenfalls ausgelagert. Die publizierte
Pydantic-Schemaidentitaet ist erhalten, ebenso die bisherigen Route-Docstrings.
Kein neuer Fachservice, Kontext, API-Pfad oder konkurrierendes Modell.

| Endpunkt | Original | Ergebnis | Grenze |
|---|---:|---:|---:|
| training.py | 1154 | 905 | unter 1000 |
| einkauf_bestellvorschlag.py | 1202 | 1036 | 1058 auf 1036 gesenkt |
| logistics_tours.py | 1202 | 1020 | 1031 auf 1020 gesenkt |

Alle anderen Baselinewerte bleiben erhalten. Neue Implementierungsdateien
bleiben deutlich unter 1000 Zeilen. Ein gleichzeitiger fremder Rueckbau an
`mask_frontend_bridges.py` ist separat: dessen Baseline wird hier nicht
veraendert oder still als eigener Nachweis uebernommen.

## Abnahme und Betrieb

Die vorhandenen Batch2-/Batch4-/MCP-Tests bestanden nach der ersten Auslagerung
mit 139 Tests. Die finale isolierte Abnahme umfasst zusaetzlich die Reporting-,
Masken-, Mandanten-, Einkaufs-, Touren- und Godfile-Vertraege. Die generierten
Mask-Map-, Screen-Action- und Handbuch-Vertraege werden weiter mit `--check`
geprueft. Die Groessenratsche ist im isolierten Lieferstand gruen.

Die OpenAPI-Spezifikation wird aus genau diesem Snapshot erzeugt und mit dem
Vertrag vor der Auslagerung verglichen; die fremde globale Arbeitsbaum-Spec
bleibt unveraendert. Die pruefende CI bleibt fail-closed.

Keine neue PostgreSQL-Testdatenbank, Docker-Ressource, Migration oder Reset.
Fuenf Fuhrpark-Aktionen ohne Mandantentrennung, FIN-CLOSE/ADR-076 und der
Zahlauf-Freigabevertrag bleiben offen; eine Modulzerlegung schliesst sie nicht.

## Finaler isolierter Nachweis

326 Tests ohne Skip in 24,62 Sekunden gruen. OpenAPI nach Auslagerung
bytegleich zur vorherigen Generierung: 3125 Pfade, gegen versionierte3113
exakt12 fehlende Pfade ergaenzt und keine alten Pfade entfernt. Event-
Quellverweise im Agent-Handbuch aus demselben Snapshot regeneriert;
Handbuch, Mask-Map und Screen-Action-Katalog aktuell.

Ein zusaetzlicher breiter Lauf mit vier alten Live-Einkaufs-API-Tests
war keine Abnahme: drei Auth-503 bei falschem Dev-Token/OIDC-Konfiguration
und ein datenabhaengiger Skip. Diese Dateien wurden nicht veraendert;
die finale326er-Auswahl prueft die betroffenen Fach- und API-Vertraege
ohne diese externe Auth-/Datenbestandsabhaengigkeit. Kein gruener
Gesamt-PG-/OIDC- oder UAT-Lauf wird behauptet.
