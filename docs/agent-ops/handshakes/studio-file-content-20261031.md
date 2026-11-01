---
title: Uebergabe Studio-Dateieingabe
type: reference
audience: [agent, entwickler]
owner: Codex Lead
status: abgeschlossen
last_reviewed: 2026-10-31
version: 1.0.0
description: Integrationsvertrag fuer begrenzte UTF-8-Dateitexte in Studio-Importaktionen.
---

# Studio-Dateieingabe

`type: file` mit `fileContent={encoding:utf-8,maxBytes,accept}` liefert gueltigen
Text an das Formular. maxBytes bis1MiB; accept explizit csv/txt-Endungen.
Backend-Draftvalidator und Compiler lehnen ungueltige Deklarationen ab.
Pflicht-, Pending-, Fehler-, Reset- und Auswahlschutz werden zentral geprueft.
Keine automatische Fachmutation, neue Berechtigung, Datenbank oder Container.

[Vertrag und Abnahme](../../quality-assurance/studio-file-content-20261031.md).
80Frontendtests und46reineBackendfaelle gruen. AufnahmeUnit isoliert nur die
fachfremde semantische Erntevorschau; kein echter Angebots-/SQL-/SSONachweis.

Naechster Schritt: reservierten sales.offer.import_csv.v1-Fachcommand mit der
Angebotsdefinition zusammenfuehren; Pflicht-Dateifeld auf dessen Payloadnamen
binden. Der Server muss Dateiinhalt unabhaengig pruefen und alle Zeilen atomar
mit Mandant, Rolle, Kundenreferenz, Audit und Idempotenz speichern. Danach
Angebots-/Lieferungsparitaet, Arbeitsfokus und Gate E messen. 46Runtimepunkte
bleiben bis zu ihren jeweiligen Fachabnahmen offen.

Vollstaendige Typpruefung/Produktionsbuild/Lint gruen. Architekturcheck hat
weiterhin1unmappteRoute/7Services in unveraendertenInventaren; keineGesamtfreigabe.
