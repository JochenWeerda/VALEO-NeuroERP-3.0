---
title: L3 zu VALEO NeuroERP Gewohnheitsbruecke
type: training-guide
status: pilotbereit
owner: Key User und Fachbereich
last_reviewed: 2026-08-23
---

# L3 zu VALEO NeuroERP Gewohnheitsbrücke

Diese Arbeitsunterlage verkürzt den Wechsel für erfahrene L3-Anwender. Sie ist
rollenbezogen vor dem Pilot mit den im Mandanten tatsächlich freigeschalteten
Masken zu ergänzen und anschließend als Evidenz `habit_bridge.*` freizugeben.

## Das vertraute Muster bleibt erhalten

| L3-Gewohnheit | Entsprechung in VALEO | Pilotprüfung |
|---|---|---|
| Funktion über Menübaum öffnen | Navigation nach Domäne und Prozess; häufige Masken als Favorit/Startkachel | Rolle findet jede Pflichtmaske ohne Hilfe |
| Belegkopf und Positionen bearbeiten | Einheitliche Desktop-Maske mit Kopf, Positionsraster, Aktionsleiste und Kontextbereich | Tab-Reihenfolge und Speichern funktionieren |
| Nummer/Bezeichnung zur Suche nutzen | Such-/Lookup-Feld mit fachlichem Schlüssel und Klartext | Treffer und Auswahl sind eindeutig |
| Folgebeleg aus Vorgänger erzeugen | Belegkette und fachliche Folgeaktion | Herkunft bleibt im Zielbeleg nachvollziehbar |
| Listen filtern und sortieren | Tabellenfilter, Sortierung und gespeicherte Ansicht | Key User stellt seine Tagesliste wieder her |
| Status/Fehler im Maskenkontext sehen | Status, Validierung und blockierende Meldung an Feld bzw. Aktion | Kein Fehler bleibt nur technisch sichtbar |
| Druck oder Dokumentablage aus Beleg | Druck-/Dokumentaktion mit Archivbezug | Originalformular und Wiederaufruf geprüft |

## Rollen-Startset

| Rolle | Startmasken/Favoriten | Tagesübung |
|---|---|---|
| Verkauf | Kunden, Angebote, Aufträge, Lieferscheine, Rechnungen, OP | einen vollständigen Sales-to-Cash-Fall |
| Einkauf | Lieferanten, Bestellungen, Wareneingänge, Eingangsrechnungen | einen vollständigen Procure-to-Pay-Fall |
| Lager/Logistik | Warenbewegung, Bestand, Chargen, Inventur, Verladung | Bewegung samt Charge und Rückverfolgung |
| Finanzbuchhaltung | Debitoren/Kreditoren, OP, Zahlung, Abstimmung | Rechnung, OP-Ausgleich und Tagesabgleich |
| Agrar | Kontrakte, Disposition, Ernteannahme, Qualität, Abrechnung | Kontrakt bis Abrechnung |
| IT/Betrieb | Integration, Jobs/Queues, Monitoring, Druck, Audit | Fehler erkennen, stoppen, nachweisen, fortsetzen |

## Kurzanleitung pro Prozess

Für jede Pflicht-Journey wird diese Karte ausgefüllt:

```text
Journey-ID:
L3-Einstieg/Funktionsname:
VALEO-Navigation oder Favorit:
Benötigte Rolle:
Schlüssel/Felder in gewohnter Reihenfolge:
Speichern/Prüfen/Folgeaktion:
Erwarteter Status und Folgebeleg:
Druck/Dokument/Integration:
Abweichung zu L3 und bewusster Grund:
Hilfe- oder Eskalationsweg:
```

## Tastatur- und Bedienabnahme

Konkrete Tastenkombinationen werden nur eingetragen, wenn sie in der
Pilotversion tatsächlich funktionieren. Zu prüfen sind: Vorwärts-/Rückwärts-
Tabben, Öffnen einer Auswahl, Bestätigen/Abbrechen, Speichern, Suche, neue
Position, Navigation im Raster und konfliktfreies Arbeiten mit Scanner/MDE.
Nicht unterstützte L3-Kürzel werden als Gap mit gewünschter Aktion erfasst;
inoffizielle Browser-Kürzel gelten nicht als Ersatz.

## 30-Minuten-Übung je Key User

1. Zwei häufige Masken ohne Anleitung finden und als Startzugang festlegen.
2. Einen vorhandenen Datensatz anhand Nummer und Bezeichnung finden.
3. Einen Beleg mit mindestens zwei Positionen erfassen, validieren und speichern.
4. Folgebeleg, Dokument/Druck und fachlichen Status kontrollieren.
5. Einen absichtlichen Eingabefehler erkennen und korrigieren.
6. Dauer, Hilfestellung und Bedienfehler im Journey-Protokoll erfassen.

Freigegeben wird die Gewohnheitsbrücke erst, wenn alle Rollen ihr Startset und
ihre Prozesskarten geprüft haben. Erkenntnisse, die mehrere Masken betreffen,
werden zentral in der ScreenDefinition→RenderPlan→UniversalMaskRuntime-Kette
umgesetzt und nicht als lokale Seiten-Sonderlösung.
