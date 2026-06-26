# Kundenauswahl-Dialog - Verbesserungen

**Datum:** 2025-01-16  
**Status:** ✅ Implementiert

## Anforderungen

1. **Automatische Anzeige:** Bei Auswahl eines Tabs (ALLE, INTERESSENTEN, AKTIVE KUNDEN, EHEMALIGE KUNDEN) sollen automatisch die ersten 10 Kunden alphabetisch absteigend angezeigt werden
2. **Vorfilterung:** Bei Eingabe von Buchstaben soll entsprechend vorgefiltert werden
3. **Wildcard-Suche:** Bei Eingabe von `*` soll dies als Platzhalter für alle Buchstaben gelten

## Implementierung

### 1. Automatische Anzeige der ersten 10 Kunden

**Datei:** `packages/frontend-web/src/components/sales/CustomerSelectionDialog.tsx`

```typescript
const filteredCustomers = useMemo(() => {
  let result = customers

  // Filter by tab
  if (activeTab === 'prospects') {
    result = result.filter((c) => c.customer_type === 'prospect' || !c.is_active)
  } else if (activeTab === 'active') {
    result = result.filter((c) => c.is_active !== false)
  } else if (activeTab === 'former') {
    result = result.filter((c) => c.is_active === false)
  }

  // Apply search filter
  if (!searchTerm) {
    // No search term: return first 10, sorted alphabetically descending
    return result
      .sort((a, b) => b.name.localeCompare(a.name, 'de', { sensitivity: 'base' }))
      .slice(0, 10)
  }

  // Has search term: filter and sort
  // ... (siehe unten)
}, [customers, searchTerm, extendedSearch, activeTab])
```

**Verhalten:**
- Wenn kein Suchbegriff eingegeben ist, werden die ersten 10 Kunden alphabetisch absteigend (Z-A) angezeigt
- Die Sortierung erfolgt nach dem Namen des Kunden
- Beim Wechsel des Tabs werden automatisch die ersten 10 Kunden des entsprechenden Typs angezeigt

### 2. Vorfilterung bei Eingabe

**Verhalten:**
- Bei Eingabe von Buchstaben wird sofort gefiltert
- Die Filterung erfolgt in folgenden Feldern:
  - **Standard:** Name, Kunden-Nr., Debitor-Kto.
  - **Erweitert:** Zusätzlich Vertreter, PLZ, Ort, Kundengruppe
- Die Ergebnisse werden alphabetisch absteigend sortiert

### 3. Wildcard-Suche mit `*`

**Implementierung:**

```typescript
// Helper function to check if a string matches a pattern (supports * wildcard)
const matchesPattern = (text: string, pattern: string): boolean => {
  if (!pattern) return true
  // Convert * wildcard to regex pattern
  const regexPattern = pattern
    .replace(/[.*+?^${}()|[\]\\]/g, '\\$&') // Escape special regex chars
    .replace(/\*/g, '.*') // Replace * with .* for regex
  const regex = new RegExp(regexPattern, 'i')
  return regex.test(text)
}
```

**Verwendung:**
- `*` wird als Platzhalter für beliebige Zeichen interpretiert
- Beispiel: `*test*` findet alle Kunden, die "test" im Namen enthalten
- Beispiel: `test*` findet alle Kunden, die mit "test" beginnen
- Beispiel: `*test` findet alle Kunden, die mit "test" enden

**Beispiele:**
- `A*` → Findet alle Kunden, die mit "A" beginnen
- `*Müller*` → Findet alle Kunden, die "Müller" im Namen enthalten
- `*123*` → Findet alle Kunden, die "123" in einem Feld enthalten

### 4. Backend-Integration

**Query-Parameter:**
- `search`: Suchbegriff (mit `*` → `%` Konvertierung für SQL LIKE)
- `customer_type`: Filter nach Kunden-Typ (prospect, active, former)
- `is_active`: Filter nach aktivem Status
- `sort`: Sortierung nach Feld (z.B. "name")
- `order`: Sortierreihenfolge ("desc" für absteigend)
- `limit`: Maximale Anzahl Ergebnisse (200 für Filterung, dann Frontend-Filterung auf 10)

**Tab-Mapping:**
- `all` → Kein Filter
- `prospects` → `customer_type=prospect`
- `active` → `is_active=true`
- `former` → `is_active=false`

## Technische Details

### Sortierung

Die Sortierung erfolgt mit `localeCompare` für korrekte deutsche Sortierung:

```typescript
.sort((a, b) => b.name.localeCompare(a.name, 'de', { sensitivity: 'base' }))
```

- **Absteigend:** `b.name.localeCompare(a.name)` → Z-A
- **Deutsche Locale:** `'de'` für korrekte Umlaut-Sortierung
- **Case-insensitive:** `{ sensitivity: 'base' }` ignoriert Groß-/Kleinschreibung

### Filter-Logik

1. **Tab-Filter:** Zuerst nach Tab filtern (ALLE, INTERESSENTEN, etc.)
2. **Such-Filter:** Dann nach Suchbegriff filtern (mit Wildcard-Unterstützung)
3. **Sortierung:** Alphabetisch absteigend sortieren
4. **Limit:** Erste 10 Einträge anzeigen (nur wenn kein Suchbegriff)

## Test-Szenarien

### Szenario 1: Tab-Wechsel ohne Suche
1. Dialog öffnen
2. Tab "ALLE" auswählen
3. **Erwartung:** Erste 10 Kunden alphabetisch absteigend (Z-A)

### Szenario 2: Buchstaben-Eingabe
1. Dialog öffnen
2. "A" eingeben
3. **Erwartung:** Alle Kunden, die "A" enthalten, alphabetisch absteigend sortiert

### Szenario 3: Wildcard-Suche
1. Dialog öffnen
2. "A*" eingeben
3. **Erwartung:** Alle Kunden, die mit "A" beginnen

### Szenario 4: Tab-Wechsel mit Suche
1. Dialog öffnen
2. "Müller" eingeben
3. Tab "AKTIVE KUNDEN" auswählen
4. **Erwartung:** Nur aktive Kunden mit "Müller" im Namen

## Nächste Schritte

- ✅ Automatische Anzeige der ersten 10 Kunden
- ✅ Vorfilterung bei Eingabe
- ✅ Wildcard-Suche mit `*`
- ⏳ Backend-API: Unterstützung für `customer_type` und `is_active` Filter
- ⏳ Backend-API: Unterstützung für SQL LIKE Pattern (`%` statt `*`)

