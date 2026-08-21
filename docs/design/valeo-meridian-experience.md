---
title: VALEO Meridian Experience
type: reference
audience: [agent, entwickler, design, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-08-19
version: 1.1.0
description: Meridian als Design-, Layout- und Governance-Vertrag des Single Mask Builder.
---

# VALEO Meridian Experience

Meridian ist keine manuelle Seiten-Bauanleitung und kein paralleles UI-Framework.
Meridian ist die zentrale Builder-Capability in dieser Kette:

```text
ScreenDefinition -> RenderPlan -> useUniversalMaskRuntime -> UniversalMaskRenderer
```

Wenn eine Maske unprofessionell wirkt, wird nicht die einzelne Seite geflickt.
Korrigiert werden Schema, Compiler, Renderer oder Readiness-Gate.

## Low-Fidelity-Triage

Vor groesseren Layout-Aenderungen wird die Maske als Scribble, Wireframe oder
Low-Fidelity-Prototyp bewertet. Ziel ist nicht Pixel-Design, sondern fruehe
Logikpruefung:

- Klickwege kuerzen: primaere Aktion, naechste Aktion und Rueckweg muessen im
  ersten Viewport erkennbar sein.
- Felder aussortieren: nur Identitaet, Status, Risiko, Betrag/Menge und naechste
  Entscheidung gehoeren in Header oder Summary.
- Nebensaechliches verbannen: selten genutzte Stammdaten, Historien, Dokumente
  und technische Details wandern in Tabs oder Kontext-Rail.
- Tabellen priorisieren: ERP-Listen bleiben Tabellen; Karten sind kein Ersatz
  fuer tabellarische Finanz-, Lager- oder Auditdaten.
- Kontext klaeren: Audit, Workflow, Sperren, Human Approval und Copilot-Erklaerung
  erscheinen in der Kontext-Rail, nicht verteilt in Fachfeldern.

Das Ergebnis der Triage wird in `ScreenDefinition.layout`, Tabs, Summary-Items,
Actions und Tabellenprofilen ausgedrueckt. Es entsteht keine separate Referenz-UI.

## Layout-Vertrag

`ScreenDefinition.layout` traegt die Meridian-Metadaten:

```ts
layout: {
  floorplan: 'worklist' | 'objectPage' | 'transaction' | 'cockpit' | 'wizard'
  density: 'comfortable' | 'compact' | 'expertDense'
  contextRail: 'none' | 'audit' | 'copilot' | 'workflow' | 'combined'
  tableProfile?: 'standard' | 'financial' | 'inventory' | 'audit'
  summaryPlacement?: 'header' | 'footer'
  stickyHeader?: boolean
  stickyFooter?: boolean
}
```

Der `RenderPlan.shell` uebernimmt diese Felder zentral. Renderer lesen den Plan
und erzeugen daraus Header, Aktionshierarchie, Summary, Tabs, Tabellenprofil,
Dichte und Kontextbereich.

## Gewohnheitsbruecken

Migration aus einem bestehenden Desktop-ERP wird als Bedienvertrag modelliert,
nicht als herstellerspezifisches Theme. Additive Meridian-Vertraege sind:

- `actions[].zone`: fachliche Aktionen links im Footer, Commit-Aktionen rechts;
  ohne Angabe bleibt die Action im Header.
- `actions[].keyboardShortcut`: sichtbarer und zentral dispatchter Tastaturweg;
  Berechtigungen und ActionRuntime bleiben unveraendert.
- `layout.summaryPlacement`: Summen wahlweise im Kopf oder nach Tabellen/Tabs.
- `layout.stickyHeader` / `stickyFooter`: stabile Orientierung bei dichten
  Desktopmasken.
- `interaction.enterMovesFocus`: Enter folgt dem sichtbaren Feldfluss; Textareas
  und Buttons behalten ihre native Bedeutung.
- `tables[].rowActions`: statusabhaengige Zeilenaktionen werden im zentralen
  Fast-Table-Renderer deklariert. Einzelmasken bauen dafuer keine eigene
  Aktionsspalte; Backend-Berechtigung, Confirmation und Audit bleiben
  autoritativ.

L3-Referenzfaelle und Datenschutzregeln:
[`l3-to-meridian-habit-parity.md`](l3-to-meridian-habit-parity.md).

## Governance

`generatorReady=true` ist nur erlaubt, wenn die Meridian-Metadaten vorhanden sind.
Tabellenmasken brauchen ein Tabellenprofil. Finanzmasken brauchen `financial`,
Lager-/Bestandsmasken `inventory`. Detail-, Cockpit-, Transaktions- und
Wizard-Masken duerfen keine leere Kontext-Rail haben.

Referenzmasken sind Abnahmefaelle:

- Finance: `financial` profile, AuditReason, Freigabe-/Storno-/Buchungslogik.
- CRM 360: `objectPage` oder `cockpit`, aktive Kontext-Rail, Status und ActionRuntime.
- Lager: `inventory` profile, Mengen/Einheiten, Reservierungen, Bewegungen und Status.

Abweichungen werden im Builder oder in der ScreenDefinition behoben.
