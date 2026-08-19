---
title: L3 zu Meridian Gewohnheits- und Paritaetsmatrix
type: reference
audience: [fachlich, design, entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-08-19
version: 1.0.0
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

## Bewusste Nicht-Uebernahmen

- Keine L3-Farbcodierung als VALEO-Theme und keine Marken-/Icon-Kopie.
- Keine unsichtbaren Schreibaktionen waehrend der Inventur.
- Keine Buttons ohne echten Berechtigungs- und Command-Vertrag.
- Keine clientseitige Volltabelle als Ersatz fuer Pagination und Virtualisierung.
- Keine maskenspezifische Parallelkomponente ausserhalb des Single Mask Builder.

## Abnahmevertrag

- Unit: Compiler transportiert alle Interaktionsmetadaten verlustfrei.
- Component: Header-/Footer-/Commit-Zonen, Shortcut-Dispatch und Enter-Fokus.
- Backend: die drei ausgelieferten ScreenDefinitions bleiben `generatorReady=true`.
- Visual: CRM, Artikelbestand und Verkaufs-Lieferschein bei 1366x768,
  1440x900 und 1920x1080 ohne horizontalen Viewport-Ueberlauf.
- Rollout: fachliche Pilotabnahme durch erfahrene L3-Anwender bleibt ein
  externes Gate; sie ist kein Grund, technische Paritaet vorzutäuschen.
