# VALEO Designsystem (Gap 021, 024)

Verbindliche UI-Patterns und Komponenten für alle neuen Seiten.

## Kernprinzipien

- **100 % neue Seiten nutzen DS-Komponenten** (Gap 021)
- **Touch-Targets ≥ 44 px** für Lager, Waage, Annahme (Gap 024)

## Komponenten-Basis

| Quelle | Verwendung |
|--------|------------|
| `@/components/ui/` | Radix-basierte Basiskomponenten (Button, Card, Input, Select, etc.) |
| `@/components/mask-builder/` | ObjectPage, ListReport, Wizard, OverviewPage |
| `@/components/ErrorState` | Fehler-Recovery |
| `@/components/BackButton` | Konsistente Navigation |

## Touch-Optimierung (Gap 024)

Für Tablet-, Lager- und Waagen-Masken:

```tsx
// Tailwind-Klassen
className="min-h-touch min-w-touch touch-manipulation"
```

- **Variable:** `--touch-target: 44px` (index.css)
- **Tailwind:** `min-h-touch`, `min-w-touch`
- **Bestehende Patterns:** `TouchBedienfeld` (POS), `QuickActionGrid` (Lager), `ScannerInput`

## Mask Builder

Neue Masken bevorzugt über Mask-Builder-Config statt Einzel-JSX:

- `ObjectPage` – Detail-Ansichten mit Tabs
- `ListReport` – filterbare Listen
- `Wizard` – mehrstufige Assistenten
- `OverviewPage` – Übersichten mit Karten

## Designsystem-Status

| Bereich | Status |
|---------|--------|
| Basiskomponenten | vorhanden (Radix) |
| Touch-Utilities | ergänzt (min-h-touch, min-w-touch) |
| Prozesspatterns | in MASKEN.md |
| Vollständiger DS-Katalog | ausstehend (Hauptstrang) |
