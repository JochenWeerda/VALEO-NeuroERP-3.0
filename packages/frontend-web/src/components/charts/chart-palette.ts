/**
 * Zentrale Chart-Palette aus Design-Tokens (DESIGN-CHARTS-TOKEN-006).
 *
 * Alle Farben sind CSS-Custom-Property-Referenzen und damit theme-reaktiv
 * (:root hell, .dark/.theme-warehouse dunkel — Werte in src/index.css,
 * beide Modi mit dem dataviz-Sechs-Checks-Validator bestanden).
 *
 * Regeln:
 * - Kategoriale Serien erhalten die Slots 1..6 in fester Reihenfolge,
 *   nie zyklisch: ab dem 7. Element fällt alles auf den neutralen
 *   Sonstige-Slot (zusammenfassen statt neue Hues erfinden).
 * - Grün/Rot sind den Statusfarben vorbehalten: eine Serie, die fachlich
 *   „gut/schlecht" bedeutet, nutzt CHART_POSITIVE/CHART_NEGATIVE — eine
 *   bloße „Serie 4" nie.
 * - Soll-/Referenzlinien sind bewusst rezessiv (CHART_TARGET, gestrichelt).
 */

/** Kategoriale Slots in fester Reihenfolge — nie umsortieren, nie zyklisch vergeben. */
export const CHART_SERIES = [
  'hsl(var(--chart-1-hsl))', // Ozeanblau
  'hsl(var(--chart-2-hsl))', // Bernstein
  'hsl(var(--chart-3-hsl))', // Petrol
  'hsl(var(--chart-4-hsl))', // Violett
  'hsl(var(--chart-5-hsl))', // Beere
  'hsl(var(--chart-6-hsl))', // Erdbraun
] as const

/** Neutraler Slot für „Sonstige"/Überlauf jenseits von 6 Kategorien. */
export const CHART_OTHER = 'hsl(var(--chart-other-hsl))'

/** Soll-/Referenzlinien (rezessiv; im Chart gestrichelt zeichnen). */
export const CHART_TARGET = 'hsl(var(--chart-target-hsl))'

/** Statusgebundene Serienfarben — nur wenn die Serie fachlich gut/schlecht bedeutet. */
export const CHART_POSITIVE = 'hsl(var(--status-success-hsl))'
export const CHART_NEGATIVE = 'hsl(var(--status-error-hsl))'
export const CHART_WARNING = 'hsl(var(--status-warning-hsl))'
export const CHART_INFO = 'hsl(var(--status-info-hsl))'

/** Chart-Anatomie: Gitterlinien und Achsentext. */
export const CHART_GRID = 'hsl(var(--chart-grid-hsl))'
export const CHART_AXIS_TEXT = 'hsl(var(--chart-axis-text-hsl))'

/**
 * Farbe für den n-ten kategorialen Slot (0-basiert).
 * Ab Index 6 wird bewusst NICHT zykliert, sondern der neutrale
 * Sonstige-Slot geliefert — mehr als 6 Kategorien gehören fachlich
 * zusammengefasst (Top-N + Sonstige) statt farblich unterschieden.
 */
export function chartSeriesColor(index: number): string {
  return index >= 0 && index < CHART_SERIES.length ? CHART_SERIES[index] : CHART_OTHER
}

/**
 * Transparente Füllung zu einem Slot (Flächen-Charts, Legenden-Chips).
 * `alpha` in [0..1].
 */
export function chartSeriesFill(index: number, alpha = 0.12): string {
  const token = index >= 0 && index < CHART_SERIES.length ? `--chart-${index + 1}-hsl` : '--chart-other-hsl'
  return `hsl(var(${token}) / ${alpha})`
}
