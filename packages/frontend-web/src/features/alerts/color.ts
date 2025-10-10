/**
 * Color-Utility für KPI-Heatmap & Alert-System
 * Konvertiert Scores in Severity-Levels und Farben
 */

const SEVERITY_THRESHOLD_CRITICAL = -0.4
const SEVERITY_THRESHOLD_WARNING = -0.15
const SCORE_MIN = -1
const SCORE_MAX = 1

const COLOR_RED_100 = "#FEE2E2"
const COLOR_AMBER_100 = "#FEF3C7"
const COLOR_CYAN_50 = "#ECFEFF"
const COLOR_EMERALD_100 = "#D1FAE5"
const COLOR_EMERALD_200 = "#A7F3D0"

const COLOR_RED_300 = "#FCA5A5"
const COLOR_AMBER_300 = "#FCD34D"
const COLOR_EMERALD_300 = "#6EE7B7"

export type Severity = "ok" | "warn" | "crit"

/**
 * Konvertiert einen Score in ein Severity-Level
 * @param score - Score zwischen -1 (schlecht) und 1 (gut)
 * @returns Severity-Level
 */
export function toSeverity(score: number): Severity {
  if (score <= SEVERITY_THRESHOLD_CRITICAL) {
    return "crit"
  }
  if (score <= SEVERITY_THRESHOLD_WARNING) {
    return "warn"
  }
  return "ok"
}

/**
 * Gibt die Hintergrundfarbe für einen Score zurück
 * @param score - Score zwischen -1 (schlecht) und 1 (gut)
 * @returns Hex-Farbcode für Tailwind-kompatible Inline-Styles
 */
export function heatColor(score: number): string {
  const normalizedScore = Math.max(SCORE_MIN, Math.min(SCORE_MAX, score))

  if (normalizedScore <= SEVERITY_THRESHOLD_CRITICAL) {
    return COLOR_RED_100
  }
  if (normalizedScore <= SEVERITY_THRESHOLD_WARNING) {
    return COLOR_AMBER_100
  }
  if (normalizedScore < SEVERITY_THRESHOLD_WARNING) {
    return COLOR_CYAN_50
  }
  if (normalizedScore < SEVERITY_THRESHOLD_CRITICAL * -1) {
    return COLOR_EMERALD_100
  }
  return COLOR_EMERALD_200
}

/**
 * Gibt die Border-Farbe für ein Severity-Level zurück
 * @param severity - Severity-Level
 * @returns Hex-Farbcode für Border
 */
export function severityBorder(severity: Severity): string {
  if (severity === "crit") {
    return COLOR_RED_300
  }
  if (severity === "warn") {
    return COLOR_AMBER_300
  }
  return COLOR_EMERALD_300
}
