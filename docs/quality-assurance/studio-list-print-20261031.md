---
title: Studio-Listen — deklarierter lokaler Druck
type: reference
audience: [entwickler, qa]
owner: Codex Lead
status: abgeschlossen
last_reviewed: 2026-10-31
version: 1.0.0
description: Gefilterter Listendruck als zentrale Voraussetzung fuer die Runtime46-Verkaufslisten.
---

# Deklarierter Listendruck

## Vertrag

NativeListPage behandelt vorhandene Aktionen mit `localEffect: print` ohne
`commandEndpoint` lokal. Der vorhandene `printTable`-Helper rendert Titel,
Spaltennamen und Werte HTML-escaped. Grundlage sind exakt die vollstaendigen,
vor der Seitenteilung gefilterten Runtime-Zeilen und die deklarierten
`listExperience.export.columns`; damit teilen CSV und Druck ihren Datenvertrag.
Verborgene zusaetzliche Datensatzfelder werden nicht als Spalten gedruckt.

Die Aktion prueft zuerst ihre deklarierte Berechtigung. Eine leere oder noch
nicht geladene Ergebnismenge beziehungsweise eine fehlende Listendeklaration
fuehrt zu einer Fehlermeldung. Es erfolgt kein unfiltrierter Ersatzabruf und
kein Fachwrite. Fehler beim Oeffnen/Erstellen des Druckfensters werden gemeldet;
der vorhandene Helper meldet blockierte Pop-ups selbst.

Fachbelegdruck mit einem `commandEndpoint` behält den bestehenden
Bestaetigungs-/Commandweg. Diese Aenderung stellt keine Belegbuchung oder
serverseitige Druckfreigabe bereit.

## Abnahme

Die neue Komponentenpruefung verwendet eine ersetzte Runtime-Datenuebergabe,
die echte NativeListPage und ihren Aktionsdialog. Sie prueft gefilterte Zeilen,
Spalten, Rechte, leere/nicht deklarierte Listen, Fehler und den getrennten
Fachcommandweg. Der vorhandene export-utils-Test prueft HTML-Escaping im
wirklichen Druckhelper. Das ist keine angemeldete Browser-/Fachkettenabnahme.

Gezielter Nachlauf: **29 Tests in 5 Dateien bestanden** (sechs neue
Druckfaelle, bestehende Listenaktionen/Vorbelegung, Listenvertrag und HTML-
Escaping). Vollstaendige Frontend-Typpruefung und Produktionsbuild erfolgreich.
ESLint fuer Implementierung und neuen Test erfolgreich; Markdown-/Doku-
Governance, Pfadschutz, Datenschutzpruefung und git diff --check erfolgreich.
Build meldet bestehende Annotation-/Chunkhinweise; keine Buildfehler.

## Offene Integration

Die beiden Verkaufsseiten sind im veroeffentlichten Ausgangsstand weiterhin
handgebaut; die Unterclaims SALES-LISTS und INTAKE-WEIGHING sind reserviert.
Diese zentrale Voraussetzung schliesst allein keinen der 46 Runtimepunkte.
Dateieingabe, atomarer Angebotsimport, Arbeitsfokus und fachliche
Verkaufslisten-/Waagenabnahme bleiben gesondert nachzuweisen.

Am Ausgangscommit `662dfaed03b0397e113ebe36f5689d00cb9524bd` scheitert das
Backend-CI vor pytest am Doku-Drift-Gate mit 261 nicht erreichbaren Seiten.
Das Frontend-CI meldet 186 fehlgeschlagene Tests in 40 Dateien bei 1884
bestandenen Tests. Diese bestehenden Befunde werden durch den engen
Druck-Nachweis nicht geschlossen; Gate-Schwellen und Ausnahmen bleiben gleich.
