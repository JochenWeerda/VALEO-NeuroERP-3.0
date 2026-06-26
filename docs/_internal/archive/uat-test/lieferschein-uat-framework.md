# Vollautomatisches UAT-Testsystem für Lieferschein-Erfassung

## Vision

Ein vollautomatisches User Acceptance Testing (UAT) System, das alle Eventualitäten durchspielt und für menschliche Tester zu komplex wäre.

## Architektur

### 1. Keyboard-Shortcuts (LLM-Agenten-freundlich)

**Implementiert:**
- ✅ Strg+F1: Kundenauswahl öffnen
- ✅ Strg+F2: Artikelauswahl öffnen
- ✅ Strg+F3: Position OK
- ✅ Strg+F4: Lieferschein speichern
- ✅ Strg+F5: Lieferschein drucken
- ✅ Strg+F7: Schließen

**Vorteile:**
- LLM-Agenten können Shortcuts verwenden (keine komplexe DOM-Navigation)
- Robuster als CSS-Selektoren (funktioniert auch bei UI-Änderungen)
- Schneller als Maus-Klicks

### 2. Test-Framework (Playwright + LLM-Agenten)

```typescript
// Beispiel: Vollautomatischer Test
test('Lieferschein kompletter Workflow', async ({ page }) => {
  // 1. Navigiere zur Maske
  await page.goto('http://localhost:3000/verkauf/lieferschein-erfassung')
  
  // 2. Kundenauswahl öffnen (Strg+F1)
  await page.keyboard.press('Control+F1')
  await page.waitForSelector('[role="dialog"]')
  
  // 3. Kunde auswählen (per Suche oder Shortcut)
  await page.fill('input[placeholder*="Kunde"]', 'Test-Kunde')
  await page.keyboard.press('Enter') // Oder Dialog-Shortcut
  
  // 4. Artikelauswahl öffnen (Strg+F2)
  await page.keyboard.press('Control+F2')
  await page.waitForSelector('[role="dialog"]')
  
  // 5. Artikel auswählen
  await page.fill('input[placeholder*="Artikel"]', 'Test-Artikel')
  await page.keyboard.press('Enter')
  
  // 6. Position übernehmen (Strg+F3)
  await page.keyboard.press('Control+F3')
  
  // 7. Speichern (Strg+F4)
  await page.keyboard.press('Control+F4')
  await page.waitForSelector('text="Lieferschein erfolgreich gespeichert"')
})
```

### 3. Test-Szenarien

#### Happy Path
1. Kunde auswählen
2. Artikel auswählen
3. Position hinzufügen
4. Speichern
5. Drucken

#### Edge Cases
- Fehlende Pflichtfelder
- Ungültige Daten
- Netzwerk-Fehler
- Doppelte Eingaben
- Race Conditions

#### Randfälle
- Sehr große Mengen
- Negative Werte
- Sonderzeichen
- Sehr lange Texte
- Gleichzeitige Bearbeitung

## Nächste Schritte

1. **Dialog-Shortcuts**: Shortcuts für Dialog-Interaktionen (OK, Abbrechen, Suche)
2. **Test-Suite**: Vollständige Playwright-Test-Suite
3. **LLM-Agent-Integration**: Framework für LLM-Agenten-basierte Tests
4. **CI/CD-Integration**: Automatische Tests bei jedem Commit

## Referenzen

- Keyboard-Shortcuts: `docs/lieferschein-keyboard-shortcuts.md`
- Test-Ergebnisse: `docs/lieferschein-test-ergebnisse.md`

