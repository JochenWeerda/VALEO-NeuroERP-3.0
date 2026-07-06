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

export interface NoneIntent {
  kind: 'none'
  /** Top-Vorschläge (Command-Labels) für die Leer-Hilfe */
  suggestions: string[]
}

export type IntentPlan = NavigateIntent | NoneIntent

export interface CompileOptions {
  /** heutiges Datum für deterministische Tests (ISO yyyy-mm-dd) */
  today?: string
  maxResults?: number
}
