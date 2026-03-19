# Wave 77 — Keyboard-first Kernmasken (Gap 023)

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-19
**Tests:** 34 passed, 0 failed
**Gap:** 023 — Keyboard-first für alle Kernmasken, KPI: >=90% Kernflows ohne Maus bedienbar

## Lieferumfang

### A) useKeyboardShortcuts Hook (`hooks/useKeyboardShortcuts.ts`)

Neuer Hook für alle ERP-Masken:

```ts
useKeyboardShortcuts([
  { key: 's', ctrl: true, label: 'Speichern', action: handleSave },
  { key: 'Escape', label: 'Abbrechen', action: handleCancel },
])
```

Features:
- Event-Handler auf `window` mit `capture: true` (keine Bubbling-Unterbrechung)
- **Input-Guard**: Buchstaben-Shortcuts feuern nicht in Eingabefeldern (außer Ctrl/Alt-Modifier oder explizit erlaubt)
- **Input-Safe Keys**: `Escape`, F1–F12 feuern immer (auch in Inputs)
- `allowInInputs: true` für Ctrl+S (soll auch beim Tippen in Inputs auslösen)
- Shortcut-Liste per Ref → kein Re-Mount bei State-Änderungen
- Automatisches Cleanup beim Unmount

### B) buildCoreMaskShortcuts() — Standard-Shortcuts

```ts
const shortcuts = buildCoreMaskShortcuts({
  onSave: handleSave,
  onCancel: onCancel,
  onNew: handleNew,
  isSaveDisabled: isSubmitting || !isDirty,
})
```

| Aktion | Shortcut | Scope |
|--------|---------|-------|
| Speichern | Ctrl+S | Immer (auch in Inputs) |
| Abbrechen | Escape | Nicht in Inputs |
| Neu | Ctrl+N | — |
| Löschen | Ctrl+Delete | — |
| Suchen | Ctrl+F | Nicht in Inputs |
| Aktualisieren | F5 | Immer |

### C) KeyboardShortcutBar (`components/keyboard/KeyboardShortcutBar.tsx`)

Footer-Leiste mit aktiven Shortcuts:
- Erscheint nur auf **Desktop** (nicht auf Touch-Geräten, erkannt via `pointer: coarse`)
- `<kbd>`-Elemente für visuelle Tasten-Darstellung
- Formatierung: `Ctrl+S` auf Windows, `⌘S` auf Mac
- Maximal 6 Shortcuts sichtbar (konfigurierbar)
- `role="status"` für Screen-Reader

### D) ObjectPage Integration

`components/mask-builder/ObjectPage.tsx` nutzt jetzt:
- `useKeyboardShortcuts()` für Ctrl+S (Speichern) und Escape (Abbrechen)
- `KeyboardShortcutBar` am unteren Rand des Formulars
- Deaktiviert wenn `isSubmitting || !isDirty`

## Kontrakt-Tests (34 Tests)

- `TestKeyboardShortcut` (10): Validierung, Fingerprint, Modifier-Regeln
- `TestKeyboardShortcutRegistry` (5): Register, Konflikt-Erkennung
- `TestCoreMaskCoverage` (6): Coverage >= 90% für alle 5 Maskentypen
- `TestKernShortcuts` (6): Kern-Shortcuts in allen Maskentypen vorhanden
- `TestConflictDetection` (3): Duplikat-Fingerprint erkannt
- `TestTabNavigation` (4): WCAG 2.1 SC 2.4.3 — Focus Order

## Coverage-Ergebnis (KPI erfüllt)

| Maskentyp | Required Flows | Covered | Coverage |
|-----------|---------------|---------|---------|
| ObjectPage | save, cancel, refresh | 3/3 | **100%** |
| ListReport | search, refresh, new | 3/3 | **100%** |
| Wizard | next, back, cancel | 3/3 | **100%** |
| Worklist | refresh, search | 2/2 | **100%** |
| OverviewPage | refresh | 1/1 | **100%** |

**KPI erfüllt: >=90% aller Kernflows ohne Maus bedienbar** ✓
