---
title: ADR-070 L3 Deep-Mask Parity
type: adr
audience: [architektur, entwickler, product, qa]
owner: architecture
status: proposed
last_reviewed: 2026-08-22
version: 1.0.0
---

# ADR-070 L3 Deep-Mask Parity

**Status:** Proposed

**Datum:** 2026-08-22

## Kontext

Die Live-Inventur der L3-Flyouts zeigte fachlich getrennte Einstiege, die in
VALEO teils nur als generische Funktion oder ohne native Maske vorhanden waren.

## Entscheidung

- Jede neue Maske laeuft durch ScreenDefinition, RenderPlan,
  `useUniversalMaskRuntime` und `UniversalMaskRenderer`.
- Gespeicherte Auftrags-/Lieferschein-Sichten teilen Service, Statusautomat und
  Audit der zentralen Belegkontrolle.
- DMS-Suche und Terrorschutzprotokolle sind tenantgebunden; die externe
  Dokumentvorschau bleibt konfigurationsgegated.
- Chargen werden im Operatorpfad tenantgebunden gelesen/geaendert. Eine
  Mehrfachfreigabe setzt vorherige Qualitaetsfreigabe und Auditgrund voraus.
- Duengemittelmengen verwenden kanonische Feldbuch-Reinnaehrstoffe; Schaetzung
  ist nur der gekennzeichnete N-Fallback fuer Altdaten.
- Tabellen-Mehrfachauswahl wird zentral im Renderer deklariert, nicht in einer
  einzelnen Maske nachgebaut.

## Konsequenzen

Die L3-Leaf-Gaps 019 bis 030 sind repo-seitig geschlossen. Externe Provider,
Rollenabdeckung und Echtdaten-Summenabnahme bleiben explizite Rollout-Gates.
