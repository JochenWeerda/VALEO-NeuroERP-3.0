# Wave 103 — Gap 024: Touch-optimierte Feldworkflows + Gap 023: Keyboard-first

## Scope
Gap 024 (Touch-optimierte Feldworkflows) + Gap 023 (Keyboard-first Kernmasken).

## Zielbild
Touch-Targets ≥44×44px, Fehlbedienungen -40%; ≥90% Kernflows ohne Maus bedienbar.

## Lieferumfang
Siehe Abschnitte Gap 024 und Gap 023 unten.

## Abnahmekriterien
- `size="touch"` (56px) und `size="touch-xl"` (64px) in button.tsx vorhanden
- TouchNumpad-Komponente implementiert und in Waage/Annahme verwendet
- ObjectPage: `Ctrl+S` / `Escape` aktiv
- ListReport: `Ctrl+F` / `Ctrl+N` aktiv
- Keyboard-Abdeckung von ~7% auf ~85% gestiegen

## Gap 024: Touch-optimierte Feldworkflows

**KPI-Ziel:** Fehlbedienungen auf Touch -40% (≥44×44px Touch-Targets, 8px Spacing)

### A) Button-Komponente: Touch-Größen-Varianten
`packages/frontend-web/src/components/ui/button.tsx`:
- `size="touch"` — `h-14 px-6 text-base rounded-lg min-w-[56px]` (56px ≥ WCAG 2.5.5 Minimum)
- `size="touch-xl"` — `h-16 px-8 text-lg rounded-xl min-w-[64px] font-semibold`
- `size="touch-icon"` — `h-14 w-14 rounded-lg`

### B) TouchNumpad-Komponente (neu)
`packages/frontend-web/src/components/ui/touch-numpad.tsx`:
- Numerisches Eingabepad mit 56×56px Tasten, 8px Gap
- Modus: `int` | `decimal` | `text`
- Verwendung: Waage-Gewichtseingabe, Lager-Mengen, Annahme-Zahlen
- Bestätigen-Button (optional, mit `onConfirm`)

### C) waage/wiegungen.tsx — Touch-optimiert
- Gewicht-Inputs (Brutto/Tara): `className="h-14 text-base"` + `inputMode="decimal"`
- Feuchte/Besatz: `h-14 text-base`
- Selects (Ticket/Kontrakt): `h-14 text-base`
- Buttons: `size="touch"` auf Anlegen + Allokieren
- Fix: `useKeyboardShortcuts` vor Early-Return verschoben (react-hooks/rules-of-hooks)

### D) annahme/qr-scanner.tsx — Touch-optimiert
- QR-Input: `h-14`
- Erkennen-Button: `size="touch"`
- Priorität-Select: `h-14 text-base`
- Hauptaktion "In Warteschlange einreihen": `size="touch"`
- Erfolgs-Screen-Buttons: `size="touch"`

## Gap 023: Keyboard-first Kernmasken

**KPI-Ziel:** ≥90% Kernflows ohne Maus bedienbar

### A) ObjectPage — Keyboard-Shortcuts integriert
`packages/frontend-web/src/components/mask-builder/ObjectPage.tsx`:
- `Ctrl+S` → Speichern (auch aus Eingabefeldern heraus, `allowInInputs: true`)
- `Escape` → Abbrechen

→ Gilt für alle ~200 Seiten die ObjectPage verwenden

### B) ListReport — Keyboard-Shortcuts integriert
`packages/frontend-web/src/components/mask-builder/ListReport.tsx`:
- `Ctrl+F` → Fokus auf Suchfeld
- `Ctrl+N` → Neu (wenn `onCreate` vorhanden)
- `searchRef` auf Search-Input verdrahtet

→ Gilt für alle ~150 Seiten die ListReport verwenden

### Gesamtabdeckung
Vor Wave 103: 33 von 451 Seiten mit Keyboard-Shortcuts (~7%)
Nach Wave 103: ~380+ Seiten durch Mask-Builder-Integration (~85%)
→ KPI ≥90% wird durch verbleibende manuelle Optimierungen in Wellen erreicht

## Tests
Keine dedizierten Wave-103-Tests (UI-Komponenten); bestehende Vitest-Suite unverändert grün.

## Status
`abgeschlossen` — 2026-03-24
