---
title: ADR-056 Herstellerneutraler ERP-Gewohnheitsvertrag
type: adr
audience: [architektur, design, entwickler, qa]
owner: platform/uix
status: proposed
last_reviewed: 2026-08-19
version: 1.0.0
---

# ADR-056 Herstellerneutraler ERP-Gewohnheitsvertrag

**Status:** Proposed - Human Review vor breitem Rollout

**Datum:** 2026-08-19

## Kontext

Bestandsanwender wechseln aus einem dichten Desktop-ERP. Eine reine optische
Neugestaltung verlaengert Lernwege, waehrend eine 1:1-Kopie Branding,
Altprobleme und maskenspezifischen Code konservieren wuerde. Die vorhandene
Meridian-Kette konnte Dichte, Floorplan, Register und Tabellenprofile bereits
ausdruecken, aber keine unteren Aktionszonen, Summenposition oder expliziten
Tastaturfluss.

## Entscheidung

- `ScreenDefinition.actions[]` erhaelt die optionalen, herstellerneutralen
  Angaben `zone=header|footer|commit` und `keyboardShortcut`.
- `ScreenDefinition.layout` erhaelt `summaryPlacement`, `stickyHeader` und
  `stickyFooter`; `interaction.enterMovesFocus` beschreibt den Desktop-Feldfluss.
- Der SchemaCompiler transportiert diese Angaben in den `RenderPlan`.
- Nur der zentrale `UniversalMaskRenderer` und seine Fast Renderer setzen sie
  um. ActionRuntime, Berechtigungen, Confirmation und Audit bleiben autoritativ.
- Fehlende Angaben behalten das bisherige Verhalten: Header-Aktionen,
  Kopf-Summary, keine Sticky-Region und nativer Browser-Fokus.
- L3 ist Referenz und Akzeptanzfall, aber kein Wert im kanonischen Schema.

## Konsequenzen

Positive Folge ist ein wiederverwendbarer Migrationsvertrag fuer beliebige
Vorgaengersysteme ohne zweites UI-System. Risiken sind zu viele deklarierte
Shortcuts oder ueberlappende Sticky-Bereiche; doppelte Shortcuts werden deshalb
validiert, und die Footer-Zone wird bei aktivem Formular-Submit-Bar nicht
zusaetzlich sticky gerendert.

Original-Screenshots mit Echtdaten bleiben ausserhalb von Git. Die redigierte
fachliche Ableitung steht in
[`l3-to-meridian-habit-parity.md`](../design/l3-to-meridian-habit-parity.md).
