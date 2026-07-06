/**
 * Omnibox-Intent-Compiler v1 (UIX-060) — deterministisch, ohne LLM.
 *
 * Pipeline: Normalisierung → Datums-/Vergleichs-Token → Mehrwort-Matching
 * gegen den PaletteCommand-Katalog → Filter-Extraktion aus Rest-Tokens →
 * Konfidenz. Read-only per Vertrag: Ergebnis ist immer Navigation+Filter;
 * Command-Drafts folgen erst mit UIX-070 über das Confirmation-Ritual.
 */
import type { PaletteCommand } from '@/components/navigation/command-palette-model'
import type { CompileOptions, IntentFilter, IntentPlan, NavigateIntent } from './types'

export const MIN_CONFIDENCE = 0.35

/** Umlaut-Folding + lowercase; erhält Ziffern, '>' und '.' für Datumsphrasen. */
export function normalize(text: string): string {
  return text
    .toLowerCase()
    .replace(/ä/g, 'ae')
    .replace(/ö/g, 'oe')
    .replace(/ü/g, 'ue')
    .replace(/ß/g, 'ss')
    .replace(/[^\p{L}\p{N}>< .-]/gu, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

function tokenize(text: string): string[] {
  return normalize(text).split(' ').filter((t) => t.length > 0)
}

const STOPWORDS = new Set([
  'der', 'die', 'das', 'den', 'dem', 'ein', 'eine', 'mit', 'und', 'oder',
  'fuer', 'von', 'im', 'in', 'am', 'an', 'auf', 'zeig', 'zeige', 'mir',
  'alle', 'oeffne', 'bitte', 'was', 'steht', 'los', 'ist',
])

interface DateFilterMatch {
  filters: IntentFilter[]
  consumed: Set<string>
}

/**
 * Erkennt Zeit-/Vergleichsphrasen und übersetzt sie in Query-Param-Filter
 * (Konvention: overdue=1, date/from/to/due_lt als ISO-Datum, q=Suchtext).
 */
export function extractDateFilters(tokens: string[], todayIso: string): DateFilterMatch {
  const filters: IntentFilter[] = []
  const consumed = new Set<string>()
  const today = new Date(`${todayIso}T00:00:00Z`)
  const iso = (d: Date): string => d.toISOString().slice(0, 10)
  const joined = tokens.join(' ')

  if (/\bueberfaellig\w*\b/.test(joined)) {
    filters.push({ key: 'overdue', label: 'überfällig', value: '1' })
    for (const t of tokens) if (t.startsWith('ueberfaellig')) consumed.add(t)
  }

  if (/\bheute\b/.test(joined)) {
    filters.push({ key: 'date', label: 'heute', value: todayIso })
    consumed.add('heute')
  }

  // "naechste woche" → Mo–So der Folgewoche
  if (/\bnaechste\w* woche\b/.test(joined)) {
    const dow = today.getUTCDay() === 0 ? 7 : today.getUTCDay()
    const nextMonday = new Date(today)
    nextMonday.setUTCDate(today.getUTCDate() + (8 - dow))
    const nextSunday = new Date(nextMonday)
    nextSunday.setUTCDate(nextMonday.getUTCDate() + 6)
    filters.push({ key: 'from', label: 'nächste Woche', value: iso(nextMonday) })
    filters.push({ key: 'to', label: 'bis', value: iso(nextSunday) })
    for (const t of tokens) if (t.startsWith('naechste') || t === 'woche') consumed.add(t)
  }

  // "> 30 tage" / "aelter als 30 tage" → due_lt = heute − N
  const older = joined.match(/(?:>\s*|aelter als )(\d{1,3}) ?tage?\w*/)
  if (older) {
    const days = Number(older[1])
    const cutoff = new Date(today)
    cutoff.setUTCDate(today.getUTCDate() - days)
    filters.push({ key: 'due_lt', label: `älter als ${days} Tage`, value: iso(cutoff) })
    for (const t of tokens) {
      if (t === '>' || t === String(days) || t.startsWith('tage') || t === 'aelter' || t === 'als') {
        consumed.add(t)
      }
    }
  }

  return { filters, consumed }
}

interface ScoredCommand {
  command: PaletteCommand
  score: number
  matchedTokens: Set<string>
}

/**
 * Mehrwort-Matching: jedes Query-Token zählt, wenn es Label ODER Keyword
 * trifft (Präfix ab 3 Zeichen). Score = gewichteter Anteil getroffener Tokens.
 */
/** Gemeinsamer Wortanfang ≥5 Zeichen deckt Flexionen (zahlungslauf/-läufe). */
function sharesStem(a: string, b: string): boolean {
  const min = Math.min(a.length, b.length)
  if (min < 5) return false
  let common = 0
  while (common < min && a[common] === b[common]) common += 1
  return common >= 5 && common >= Math.ceil(min * 0.7)
}

export function scoreCommand(command: PaletteCommand, tokens: string[]): ScoredCommand {
  const label = normalize(command.label)
  const labelTokens = label.split(' ')
  const keywords = command.keywords.map((k) => normalize(k))
  const matched = new Set<string>()
  let weight = 0

  for (const token of tokens) {
    const exactLabel = labelTokens.includes(token)
    const inLabel =
      exactLabel ||
      label.includes(token) ||
      labelTokens.some((lt) => (lt.startsWith(token) && token.length >= 3) || sharesStem(lt, token))
    const inKeywords = keywords.some(
      (k) =>
        k === token ||
        (k.startsWith(token) && token.length >= 3) ||
        k.includes(` ${token}`) ||
        sharesStem(k, token),
    )
    if (inLabel) {
      matched.add(token)
      weight += exactLabel ? 1.2 : 1.0 // exakter Label-Treffer schlägt Stamm-Treffer
    } else if (inKeywords) {
      matched.add(token)
      weight += keywords.includes(token) ? 0.9 : 0.8
    }
  }
  const score = tokens.length === 0 ? 0 : weight / tokens.length
  return { command, score, matchedTokens: matched }
}

function buildRoutePath(command: PaletteCommand, filters: IntentFilter[]): string {
  const basePath = typeof command.actionParams?.path === 'string' ? command.actionParams.path : ''
  if (!basePath || filters.length === 0) return basePath
  const params = new URLSearchParams()
  for (const f of filters) params.append(f.key, f.value)
  return `${basePath}${basePath.includes('?') ? '&' : '?'}${params.toString()}`
}

interface CompileCore {
  plans: NavigateIntent[]
  suggestions: string[]
}

function compileCore(
  query: string,
  catalog: PaletteCommand[],
  options: CompileOptions,
): CompileCore {
  const todayIso = options.today ?? new Date().toISOString().slice(0, 10)
  const maxResults = options.maxResults ?? 3
  const allTokens = tokenize(query)
  if (allTokens.length === 0) return { plans: [], suggestions: [] }

  const { filters: dateFilters, consumed } = extractDateFilters(allTokens, todayIso)
  const searchTokens = allTokens.filter((t) => !consumed.has(t) && !STOPWORDS.has(t))
  if (searchTokens.length === 0 && dateFilters.length === 0) {
    return { plans: [], suggestions: [] }
  }

  // Nur navigierbare Kommandos (mit Pfad) — Event-Kommandos bleiben der Liste
  const navigable = catalog.filter((c) => typeof c.actionParams?.path === 'string')
  const effectiveTokens = searchTokens.length > 0 ? searchTokens : allTokens
  const scored = navigable
    .map((c) => scoreCommand(c, effectiveTokens))
    .filter((s) => s.score > 0)
    .sort((a, b) => b.score - a.score)

  const best = scored[0]
  if (!best || best.score < MIN_CONFIDENCE) {
    return { plans: [], suggestions: scored.slice(0, 3).map((s) => s.command.label) }
  }

  // Unerklärte Rest-Tokens werden zum Freitext-Filter q (z. B. "folkerts")
  const rest = searchTokens.filter((t) => !best.matchedTokens.has(t))
  const bestFilters: IntentFilter[] = [...dateFilters]
  if (rest.length > 0) {
    bestFilters.push({ key: 'q', label: rest.join(' '), value: rest.join(' ') })
  }

  const coverage = searchTokens.length === 0
    ? 1
    : (searchTokens.length - rest.length) / searchTokens.length
  const bestConfidence = Math.min(1, best.score * (0.6 + 0.4 * coverage))

  const plans: NavigateIntent[] = scored.slice(0, maxResults).map((s, idx) => {
    const filters = idx === 0 ? bestFilters : dateFilters
    return {
      kind: 'navigate',
      command: s.command,
      routePath: buildRoutePath(s.command, filters),
      filters,
      confidence: idx === 0 ? bestConfidence : Math.min(1, s.score * 0.6),
      label: s.command.label,
    }
  })
  return { plans, suggestions: [] }
}

/** Bester Plan oder none — die Einzelergebnis-API für Enter-Verhalten. */
export function compileIntent(
  query: string,
  catalog: PaletteCommand[],
  options: CompileOptions = {},
): IntentPlan {
  const { plans, suggestions } = compileCore(query, catalog, options)
  return plans[0] ?? { kind: 'none', suggestions }
}

/** Top-N-Pläne für die "Verstanden als"-Vorschau (Index 0 = bester Plan). */
export function compileIntents(
  query: string,
  catalog: PaletteCommand[],
  options: CompileOptions = {},
): NavigateIntent[] {
  return compileCore(query, catalog, options).plans
}
