---
title: Dokumentationsumgebung fuer den Postfach-Maskenvertrag
type: qa
audience: [entwickler, qa, agent]
owner: Codex-01a0f3fc
status: active
last_reviewed: 2026-10-08
version: 1.0.0
---

# Dokumentationsumgebung fuer Postfaecher

## Ursache und Umsetzung

Docs Build37786113441 auf eaf678e6b scheitert beim bestehenden
Handbuch-Driftcheck mit `No module named 'httpx'`. Die native Postfach-Maske
bezieht ihre Verwendungswerte aus dem kanonischen `mailkonto_service`.
Dieser importiert den HTTP-Client, SQLAlchemy und den Geheimnisdienst;
dessen Ausnahmevertrag importiert FastAPI. Die reine MkDocs-Umgebung hatte
diese vier Importabhaengigkeiten nicht installiert.

`requirements-docs.txt` deklariert jetzt ausschliesslich diese vier
zusaetzlichen Pakete: httpx0.28.1, SQLAlchemy2.0.41, cryptography50.0.1 und
FastAPI0.136.3. HTTP-, ORM- und API-Versionen entsprechen dem Backend;
cryptography entspricht dem bestehenden CRM-Security-Pin. Keine komplette
Backendinstallation, keine zweite Kopie des Verwendungswoerterbuchs,
keine Aenderung der fremden Mail-/Maskenimplementierung.

## Abnahme und Betrieb

Die bestehende Docs-Pipeline installiert `requirements-docs.txt`; ihr
Cache-Key enthaelt diese Datei. Die Erweiterung erreicht deshalb auch
den naechsten frischen GitHub-Lauf. Handbuch-Driftcheck und MkDocs-Build
bleiben unveraendert verbindlich.

Lokaler Nachweis: frische, wiederverwendbare isolierte Docs-Umgebung ohne
global installierte Backendpakete; Quellcode, Dokumentation und Routeninventar
aus committed HEAD. Ein alter eigener Ereigniscache wurde ausserhalb des
Pruefverzeichnisses gesichert, damit die vorhandene Clean-CI-Regenerierung
verwendet wird. Keine Datenbank, kein Container, kein Versand oder OAuth-Aufruf.

Ergebnis: Handbuch meldet fuenf aktuelle Artefakte; kompletter MkDocs-Build
erfolgreich in 126,61 Sekunden (Exit 0). Bestehende Linkwarnungen bleiben
sichtbar und wurden weder ausgeblendet noch zum bestandenen Link-Audit erklaert.

Der zusaetzliche Schema-Artefaktupload aus CI-CATALOG-SYNC bleibt eine
getrennte, nicht aktivierte Vorlage und wartet auf ausdrueckliche Freigabe.
