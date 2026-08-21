---
title: L3 RDP Navigations-Drill
type: reference
audience: [agent, entwickler]
owner: Cursor Agent
status: aktiv
last_reviewed: 2026-08-21
version: 1.1.0
description: Geuebte Gesten zum Oeffnen und Schliessen von L3-Ribbons und Masken per Remote Desktop.
---

# L3 RDP Navigations-Drill

## Harte Regel (verbindlich)

**Nur ein Linksklick mit dem Mauszeiger genau auf dem Icon oeffnet die Maske.**

- Der Cursor muss auf der **Icon-Flaeche** landen (Bildmitte), nicht daneben,
  nicht auf dem Tab-Text und nicht auf dem Dropdown-Pfeil rechts neben dem Icon.
- Danach kurzes Warten und Screenshot-Pruefung: Workspace darf nicht leer bleiben.
- Daneben geklickt = kein Fortschritt. Keine Tastatur-Ersatzannahme fuer Ribbon-Icons.

## Gesten (read-only)

1. RDP-Fenster maximieren und fokussieren (`mstsc` auf `10.200.1.3`).
2. Fensterursprung merken (`GetWindowRect`) — Klicks immer `windowOrigin + localXY`.
3. Ribbon-Tab per Linksklick aktivieren; aktive Tab-Unterstreichung pruefen.
4. Icon-Mitten aus dem aktuellen Screenshot pixelweise bestimmen (farbige Glyphs).
5. `SetCursorPos` auf Icon-Mitte → `MOUSEEVENTF_LEFTDOWN/UP`.
6. Maske schliessen: `Esc`, danach `Ctrl+F4` (mehrfach bei MDI).
7. Keine Speichern-/Buchen-/Loesch-Aktionen.

## Evidenz 2026-08-21

- Captures: `C:\Users\Jochen\Pictures\L3-Capture-2026-08-21-nav-precise`
- Annotation: `_icons_annotated.png` (rote Kreise = erkannte Icon-Mitten)
- Fehlermuster: Tab-X zu weit rechts → ABRECHNUNG statt ERFASSUNG;
  Klick neben Icon → leerer Workspace (kein Maskenfenster).

## Abgleich

Siehe [`l3-delta-mask-inventory-2026-08-21.md`](l3-delta-mask-inventory-2026-08-21.md)
und [`l3-full-mask-functional-gap-inventory.md`](l3-full-mask-functional-gap-inventory.md).
