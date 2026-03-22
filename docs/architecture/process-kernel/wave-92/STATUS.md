# Wave 92 — Touch/Keyboard-Härtung Logistik-Kernflow (Gap 002, 024)

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-20
**Tests:** 66 grün (Frontend Vitest), 0 Fehler (3 pre-existing failures unverändert)

## Gaps

| Gap | Beschreibung | Status |
|-----|--------------|--------|
| 002 | Rohware-Annahme: Touch-Library + Keyboard-Shortcuts | GESCHLOSSEN |
| 024 | LKW-Beladung: Touch-Library + API-Call + Keyboard-Shortcuts | GESCHLOSSEN |

## Geänderte Dateien

### `pages/annahme/rohware.tsx`
- `<select>` für Artikel → `TouchCardGroup`/`TouchCard` (6 Optionen)
- `<select>` für Lager-Ziel → `TouchCardGroup`/`TouchCard` (4 Optionen mit Beschreibung)
- `<Label>/<Input>` für Textfelder → `TouchTextInput` / `TouchNumericInput`
- Übersicht-Schritt → `TouchConfirmCard` (2x: Lieferant/Fahrzeug + Ware/Gewicht, optional Qualität)
- `buildCoreMaskShortcuts({ onSave, onCancel })` + `KeyboardShortcutBar`
- Wrapper-Pattern: `<div className="flex flex-col">` + `<KeyboardShortcutBar>` am Ende

### `pages/verladung/lkw-beladung.tsx`
- `<select>` für Verladeort → `TouchCardGroup`/`TouchCard` (3 Optionen: Silo 1/2, Halle A)
- `<Label>/<Input>` für alle Felder → `TouchTextInput` / `TouchNumericInput`
- Artikel-Schritt: `TouchCardGroup` für 7 Standard-Artikel
- Bestätigung-Schritt: `TouchConfirmCard`
- **API-Call ergänzt**: `POST /api/v1/lager/verladung` (war vorher nur `navigate`)
- `buildCoreMaskShortcuts({ onSave, onCancel, isSaveDisabled: saving })` + `KeyboardShortcutBar`
- Wrapper-Pattern: `<div className="flex flex-col">` + `<KeyboardShortcutBar>` am Ende

## Architekturentscheidungen

- `TouchNumericInput.onChange` gibt den Rohwert zurück; optionale Qualitätsfelder nutzen `String(v)` als Durchreiche (Backend führt Falsy-Check auf leerem String)
- `api` aus `@/lib/axios` (konsistent mit `auslagerung.tsx`)
- Qualitätswerte (Feuchte, Besatz, Fallzahl) bleiben optional; `String(v)` statt Nullvergleich vermeidet TS-Typfehler bei mixed `string | number` onChange-Signatur
- `loading={saving}` auf Wizard-Komponente für visuelles Feedback während API-Call

## Kernflow-Vollständigkeit nach Wave 92

| Seite | Touch | Keyboard | API |
|-------|-------|----------|-----|
| `annahme/lkw-registrierung.tsx` | ✓ | ✓ | ✓ |
| `annahme/qualitaets-check.tsx` | ✓ | ✓ | ✓ |
| `annahme/abrechnung.tsx` | ✓ | ✓ | ✓ |
| `annahme/rohware.tsx` | ✓ | ✓ | ✓ |
| `lager/einlagerung.tsx` | ✓ | ✓ | ✓ |
| `lager/auslagerung.tsx` | ✓ | ✓ | ✓ |
| `waage/wiegungen.tsx` | — | ✓ | ✓ |
| `waage/wiegeschein-detail.tsx` | — | ✓ | ✓ |
| `lager/inventur.tsx` | — | ✓ | ✓ |
| `verladung/lkw-beladung.tsx` | ✓ | ✓ | ✓ |
