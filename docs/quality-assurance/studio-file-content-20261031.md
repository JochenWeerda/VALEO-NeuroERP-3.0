---
title: Studio UTF-8-Dateieingabe — Vertrag und Abnahme
type: reference
audience: [entwickler, qa, agent]
owner: Codex Lead
status: abgeschlossen
last_reviewed: 2026-10-31
version: 1.0.0
description: Begrenzte lokale Textdateieingabe als gemeinsame Voraussetzung fuer native Verkaufslisten-Importaktionen.
---

# Lokale Textdateieingabe

## Vertrag

Ein Studio-Feld kann `type: file` und genau diesen optionalen Vertrag deklarieren:

```json
{"fileContent":{"encoding":"utf-8","maxBytes":1048576,"accept":[".csv",".txt"]}}
```

Die drei Eigenschaften sind verpflichtend; weitere Eigenschaften sind verboten.
`maxBytes` ist eine positive Ganzzahl bis einschliesslich 1 MiB. `accept` enthaelt
mindestens eine der beiden angegebenen Endungen, ohne Duplikate. Andere
Feldtypen, null-Vertraege, MIME-Werte statt Endungen, freie Uploadendpunkte und
unbekannte Kodierungen werden abgewiesen. Felder ohne diese Deklaration behalten
ihren bisherigen Vertrag.

Backend-Draftvalidierung und Frontend-Compiler pruefen rekursiv auch Reiter,
Tabellenunterfelder und Aktionseingaben. Der Compiler lehnt ungueltige
Deklarationen vor jedem Cachezugriff ab. RenderPlan, schnelle Formularprojektion,
Legacy-Projektion und Rueckprojektion erhalten die Metadaten. Dabei werden
fehlende optionale Vertraege nicht als explizites undefined-Feld materialisiert.

## Lesepfad und Formularzustand

Die Eingabe liest lokal ueber FileReader. Sie prueft Endung unabhaengig vom MIME,
Dateigroesse vor dem Lesen und tatsaechliche Bytezahl danach. Der UTF-8-Decoder
arbeitet fatal statt fehlerhafte Bytes still zu ersetzen; ein UTF-8-BOM wird
entfernt. Leere Dateien, unzulaessige Steuerzeichen und ungueltige direkte
Formularwerte werden abgewiesen. Fuer Mehrbytezeichen zaehlen Bytes statt
Zeichen. Zeilenumbrueche und Tabulatoren bleiben erhalten.

Eine neue Auswahl entwertet sofort den vorherigen Inhalt. Der voruebergehende
Wert null blockiert auch ein optionales Feld waehrend des Lesens oder nach einem
Fehler. Erst gueltiger Text darf den Aktionsdialog passieren; explizites Leeren
setzt den Wert auf den leeren String. Bei einem Pflichtfeld bleibt das gesperrt,
bei einem optionalen Feld ist danach eine Aktion ohne Dateifeld moeglich.

Eine Sequenzbindung verwirft spaete Antworten alter Auswahlen, nach Leeren,
Unmount, Feld-/Vertragswechsel, Schreibschutz und externem Formularreset.
Der Aktionsdialog erhaelt dafuer den null-Zustand unverfaelscht. Inhalte werden
weder automatisch uebertragen noch geloggt; die Vorschau meldet nur den
Ladezustand. Dateiinhalt bleibt ein Formulartext bis zur bestaetigten Fachaktion.

## Nachweise

- 80 Frontendtests in 9 Dateien bestanden: neue Datei-/Dialog-/Compilervertraege,
  bestehende Dialoge, Feldrenderer, RenderPlan und Listen-/Druckregression.
- 46 Backendfaelle bestanden: genaue Metadatenschluessel, Typ-/Bytegrenzen,
  verschachtelte Eingaben, Altkompatibilitaet und Studio-Aufnahme.
- Backendtests sind reine Unit-Tests mit `--noconftest`; keine API-Anmeldung,
  Testdatenbank oder Datenmutation. Im engen Studio-Aufnahmetest wird nur die
  fachfremde semantische Erntevorschau ersetzt; der echte Draftvalidator,
  Dateivertrag und die Katalogpruefung bleiben aktiv. Das ist kein Nachweis der
  semantischen Vorschau oder eines fachlichen Imports.
- Vollstaendige Frontend-Typpruefung und Produktionsbuild bestanden;
  Implementierungs-/Testlint, Dokuchecks und regulaere Commitchecks bestanden.
- Zusaetzlicher Architekturcheck bleibt rot: eine bereits unmappte Frontendroute
  und sieben Services in den unveraenderten Routing-/Serviceinventaren.
  Checker, Prefixregeln und Inventarinputs wurden nicht veraendert;
  dieser Befund wird nicht als gruene Architekturgesamtfreigabe ausgegeben.

## Implementierungsorte

Die reine Backendpruefung liegt in `app/services/studio_file_content_contracts.py`
und wird von `studio_validation.py` aufgerufen. Der gemeinsame Browservertrag
liegt in `runtime/text-file-contract.ts`, die lokale Eingabe in
`renderers/TextFileField.tsx`; FieldRenderer, RenderPlan und Formularzustand
reichen diesen Vertrag weiter. Die bisherigen Tabellenzellentypen bleiben
unveraendert; rekursive Metadatenpruefung ist keine Freigabe fuer Dateizellen.

## Grenzen und naechste Integration

Diese Eingabe ist kein atomarer Angebotsimport. Der serverseitige Fachcommand
muss Dateipayload, Groessenlimit, Zeilen, Kundenreferenz, Mandant, Rollen,
Idempotenz und gesamte Transaktion unabhaengig pruefen. CLI/MCP liefern denselben
Text statt einer Browserdatei; eine neue Agentenschreibfreigabe entsteht nicht.
Verkaufsseiten und Waagen-Backend wurden in diesem Slice nicht uebernommen.

Der zentrale Baustein schliesst allein keinen der 46 offenen Runtimepunkte.
Eine angemeldete Browser-/Fachkettenabnahme, atomarer Verkaufsimport und
Gesamt-CI bleiben offen. Keine DB-/Container-/Schemaaenderung oder Gate-Lockerung.
