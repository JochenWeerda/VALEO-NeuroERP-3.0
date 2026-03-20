# VALEO Designsystem (Gap 021, 024)

Verbindliche UI-Patterns und Komponenten fuer alle neuen Seiten.

## Kernprinzipien

- **100 % neue Seiten nutzen DS-Komponenten** (Gap 021)
- **Touch-Targets >= 44 px** fuer Lager, Waage, Annahme (Gap 024)
- **Neue Seiten nutzen verpflichtend `PageSurface` + `PageToolbar` + Pattern-Komponente oder explizite DS-Sektionen**
- **Bestehende Seiten werden bei Anpassungen auf dieselbe Surface-/Section-Logik zurueckgefuehrt**

## Komponenten-Basis

| Quelle | Verwendung |
|--------|------------|
| `@/components/ui/` | Radix-basierte Basiskomponenten (Button, Card, Input, Select, etc.) |
| `@/components/mask-builder/` | ObjectPage, ListReport, Wizard, OverviewPage |
| `@/components/patterns/PageSurface` | Verbindliche Seitenhuelle und Sektionen fuer neue und modernisierte Seiten |
| `@/components/ErrorState` | Fehler-Recovery |
| `@/components/BackButton` | Konsistente Navigation |

## Touch-Optimierung (Gap 024)

Fuer Tablet-, Lager- und Waagen-Masken:

```tsx
className="min-h-touch min-w-touch touch-manipulation"
```

- **Variable:** `--touch-target: 44px` (index.css)
- **Tailwind:** `min-h-touch`, `min-w-touch`
- **Bestehende Patterns:** `TouchBedienfeld` (POS), `QuickActionGrid` (Lager), `ScannerInput`
- **Toolbar- und Overflow-Aktionen:** ebenfalls `min-h-touch min-w-touch touch-manipulation`

## Mask Builder

Neue Masken bevorzugt ueber Mask-Builder-Config statt Einzel-JSX:

- `ObjectPage` - Detail-Ansichten mit Tabs
- `ListReport` - filterbare Listen
- `Wizard` - mehrstufige Assistenten
- `OverviewPage` - Uebersichten mit Karten

## Verbindliche Seitenregeln

- Neue Seiten:
  - `PageToolbar` als einzige Aktionsleiste
  - `PageSurface` als Seitenrahmen
  - fachliche Inhalte in `PageSection` oder bestehenden Pattern-Komponenten
- Bestehende Seiten:
  - bei Refactorings keine freien `p-6 + Card`-Layouts mehr neu einfuehren
  - stattdessen auf `PageSurface` und konsistente Section-Struktur umstellen
- Pattern-Komponenten:
  - `OverviewPage`, `ObjectPage`, `ListReport`, `Wizard` tragen den DS-Rahmen zentral, damit Bestandsseiten automatisch mitgezogen werden

## Rueckwirkende Umstellung

Diese Seiten bzw. Seitenfamilien sind jetzt bereits an den neuen DS-Rahmen angeschlossen:

- alle Seiten, die `OverviewPage`, `ObjectPage`, `ListReport` oder `Wizard` verwenden
- `packages/frontend-web/src/pages/sales/orders-modern.tsx`
- `packages/frontend-web/src/pages/controlling/benchmark-cockpit.tsx`

## Designsystem-Status

| Bereich | Status |
|---------|--------|
| Basiskomponenten | vorhanden (Radix) |
| Touch-Utilities | vorhanden und in Toolbar/Patterns verankert |
| Process-Patterns | zentral ueber `PageSurface` + Pattern-Komponenten gehaertet |
| Vollstaendiger DS-Katalog | weiterhin ausstehend |
