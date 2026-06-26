# Keyboard-Shortcuts für Lieferschein-Erfassungsmaske

## Übersicht

Die Lieferschein-Erfassungsmaske unterstützt Keyboard-Shortcuts für vollautomatische UAT-Tests durch LLM-Agenten.

## Verfügbare Shortcuts

| Shortcut | Aktion | Status |
|----------|--------|--------|
| **Strg+F1** | Kundenauswahl-Dialog öffnen | ✅ Implementiert |
| **Strg+F2** | Artikelauswahl-Dialog öffnen | ✅ Implementiert |
| **Strg+F3** | Position OK (Zeile übernehmen) | ✅ Implementiert |
| **Strg+F4** | Lieferschein speichern | ✅ Implementiert |
| **Strg+F5** | Lieferschein drucken | ✅ Implementiert |
| **Strg+F6** | Lieferschein löschen | ⏳ TODO |
| **Strg+F7** | Schließen (zurück navigieren) | ✅ Implementiert |
| **Strg+F8** | Wie vorheriger (nur Positionen) | ⏳ TODO |
| **Strg+F9** | Sofort-Rechnung | ⏳ TODO |
| **Strg+F10** | Unterlagen | ⏳ TODO |
| **F11** | Wie vorheriger Beleg | ⏳ TODO |
| **Strg+F12** | Information | ⏳ TODO |

## Verwendung für automatisierte Tests

### Beispiel-Workflow

```typescript
// 1. Kundenauswahl öffnen
await page.keyboard.press('Control+F1')
await page.waitForSelector('[role="dialog"]')

// 2. Kunde auswählen (manuell oder per Shortcut)
// TODO: Shortcuts für Dialog-Interaktionen

// 3. Artikelauswahl öffnen
await page.keyboard.press('Control+F2')
await page.waitForSelector('[role="dialog"]')

// 4. Artikel auswählen

// 5. Position übernehmen
await page.keyboard.press('Control+F3')

// 6. Lieferschein speichern
await page.keyboard.press('Control+F4')
await page.waitForSelector('text="Lieferschein erfolgreich gespeichert"')
```

## Implementierungsdetails

Die Shortcuts sind in `packages/frontend-web/src/pages/verkauf/lieferschein-erfassung.tsx` implementiert:

```typescript
useEffect(() => {
  const handleKeyDown = (e: KeyboardEvent): void => {
    if (e.ctrlKey && e.key.startsWith('F')) {
      const fKey = parseInt(e.key.substring(1))
      // ... Shortcut-Logik
    }
  }
  window.addEventListener('keydown', handleKeyDown)
  return () => window.removeEventListener('keydown', handleKeyDown)
}, [navigate, push, showPrintDialog])
```

## Nächste Schritte

1. **Dialog-Shortcuts**: Shortcuts für Dialog-Interaktionen (OK, Abbrechen, Suche)
2. **Erweiterte Aktionen**: Implementierung der TODO-Funktionen
3. **Test-Framework**: Vollautomatisches UAT-System mit Playwright/LLM-Agenten

