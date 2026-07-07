/**
 * Omnibox-Intent-Verträge (UIX-060).
 *
 * Der Intent-Compiler übersetzt natürliche Eingaben deterministisch in
 * Navigations-Pläne mit Vorschau — Mutationen sind hier per Vertrag
 * ausgeschlossen (Command-Drafts folgen erst mit UIX-070 über das
 * Confirmation-Ritual der Maske).
 */
import type { PaletteCommand } from '@/components/navigation/command-palette-model'

export interface IntentFilter {
  /** Query-Param-Schlüssel (Konvention: q, due_lt, due_gt, overdue) */
  key: string
  /** Anzeigelabel für die Vorschau-Chips ("überfällig", "Folkerts") */
  label: string
  value: string
}

export interface NavigateIntent {
  kind: 'navigate'
  command: PaletteCommand
  /** Zielpfad inkl. Query-String (Filter angehängt) */
  routePath: string
  filters: IntentFilter[]
  /** 0..1 — unter MIN_CONFIDENCE liefert der Compiler kind:'none' */
  confidence: number
  label: string
}

/**
 * Command-Draft (UIX-070): NL wird zu einer vorbereiteten Aktion, die durch das
 * volle Confirmation-Ritual der Maske laeuft (nie Auto-Submit). Nur fuer
 * safe+requiresConfirmation und moderate Aktionen — high/critical/forbidden
 * erreichen diesen Zweig per Sicherheitsmatrix nie.
 */
export interface CommandDraftIntent {
  kind: 'commandDraft'
  screenId: string
  actionKey: string
  /** Zielroute der Maske (fuer Ritual-Kontext / Fallback). */
  routePath: string
  /** Nur aus Schema-Feldern befuellt — keine Freitext-Payloads. */
  payloadDraft: Record<string, unknown>
  /** Pflichtfelder ohne erkannten Wert → Ritual fragt nach. */
  missingFields: string[]
  label: string
  confidence: number
}

/**
 * Degradations-Pfad (UIX-070): Maske oeffnen und Felder vorfuellen, aber nichts
 * armieren. Greift bei safe-Aktionen ohne Confirmation oder bei Konfidenz < 0.75.
 */
export interface FormPrefillIntent {
  kind: 'formPrefill'
  screenId: string
  actionKey?: string
  routePath: string
  payloadDraft: Record<string, unknown>
  label: string
  confidence: number
}

export interface NoneIntent {
  kind: 'none'
  /** Top-Vorschläge (Command-Labels) für die Leer-Hilfe */
  suggestions: string[]
}

export type IntentPlan = NavigateIntent | CommandDraftIntent | FormPrefillIntent | NoneIntent

export interface CompileOptions {
  /** heutiges Datum für deterministische Tests (ISO yyyy-mm-dd) */
  today?: string
  maxResults?: number
}
