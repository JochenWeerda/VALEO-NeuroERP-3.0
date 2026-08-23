---
title: L3 zu Meridian Gewohnheits- und Paritaetsmatrix
type: reference
audience: [fachlich, design, entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-08-23
version: 1.1.0
description: Redigierte, datenfreie Ableitung von L3-Arbeitsgewohnheiten in herstellerneutrale Meridian-Vertraege.
---

# L3 zu Meridian Gewohnheits- und Paritaetsmatrix

## Datenschutz und Quelle

Die Referenzaufnahmen wurden am 19.08.2026 read-only in einer bereits
angemeldeten Remote-Desktop-Sitzung erstellt. Sie enthalten teilweise reale
Geschaefts- und Personendaten und bleiben deshalb ausschliesslich im lokalen,
nicht versionierten Bildordner. In Git werden weder Bilder noch Feldwerte,
Kundenbezeichnungen oder andere Identifikatoren abgelegt. Dieses Dokument
enthaelt nur abstrahierte Bedienmuster.

Die Vollabnahme vom 23.08.2026 hat acht lokale Capture-Verzeichnisse mit
insgesamt 1.022 PNG-Dateien wiedergefunden: 373 Vollmasken, 216
Dropdown-/Leaf-Aufnahmen und 433 fruehere Referenz-, Navigations- und
Kalibrierbilder. Diese Zahlen beschreiben nur den lokalen Evidenzbestand; die
Bilder selbst und darin sichtbare Werte werden weiterhin nicht versioniert.

## Leitentscheidung

VALEO kopiert weder Produktbranding noch Pixel-Layout von L3. Uebernommen werden
stabile Arbeitsgewohnheiten: Reihenfolge, feste Regionen, Registerlogik,
Tabellenorientierung, Aktionsgruppen und Tastaturwege. Die Umsetzung erfolgt
zentral ueber:

`ScreenDefinition -> RenderPlan -> useUniversalMaskRuntime -> UniversalMaskRenderer`

## Referenzmuster

| Referenz | Beobachtete Gewohnheit | Meridian-Vertrag | VALEO-Referenz | Stand |
|---|---|---|---|---|
| Artikelstamm | Dichte Stammdaten, viele Register, aktuelle Entitaet bleibt sichtbar | `expertDense`, Register-Tabs, `stickyHeader`, `stickyFooter`, `enterMovesFocus` | `lager/article-stock` | umgesetzt |
| Artikelstamm | Fachaktionen links unten, Abschlussaktion rechts unten | `action.zone=footer|commit` | `lager/article-stock` | umgesetzt fuer vorhandene Action; weitere Actions erst mit echten Commands |
| Kunden-Artikel | Filterbarer Master-Detail-Bestand und feste Druck-/Preisaktionen | serverseitige Tabelle, Register, Footer-Zonen | CRM/KIM Kundeninformationen und `crm/customer-360` | Interaktionsmuster umgesetzt; eigene native Kunden-Artikel-Entitaet ist nicht Teil dieses Slices |
| Kundenstamm | Bearbeitung rechts, fachliche Folgeaktionen links | `edit.zone=commit`, `create_activity.zone=footer` | `crm/customer-360` | umgesetzt |
| Verkaufs-Lieferschein | Kopf und Adressregister, grosses Positionsraster | `transaction`, Register-Tabs, Tabellenprofil | `sales/delivery-note` | umgesetzt |
| Verkaufs-Lieferschein | Summen nach Positionen, danach feste Aktionsleiste | `layout.summaryPlacement=footer`, `stickyFooter` | `sales/delivery-note` | umgesetzt |
| Verkaufs-Lieferschein | Drucken als direkter Tastaturweg | `keyboardShortcut=Ctrl+P` | `sales/delivery-note` | umgesetzt; ActionRuntime bleibt autoritativ |
| Alle drei | Enter folgt dem sichtbaren Feldfluss | `interaction.enterMovesFocus=true` | alle drei nativen ScreenDefinitions | umgesetzt |

## Vollabnahme 2026-08-23

- Alle 69 produktiven nativen ScreenDefinitions sind `generatorReady` und
  verwenden nach zentraler Normalisierung nur renderbare Floorplans,
  Context-Rails und Tabellenprofile.
- Historische Aliaswerte (`listReport`, `crm`, `document`, `preview`,
  `summary`, `findings`) werden an einer Stelle in den kanonischen
  Meridian-Vertrag uebersetzt.
- `expertDense` wirkt nun auch tatsaechlich auf Root- und Registertabellen:
  die zentrale RenderPlan-Kompilierung begrenzt deren Zeilenhoehe auf 36 px;
  `compact` bleibt bei 44 px und `comfortable` bei mindestens 52 px.
- Alte Gefahrenstufen werden zentral normalisiert; hohe und kritische Aktionen
  erhalten zwingend Bestaetigung und Human-Freigabe.
- Der Browser-Audit prueft an allen drei Zielaufloesungen nicht nur Container,
  sondern sichtbare Datenzeilen, deren Dichte und horizontalen Viewport-
  Ueberlauf. Ergebnis: 12/12 gruen.

## Bewusste Nicht-Uebernahmen

- Keine L3-Farbcodierung als VALEO-Theme und keine Marken-/Icon-Kopie.
- Keine unsichtbaren Schreibaktionen waehrend der Inventur.
- Keine Buttons ohne echten Berechtigungs- und Command-Vertrag.
- Keine clientseitige Volltabelle als Ersatz fuer Pagination und Virtualisierung.
- Keine maskenspezifische Parallelkomponente ausserhalb des Single Mask Builder.

## Abnahmevertrag

- Unit: Compiler transportiert alle Interaktionsmetadaten verlustfrei.
- Component: Header-/Footer-/Commit-Zonen, Shortcut-Dispatch und Enter-Fokus.
- Backend: alle produktiven nativen ScreenDefinitions bleiben `generatorReady=true`
  und nutzen das renderbare Meridian-Vertragsvokabular.
- Visual: CRM, Artikelbestand und Verkaufs-Lieferschein bei 1366x768,
  1440x900 und 1920x1080 mit sichtbaren Datenzeilen, korrekter Dichte und ohne
  horizontalen Viewport-Ueberlauf; Finance ergaenzt die Referenzmatrix.
- Rollout: fachliche Pilotabnahme durch erfahrene L3-Anwender bleibt ein
  externes Gate; sie ist kein Grund, technische Paritaet vorzutäuschen.
