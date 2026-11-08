---
title: Studio Listenmigration mit Funktionsparitaet
type: reference
audience: [entwickler, product, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-28
version: 1.0.0
description: Funktionale Studio Reklamationsliste, gemeinsame Kanalvertraege und visuelle Komponentenabnahme.
---

# Studio-Listenmigration

Die Reklamationsliste unter /qualitaet/reklamationen wird jetzt ausschliesslich
durch NativeListPage mit der kanonischen Definition qualitaet/reklamationen-liste
gerendert. Suche, Zeilennavigation, Neuanlage, Kennzahlen, CSV, Tastatur, Touch und
uebergebener Workflowkontext sind in die gemeinsame Runtime ueberfuehrt.
Es existiert kein verborgener Legacy-Aufruf und keine zweite Seitenlogik.

## Wiederverwendbarer Vertrag

listExperience durchlaeuft ScreenDefinition, Compiler, RenderPlan und Runtime.
Deklarierte Suchfelder, gefilterte Zaehler und bedingte Hinweise ersetzen
seitenspezifische Berechnung. Die Clientliste sammelt die freigegebene Quelle
vor dem Seitenschnitt, begrenzt auf5000 Zeilen/50 Seiten. Wechselnde Summen,
Wiederholungen und unvollstaendige Ergebnisse werden abgewiesen. Ein Abbruch
beendet weitere Abrufe. Quellenwechsel aendern den Query-Key; lokales Filtern
oder Export loesen keinen erneuten unfiltrierten Abruf aus.

Die bestehende MaskData-Projektion verwendet dieselben deklarierten Suchfelder
fuer REST, MCP und CLI. Echte signierte Aufrufe gegen eigene, zurueckgerollte
Pruefstanddaten bestaetigen identische Sortierung, Suche und Seite; fremder
Mandantenkontext wird abgelehnt. Es gibt keine neue Schreibfreischaltung.

Der Workflow-Checkpoint wird vor Navigation bestaetigt; Fehler halten die Maske
und erlauben Wiederholung. Gleichzeitige Klicks starten keinen zweiten Auftrag.
Der CSV-Export verwendet alle gefilterten geladenen Faelle, erklaerte Spalten
und Semikolon; Anfuehrungszeichen und Spreadsheet-Formelpraefixe werden behandelt.
Die gemeinsame Tastaturleiste verwendet jetzt semantische Theme-Tokens.

Studio validiert die Metadaten auch serverseitig: Typen, Groessen, eindeutige
Schluessel, reservierte Namen sowie Feld- und Aggregatreferenzen. Der Compiler
weist ungueltige Listenmetadaten vor dem Cachezugriff zurueck. Die Frontendfixture
entspricht dem unveraenderten kanonischen Python-Builder.

## Fachliche Datenbasis

Die bisherige Quelle umfasst hoechstens200 neueste Reklamationen des Mandanten;
die Oberflaeche benennt diesen Umfang. Im Domainmodell existiert keine gespeicherte
Prioritaet. Fehlende Werte werden daher unbekannt ausgewiesen, niemals als normal
erfunden. Unbekannte Statuswerte bleiben erhalten und werden nicht als neu
umgedeutet. Datenbankfehler ergeben eine bereinigte503 statt einer leeren Erfolgsliste.
Die fachlichen Create-/Update-Regeln und Bereichsrollen bleiben fuehrend.

## Abnahme

- 42 Frontendfaelle fuer Runtime, Compiler, gemeinsame Listen und Reklamationen.
- 35 Backendfaelle einschliesslich signierter REST-/MCP-/CLI- und SQL-Vertraege.
- 23 positive/negative serverseitige Studio-Vertraege.
- 4 kanonische Identitaetsvertraege.
- 4 Prozessraumfaelle: Fehler verhindert Navigation, Erfolg und Link funktionieren.

Gesamt108 gezielte Faelle. Die vollstaendige Typpruefung und der Produktionsbuild
sind ebenfalls erfolgreich abgeschlossen; keine Pruefgrenzen wurden gelockert.
Protokolle liegen unter ignorierten artifacts/studio-list-*-20261028.log.
Vier obsolete Screen-Identitaeten sind entfernt; aktive Routen und kanonische
Detailbindungen bleiben erhalten. Der erzeugte Bericht zeigt853 Definitionen,
C852, E801 und52 verbleibende Runtime-Punkte;844 native Katalogeintraege,
weiterhin5 strukturell freigabefaehige Draft-Projektionen. Dies ist keine
Gesamtfreigabe aller Masken. Die restlichen Prozessraeume benoetigen die im
[Familienplan](studio-workflow-migration-plan-20261028.md) beschriebenen Primitive.

## Visuelle Komponentenabnahme

Echte NativeListPage, Compiler und Renderer wurden mit synthetischer Definition
und synthetischen Daten im Browser geladen. Der Transport wurde ersetzt;
es wurden weder persoenliche Zugangsdaten noch produktive Geschaeftsdaten benutzt.
Dies ist eine Komponentenabnahme, keine angemeldete End-to-End-Abnahme.

| Aufloesung | Hell | Dunkel |
| --- | --- | --- |
|1366x768|[Bild](screenshots/studio-reklamationen-20261028/1366x768-light.png)|[Bild](screenshots/studio-reklamationen-20261028/1366x768-dark.png)|
|1440x900|[Bild](screenshots/studio-reklamationen-20261028/1440x900-light.png)|[Bild](screenshots/studio-reklamationen-20261028/1440x900-dark.png)|
|1920x1080|[Bild](screenshots/studio-reklamationen-20261028/1920x1080-light.png)|[Bild](screenshots/studio-reklamationen-20261028/1920x1080-dark.png)|

Alle sechs Ansichten:kein horizontaler Ueberlauf; axe-core meldet fuer die
Pruefung WCAG2A/AA keine Verletzung. Texte und Konturen wurden gesichtet.
Ein gefilterter CSV-Download wurde im Browser ausgeloest und inhaltlich geprueft.
Die [Ergebnisse](screenshots/studio-reklamationen-20261028/results.json) dokumentieren
Viewport, Theme, gemessene Grundfarben und Download. Automatisierte Ergebnisse
ersetzen keine allgemeine Zertifizierung. Der eigene Vorschauprozess und seine
zwei temporaeren Einstiegsdateien wurden nach der Abnahme beendet/entfernt.
