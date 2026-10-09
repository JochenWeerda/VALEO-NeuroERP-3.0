---
title: Reporting-Fachcommands atomar und fachlich konsistent
type: reference
audience: [agent, entwickler, qa]
owner: Codex-01a0f3fc
status: abgeschlossen
last_reviewed: 2026-10-09
description: Bonusberechnung und signierter Query-Import mit gemeinsamer Transaktionsgrenze und identischer Vorschauvalidierung.
---

# Reporting-Fachcommands — Abnahme 2026-10-09

## Befunde und Korrektur

Die abgeschlossenen Cursor-Batch2-Commands riefen Fachservices auf, die vor
Command-Audit/Outbox beziehungsweise MCP-Audit/Replay bereits committeten.
Ein nachfolgender Fehler hinterliess Fachdaten trotz abgelehnter Aktion.
Der originale echte Transaktionsnachweis ergab 15 Fehler und 11 gruene Tests:
vier Rueckrollfehler, drei falsche positive Importvorschauen und acht
ungefangene NaN/sNaN-Faelle. Kein Fachtest wurde entfernt oder uebersprungen.

`create_bonus_run` und `import_signed` ueberlassen nun standardmaessig dem
Command den Commit. Der direkte REST-Aufruf optiert explizit mit `commit=True`
in seinen Abschluss; normale Query-Speicherung behaelt ihren bisherigen
Standalone-Vertrag. Der interne Query-Save kann ohne Zwischencommit laufen.
Damit bleiben auch die bestehenden MCP-Transaktionslocks bis zum aeusseren
Abschluss erhalten. SQL, Fach-Audit und Wiederholungsnachweis gehoeren zusammen.

Importvorschauen pruefen nach der HMAC-Signatur auch Datenprodukt, Felder,
Filter und Aggregationen mit derselben bestehenden Allowlist wie das Speichern.
NaN, sNaN und unendliche Bonussaetze sind Fachvalidierungsfehler in jedem Modus.
Diese vier Codekorrekturen wurden waehrend der gemeinsamen Arbeit bereits in
`6bfe6833c` integriert; dieser Abnahmeslice liefert die fehlenden Wirkungsnachweise
und korrigiert ein falsches Mock-Ziel in `test_mcp_execution.py`.

## Abnahme

- 44 neue Wirkungstests: HTTP-Audit/Outbox/Commit-Fehler, positive Persistenz
  mit korrekter Ergebnis-/Audit-ID, alle Vorschau-Modi ohne Schreibwirkung,
  signierte unerlaubte Felder, nicht endliche Bonussaetze, Standalone-REST-Commit,
  MCP-Mutation/Audit/Replay atomar und echte Wiederholung ohne zweite Mutation.
- Zusammen mit bestehenden Reporting-, MCP-, Mandanten-, Masken- und
  Batch2–4-Vertraegen: 295 Tests gruen, keine Skips.
- Mask-Map, Screen-Action-Katalog und Agent-Handbuch: Generatorchecks gruen.
- Nur SQLite im Arbeitsspeicher. Keine PostgreSQL-Testdatenbank, Docker-Ressource,
  Migration, Reset oder Fachschreibtest auf der Entwicklungsdatenbank.

Die Tests verwenden reale SQLAlchemy-Sitzungen und echte SQL-Wirkungen.
SQLite repraesentiert PostgreSQL-JSON als Text und Dezimalwerte als Strings;
der PostgreSQL-Advisory-Lock wird fuer diese Transaktionspruefung simuliert.
Dies ist kein Nachweis konkurrierender PostgreSQL-Locks oder einer Gesamt-UAT.

## Integration und Handshake

Die HTTP-/SD-/MCP-Lieferungen liegen im gemeinsamen Commit `6bfe6833c`.
Der verbleibende Command-Stand ist **36 mapped**, **13 local_ui**,
**5 blocked_missing_tenant**, **0 blocked_no_endpoint** und **1 open_high**.
Die fuenf Fuhrpark-Aktionen sind dadurch nicht fachlich geschlossen: ihnen
fehlt weiterhin sichere Mandantentrennung. FIN-CLOSE/ADR-076 und Zahlauf bleiben
gesperrt beziehungsweise unter ihrem Freigabevertrag.

Der neue OpenAPI-Drift auf GitHub `37887019065` gehoert zum vorhandenen
CI-Integrationsclaim: Spec ausschliesslich aus committed HEAD erzeugen und
indexseitig integrieren; fremde Arbeitsbaumfassung unveraendert erhalten.
Eine neue GitHub-Gesamtfreigabe folgt erst aus den Laeufen nach dem Push.

Finale Integrationsabnahme zusammen mit der Command-Auslagerung:
326 Tests ohne Skip in24,62s gruen. Die API-Spezifikation ergaenzt die
12 auf GitHub belegten fehlenden Pfade (3113 auf3125); vor/nach
Auslagerung bytegleich. [Godfile-Abnahme](command-endpoint-godfile-20261009.md).
