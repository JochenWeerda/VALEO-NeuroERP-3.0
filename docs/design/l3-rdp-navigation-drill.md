---
title: L3 RDP Navigations-Drill
type: reference
audience: [agent, entwickler]
owner: Cursor Agent
status: aktiv
last_reviewed: 2026-08-22
version: 1.3.0
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

- Captures (Delta): `C:\Users\Jochen\Pictures\L3-Capture-2026-08-21-delta`
- Captures (Nav-Drill): `C:\Users\Jochen\Pictures\L3-Capture-2026-08-21-nav-drill`
- Captures (praezise Icons): `C:\Users\Jochen\Pictures\L3-Capture-2026-08-21-nav-precise`
- Captures (Vollmasken 2026-08-21): `C:\Users\Jochen\Pictures\L3-Capture-2026-08-21-full-masks`
  (~370 PNGs, Logs `full-mask-*.txt`, `final_*`, `submenu_*`)
- Annotation: `_icons_annotated.png` / `401_icons_annotated.png`
- Fehlermuster: Tab-X zu weit rechts → falscher Ribbon;
  Klick neben Icon → leerer Workspace; modaler Dialog (Abfrage-Center)
  braucht `Alt+S` / Schliessen, nicht nur `Ctrl+F4`;
  `Alt+F4` riskiert App-Exit-Dialog (Nein!).

## Abgleich

Siehe [`l3-delta-mask-inventory-2026-08-21.md`](l3-delta-mask-inventory-2026-08-21.md)
und [`l3-full-mask-functional-gap-inventory.md`](l3-full-mask-functional-gap-inventory.md).

## Kalibrierte Tab-X (Fenster `-8,-8`, 1936x1048, Y≈58)

FAVORITEN ~175, ALLGEMEIN ~265, ERFASSUNG ~370, ABRECHNUNG ~480,
LAGER ~560, PRODUKTION ~620, AUSWERTUNGEN ~660, SCHNITTSTELLE ~760,
FENSTER ~900. Icon-Klick Y≈108 (Icon-Mitte).

## Dropdown-Leaf-Protokoll (2026-08-22)

1. Tab aktivieren → Dropdown-Icon **einmal** klicken (Y≈108) → Screenshot
   `menu_*_open.png`.
2. Menue-Eintraege **nicht** mit festem Offset aus PRODUKTION uebernehmen.
   Kalibrierung aus `final_aw_01_belegkontrolle.png`:
   - Beleg-Kontrolle Icon X≈215; Menü-Einträge X≈200, Y ab 133 (+22/Leaf) — bestätigt Live 22.08.
   - Weitere Icon X≈673 (bestätigt Live 22.08.)
   - Erster Eintrag Y≈133, Zeilenhoehe ≈22 px, Klick X≈175
3. Nach Leaf-Klick 900–1200 ms warten, Screenshot `leaf_*`, dann `Esc` +
   `Ctrl+F4` (mehrfach bei MDI). **Kein** `Alt+F4` auf Hauptfenster.
4. Flyout-Untermenues (Auftrags-/Lieferschein-Kontrolle): zuerst Zeile mit Pfeil,
   dann Flyout-Eintrag separat kalibrieren.
5. Skript: [`scripts/l3-dropdown-leaf-capture.ps1`](../../scripts/l3-dropdown-leaf-capture.ps1)
6. Gap-Abgleich: [`l3-dropdown-leaf-gap-inventory.md`](l3-dropdown-leaf-gap-inventory.md)

**Live-Captures 22.08.2026:** Ordner
`C:\Users\Jochen\Pictures\L3-Capture-2026-08-22-dropdown-leaves` (63 PNGs).

| Evidenz | Status |
|---------|--------|
| `beleg_menu_open.png` | **verlaesslich** — Beleg-Dropdown, Icon X=215 |
| `aw_artikel_leaf_7_artikel_konto.png` | **verlaesslich** — Weitere-Dropdown, Icon X=673 |
| `beleg_leaf_*.png`, `beleg_leaf_v3_*` | **ungueltig** — Abfrage-Center-Modal statt Beleg-Arbeitsmaske |
| `beleg_leaf_v2_*` | **ungueltig** — gleiches Modal-Muster |
| `beleg_menu_open_v2/v3` | **ungueltig** — kein Dropdown (DATEI/FENSTER/Fremdware offen) |

### Blocker Beleg-Leaf-Arbeitsmasken (22.08. Nachmittag)

1. **Modale Dialoge** (Abfrage-Center, Auswahl Kunden, EMPFANGSSCHEIN) fangen
   Ribbon-Klicks ab — Leaf-Skripte landen auf falschem UI.
2. **`SetForegroundWindow`** auf maximiertem RDP haengt intermittierend, wenn
   modale Fenster offen sind → Skripte mit `MoveWindow`/`SetForegroundWindow`
   vermeiden; [`l3-beleg-mini.ps1`](../../scripts/l3-beleg-mini.ps1) nutzen.
3. **Manueller Reset vor Capture:** alle MDI-Fenster schliessen (FENSTER →
   Alle Fenster **oder** Schliessen-Button im Dialog), dann Tab AUSWERTUNGEN
   pruefen, **RDP waehrend Skript nicht anfassen**, nur **ein** `mstsc`-Fenster.

### Manuelle Leaf-Reihenfolge (Beleg-Kontrolle)

| Index | Leaf | Flyout |
|------:|------|--------|
| 0 | Unerledigte Bestellungen | — |
| 1 | Eingangslieferschein-Kontrolle | — |
| 2 | Auftrags-Kontrolle | ▶ separat |
| 3 | Lieferschein-Kontrolle | ▶ separat |
| 4 | Gesperrte Lieferscheine | — |
| 5 | Nicht fakturierte Artikel | — |

Skripte: `l3-beleg-single-leaf.ps1` (ein Leaf), `l3-beleg-mini.ps1` (Reset +
ein Leaf ohne Foreground-Hang). Gap-Abgleich unveraendert in
[`l3-dropdown-leaf-gap-inventory.md`](l3-dropdown-leaf-gap-inventory.md).

`final_all_05_weitere` landeten auf PRODUKTION → Chargen-Nummern bearbeiten.
