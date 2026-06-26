# Globales Shortcut-System für Eingabemasken

## Übersicht

Einheitliches Keyboard-Shortcut-System für alle Eingabemasken im VALEO NeuroERP System. Die Shortcuts bleiben konsistent über alle Masken hinweg und unterstützen verschiedene Anzeige-Modi für unterschiedliche Benutzer-Level.

## Architektur

### 1. Globale Shortcut-Definitionen

**Datei**: `packages/frontend-web/src/lib/shortcuts/global-shortcuts.ts`

- Zentrale Definition aller Shortcuts
- Konsistente Aktionen über alle Masken
- Typ-sichere Handler-Registrierung

### 2. Shortcut-Help-Panel

**Datei**: `packages/frontend-web/src/components/shortcuts/ShortcutHelpPanel.tsx`

- Einklappbares Panel am rechten Bildschirmrand
- Halbtransparent (95% Opacity, Backdrop-Blur)
- Drei Anzeige-Modi:
  - **Immer**: Panel immer sichtbar (für Anfänger)
  - **Bei Hover**: Panel erscheint bei Hover über rechten Rand (für Geübte)
  - **Ausblenden**: Panel komplett versteckt (für Experten)

### 3. Shortcut-Hint-Buttons

**Komponente**: `ShortcutHintButton`

- Wrappt Buttons mit Shortcut-Hinweisen
- Zeigt Shortcut bei Hover oder Rechtsklick (je nach Display-Mode)
- Automatische Anpassung an Benutzer-Präferenz

## Standard-Shortcuts

| Shortcut | Aktion | Kategorie |
|----------|--------|-----------|
| **Strg+F1** | Kundenauswahl öffnen | Navigation |
| **Strg+F2** | Artikelauswahl öffnen | Navigation |
| **Strg+F3** | Position OK | Aktionen |
| **Strg+F4** | Dokument speichern | Aktionen |
| **Strg+F5** | Dokument drucken | Aktionen |
| **Strg+F6** | Dokument löschen | Aktionen |
| **Strg+F7** | Dokument schließen | Navigation |
| **Strg+F8** | Wie vorheriger (nur Positionen) | Aktionen |
| **Strg+F9** | Sofort-Rechnung | Aktionen |
| **Strg+F10** | Unterlagen | Navigation |
| **F11** | Wie vorheriger Beleg | Aktionen |
| **Strg+F12** | Information | Navigation |
| **Esc** | Abbrechen | Navigation |

## Verwendung

### 1. Provider in main.tsx integrieren

```typescript
import { GlobalShortcutProvider } from '@/components/shortcuts/GlobalShortcutProvider'

<GlobalShortcutProvider>
  <RouterProvider router={router} />
</GlobalShortcutProvider>
```

### 2. Shortcuts in Eingabemaske registrieren

```typescript
import { useGlobalShortcuts } from '@/lib/shortcuts/global-shortcuts'

useGlobalShortcuts({
  'open-customer-selection': () => setShowCustomerDialog(true),
  'open-article-selection': () => setShowArticleDialog(true),
  'confirm-position': () => handlePositionOK(),
  'save-document': () => void handleSave(),
  'print-document': () => setShowPrintDialog(true),
  'close-document': () => navigate(-1),
  'cancel': () => {
    setShowCustomerDialog(false)
    setShowArticleDialog(false)
  },
})
```

### 3. Buttons mit Shortcut-Hints wrappen

```typescript
import { ShortcutHintButton } from '@/components/shortcuts/ShortcutHelpPanel'

<ShortcutHintButton shortcut="Strg+F1">
  <Button onClick={() => setShowCustomerDialog(true)}>
    Kunde auswählen
  </Button>
</ShortcutHintButton>
```

## Benutzer-Präferenzen

Die Display-Mode-Präferenz wird in `localStorage` gespeichert:

- **Key**: `shortcut-help-display-mode`
- **Werte**: `'always'` | `'hover'` | `'hidden'`
- **Standard**: `'always'`

Benutzer können den Modus über das Dropdown im Panel-Header ändern.

## Vorteile

1. **Konsistenz**: Gleiche Shortcuts über alle Masken
2. **Lernhilfe**: Anfänger sehen immer die Shortcuts
3. **Flexibilität**: Geübte können Hints bei Bedarf anzeigen
4. **Produktivität**: Experten können alles ausblenden
5. **Automatisierung**: LLM-Agenten können Shortcuts verwenden

## Nächste Schritte

1. **Dialog-Shortcuts**: Shortcuts für Dialog-Interaktionen (OK, Abbrechen)
2. **Masken-spezifische Shortcuts**: Erweiterte Shortcuts pro Maske
3. **Customization**: Benutzer können Shortcuts anpassen
4. **Tutorial-Modus**: Interaktive Einführung für neue Benutzer

