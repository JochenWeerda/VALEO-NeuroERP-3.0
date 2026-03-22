/**
 * VALEO NeuroERP Design Tokens — Gap 021
 * Einheitliches Designsystem: Farben, Abstände, Typografie, Breakpoints
 *
 * Verwendung: import { colors, spacing, typography } from '@/lib/design-tokens'
 */

// ─── Farben ──────────────────────────────────────────────────────────────────

export const colors = {
  // Status-Farben (konsistent über alle Masken)
  success: {
    bg: 'bg-green-50',
    border: 'border-green-500',
    text: 'text-green-700',
    badge: 'bg-green-100 text-green-800 border-green-200',
  },
  warning: {
    bg: 'bg-orange-50',
    border: 'border-orange-500',
    text: 'text-orange-700',
    badge: 'bg-amber-100 text-amber-800 border-amber-200',
  },
  error: {
    bg: 'bg-red-50',
    border: 'border-red-500',
    text: 'text-red-700',
    badge: 'bg-red-100 text-red-800 border-red-200',
  },
  info: {
    bg: 'bg-blue-50',
    border: 'border-blue-300',
    text: 'text-blue-700',
    badge: 'bg-blue-100 text-blue-800 border-blue-200',
  },
  neutral: {
    bg: 'bg-slate-50',
    border: 'border-slate-200',
    text: 'text-slate-700',
    badge: 'bg-slate-100 text-slate-800 border-slate-200',
  },
  agent: {
    bg: 'bg-violet-50',
    border: 'border-violet-300',
    text: 'text-violet-700',
    badge: 'bg-violet-100 text-violet-800 border-violet-200',
  },
} as const

// ─── Abstände (4px-Grid) ─────────────────────────────────────────────────────

export const spacing = {
  xs: 'gap-1',    // 4px
  sm: 'gap-2',    // 8px
  md: 'gap-3',    // 12px
  lg: 'gap-4',    // 16px
  xl: 'gap-6',    // 24px
  '2xl': 'gap-8', // 32px
  pageInset: 'p-6',
  cardInset: 'p-4',
  cardInsetSm: 'p-3',
} as const

// ─── Typografie ───────────────────────────────────────────────────────────────

export const typography = {
  pageTitle: 'text-3xl font-bold',
  pageSubtitle: 'text-muted-foreground',
  sectionTitle: 'text-xl font-semibold',
  cardTitle: 'text-sm font-medium',
  metricValue: 'text-2xl font-bold',
  metricValueLg: 'text-3xl font-bold',
  label: 'text-sm',
  labelSm: 'text-xs',
  mono: 'font-mono text-sm',
  monoSm: 'font-mono text-xs',
} as const

// ─── Responsive Breakpoints ───────────────────────────────────────────────────

export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const

// ─── Touch-Targets (Gap 024: min 44x44dp) ────────────────────────────────────

export const touch = {
  minTarget: 'min-h-[44px] min-w-[44px]',
  buttonLg: 'h-12 px-6 text-base',
  inputLg: 'h-12 text-base',
  spacing: 'gap-3', // 12px minimum between touch targets
} as const

// ─── Masken-Komponent-Status ──────────────────────────────────────────────────

export const maskComponents = {
  ObjectPage: 'complete',   // Detail-Ansicht mit Tabs
  ListReport: 'complete',   // Filterliste
  Wizard: 'complete',       // Mehrstufige Formulare
  Worklist: 'complete',     // Aufgabenlisten
  OverviewPage: 'complete', // Dashboards
  FormBuilder: 'complete',  // Konfigurierbare Formulare
} as const

// ─── Agent-Capability UI Konventionen ────────────────────────────────────────

export const agentUx = {
  /** Assistierter Modus: Vorschlag vor Benutzer-Aktion */
  assisted: 'AgentSuggestionBadge + autoTrigger=false',
  /** Produktiver Modus: Direkte Übernahme nach Bestätigung */
  productive: 'AgentSuggestionBadge + autoTrigger=true',
  /** Hintergrund-Aktivität: SSE-Stream ohne UI-Unterbrechung */
  background: 'AgentProcessPanel (returns null when idle)',
} as const
